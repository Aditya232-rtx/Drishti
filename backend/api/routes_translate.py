"""Translation endpoint with optional TTS."""
import base64
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.services.tts.indic_parler_service import get_tts_service


router = APIRouter(prefix="/translate", tags=["translation"])


# Dependency injection placeholder
_llm_client = None


def set_llm_client(client):
    """Set LLM client instance."""
    global _llm_client
    _llm_client = client


class TranslationRequest(BaseModel):
    """Translation request model."""
    text: str
    source_lang: str
    target_lang: str
    tts: bool = False


class TranslationResponse(BaseModel):
    """Translation response model."""
    input_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    audio_base64: Optional[str] = None


@router.post("", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """Translate text between languages.
    
    Args:
        request: TranslationRequest with text and language pair
    
    Returns:
        TranslationResponse with translated text and optional audio
    """
    if _llm_client is None:
        raise HTTPException(status_code=500, detail="LLM client not initialized")
    
    # Translate using LLM
    try:
        translated_text = _llm_client.translate(
            text=request.text,
            source_lang=request.source_lang,
            target_lang=request.target_lang
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")
    
    # Generate TTS if requested
    audio_base64 = None
    if request.tts:
        try:
            tts_service = get_tts_service()
            audio_bytes = tts_service.synthesize_speech(translated_text, request.target_lang)
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        except Exception as e:
            # TTS is optional, so just log error but don't fail
            print(f"⚠️  TTS generation failed: {e}")
    
    return TranslationResponse(
        input_text=request.text,
        translated_text=translated_text,
        source_lang=request.source_lang,
        target_lang=request.target_lang,
        audio_base64=audio_base64
    )
