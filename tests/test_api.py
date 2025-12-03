"""Tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient
from src.api import app, sessions

client = TestClient(app)


class TestAPIEndpoints:
    """Test suite for API endpoints."""
    
    def setup_method(self):
        """Clear sessions before each test."""
        sessions.clear()
    
    def test_root_endpoint(self):
        """Test root endpoint returns health status."""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
    
    def test_health_endpoint(self):
        """Test health endpoint returns detailed status."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "agent_initialized" in data
        assert "active_sessions" in data
    
    def test_chat_endpoint_new_conversation(self):
        """Test chat endpoint creates new conversation."""
        response = client.post(
            "/chat",
            json={"message": "Hello, I want to plan a bike trip"}
        )
        
        # May fail if API key not set, which is expected
        if response.status_code == 503:
            pytest.skip("Agent not initialized (API key not set)")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "response" in data
        assert "conversation_id" in data
        assert "session_state" in data
        assert "tools_used" in data
        
        # Conversation ID should be generated
        assert len(data["conversation_id"]) > 0
    
    def test_chat_endpoint_existing_conversation(self):
        """Test chat endpoint with existing conversation ID."""
        # First message
        response1 = client.post(
            "/chat",
            json={"message": "I want to cycle from Amsterdam to Copenhagen"}
        )
        
        if response1.status_code == 503:
            pytest.skip("Agent not initialized (API key not set)")
        
        assert response1.status_code == 200
        conv_id = response1.json()["conversation_id"]
        
        # Second message with same conversation ID
        response2 = client.post(
            "/chat",
            json={
                "message": "What about accommodation?",
                "conversation_id": conv_id
            }
        )
        
        assert response2.status_code == 200
        data2 = response2.json()
        
        # Should use same conversation ID
        assert data2["conversation_id"] == conv_id
    
    def test_chat_endpoint_with_session_state(self):
        """Test chat endpoint preserves session state."""
        response = client.post(
            "/chat",
            json={
                "message": "I can cycle 100km per day",
                "session_state": {"daily_distance": 100}
            }
        )
        
        if response.status_code == 503:
            pytest.skip("Agent not initialized (API key not set)")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "session_state" in data
    
    def test_reset_conversation(self):
        """Test resetting a conversation."""
        # Create a conversation
        response = client.post(
            "/chat",
            json={"message": "Hello"}
        )
        
        if response.status_code == 503:
            pytest.skip("Agent not initialized (API key not set)")
        
        conv_id = response.json()["conversation_id"]
        
        # Reset it
        reset_response = client.post(f"/reset/{conv_id}")
        assert reset_response.status_code == 200
        assert reset_response.json()["status"] == "success"
    
    def test_reset_nonexistent_conversation(self):
        """Test resetting a conversation that doesn't exist."""
        response = client.post("/reset/nonexistent-id")
        assert response.status_code == 404
    
    def test_list_sessions(self):
        """Test listing active sessions."""
        response = client.get("/sessions")
        
        assert response.status_code == 200
        data = response.json()
        assert "active_sessions" in data
        assert "session_ids" in data
    
    def test_clear_all_sessions(self):
        """Test clearing all sessions."""
        # Create some sessions first
        client.post("/chat", json={"message": "Hello"})
        
        # Clear them
        response = client.delete("/sessions")
        
        assert response.status_code == 200
        assert response.json()["status"] == "success"
        
        # Verify they're cleared
        sessions_response = client.get("/sessions")
        assert sessions_response.json()["active_sessions"] == 0
    
    def test_chat_response_model_validation(self):
        """Test that chat response follows the expected model."""
        response = client.post(
            "/chat",
            json={"message": "Plan a trip"}
        )
        
        if response.status_code == 503:
            pytest.skip("Agent not initialized (API key not set)")
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
        assert isinstance(data["response"], str)
        assert isinstance(data["conversation_id"], str)
        assert isinstance(data["session_state"], dict)
        assert isinstance(data["tools_used"], list)
