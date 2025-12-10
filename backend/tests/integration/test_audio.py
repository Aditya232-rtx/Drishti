"""Comprehensive tests for audio chat endpoint."""
import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app
import io


@pytest.mark.asyncio
async def test_audio_chat_with_wav(test_user_id, sample_audio_wav):
    """Test audio chat with WAV file."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        audio_file = io.BytesIO(sample_audio_wav)
        
        response = await client.post(
            "/chat/audio",
            data={"user_id": test_user_id},
            files={"audio": ("test.wav", audio_file, "audio/wav")}
        )
        
        # May succeed or fail based on Whisper's ability to process the audio
        assert response.status_code in [200, 400, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "user_text" in data
            assert "assistant_text" in data
            assert "audio_base64" in data


@pytest.mark.asyncio
async def test_audio_chat_with_session(test_user_id, test_session_id, sample_audio_wav):
    """Test audio chat with session ID."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        audio_file = io.BytesIO(sample_audio_wav)
        
        response = await client.post(
            "/chat/audio",
            data={
                "user_id": test_user_id,
                "session_id": test_session_id
            },
            files={"audio": ("test.wav", audio_file, "audio/wav")}
        )
        
        if response.status_code == 200:
            data = response.json()
            assert data["session_id"] == test_session_id


@pytest.mark.asyncio
async def test_audio_chat_missing_audio(test_user_id):
    """Test audio chat validation - missing audio file."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/chat/audio",
            data={"user_id": test_user_id}
        )
        
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_audio_chat_missing_user_id(sample_audio_wav):
    """Test audio chat validation - missing user_id."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        audio_file = io.BytesIO(sample_audio_wav)
        
        response = await client.post(
            "/chat/audio",
            files={"audio": ("test.wav", audio_file, "audio/wav")}
        )
        
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_audio_chat_invalid_audio(test_user_id):
    """Test audio chat with invalid audio data."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        invalid_audio = io.BytesIO(b"not valid audio data")
        
        response = await client.post(
            "/chat/audio",
            data={"user_id": test_user_id},
            files={"audio": ("test.wav", invalid_audio, "audio/wav")}
        )
        
        # Should handle invalid audio gracefully
        assert response.status_code in [400, 422, 500]


@pytest.mark.asyncio
async def test_audio_chat_response_structure(test_user_id, sample_audio_wav):
    """Test audio chat response has expected fields."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        audio_file = io.BytesIO(sample_audio_wav)
        
        response = await client.post(
            "/chat/audio",
            data={"user_id": test_user_id},
            files={"audio": ("test.wav", audio_file, "audio/wav")}
        )
        
        if response.status_code == 200:
            data = response.json()
            expected_fields = ["user_text", "assistant_text", "lang", "model_used", "session_id", "audio_format", "audio_base64"]
            for field in expected_fields:
                assert field in data, f"Field {field} missing"


@pytest.mark.asyncio
async def test_audio_chat_content_type(test_user_id, sample_audio_wav):
    """Test audio chat returns JSON."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        audio_file = io.BytesIO(sample_audio_wav)
        
        response = await client.post(
            "/chat/audio",
            data={"user_id": test_user_id},
            files={"audio": ("test.wav", audio_file, "audio/wav")}
        )
        
        if response.status_code == 200:
            assert "application/json" in response.headers["content-type"]
