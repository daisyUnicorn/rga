"""
Phone Agent module - Shared utilities for phone automation.

This module contains shared utilities used by all agents:
- adb/: ADB operations (screenshot, input, device control)
- actions/: Action execution (ActionHandler)
- config/: Shared configuration (apps, timing, i18n)
"""

from app.phone_agent.adb import get_screenshot, get_current_app
from app.phone_agent.actions import ActionHandler, parse_action, finish

__all__ = [
    "get_screenshot",
    "get_current_app",
    "ActionHandler",
    "parse_action",
    "finish",
]
