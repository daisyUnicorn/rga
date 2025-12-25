"""Core configuration and utilities."""

from .config import settings
from .supabase import get_supabase_client

__all__ = ["settings", "get_supabase_client"]

