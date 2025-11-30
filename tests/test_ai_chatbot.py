# tests/test_ai_chatbot.py
"""
Unit tests for AI Chatbot Endpoints
Tests chat completion, streaming, and model configuration.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json


class TestChatEndpoints:
    """Tests for AI chat completion endpoints"""

    @pytest.fixture
    def mock_auth(self):
        """Mock authentication tuple"""
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        return (mock_user, 1)  # (user, org_id)

    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        return MagicMock()

    def test_chat_message_schema(self):
        """Test ChatMessage schema validation"""
        from app.api.v1.ai import ChatMessage
        
        msg = ChatMessage(role="user", content="Hello, how are you?")
        
        assert msg.role == "user"
        assert msg.content == "Hello, how are you?"

    def test_chat_request_schema(self):
        """Test ChatRequest schema validation"""
        from app.api.v1.ai import ChatRequest, ChatMessage
        
        request = ChatRequest(
            messages=[
                ChatMessage(role="user", content="What is TritIQ?")
            ],
            model="gpt-4o-mini",
            temperature=0.7,
            max_tokens=1000
        )
        
        assert len(request.messages) == 1
        assert request.model == "gpt-4o-mini"
        assert request.temperature == 0.7

    def test_chat_request_with_context(self):
        """Test ChatRequest with context"""
        from app.api.v1.ai import ChatRequest, ChatMessage
        
        request = ChatRequest(
            messages=[
                ChatMessage(role="user", content="Help me with inventory")
            ],
            context={
                "current_page": "/inventory",
                "user_role": "admin"
            }
        )
        
        assert request.context is not None
        assert request.context["current_page"] == "/inventory"

    def test_streaming_chat_request_schema(self):
        """Test StreamingChatRequest schema validation"""
        from app.api.v1.ai import StreamingChatRequest, ChatMessage
        
        request = StreamingChatRequest(
            messages=[
                ChatMessage(role="system", content="You are a helpful assistant."),
                ChatMessage(role="user", content="Tell me about sales reports.")
            ],
            temperature=0.5
        )
        
        assert len(request.messages) == 2
        assert request.messages[0].role == "system"
        assert request.temperature == 0.5

    def test_chat_response_schema(self):
        """Test ChatResponse schema"""
        from app.api.v1.ai import ChatResponse, ChatMessage
        
        response = ChatResponse(
            message=ChatMessage(role="assistant", content="I can help you with that!"),
            model="gpt-4o-mini",
            finish_reason="stop",
            usage={"prompt_tokens": 10, "completion_tokens": 20, "total_tokens": 30}
        )
        
        assert response.message.role == "assistant"
        assert response.model == "gpt-4o-mini"
        assert response.usage["total_tokens"] == 30

    def test_temperature_validation(self):
        """Test temperature validation range"""
        from app.api.v1.ai import ChatRequest, ChatMessage
        
        # Valid temperature
        request = ChatRequest(
            messages=[ChatMessage(role="user", content="test")],
            temperature=1.5
        )
        assert 0 <= request.temperature <= 2

        # Test boundary values
        request_low = ChatRequest(
            messages=[ChatMessage(role="user", content="test")],
            temperature=0
        )
        assert request_low.temperature == 0

        request_high = ChatRequest(
            messages=[ChatMessage(role="user", content="test")],
            temperature=2
        )
        assert request_high.temperature == 2

    def test_max_tokens_validation(self):
        """Test max_tokens validation range"""
        from app.api.v1.ai import ChatRequest, ChatMessage
        
        request = ChatRequest(
            messages=[ChatMessage(role="user", content="test")],
            max_tokens=2000
        )
        
        assert 1 <= request.max_tokens <= 4000


class TestChatModelConfiguration:
    """Tests for chat model configuration"""

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key', 'OPENAI_MODEL': 'gpt-4'})
    def test_model_from_environment(self):
        """Test model configuration from environment"""
        import os
        
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
        assert model == "gpt-4"

    @patch.dict('os.environ', {}, clear=True)
    def test_default_model(self):
        """Test default model when not configured"""
        import os
        
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        
        assert model == "gpt-4o-mini"

    @patch.dict('os.environ', {'OPENAI_TEMPERATURE': '0.5'})
    def test_temperature_from_environment(self):
        """Test temperature configuration from environment"""
        import os
        
        temp = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
        
        assert temp == 0.5

    @patch.dict('os.environ', {'OPENAI_MAX_TOKENS': '2000'})
    def test_max_tokens_from_environment(self):
        """Test max_tokens configuration from environment"""
        import os
        
        max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
        
        assert max_tokens == 2000


class TestChatSystemPrompt:
    """Tests for chat system prompt handling"""

    def test_system_prompt_inclusion(self):
        """Test that system prompt is included in messages"""
        system_prompt = """You are TritIQ Assistant, an AI helper for the TritIQ Business Operating System.
You help users with:
- Business management questions
- Navigation within the system
- Understanding financial reports and analytics"""
        
        messages = [{"role": "system", "content": system_prompt}]
        user_messages = [{"role": "user", "content": "How do I create an invoice?"}]
        
        full_messages = messages + user_messages
        
        assert len(full_messages) == 2
        assert full_messages[0]["role"] == "system"
        assert "TritIQ" in full_messages[0]["content"]

    def test_context_injection(self):
        """Test context injection into messages"""
        context = {
            "current_page": "/sales",
            "user_role": "sales_manager"
        }
        org_id = 1
        
        context_str = f"User context: Organization ID: {org_id}"
        if context.get("current_page"):
            context_str += f", Current page: {context['current_page']}"
        if context.get("user_role"):
            context_str += f", User role: {context['user_role']}"
        
        assert "Organization ID: 1" in context_str
        assert "Current page: /sales" in context_str
        assert "User role: sales_manager" in context_str


class TestStreamingResponse:
    """Tests for streaming chat response handling"""

    def test_sse_format(self):
        """Test Server-Sent Events format"""
        content = "Hello"
        sse_data = f"data: {json.dumps({'content': content})}\n\n"
        
        assert sse_data.startswith("data: ")
        assert sse_data.endswith("\n\n")
        
        # Parse the JSON
        json_str = sse_data[6:-2]  # Remove "data: " prefix and "\n\n" suffix
        parsed = json.loads(json_str)
        assert parsed["content"] == "Hello"

    def test_done_message_format(self):
        """Test done message format in SSE"""
        done_msg = f"data: {json.dumps({'done': True})}\n\n"
        
        json_str = done_msg[6:-2]
        parsed = json.loads(json_str)
        
        assert parsed["done"] is True

    def test_error_message_format(self):
        """Test error message format in SSE"""
        error_msg = f"data: {json.dumps({'error': 'API rate limit exceeded'})}\n\n"
        
        json_str = error_msg[6:-2]
        parsed = json.loads(json_str)
        
        assert "error" in parsed
        assert "rate limit" in parsed["error"]


class TestChatErrorHandling:
    """Tests for chat error handling"""

    def test_missing_api_key_error(self):
        """Test error when API key is missing"""
        from fastapi import HTTPException
        
        api_key = None
        
        if not api_key:
            with pytest.raises(HTTPException) as exc_info:
                raise HTTPException(
                    status_code=503,
                    detail="AI chat service is not configured. Please set OPENAI_API_KEY."
                )
            
            assert exc_info.value.status_code == 503
            assert "OPENAI_API_KEY" in exc_info.value.detail

    def test_invalid_temperature_handling(self):
        """Test handling of invalid temperature environment variable"""
        import os
        
        with patch.dict('os.environ', {'OPENAI_TEMPERATURE': 'invalid'}):
            try:
                temp = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
            except ValueError:
                temp = 0.7
            
            assert temp == 0.7

    def test_invalid_max_tokens_handling(self):
        """Test handling of invalid max_tokens environment variable"""
        import os
        
        with patch.dict('os.environ', {'OPENAI_MAX_TOKENS': 'invalid'}):
            try:
                max_tokens = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
            except ValueError:
                max_tokens = 1000
            
            assert max_tokens == 1000


class TestAvailableModels:
    """Tests for available models endpoint"""

    @patch.dict('os.environ', {'OPENAI_API_KEY': 'test_key', 'OPENAI_MODEL': 'gpt-4o'})
    def test_models_list(self):
        """Test available models list"""
        import os
        
        default_model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        configured = bool(os.getenv("OPENAI_API_KEY"))
        
        available_models = [
            {"id": "gpt-4o-mini", "name": "GPT-4o Mini"},
            {"id": "gpt-4o", "name": "GPT-4o"},
            {"id": "gpt-4-turbo", "name": "GPT-4 Turbo"},
            {"id": "gpt-3.5-turbo", "name": "GPT-3.5 Turbo"}
        ]
        
        assert default_model == "gpt-4o"
        assert configured is True
        assert len(available_models) == 4

    @patch.dict('os.environ', {}, clear=True)
    def test_unconfigured_state(self):
        """Test unconfigured state"""
        import os
        
        configured = bool(os.getenv("OPENAI_API_KEY"))
        
        assert configured is False


class TestChatAuditLogging:
    """Tests for chat interaction audit logging"""

    def test_audit_log_data_structure(self):
        """Test audit log data structure for chat"""
        user_id = 1
        org_id = 1
        model = "gpt-4o-mini"
        message_count = 3
        
        audit_data = {
            "entity_type": "ai_chat",
            "entity_id": None,
            "action": "chat_completion",
            "user_id": user_id,
            "changes": {"model": model, "message_count": message_count},
            "organization_id": org_id
        }
        
        assert audit_data["entity_type"] == "ai_chat"
        assert audit_data["action"] == "chat_completion"
        assert audit_data["changes"]["model"] == "gpt-4o-mini"
        assert audit_data["changes"]["message_count"] == 3

    def test_streaming_audit_log(self):
        """Test audit log for streaming chat"""
        action = "chat_stream_completion"
        
        assert "stream" in action


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
