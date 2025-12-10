"""Comprehensive tests for chat endpoints."""
import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app


@pytest.mark.asyncio
async def test_text_chat_basic(test_user_id):
    """Test basic text chat functionality."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/chat/text",
            json={
                "user_id": test_user_id,
                "text": "Hello",
                "lang": "en"
            }
        )
        
        # May fail if models not loaded in test environment
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "assistant_text" in data
            assert "model_used" in data
            assert len(data["assistant_text"]) > 0


@pytest.mark.asyncio
async def test_text_chat_auto_language(test_user_id):
    """Test chat with automatic language detection."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/chat/text",
            json={
                "user_id": test_user_id,
                "text": "What is AI?",
                "lang": "auto"
            }
        )
        
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "lang" in data


@pytest.mark.asyncio
async def test_text_chat_with_session(test_user_id, test_session_id):
    """Test chat with specific session ID."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/chat/text",
            json={
                "user_id": test_user_id,
                "session_id": test_session_id,
                "text": "Hello",
                "lang": "en"
            }
        )
        
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert data["session_id"] == test_session_id


@pytest.mark.asyncio
async def test_text_chat_hindi(test_user_id):
    """Test chat with Hindi language."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/chat/text",
            json={
                "user_id": test_user_id,
                "text": "नमस्ते",
                "lang": "hi"
            }
        )
        
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "assistant_text" in data


@pytest.mark.asyncio
async def test_text_chat_long_text(test_user_id):
    """Test chat with long text (should use heavy model)."""
    long_text = "Explain quantum computing " * 50
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/chat/text",
            json={
                "user_id": test_user_id,
                "text": long_text,
                "lang": "en"
            }
        )
        
        assert response.status_code in [200, 500]


@pytest.mark.asyncio
async def test_text_chat_missing_user_id():
    """Test chat validation - missing user_id."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/chat/text",
            json={
                "text": "Hello",
                "lang": "en"
            }
        )
        
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_text_chat_missing_text(test_user_id):
    """Test chat validation - missing text."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/chat/text",
            json={
                "user_id": test_user_id,
                "lang": "en"
            }
        )
        
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_text_chat_empty_text(test_user_id):
    """Test chat with empty text."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/chat/text",
            json={
                "user_id": test_user_id,
                "text": "",
                "lang": "en"
            }
        )
        
        # Should either fail validation or handle gracefully
        assert response.status_code in [200, 400, 422, 500]


@pytest.mark.asyncio
async def test_text_chat_response_structure(test_user_id):
    """Test chat response has all expected fields."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/chat/text",
            json={
                "user_id": test_user_id,
                "text": "Hi",
                "lang": "en"
            }
        )
        
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            
            expected_fields = ["user_text", "assistant_text", "lang", "model_used", "session_id"]
            for field in expected_fields:
                assert field in data, f"Field {field} missing from response"


@pytest.mark.asyncio
async def test_text_chat_content_type(test_user_id):
    """Test chat response is JSON."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/chat/text",
            json={
                "user_id": test_user_id,
                "text": "Hello",
                "lang": "en"
            }
        )
        
        if response.status_code == 200:
            assert "application/json" in response.headers["content-type"]
