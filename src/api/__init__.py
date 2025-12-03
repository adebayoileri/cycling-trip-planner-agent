"""FastAPI application for cycling trip planner."""
import os
import uuid
from typing import Dict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from src.models import ChatRequest, ChatResponse
from src.agent.factory import AgentFactory

app = FastAPI(
    title="Cycling Trip Planner API",
    description="AI-powered multi-day cycling trip planning assistant",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage (in production, use Redis or database)
sessions: Dict[str, Dict] = {}

# Initialize agent using factory
try:
    agent = AgentFactory.create_agent(
        "cycling",
        api_key=os.environ.get("ANTHROPIC_API_KEY")
    )
except ValueError as e:
    print(f"Warning: Agent initialization failed: {e}")
    print("Set ANTHROPIC_API_KEY environment variable to enable agent functionality")
    agent = None


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Cycling Trip Planner",
        "version": "1.0.0"
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    return {
        "status": "healthy",
        "agent_initialized": agent is not None,
        "active_sessions": len(sessions)
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint for conversing with the trip planner agent.
    
    The agent will:
    - Understand trip requirements
    - Ask clarifying questions
    - Use tools to gather information
    - Create detailed itineraries
    - Adjust based on feedback
    """
    if agent is None:
        raise HTTPException(
            status_code=503,
            detail="Agent not initialized. Please set ANTHROPIC_API_KEY environment variable."
        )
    
    # Get or create conversation ID
    conversation_id = request.conversation_id or str(uuid.uuid4())
    
    # Retrieve or initialize session
    if conversation_id not in sessions:
        sessions[conversation_id] = {
            "history": [],
            "state": request.session_state or {}
        }
    
    session = sessions[conversation_id]
    
    # Get conversation history and state
    history = session["history"]
    state = session["state"]
    
    try:
        # Process message with agent
        response_text, updated_history, updated_state, tools_used = agent.chat(
            user_message=request.message,
            conversation_history=history.copy(),
            session_state=state.copy()
        )
        
        # Update session
        session["history"] = updated_history
        session["state"] = updated_state
        
        # Create next request template for easy continuation
        next_request_template = {
            "message": "",
            "conversation_id": conversation_id,
            "session_state": updated_state
        }
        
        return ChatResponse(
            response=response_text,
            conversation_id=conversation_id,
            session_state=updated_state,
            tools_used=tools_used,
            next_request=next_request_template
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.post("/chat/{conversation_id}/continue", response_model=ChatResponse)
async def continue_conversation(conversation_id: str, request: ChatRequest):
    """Simplified endpoint to continue an existing conversation.
    
    The conversation_id is taken from the URL path, making it easier to continue
    conversations without manually copying IDs. This is especially useful in
    Swagger UI and other API exploration tools.
    
    Args:
        conversation_id: The ID of the conversation to continue
        request: Chat request (conversation_id in body is ignored)
    
    Returns:
        ChatResponse with agent's reply and next request template
    """
    if agent is None:
        raise HTTPException(
            status_code=503,
            detail="Agent not initialized. Please set ANTHROPIC_API_KEY environment variable."
        )
    
    # Check if conversation exists
    if conversation_id not in sessions:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation {conversation_id} not found. Use POST /chat to start a new conversation."
        )
    
    session = sessions[conversation_id]
    
    # Get conversation history and state
    history = session["history"]
    state = session["state"]
    
    try:
        # Process message with agent
        response_text, updated_history, updated_state, tools_used = agent.chat(
            user_message=request.message,
            conversation_history=history.copy(),
            session_state=state.copy()
        )
        
        # Update session
        session["history"] = updated_history
        session["state"] = updated_state
        
        # Create next request template
        next_request_template = {
            "message": "",
            "conversation_id": conversation_id,
            "session_state": updated_state
        }
        
        return ChatResponse(
            response=response_text,
            conversation_id=conversation_id,
            session_state=updated_state,
            tools_used=tools_used,
            next_request=next_request_template
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")


@app.post("/reset/{conversation_id}")
async def reset_conversation(conversation_id: str):
    """Reset a conversation session."""
    if conversation_id in sessions:
        del sessions[conversation_id]
        return {"status": "success", "message": "Conversation reset"}
    else:
        raise HTTPException(status_code=404, detail="Conversation not found")


@app.get("/sessions")
async def list_sessions():
    """List all active sessions (for debugging)."""
    return {
        "active_sessions": len(sessions),
        "session_ids": list(sessions.keys())
    }


@app.delete("/sessions")
async def clear_all_sessions():
    """Clear all sessions (for debugging)."""
    sessions.clear()
    return {"status": "success", "message": "All sessions cleared"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
