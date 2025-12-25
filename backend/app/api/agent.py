"""Agent interaction API routes with SSE + REST support."""

import asyncio
import json
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.api.auth import get_current_user
from app.core.logging import get_logger
from app.models import EventType, TaskRequest, TakeoverResponse, UserInfo
from app.agents.glm.prompts import get_system_prompt
from app.services.database import get_database_service
from app.agents import AgentFactory, BaseAgentService

logger = get_logger("agent")

router = APIRouter()


# Store active agent instances and control events
_agents: dict[str, BaseAgentService] = {}
_takeover_events: dict[str, asyncio.Event] = {}
_stop_events: dict[str, asyncio.Event] = {}
_task_running: dict[str, bool] = {}
_task_locks: dict[str, asyncio.Lock] = {}  # Locks to prevent concurrent task execution
_task_start_times: dict[str, float] = {}  # Track when tasks started for timeout detection

# Maximum task duration before considering it stale (10 minutes)
TASK_TIMEOUT_SECONDS = 600


def get_task_lock(session_id: str) -> asyncio.Lock:
    """Get or create a lock for a session to prevent concurrent tasks."""
    if session_id not in _task_locks:
        _task_locks[session_id] = asyncio.Lock()
    return _task_locks[session_id]


def check_and_cleanup_stale_task(session_id: str) -> bool:
    """
    Check if a task is stale (running too long) and clean it up.
    Returns True if a stale task was cleaned up.
    """
    import time
    
    task_lock = get_task_lock(session_id)
    if not task_lock.locked():
        return False
    
    start_time = _task_start_times.get(session_id)
    if start_time is None:
        # No start time recorded, assume it's stale
        logger.warning(f"Task for session {session_id} has no start time, cleaning up")
    else:
        elapsed = time.time() - start_time
        if elapsed < TASK_TIMEOUT_SECONDS:
            return False  # Task is still within timeout
        logger.warning(f"Task for session {session_id} timed out after {elapsed:.1f}s, cleaning up")
    
    # Clean up stale task
    try:
        task_lock.release()
    except RuntimeError:
        pass  # Lock wasn't held
    
    _task_running[session_id] = False
    if session_id in _task_start_times:
        del _task_start_times[session_id]
    
    # Stop the agent if it exists
    if session_id in _agents:
        _agents[session_id].stop()
    
    return True


# Get system prompt
SYSTEM_PROMPT = get_system_prompt("cn")


async def get_session_from_db(session_id: str, user_id: str) -> Optional[dict]:
    """Get session from database."""
    db = get_database_service()
    return await db.get_session(session_id, user_id)


def format_sse_event(event_type: str, data: dict) -> str:
    """Format data as SSE event."""
    json_data = json.dumps(data, ensure_ascii=False, default=str)
    return f"event: {event_type}\ndata: {json_data}\n\n"


async def validate_session(session_id: str, user_id: str) -> dict:
    """Validate session and return session data."""
    session = await get_session_from_db(session_id, user_id)

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.get("status") != "active":
        raise HTTPException(
            status_code=400,
            detail=f"Session is not active (status: {session.get('status')})"
        )

    device_id = session.get("device_id")
    if not device_id:
        raise HTTPException(status_code=400, detail="No device connected to this session")

    agentbay_session_id = session.get("agentbay_session_id")
    if not agentbay_session_id:
        raise HTTPException(status_code=400, detail="No AgentBay session ID found")

    return session


async def get_or_create_agent(
    session_id: str,
    session: dict,
    agent_type: str = "glm"
) -> BaseAgentService:
    """Get existing agent or create a new one."""
    if session_id in _agents:
        return _agents[session_id]

    device_id = session.get("device_id")
    agentbay_session_id = session.get("agentbay_session_id")

    # Use session's agent_type if available
    session_agent_type = session.get("agent_type", agent_type)
    if session_agent_type:
        agent_type = session_agent_type

    # Create takeover event
    takeover_event = asyncio.Event()
    _takeover_events[session_id] = takeover_event

    # Create stop event
    stop_event = asyncio.Event()
    _stop_events[session_id] = stop_event

    # Create takeover callback
    async def on_takeover(message: str):
        """Called when agent requests takeover."""
        takeover_event.clear()
        await takeover_event.wait()

    # Create agent instance using factory
    try:
        agent = AgentFactory.create_agent(
            agent_type=agent_type,
            device_id=device_id,
            on_takeover=on_takeover,
            session_id=agentbay_session_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    _agents[session_id] = agent
    logger.info(f"Created {agent_type} agent for session {session_id}")

    return agent


def cleanup_session(session_id: str):
    """Cleanup session resources."""
    if session_id in _agents:
        del _agents[session_id]
    if session_id in _takeover_events:
        del _takeover_events[session_id]
    if session_id in _stop_events:
        del _stop_events[session_id]
    if session_id in _task_running:
        del _task_running[session_id]
    if session_id in _task_start_times:
        del _task_start_times[session_id]


@router.post("/{session_id}/task")
async def run_task_stream(
    session_id: UUID,
    request: TaskRequest,
    current_user: UserInfo = Depends(get_current_user),
    agent_type: str = "glm",
):
    """
    Run a task with SSE streaming response.

    This endpoint streams events as Server-Sent Events (SSE).

    Event types:
    - ready: Connection established
    - thinking: Agent is thinking (contains chunk and full text)
    - action: Agent performed an action
    - screenshot: New screenshot available
    - takeover: Manual intervention required
    - completed: Task completed successfully
    - error: An error occurred
    - stopped: Task was stopped by user

    Query params:
    - agent_type: Agent type to use ("glm" | "gelab"), default "glm"
    """
    session_id_str = str(session_id)
    
    logger.info(f"[API] Task request: session={session_id_str[:8]}... task={request.task[:50]}{'...' if len(request.task) > 50 else ''}")

    # Validate session
    session = await validate_session(session_id_str, current_user.id)
    logger.debug(f"[API] Session validated: device={session.get('device_id')}, agent_type={session.get('agent_type')}")

    # Get lock for this session to prevent concurrent task execution
    task_lock = get_task_lock(session_id_str)

    # Try to acquire lock without blocking to check if task is running
    if task_lock.locked():
        # Check if the task is stale and clean it up
        if check_and_cleanup_stale_task(session_id_str):
            logger.info(f"[API] Cleaned up stale task for session {session_id_str}")
        else:
            logger.warning(f"[API] Task rejected: concurrent task running for session {session_id_str}")
            raise HTTPException(status_code=409, detail="A task is already running for this session")

    # Get or create agent
    agent = await get_or_create_agent(session_id_str, session, agent_type)
    logger.info(f"[API] Agent ready: type={agent.agent_type}")

    task = request.task
    if not task:
        raise HTTPException(status_code=400, detail="Task is required")

    # Save user message to database
    db = get_database_service()
    await db.create_conversation(
        session_id=session_id_str,
        role="user",
        content=task,
    )

    async def event_generator():
        """Generate SSE events from agent execution."""
        nonlocal session_id_str

        all_steps = []
        current_step = {"stepNumber": 0}
        task_completed = False

        import time
        
        # Acquire lock for the duration of task execution
        await task_lock.acquire()
        _task_running[session_id_str] = True
        _task_start_times[session_id_str] = time.time()

        try:
            # Reset stop event
            if session_id_str in _stop_events:
                _stop_events[session_id_str].clear()

            # Send ready event
            yield format_sse_event("ready", {
                "session_id": session_id_str,
                "device_id": session.get("device_id"),
            })

            # Helper function to save collected steps
            async def save_conversation_if_needed(message: str = "任务未完成"):
                nonlocal all_steps, current_step
                # Add current step if it has content
                if current_step.get("thinking") or current_step.get("action"):
                    all_steps.append(current_step.copy())
                # Save if there are any steps
                if all_steps:
                    await db.create_conversation(
                        session_id=session_id_str,
                        role="assistant",
                        content=message,
                        thinking=None,
                        action={"steps": all_steps},
                    )
                    # Clear to prevent double saving
                    all_steps = []
                    current_step = {}

            # Stream events from agent
            async for event in agent.run_task(task, SYSTEM_PROMPT):
                # Check if stop was requested
                if session_id_str in _stop_events and _stop_events[session_id_str].is_set():
                    agent.stop()
                    # Save collected steps before stopping
                    await save_conversation_if_needed("任务已被用户停止")
                    yield format_sse_event("stopped", {"message": "任务已停止"})
                    break

                # Collect steps for saving (before sending to client)
                if event.type == EventType.THINKING:
                    thinking_content = event.data.get("full", "")
                    if current_step.get("action") is not None:
                        if current_step.get("thinking") or current_step.get("action"):
                            all_steps.append(current_step.copy())
                        current_step = {
                            "stepNumber": len(all_steps) + 1,
                            "thinking": thinking_content,
                            "status": "thinking"
                        }
                    else:
                        current_step["stepNumber"] = len(all_steps) + 1
                        current_step["thinking"] = thinking_content
                        current_step["status"] = "thinking"

                elif event.type == EventType.ACTION:
                    action_data = event.data.get("action")
                    current_step["action"] = action_data
                    current_step["status"] = "completed"

                elif event.type == EventType.COMPLETED:
                    task_completed = True
                    task_duration = time.time() - _task_start_times.get(session_id_str, time.time())
                    logger.info(f"[API] Task completed: session={session_id_str[:8]}... steps={len(all_steps)+1} duration={task_duration:.2f}s")
                    # Save assistant message BEFORE sending to client
                    # This ensures the message is persisted even if client disconnects
                    await save_conversation_if_needed(event.data.get("message", "任务完成"))

                # Send event to client (after saving for COMPLETED event)
                yield format_sse_event(event.type.value, {
                    **event.data,
                    "timestamp": event.timestamp.isoformat(),
                })

        except asyncio.CancelledError:
            # Connection was aborted by client
            logger.info(f"SSE connection cancelled for session {session_id_str}")
            # Try to stop the agent gracefully
            if session_id_str in _agents:
                _agents[session_id_str].stop()
            # Save collected steps before exiting
            try:
                await save_conversation_if_needed("任务被中断")
            except Exception as save_error:
                logger.error(f"Failed to save conversation on cancel: {save_error}")
            # Don't yield here as connection is already closed
        except GeneratorExit:
            # Client disconnected
            logger.info(f"Client disconnected for session {session_id_str}")
            if session_id_str in _agents:
                _agents[session_id_str].stop()
            # Save collected steps before exiting
            try:
                # Add current step if it has content
                if current_step.get("thinking") or current_step.get("action"):
                    all_steps.append(current_step.copy())
                # Save if there are any steps
                if all_steps:
                    # Use create_task since we're in GeneratorExit context
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        asyncio.create_task(db.create_conversation(
                            session_id=session_id_str,
                            role="assistant",
                            content="任务被中断",
                            thinking=None,
                            action={"steps": all_steps},
                        ))
            except Exception as save_error:
                logger.error(f"Failed to save conversation on disconnect: {save_error}")
        except Exception as e:
            logger.error(f"Error during task execution: {e}", exc_info=True)
            # Save collected steps before returning error
            try:
                await save_conversation_if_needed(f"任务出错: {str(e)}")
            except Exception as save_error:
                logger.error(f"Failed to save conversation on error: {save_error}")
            yield format_sse_event("error", {"message": str(e)})
        finally:
            _task_running[session_id_str] = False
            if session_id_str in _task_start_times:
                del _task_start_times[session_id_str]
            task_lock.release()
            logger.info(f"Task finished for session {session_id_str}, completed={task_completed}")

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


@router.post("/{session_id}/stop")
async def stop_task(
    session_id: UUID,
    current_user: UserInfo = Depends(get_current_user),
    force: bool = False,
):
    """
    Stop the currently running task.
    
    Query params:
    - force: If True, forcefully release the task lock even if the task is stuck.
             Use this if a task is stuck and you can't start a new one.
    """
    session_id_str = str(session_id)

    # Validate session ownership
    session = await get_session_from_db(session_id_str, current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Check if task is running
    if not _task_running.get(session_id_str, False):
        # Even if no task is marked as running, check if lock is stuck
        task_lock = get_task_lock(session_id_str)
        if task_lock.locked() and force:
            # Force release the stuck lock
            try:
                task_lock.release()
                logger.info(f"Force released stuck lock for session {session_id_str}")
                return {"stopped": True, "message": "Force released stuck lock"}
            except RuntimeError:
                # Lock was not held, which is fine
                pass
        return {"stopped": False, "message": "No task is running"}

    # Set stop event
    if session_id_str in _stop_events:
        _stop_events[session_id_str].set()

    # Also call stop on the agent directly
    if session_id_str in _agents:
        _agents[session_id_str].stop()

    # If force mode, also release the lock and clean up
    if force:
        task_lock = get_task_lock(session_id_str)
        if task_lock.locked():
            try:
                task_lock.release()
                logger.info(f"Force released lock for session {session_id_str}")
            except RuntimeError:
                # Lock was not held by this task, which is fine
                pass
        # Clean up task running state
        _task_running[session_id_str] = False
        return {"stopped": True, "message": "Task force stopped and lock released"}

    return {"stopped": True, "message": "Stop signal sent"}


@router.post("/{session_id}/takeover/complete", response_model=TakeoverResponse)
async def complete_takeover(
    session_id: UUID,
    current_user: UserInfo = Depends(get_current_user),
):
    """Signal that manual takeover is complete."""
    session_id_str = str(session_id)

    session = await get_session_from_db(session_id_str, current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Set takeover event
    if session_id_str in _takeover_events:
        _takeover_events[session_id_str].set()
        return TakeoverResponse(completed=True, message="Takeover completed")

    return TakeoverResponse(completed=False, message="No active takeover")


@router.get("/{session_id}/status")
async def get_session_status(
    session_id: UUID,
    current_user: UserInfo = Depends(get_current_user),
):
    """
    Get the current status of a session.

    Returns:
    - is_connected: Whether an agent is connected
    - is_task_running: Whether a task is currently running
    - has_takeover: Whether takeover is pending
    """
    session_id_str = str(session_id)

    session = await get_session_from_db(session_id_str, current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "is_connected": session_id_str in _agents,
        "is_task_running": _task_running.get(session_id_str, False),
        "has_takeover": (
            session_id_str in _takeover_events
            and not _takeover_events[session_id_str].is_set()
        ),
    }


@router.delete("/{session_id}/agent")
async def disconnect_agent(
    session_id: UUID,
    current_user: UserInfo = Depends(get_current_user),
):
    """
    Disconnect and cleanup agent for a session.
    """
    session_id_str = str(session_id)

    session = await get_session_from_db(session_id_str, current_user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    cleanup_session(session_id_str)

    return {"disconnected": True}
