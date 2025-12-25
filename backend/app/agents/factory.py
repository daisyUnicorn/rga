"""
Agent Factory - Creates agent instances based on type.

This module implements the Factory pattern for creating different agent types.
It supports:
1. Registration of new agent types
2. Dynamic agent creation
3. Agent discovery
"""

from typing import Callable, Optional, Type
import asyncio

from app.agents.base import BaseAgentService


class AgentFactory:
    """
    Factory class for creating agent instances.

    Usage:
        agent = AgentFactory.create_agent(
            agent_type="glm",
            device_id="device-123",
            on_takeover=my_callback,
        )
    """

    _registry: dict[str, Type[BaseAgentService]] = {}

    @classmethod
    def register_agent(cls, agent_type: str, agent_class: Type[BaseAgentService]):
        """
        Register a new agent type.

        Args:
            agent_type: Unique identifier for the agent type
            agent_class: The agent class to register
        """
        cls._registry[agent_type] = agent_class

    @classmethod
    def create_agent(
        cls,
        agent_type: str,
        device_id: str,
        on_takeover: Optional[Callable[[str], asyncio.Future]] = None,
        session_id: Optional[str] = None,
    ) -> BaseAgentService:
        """
        Create an agent instance of the specified type.

        Args:
            agent_type: Agent type ("glm" | "gelab")
            device_id: Device ID to control
            on_takeover: Optional takeover callback
            session_id: Optional AgentBay session ID for native APIs

        Returns:
            BaseAgentService instance

        Raises:
            ValueError: If agent_type is not supported
        """
        if agent_type not in cls._registry:
            raise ValueError(
                f"Unknown agent type: {agent_type}. "
                f"Supported types: {list(cls._registry.keys())}"
            )

        agent_class = cls._registry[agent_type]
        return agent_class(device_id=device_id, on_takeover=on_takeover, session_id=session_id)

    @classmethod
    def get_available_agents(cls) -> list[dict]:
        """
        Get information about all available agents.

        Returns:
            List of agent info dictionaries
        """
        agents = []
        for agent_type, agent_class in cls._registry.items():
            agents.append({
                "type": agent_type,
                "name": agent_class.__name__,
                "description": agent_class.__doc__ or "",
            })
        return agents

    @classmethod
    def is_registered(cls, agent_type: str) -> bool:
        """Check if an agent type is registered."""
        return agent_type in cls._registry


# Import and register agents after factory is defined
def _register_default_agents():
    """Register default agent implementations."""
    from app.agents.glm.service import GLMAgentService
    from app.agents.gelab.service import GELabAgentService

    AgentFactory.register_agent("glm", GLMAgentService)
    AgentFactory.register_agent("gelab", GELabAgentService)


# Auto-register on import
_register_default_agents()
