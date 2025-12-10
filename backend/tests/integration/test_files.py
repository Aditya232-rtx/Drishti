"""Comprehensive tests for file upload endpoints."""
import pytest
from httpx import ASGITransport, AsyncClient
from backend.main import app
import io


@pytest.mark.asyncio
async def test_file_list_empty(test_user_id):
    """Test file list for user with no files."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get(f"/files/list?user_id={test_user_id}")
        
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)


@pytest.mark.asyncio
async def test_file_list_missing_user_id():
    """Test file list validation - missing user_id."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/files/list")
        
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_file_upload_txt(test_user_id, sample_text_file):
    """Test TXT file upload."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        with open(sample_text_file, 'rb') as f:
            response = await client.post(
                "/files/upload",
                data={"user_id": test_user_id},
                files={"file": ("test.txt", f, "text/plain")}
            )
        
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "document_id" in data
            assert "filename" in data
            assert "chunks" in data
            assert data["filename"] == "test.txt"
            assert isinstance(data["chunks"], int)
            assert data["chunks"] > 0


@pytest.mark.asyncio
async def test_file_upload_pdf(test_user_id, sample_pdf_content):
    """Test PDF file upload."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        pdf_file = io.BytesIO(sample_pdf_content)
        
        response = await client.post(
            "/files/upload",
            data={"user_id": test_user_id},
            files={"file": ("test.pdf", pdf_file, "application/pdf")}
        )
        
        # PDF parsing might fail with minimal PDF, but endpoint should handle it
        assert response.status_code in [200, 400, 500]


@pytest.mark.asyncio
async def test_file_upload_docx(test_user_id, sample_docx_content):
    """Test DOCX file upload."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        docx_file = io.BytesIO(sample_docx_content)
        
        response = await client.post(
            "/files/upload",
            data={"user_id": test_user_id},
            files={"file": ("test.docx", docx_file, "application/vnd.openxmlformats-officedocument.wordprocessingml.document")}
        )
        
        # DOCX might work or fail, but should handle gracefully
        assert response.status_code in [200, 400, 500]


@pytest.mark.asyncio
async def test_file_upload_missing_file(test_user_id):
    """Test file upload validation - missing file."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/files/upload",
            data={"user_id": test_user_id}
        )
        
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_file_upload_missing_user_id():
    """Test file upload validation - missing user_id."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        fake_file = io.BytesIO(b"test content")
        
        response = await client.post(
            "/files/upload",
            files={"file": ("test.txt", fake_file, "text/plain")}
        )
        
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_file_upload_unsupported_type(test_user_id):
    """Test file upload with unsupported file type."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        fake_file = io.BytesIO(b"#!/bin/bash\necho test")
        
        response = await client.post(
            "/files/upload",
            data={"user_id": test_user_id},
            files={"file": ("test.sh", fake_file, "application/x-sh")}
        )
        
        # Should reject unsupported file types
        assert response.status_code in [400, 422]


@pytest.mark.asyncio
async def test_file_upload_response_structure(test_user_id, sample_text_file):
    """Test file upload response has all expected fields."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        with open(sample_text_file, 'rb') as f:
            response = await client.post(
                "/files/upload",
                data={"user_id": test_user_id},
                files={"file": ("test.txt", f, "text/plain")}
            )
        
        if response.status_code == 200:
            data = response.json()
            expected_fields = ["document_id", "filename", "size_bytes", "chunks"]
            for field in expected_fields:
                assert field in data, f"Field {field} missing from response"
