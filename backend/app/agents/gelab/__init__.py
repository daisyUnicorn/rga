"""
GELabAgent - Based on GELab-Zero.

Features:
- Detailed THINK + explain + action + summary format
- Summary-based context management (lightweight)
- 9 action types (CLICK, TYPE, SLIDE, etc.)
- 0-1000 normalized coordinates
"""

from app.agents.gelab.service import GELabAgentService

__all__ = ["GELabAgentService"]
