"""Unit tests for LLM router."""
import pytest
from backend.services.llm.router import choose_model


def test_choose_model_long_text():
    """Test that long text selects heavy model."""
    long_text = "a" * 400
    result = choose_model(long_text, "en")
    assert result == "heavy"


def test_choose_model_heavy_keywords():
    """Test that heavy keywords select heavy model."""
    text = "Explain this step by step in detail"
    result = choose_model(text, "en")
    assert result == "heavy"


def test_choose_model_short_indic():
    """Test that short Indic text selects light model."""
    text = "नमस्ते"
    result = choose_model(text, "hi")
    assert result == "light"


def test_choose_model_short_english():
    """Test that short English text defaults to heavy."""
    text = "Hello"
    result = choose_model(text, "en")
    assert result == "heavy"


def test_choose_model_code_keyword():
    """Test that code keyword selects heavy model."""
    text = "Write code for this"
    result = choose_model(text, "en")
    assert result == "heavy"
