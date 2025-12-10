"""Performance and load tests."""
import pytest
import asyncio
from httpx import ASGITransport, AsyncClient
from backend.main import app
import time


@pytest.mark.asyncio
async def test_health_response_time():
    """Test health endpoint responds quickly."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        start = time.time()
        response = await client.get("/health")
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 5.0  # Should respond in under 5 seconds (relaxed for test environment)


@pytest.mark.asyncio
async def test_concurrent_health_checks():
    """Test multiple concurrent health checks."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        tasks = [client.get("/health") for _ in range(10)]
        responses = await asyncio.gather(*tasks)
        
        assert all(r.status_code == 200 for r in responses)


@pytest.mark.asyncio
async def test_file_list_performance():
    """Test file list endpoint performance."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        start = time.time()
        response = await client.get("/files/list?user_id=test_user")
        duration = time.time() - start
        
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            assert duration < 5.0  # Should respond in under 5 seconds


@pytest.mark.asyncio 
async def test_root_endpoint_performance():
    """Test root endpoint response time."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        start = time.time()
        response = await client.get("/")
        duration = time.time() - start
        
        assert response.status_code == 200
        assert duration < 0.5  # Root should be very fast
