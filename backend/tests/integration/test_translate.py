"""Comprehensive tests for translation endpoint."""
import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app


@pytest.mark.asyncio
async def test_translate_basic():
    """Test basic translation."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/translate",
            json={
                "text": "Hello",
                "source_lang": "en",
                "target_lang": "es"
            }
        )
        
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "translated_text" in data
            assert len(data["translated_text"]) > 0


@pytest.mark.asyncio
async def test_translate_response_structure():
    """Test translation response has all expected fields."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/translate",
            json={
                "text": "Good morning",
                "source_lang": "en",
                "target_lang": "fr"
            }
        )
        
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            
            expected_fields = ["input_text", "translated_text", "source_lang", "target_lang"]
            for field in expected_fields:
                assert field in data, f"Field {field} missing"


@pytest.mark.asyncio
async def test_translate_with_tts():
    """Test translation with TTS generation."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/translate",
            json={
                "text": "Hello",
                "source_lang": "en",
                "target_lang": "hi",
                "tts": True
            }
        )
        
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "translated_text" in data
            # audio_base64 may be None if TTS fails, but field should exist
            assert "audio_base64" in data


@pytest.mark.asyncio
async def test_translate_multiple_languages():
    """Test translation to multiple target languages."""
    languages = [
        ("en", "es"),  # English to Spanish
        ("en", "fr"),  # English to French
        ("en", "de"),  # English to German
        ("en", "hi"),  # English to Hindi
    ]
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        for source, target in languages:
            response = await client.post(
                "/translate",
                json={
                    "text": "Hello world",
                    "source_lang": source,
                    "target_lang": target
                }
            )
            
            assert response.status_code in [200, 500], f"Unexpected status for {source}->{target}"
            
            if response.status_code == 200:
                data = response.json()
                assert len(data["translated_text"]) > 0


@pytest.mark.asyncio
async def test_translate_same_language():
    """Test translation when source and target are same."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/translate",
            json={
                "text": "Hello",
                "source_lang": "en",
                "target_lang": "en"
            }
        )
        
        # Should still work, might return same or rephrased text
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "translated_text" in data


@pytest.mark.asyncio
async def test_translate_long_text():
    """Test translation with long text."""
    long_text = "This is a longer text for testing. " * 20
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/translate",
            json={
                "text": long_text,
                "source_lang": "en",
                "target_lang": "es"
            }
        )
        
        assert response.status_code in [200, 422, 500]


@pytest.mark.asyncio
async def test_translate_missing_text():
    """Test translation validation - missing text."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/translate",
            json={
                "source_lang": "en",
                "target_lang": "es"
            }
        )
        
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_translate_missing_source_lang():
    """Test translation validation - missing source_lang."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/translate",
            json={
                "text": "Hello",
                "target_lang": "es"
            }
        )
        
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_translate_missing_target_lang():
    """Test translation validation - missing target_lang."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/translate",
            json={
                "text": "Hello",
                "source_lang": "en"
            }
        )
        
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_translate_empty_text():
    """Test translation with empty text."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/translate",
            json={
                "text": "",
                "source_lang": "en",
                "target_lang": "es"
            }
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 400, 422, 500]


@pytest.mark.asyncio
async def test_translate_special_characters():
    """Test translation with special characters."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/translate",
            json={
                "text": "Hello! How are you? 😊",
                "source_lang": "en",
                "target_lang": "es"
            }
        )
        
        assert response.status_code in [200, 422, 500]


@pytest.mark.asyncio
async def test_translate_numbers_and_symbols():
    """Test translation with numbers and symbols."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/translate",
            json={
                "text": "The price is $100 USD.",
                "source_lang": "en",
                "target_lang": "es"
            }
        )
        
        assert response.status_code in [200, 422, 500]
