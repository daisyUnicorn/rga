"""Database service for Supabase operations."""

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from app.core.supabase import get_supabase_admin_client
from app.models import SessionStatus


class DatabaseService:
    """
    Service for database operations using Supabase.
    
    Uses service_role key to bypass RLS since user authentication
    is already handled by our JWT middleware.
    """
    
    def __init__(self):
        self._client = None
    
    @property
    def client(self):
        """Lazy initialization of Supabase admin client (bypasses RLS)."""
        if self._client is None:
            self._client = get_supabase_admin_client()
        return self._client
    
    # Session operations
    async def create_session(
        self,
        user_id: str,
        name: Optional[str] = None,
        status: str = "creating",
        agent_type: str = "glm",
    ) -> dict:
        """Create a new session."""
        data = {
            "user_id": user_id,
            "name": name,
            "status": status,
            "agent_type": agent_type,
        }

        result = self.client.table("sessions").insert(data).execute()

        if result.data:
            return result.data[0]
        raise Exception("Failed to create session")
    
    async def get_session(self, session_id: str, user_id: str) -> Optional[dict]:
        """Get session by ID (with user check)."""
        result = (
            self.client.table("sessions")
            .select("*")
            .eq("id", session_id)
            .eq("user_id", user_id)
            .single()
            .execute()
        )
        return result.data
    
    async def list_sessions(self, user_id: str) -> List[dict]:
        """List only active sessions for a user."""
        result = (
            self.client.table("sessions")
            .select("*")
            .eq("user_id", user_id)
            .eq("status", "active")
            .order("created_at", desc=True)
            .execute()
        )
        return result.data or []
    
    async def update_session(
        self,
        session_id: str,
        user_id: str,
        **updates,
    ) -> Optional[dict]:
        """Update session fields."""
        result = (
            self.client.table("sessions")
            .update(updates)
            .eq("id", session_id)
            .eq("user_id", user_id)
            .execute()
        )
        
        if result.data:
            return result.data[0]
        return None
    
    async def delete_session(self, session_id: str, user_id: str) -> bool:
        """Delete a session (soft delete by setting status to closed)."""
        result = (
            self.client.table("sessions")
            .update({"status": "closed"})
            .eq("id", session_id)
            .eq("user_id", user_id)
            .execute()
        )
        return bool(result.data)
    
    async def count_user_sessions_today(self, user_id: str) -> int:
        """Count sessions created by user today (UTC timezone)."""
        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        
        result = (
            self.client.table("sessions")
            .select("id", count="exact")
            .eq("user_id", user_id)
            .gte("created_at", today_start.isoformat())
            .execute()
        )
        return result.count or 0
    
    async def count_active_sessions(self, user_id: str) -> int:
        """Count user's active sessions (only active, creating, paused - not closed or error)."""
        # Only count sessions that are actually using resources:
        # - active: in use
        # - creating: being created
        # - paused: paused but still using resources
        # Exclude:
        # - closed: ended by user
        # - error: failed to create, not using resources
        result = (
            self.client.table("sessions")
            .select("id", count="exact")
            .eq("user_id", user_id)
            .neq("status", "closed")
            .neq("status", "error")
            .execute()
        )
        return result.count or 0
    
    # Conversation operations
    async def create_conversation(
        self,
        session_id: str,
        role: str,
        content: str,
        thinking: Optional[str] = None,
        action: Optional[dict] = None,
    ) -> dict:
        """Create a new conversation message."""
        data = {
            "session_id": session_id,
            "role": role,
            "content": content,
            "thinking": thinking,
            "action": action,
        }
        
        result = self.client.table("conversations").insert(data).execute()
        
        if result.data:
            return result.data[0]
        raise Exception("Failed to create conversation")
    
    async def list_conversations(
        self,
        session_id: str,
        limit: int = 100,
    ) -> List[dict]:
        """List conversations for a session."""
        result = (
            self.client.table("conversations")
            .select("*")
            .eq("session_id", session_id)
            .order("created_at")
            .limit(limit)
            .execute()
        )
        return result.data or []


# Singleton instance
_db_service: Optional[DatabaseService] = None


def get_database_service() -> DatabaseService:
    """Get database service singleton."""
    global _db_service
    if _db_service is None:
        _db_service = DatabaseService()
    return _db_service

