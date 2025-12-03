"""Tests for the agent architecture and extensibility."""
import pytest
from typing import List, Dict, Any, Optional
from src.agent import BaseAgent, CyclingTripAgent
from src.agent.factory import AgentFactory


class MockAgent(BaseAgent):
    """Mock agent for testing."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-5-20250929"):
        """Initialize without requiring actual API key."""
        # Override parent init to avoid API key requirement in tests
        self.api_key = api_key or "mock-key"
        self.model = model
        self.max_iterations = 10
        self.client = None  # Don't initialize real client
    
    def get_system_prompt(self) -> str:
        return "Mock system prompt"
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "mock_tool",
                "description": "A mock tool",
                "input_schema": {
                    "type": "object",
                    "properties": {
                        "input": {"type": "string"}
                    },
                    "required": ["input"]
                }
            }
        ]
    
    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        return {"result": f"Mock result for {tool_name}"}


class TestBaseAgent:
    """Test suite for BaseAgent abstract class."""
    
    def test_cannot_instantiate_base_agent(self):
        """BaseAgent is abstract and cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseAgent()
    
    def test_mock_agent_implements_interface(self):
        """Mock agent properly implements BaseAgent interface."""
        agent = MockAgent()
        
        assert agent.get_system_prompt() == "Mock system prompt"
        assert isinstance(agent.get_tool_definitions(), list)
        assert len(agent.get_tool_definitions()) == 1
        
        result = agent.execute_tool("mock_tool", {"input": "test"})
        assert "result" in result


class TestCyclingTripAgent:
    """Test suite for CyclingTripAgent."""
    
    def test_cycling_agent_initialization(self):
        """CyclingTripAgent initializes with default values."""
        # This will raise if API key not set, which is expected
        try:
            agent = CyclingTripAgent()
            assert agent.model == "claude-sonnet-4-5-20250929"
            assert agent.max_iterations == 10
        except ValueError as e:
            pytest.skip(f"API key not set: {e}")
    
    def test_cycling_agent_has_system_prompt(self):
        """CyclingTripAgent has a defined system prompt."""
        try:
            agent = CyclingTripAgent()
            prompt = agent.get_system_prompt()
            assert isinstance(prompt, str)
            assert len(prompt) > 0
            assert "cycling" in prompt.lower()
        except ValueError:
            pytest.skip("API key not set")
    
    def test_cycling_agent_has_tools(self):
        """CyclingTripAgent has tool definitions."""
        try:
            agent = CyclingTripAgent()
            tools = agent.get_tool_definitions()
            assert isinstance(tools, list)
            assert len(tools) > 0
            
            # Check tool structure
            for tool in tools:
                assert "name" in tool
                assert "description" in tool
                assert "input_schema" in tool
        except ValueError:
            pytest.skip("API key not set")
    
    def test_cycling_agent_tool_execution(self):
        """CyclingTripAgent can execute tools."""
        try:
            agent = CyclingTripAgent()
            
            # Test route tool
            result = agent.execute_tool("get_route", {
                "start": "Amsterdam",
                "end": "Copenhagen"
            })
            assert isinstance(result, dict)
            assert "distance_km" in result
            assert "waypoints" in result
        except ValueError:
            pytest.skip("API key not set")
    
    def test_cycling_agent_unknown_tool_raises_error(self):
        """Executing unknown tool raises ValueError."""
        try:
            agent = CyclingTripAgent()
            
            with pytest.raises(ValueError, match="Unknown tool"):
                agent.execute_tool("nonexistent_tool", {})
        except ValueError:
            pytest.skip("API key not set")


class TestAgentFactory:
    """Test suite for AgentFactory."""
    
    def test_factory_has_cycling_agent_registered(self):
        """Factory has cycling agent registered by default."""
        available = AgentFactory.list_available_agents()
        assert "cycling" in available
    
    def test_factory_can_register_new_agent(self):
        """Factory can register new agent types."""
        AgentFactory.register_agent("mock", MockAgent)
        available = AgentFactory.list_available_agents()
        assert "mock" in available
        
        # Cleanup
        AgentFactory._agent_registry.pop("mock", None)
    
    def test_factory_rejects_non_base_agent(self):
        """Factory rejects classes that don't extend BaseAgent."""
        class NotAnAgent:
            pass
        
        with pytest.raises(ValueError, match="must extend BaseAgent"):
            AgentFactory.register_agent("invalid", NotAnAgent)
    
    def test_factory_creates_cycling_agent(self):
        """Factory can create CyclingTripAgent instances."""
        try:
            agent = AgentFactory.create_agent("cycling")
            assert isinstance(agent, CyclingTripAgent)
            assert isinstance(agent, BaseAgent)
        except ValueError:
            pytest.skip("API key not set")
    
    def test_factory_create_unknown_agent_raises_error(self):
        """Creating unknown agent type raises ValueError."""
        with pytest.raises(ValueError, match="Unknown agent type"):
            AgentFactory.create_agent("nonexistent")
    
    def test_factory_get_agent_info(self):
        """Factory can retrieve agent information."""
        info = AgentFactory.get_agent_info("cycling")
        assert isinstance(info, dict)
        assert "name" in info
        assert "class" in info
        assert "description" in info
        assert info["name"] == "cycling"
        assert info["class"] == "CyclingTripAgent"
    
    def test_factory_get_info_unknown_agent_raises_error(self):
        """Getting info for unknown agent raises ValueError."""
        with pytest.raises(ValueError, match="Unknown agent type"):
            AgentFactory.get_agent_info("nonexistent")
    
    def test_factory_create_with_custom_model(self):
        """Factory can create agents with custom model."""
        try:
            agent = AgentFactory.create_agent(
                "cycling", 
                model="claude-3-5-sonnet-20241022"
            )
            assert agent.model == "claude-3-5-sonnet-20241022"
        except ValueError:
            pytest.skip("API key not set")


class TestAgentExtensibility:
    """Test suite for demonstrating extensibility."""
    
    def test_multiple_agent_types_can_coexist(self):
        """Multiple different agent types can be registered and used."""
        # Create two different mock agents
        class AgentTypeA(MockAgent):
            def get_system_prompt(self) -> str:
                return "Agent Type A"
        
        class AgentTypeB(MockAgent):
            def get_system_prompt(self) -> str:
                return "Agent Type B"
        
        # Register both
        AgentFactory.register_agent("type_a", AgentTypeA)
        AgentFactory.register_agent("type_b", AgentTypeB)
        
        # Create instances
        agent_a = AgentFactory.create_agent("type_a")
        agent_b = AgentFactory.create_agent("type_b")
        
        # Verify they're different
        assert agent_a.get_system_prompt() == "Agent Type A"
        assert agent_b.get_system_prompt() == "Agent Type B"
        
        # Cleanup
        AgentFactory._agent_registry.pop("type_a", None)
        AgentFactory._agent_registry.pop("type_b", None)
    
    def test_custom_agent_can_have_different_tools(self):
        """Custom agents can define their own unique tools."""
        class CustomToolAgent(MockAgent):
            def get_tool_definitions(self) -> List[Dict[str, Any]]:
                return [
                    {
                        "name": "custom_tool_1",
                        "description": "Custom tool",
                        "input_schema": {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    }
                ]
        
        agent = CustomToolAgent()
        tools = agent.get_tool_definitions()
        
        assert len(tools) == 1
        assert tools[0]["name"] == "custom_tool_1"
