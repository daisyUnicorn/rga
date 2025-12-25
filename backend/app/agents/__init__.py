"""
Multi-Agent Architecture for Phone Automation.

This module provides a pluggable architecture for different AI agents:
- GLMAgent: Based on GLM models, streaming output, full context management
- GELabAgent: Based on GELab-Zero, detailed thinking, summary-based context
"""

from app.agents.base import BaseAgentService
from app.agents.factory import AgentFactory

__all__ = ["BaseAgentService", "AgentFactory"]
