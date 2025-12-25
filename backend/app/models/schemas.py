"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SessionStatus(str, Enum):
    """Session status enumeration."""
    CREATING = "creating"
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"
    ERROR = "error"


class MessageRole(str, Enum):
    """Message role enumeration."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class EventType(str, Enum):
    """SSE event types."""
    THINKING = "thinking"
    ACTION = "action"
    SCREENSHOT = "screenshot"
    TAKEOVER = "takeover"
    COMPLETED = "completed"
    ERROR = "error"


# User schemas
class UserInfo(BaseModel):
    """User information from JWT."""
    id: str
    email: Optional[str] = None
    name: Optional[str] = None
    avatar_url: Optional[str] = None


# Agent type enumeration
class AgentType(str, Enum):
    """Available agent types."""
    GLM = "glm"
    GELAB = "gelab"


# Session schemas
class SessionCreate(BaseModel):
    """Request to create a new session."""
    name: Optional[str] = Field(None, description="Optional session name")
    agent_type: str = Field(default="glm", description="Agent type: glm | gelab")


class SessionResponse(BaseModel):
    """Session response with details."""
    id: UUID
    user_id: str
    agentbay_session_id: Optional[str] = None
    resource_url: Optional[str] = None
    device_id: Optional[str] = None
    status: SessionStatus = SessionStatus.CREATING
    name: Optional[str] = None
    agent_type: str = Field(default="glm", description="Agent type used for this session")
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Message schemas
class MessageCreate(BaseModel):
    """Request to create a new message."""
    content: str = Field(..., description="Message content")


class MessageResponse(BaseModel):
    """Message response."""
    id: UUID
    session_id: UUID
    role: MessageRole
    content: str
    thinking: Optional[str] = None
    action: Optional[dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Task schemas
class TaskRequest(BaseModel):
    """Request to execute a task."""
    task: str = Field(..., description="Task description in natural language")


# Stream event schemas
class StreamEvent(BaseModel):
    """SSE stream event."""
    type: EventType
    data: Any
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# Takeover schemas
class TakeoverRequest(BaseModel):
    """Request to handle takeover."""
    message: str = Field(..., description="Takeover reason/message")


class TakeoverResponse(BaseModel):
    """Response after takeover is completed."""
    completed: bool = True
    message: Optional[str] = None

