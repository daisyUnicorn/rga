"""
GLMAgent - Based on GLM models.

Features:
- Streaming thinking output
- Full context management
- XML-style output format
"""

from app.agents.glm.service import GLMAgentService
from app.agents.glm.prompts import get_system_prompt, SYSTEM_PROMPT
from app.agents.glm.model import MessageBuilder

__all__ = [
    "GLMAgentService",
    "get_system_prompt",
    "SYSTEM_PROMPT",
    "MessageBuilder",
]
