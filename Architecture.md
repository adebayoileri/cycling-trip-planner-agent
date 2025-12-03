# Architecture Documentation

## System Overview

The Cycling Trip Planner is built as a conversational AI agent that uses tool calling to provide intelligent trip planning assistance.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User / Client                       │
└───────────────────────────┬─────────────────────────────────┘
                            │ HTTP Request
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │              POST /chat Endpoint                       │ │
│  │  • Validates request (Pydantic)                        │ │
│  │  • Manages conversation sessions                       │ │
│  │  • Routes to agent                                     │ │
│  └────────────────┬───────────────────────────────────────┘ │
└───────────────────┼─────────────────────────────────────────┘
                    ▼
┌─────────────────────────────────────────────────────────────┐
│                    Agent Orchestration                      │
│  ┌────────────────────────────────────────────────────────┐ │
│  │            Base Agent -> CyclingTripAgent              │ │
│  │  • Maintains conversation history                      │ │
│  │  • Calls Claude API with system prompt                 │ │
│  │  • Handles tool use loop                               │ │
│  │  • Manages session state                               │ │
│  └────────────┬──────────────┬────────────────────────────┘ │
└───────────────┼──────────────┼──────────────────────────────┘
                │              │
                ▼              ▼
     ┌──────────────┐   ┌──────────────┐
     │  Claude API  │   │  Tool System │
     │  (Anthropic) │   │   (Local)    │
     └──────────────┘   └──────┬───────┘
                                │
            ┌───────────────────┼───────────────────┐
            ▼                   ▼                   ▼
    ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
    │  get_route   │   │find_accomm.  │   │get_weather   │
    │              │   │              │   │              │
    │ • Distance   │   │ • Camping    │   │ • Temperature│
    │ • Waypoints  │   │ • Hostels    │   │ • Precip     │
    │ • Est. days  │   │ • Hotels     │   │ • Suitability│
    └──────────────┘   └──────────────┘   └──────────────┘
```
## Component Details

### 1. FastAPI Layer (`src/api/__init__.py`)

**Responsibilities:**
- HTTP request handling
- Request validation (Pydantic models)
- Session management
- Response formatting
- CORS configuration

**Key Endpoints:**
- `POST /chat` - Main conversational endpoint
- `GET /health` - Health check
- `POST /reset/{conversation_id}` - Reset conversation
- `GET /sessions` - List active sessions (debug)
- `DELETE /sessions` - Clear all sessions (debug)

**Session Management:**
```python
sessions = {
    "conversation_id": {
        "history": [
            {"role": "user", "content": "..."},
            {"role": "assistant", "content": "..."}
        ],
        "state": {
            "preferences": {...},
            "current_trip": {...}
        }
    }
}
```

### 2. Agent Layer (`src/agent/__init__.py`)

**Responsibilities:**
- Claude API integration
- Tool orchestration
- Conversation flow management
- System prompt injection
- Tool result processing

**Agent Loop:**
```
1. Receive user message
2. Add to conversation history
3. Call Claude API with:
   - System prompt
   - Conversation history
   - Tool definitions
4. Process Claude's response:
   - If text → return to user
   - If tool_use → execute tools
5. Add tool results to history
6. Loop back to step 3 (max 10 iterations)
```

**Key Features:**
- Stateless agent (all state in conversation history)
- Automatic tool execution
- Multi-tool support in single turn
- Error handling for tool failures

### 3. Tool System (`src/tools/__init__.py`)

**Architecture:**
```python
class CyclingTools:
    @staticmethod
    def get_tool_definitions() -> List[Dict]:
        """Returns tool schemas for Claude API"""
        
    @staticmethod
    def execute_tool(name: str, input: Dict) -> Any:
        """Executes a tool by name"""
        
    @staticmethod
    def get_route(...) -> Dict:
        """Individual tool implementation"""
```

**Tool Design Principles:**
1. **Declarative**: Tools defined via JSON schema
2. **Type-safe**: Input validation via function signatures
3. **Composable**: Tools can be used together
4. **Idempotent**: Same input = same output
5. **Mock-friendly**: Easy to test without external APIs

### 4. Data Models (`src/models/__init__.py`)
**Pydantic Models:**
- `ChatRequest`: User message + conversation ID
- `ChatResponse`: Agent response + conversation ID
- `ToolInput/Output`: Structured tool data

## Conversation Flow
1. User sends message to `POST /chat`
2. FastAPI validates and routes to agent
3. Agent updates history and calls Claude API
4. Claude responds with text or tool use
5. If tool use, agent executes tools and updates history
6. Agent returns final response to FastAPI

## Conclusion
The overall architecture focuses on modularity given the allocated time taken to complete the task, using locally defined tools with Anthropic SDK, and the agent orchestration layer adopts the factory pattern for extensibility and future improvements.