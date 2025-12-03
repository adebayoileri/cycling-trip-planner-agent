"""Agent factory for creating and managing different agent types."""
from typing import Optional, Dict, Type
from src.agent import BaseAgent, CyclingTripAgent


class AgentFactory:
    """Factory for creating and managing different types of agents."""
    
    # Registry of available agent types
    _agent_registry: Dict[str, Type[BaseAgent]] = {
        "cycling": CyclingTripAgent,
    }
    
    @classmethod
    def register_agent(cls, agent_name: str, agent_class: Type[BaseAgent]) -> None:
        """Register a new agent type.
        
        Args:
            agent_name: Name identifier for the agent
            agent_class: Agent class that extends BaseAgent
        
        Raises:
            ValueError: If agent_class doesn't extend BaseAgent
        """
        if not issubclass(agent_class, BaseAgent):
            raise ValueError(f"{agent_class.__name__} must extend BaseAgent")
        
        cls._agent_registry[agent_name] = agent_class
    
    @classmethod
    def create_agent(
        cls, 
        agent_type: str, 
        api_key: Optional[str] = None,
        model: str = "claude-sonnet-4-5-20250929",
        **kwargs
    ) -> BaseAgent:
        """Create an agent instance by type.
        
        Args:
            agent_type: Type of agent to create (e.g., 'cycling', 'weather')
            api_key: Anthropic API key (optional, reads from env if not provided)
            model: Claude model to use
            **kwargs: Additional arguments to pass to the agent constructor
        
        Returns:
            Initialized agent instance
        
        Raises:
            ValueError: If agent_type is not registered
        
        Example:
            >>> agent = AgentFactory.create_agent("cycling")
            >>> agent = AgentFactory.create_agent("cycling", model="claude-3-5-sonnet-20241022")
        """
        if agent_type not in cls._agent_registry:
            available = ", ".join(cls._agent_registry.keys())
            raise ValueError(
                f"Unknown agent type: {agent_type}. "
                f"Available types: {available}"
            )
        
        agent_class = cls._agent_registry[agent_type]
        return agent_class(api_key=api_key, model=model, **kwargs)
    
    @classmethod
    def list_available_agents(cls) -> list:
        """List all registered agent types.
        
        Returns:
            List of agent type names
        """
        return list(cls._agent_registry.keys())
    
    @classmethod
    def get_agent_info(cls, agent_type: str) -> Dict[str, str]:
        """Get information about a specific agent type.
        
        Args:
            agent_type: Type of agent to query
        
        Returns:
            Dictionary with agent class name and docstring
        
        Raises:
            ValueError: If agent_type is not registered
        """
        if agent_type not in cls._agent_registry:
            raise ValueError(f"Unknown agent type: {agent_type}")
        
        agent_class = cls._agent_registry[agent_type]
        return {
            "name": agent_type,
            "class": agent_class.__name__,
            "description": agent_class.__doc__ or "No description available"
        }


# Extendability by registering other agents in the 
# AgentFactory.register_agent("weather", WeatherAdvisorAgent)
# AgentFactory.register_agent("travel", TravelItineraryAgent)
