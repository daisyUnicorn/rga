"""Supabase client configuration."""

from typing import Optional

from supabase import create_client, Client

from .config import settings
from .logging import get_logger

logger = get_logger("supabase")


# Global client instances (lazy initialization)
_supabase_client: Optional[Client] = None
_supabase_admin_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """Get Supabase client instance (lazy initialization)."""
    global _supabase_client
    if _supabase_client is None:
        if not settings.supabase_url or not settings.supabase_key:
            raise RuntimeError("Supabase URL and Key must be configured")
        _supabase_client = create_client(settings.supabase_url, settings.supabase_key)
    return _supabase_client


def get_supabase_admin_client() -> Client:
    """Get Supabase client with service role key for admin operations."""
    global _supabase_admin_client
    if _supabase_admin_client is None:
        if not settings.supabase_url or not settings.supabase_service_key:
            raise RuntimeError("Supabase URL and Service Key must be configured")
        _supabase_admin_client = create_client(settings.supabase_url, settings.supabase_service_key)
    return _supabase_admin_client


async def verify_jwt_token(token: str) -> Optional[dict]:
    """
    Verify JWT token from Supabase Auth.
    
    Args:
        token: JWT token from Authorization header
        
    Returns:
        User data if valid, None otherwise
    """
    try:
        client = get_supabase_client()
        # Get user from token
        user_response = client.auth.get_user(token)
        if user_response and user_response.user:
            return {
                "id": user_response.user.id,
                "email": user_response.user.email,
                "user_metadata": user_response.user.user_metadata,
            }
        return None
    except Exception as e:
        logger.error(f"Token verification failed: {e}", exc_info=True)
        return None

