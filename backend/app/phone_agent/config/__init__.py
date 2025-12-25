"""Configuration module for Phone Agent (shared utilities)."""

from app.phone_agent.config.apps import APP_PACKAGES, get_package_name, get_app_name
from app.phone_agent.config.i18n import get_messages, get_message
from app.phone_agent.config.timing import TIMING_CONFIG

__all__ = [
    "APP_PACKAGES",
    "get_package_name",
    "get_app_name",
    "get_messages",
    "get_message",
    "TIMING_CONFIG",
]
