"""Agent orchestration for cycling trip planning.

The BaseAgent class defines the interface that
all agents must implement, while specific agents (like CyclingTripAgent)
extend it with specialized behavior and tools.

Example:
    >>> from src.agent import CyclingTripAgent, BaseAgent
    >>> from src.agent.factory import AgentFactory
    >>> 
    >>> # Direct instantiation
    >>> agent = CyclingTripAgent()
    >>> 
    >>> # Using factory pattern
    >>> agent = AgentFactory.create_agent("cycling")
"""
import json
import os
from typing import List, Dict, Any, Tuple, Optional
from abc import ABC, abstractmethod
from anthropic import Anthropic
from src.tools import CyclingTools


class BaseAgent(ABC):
    """Base class for AI agents using Claude with tool support."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-5-20250929"):
        """Initialize the base agent with Anthropic API key.
        
        Args:
            api_key: Anthropic API key (if None, reads from ANTHROPIC_API_KEY env var)
            model: Claude model to use
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY must be provided or set in environment")
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = model
        self.max_iterations = 10  # Prevent infinite tool loops
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for this agent.
        
        Must be implemented by subclasses to define agent behavior.
        """
        pass
    
    @abstractmethod
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return tool definitions available to this agent.
        
        Must be implemented by subclasses to define available tools.
        """
        pass
    
    @abstractmethod
    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """Execute a tool by name with given input.
        
        Must be implemented by subclasses to handle tool execution.
        """
        pass
    
    def chat(
        self, 
        user_message: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None,
        session_state: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, List[Dict[str, str]], Dict[str, Any], List[str]]:
        """
        Process a user message and return response with updated state.
        
        Args:
            user_message: The user's input message
            conversation_history: Previous messages in the conversation
            session_state: Current session state (agent-specific data)
        
        Returns:
            Tuple of (response_text, updated_history, updated_state, tools_used)
        """
        if conversation_history is None:
            conversation_history = []
        if session_state is None:
            session_state = {}
        
        # Add user message to history
        conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        tools_used = []
        iteration = 0
        
        while iteration < self.max_iterations:
            iteration += 1
            
            # Call Claude API with tools
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self.get_system_prompt(),
                messages=conversation_history,
                tools=self.get_tool_definitions()
            )
            
            # Check stop reason
            if response.stop_reason == "end_turn":
                # Extract text response
                text_response = ""
                for block in response.content:
                    if block.type == "text":
                        text_response += block.text
                
                # Add assistant response to history
                conversation_history.append({
                    "role": "assistant",
                    "content": text_response
                })
                
                return text_response, conversation_history, session_state, tools_used
            
            elif response.stop_reason == "tool_use":
                # Process tool calls
                assistant_content = []
                tool_results = []
                
                for block in response.content:
                    if block.type == "text":
                        assistant_content.append({
                            "type": "text",
                            "text": block.text
                        })
                    elif block.type == "tool_use":
                        assistant_content.append({
                            "type": "tool_use",
                            "id": block.id,
                            "name": block.name,
                            "input": block.input
                        })
                        
                        # Execute the tool
                        try:
                            tool_result = self.execute_tool(
                                block.name,
                                block.input
                            )
                            tools_used.append(block.name)
                            
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": json.dumps(tool_result)
                            })
                        except Exception as e:
                            tool_results.append({
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": f"Error: {str(e)}",
                                "is_error": True
                            })
                
                # Add assistant's tool use to history
                conversation_history.append({
                    "role": "assistant",
                    "content": assistant_content
                })
                
                # Add tool results to history
                conversation_history.append({
                    "role": "user",
                    "content": tool_results
                })
                
                # Continue the loop to get final response
            else:
                # Unexpected stop reason
                raise ValueError(f"Unexpected stop reason: {response.stop_reason}")
        
        # If we hit max iterations, return what we have
        return "I apologize, but I'm having trouble completing this request. Please try rephrasing.", conversation_history, session_state, tools_used
    
    def reset_conversation(self) -> Tuple[List[Dict[str, str]], Dict[str, Any]]:
        """Reset conversation state."""
        return [], {}


class CyclingTripAgent(BaseAgent):
    """AI agent specialized in planning multi-day cycling trips."""
    
    SYSTEM_PROMPT = """You are an expert cycling trip planner assistant. Your role is to help users plan multi-day cycling adventures by:

1. Understanding their preferences (distance, accommodation, timeline, interests)
2. Using available tools to gather route, weather, accommodation, and terrain information
3. Creating detailed day-by-day itineraries
4. Adjusting plans based on user feedback

Guidelines:
- Ask clarifying questions if important information is missing (dates, fitness level, budget constraints)
- Consider weather, terrain difficulty, and rest days in your planning
- Suggest realistic daily distances based on terrain and user fitness
- Always provide accommodation options that match user preferences
- Include practical tips about packing, route conditions, and points of interest
- Be conversational and encouraging - cycling trips should be exciting!

Available tools:
- get_route: Get route info, distance, waypoints between cities
- find_accommodation: Find camping, hostels, or hotels along the route
- get_weather: Check typical weather for locations and months
- get_elevation_profile: Understand terrain difficulty and elevation
- get_points_of_interest: Find interesting places to visit

When presenting a trip plan:
- Break it into clear daily segments
- Include distances, accommodation, and highlights for each day
- Provide cost estimates
- Mention weather considerations
- Suggest packing based on conditions

Be proactive in using tools to provide comprehensive answers."""

    def __init__(self, api_key: Optional[str] = None, model: str = "claude-sonnet-4-5-20250929"):
        """Initialize the cycling trip agent.
        
        Args:
            api_key: Anthropic API key (if None, reads from ANTHROPIC_API_KEY env var)
            model: Claude model to use
        """
        super().__init__(api_key=api_key, model=model)
        self.tools = CyclingTools()
    
    def get_system_prompt(self) -> str:
        """Return the system prompt for the cycling trip agent."""
        return self.SYSTEM_PROMPT
    
    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """Return tool definitions available to the cycling agent."""
        return self.tools.get_tool_definitions()
    
    def execute_tool(self, tool_name: str, tool_input: Dict[str, Any]) -> Any:
        """Execute a cycling tool by name with given input."""
        return self.tools.execute_tool(tool_name, tool_input)


# Export public API
__all__ = [
    "BaseAgent",
    "CyclingTripAgent",
]
