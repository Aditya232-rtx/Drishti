"""Unit tests for document parsers."""
import pytest
from pathlib import Path
from backend.services.documents.parsers import parse_txt, chunk_text


def test_parse_txt(sample_text_file):
    """Test TXT file parsing."""
    content = parse_txt(sample_text_file)
    assert "test document" in content.lower()
    assert "sample text" in content.lower()


def test_chunk_text():
    """Test text chunking."""
    text = "This is sentence one. This is sentence two. This is sentence three."
    chunks = chunk_text(text, chunk_size=30, overlap=10)
    
    assert len(chunks) > 0
    assert all(len(chunk) <= 40 for chunk in chunks)  # Allow some overflow


def test_chunk_text_empty():
    """Test chunking empty text."""
    chunks = chunk_text("", chunk_size=100, overlap=10)
    assert chunks == []


def test_chunk_text_single():
    """Test chunking text smaller than chunk size."""
    text = "Short text"
    chunks = chunk_text(text, chunk_size=100, overlap=10)
    assert len(chunks) == 1
    assert chunks[0] == "Short text"
