"""Comprehensive tests for health check endpoint."""
import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app


@pytest.mark.asyncio
async def test_health_endpoint_returns_200():
    """Test health check returns 200 OK."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_endpoint_response_structure():
    """Test health check has correct response structure."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        data = response.json()
        
        assert "status" in data
        assert "services" in data
        assert isinstance(data["services"], dict)


@pytest.mark.asyncio
async def test_health_services_all_present():
    """Test health check includes all required services."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        data = response.json()
        
        services = data["services"]
        required_services = ["mongodb", "ollama_llama", "sarvam", "whisper", "tts", "memori"]
        
        for service in required_services:
            assert service in services, f"Service {service} not in health check"


@pytest.mark.asyncio
async def test_health_mongodb_status():
    """Test MongoDB status is reported."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        data = response.json()
        
        assert "mongodb" in data["services"]
        assert isinstance(data["services"]["mongodb"], str)


@pytest.mark.asyncio
async def test_health_response_content_type():
    """Test health check returns JSON content type."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
        
        assert "application/json" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_root_endpoint_returns_200():
    """Test root endpoint returns 200."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_root_endpoint_structure():
    """Test root endpoint has welcome message and version."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        data = response.json()
        
        assert "message" in data
        assert "version" in data
        assert isinstance(data["message"], str)
        assert isinstance(data["version"], str)


@pytest.mark.asyncio
async def test_root_endpoint_message_content():
    """Test root endpoint message is correct."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/")
        data = response.json()
        
        assert "Drishti" in data["message"] or "API" in data["message"]
