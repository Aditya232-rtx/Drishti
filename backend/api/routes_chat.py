"""Chat endpoints for text and audio interactions."""
import base64
from datetime import datetime
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import Optional
from langdetect import detect, LangDetectException
from backend.db.mongo import get_sessions_collection, get_messages_collection
from backend.services.stt.whisper_service import get_whisper_service
from backend.services.tts.indic_parler_service import get_tts_service
from backend.services.documents.document_store import get_relevant_chunks
from bson import ObjectId


router = APIRouter(prefix="/chat", tags=["chat"])


# Dependency injection placeholders - will be set in main.py
_memori_wrapper = None


def set_memori_wrapper(wrapper):
    """Set Memori wrapper instance."""
    global _memori_wrapper
    _memori_wrapper = wrapper


class TextChatRequest(BaseModel):
    """Text chat request model."""
    user_id: str
    session_id: Optional[str] = None
    text: str
    lang: str = "auto"


class TextChatResponse(BaseModel):
    """Text chat response model."""
    user_text: str
    assistant_text: str
    lang: str
    model_used: str
    session_id: str


class AudioChatResponse(BaseModel):
    """Audio chat response model."""
    user_text: str
    assistant_text: str
    lang: str
    model_used: str
    session_id: str
    audio_format: str
    audio_base64: str


@router.post("/text", response_model=TextChatResponse)
async def chat_text(request: TextChatRequest):
    """Handle text-based chat interaction.
    
    Args:
        request: TextChatRequest with user message
    
    Returns:
        TextChatResponse with assistant reply
    """
    if _memori_wrapper is None:
        raise HTTPException(status_code=500, detail="Memori not initialized")
    
    # Detect language if auto
    lang = request.lang
    if lang == "auto":
        try:
            lang = detect(request.text)
        except LangDetectException:
            lang = "en"
    
    # Get or create session
    session_id = request.session_id
    if not session_id:
        sessions_col = get_sessions_collection()
        session_record = {
            "user_id": request.user_id,
            "memori_session_id": str(ObjectId()),
            "title": request.text[:50] + ("..." if len(request.text) > 50 else ""),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await sessions_col.insert_one(session_record)
        session_id = str(result.inserted_id)
    
    # Get relevant document chunks
    chunks = await get_relevant_chunks(request.user_id, request.text, limit=5)
    context = "\n\n".join(chunks) if chunks else ""
    
    # Combine text with context
    text_with_context = request.text
    if context:
        text_with_context = f"{request.text}\n\n[Context from documents: {context}]"
    
    # Chat with Memori
    result = _memori_wrapper.chat(
        user_id=request.user_id,
        session_id=session_id,
        text=text_with_context,
        lang=lang
    )
    
    # Save messages to MongoDB
    messages_col = get_messages_collection()
    
    user_msg = {
        "session_id": session_id,
        "sender": "user",
        "text": request.text,
        "lang": lang,
        "created_at": datetime.utcnow()
    }
    await messages_col.insert_one(user_msg)
    
    assistant_msg = {
        "session_id": session_id,
        "sender": "assistant",
        "text": result["reply"],
        "lang": lang,
        "model_used": result["model_used"],
        "created_at": datetime.utcnow()
    }
    await messages_col.insert_one(assistant_msg)
    
    # Update session timestamp
    sessions_col = get_sessions_collection()
    await sessions_col.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"updated_at": datetime.utcnow()}}
    )
    
    return TextChatResponse(
        user_text=request.text,
        assistant_text=result["reply"],
        lang=lang,
        model_used=result["model_used"],
        session_id=session_id
    )


@router.post("/audio", response_model=AudioChatResponse)
async def chat_audio(
    user_id: str = Form(...),
    session_id: Optional[str] = Form(None),
    audio: UploadFile = File(...)
):
    """Handle audio-based chat interaction.
    
    Args:
        user_id: User identifier
        session_id: Optional session ID
        audio: Audio file
    
    Returns:
        AudioChatResponse with text and audio reply
    """
    if _memori_wrapper is None:
        raise HTTPException(status_code=500, detail="Memori not initialized")
    
    # Transcribe audio
    whisper_service = get_whisper_service()
    audio_bytes = await audio.read()
    
    try:
        stt_result = whisper_service.transcribe_audio(audio_bytes)
        user_text = stt_result.text
        lang = stt_result.lang
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"STT error: {str(e)}")
    
    # Get or create session
    if not session_id:
        sessions_col = get_sessions_collection()
        session_record = {
            "user_id": user_id,
            "memori_session_id": str(ObjectId()),
            "title": user_text[:50] + ("..." if len(user_text) > 50 else ""),
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        result = await sessions_col.insert_one(session_record)
        session_id = str(result.inserted_id)
    
    # Get document context
    chunks = await get_relevant_chunks(user_id, user_text, limit=5)
    context = "\n\n".join(chunks) if chunks else ""
    
    text_with_context = user_text
    if context:
        text_with_context = f"{user_text}\n\n[Context: {context}]"
    
    # Chat with Memori
    result = _memori_wrapper.chat(
        user_id=user_id,
        session_id=session_id,
        text=text_with_context,
        lang=lang
    )
    
    assistant_text = result["reply"]
    
    # Generate TTS
    tts_service = get_tts_service()
    try:
        audio_bytes = tts_service.synthesize_speech(assistant_text, lang)
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")
    
    # Save messages
    messages_col = get_messages_collection()
    
    user_msg = {
        "session_id": session_id,
        "sender": "user",
        "text": user_text,
        "lang": lang,
        "created_at": datetime.utcnow()
    }
    await messages_col.insert_one(user_msg)
    
    assistant_msg = {
        "session_id": session_id,
        "sender": "assistant",
        "text": assistant_text,
        "lang": lang,
        "model_used": result["model_used"],
        "created_at": datetime.utcnow()
    }
    await messages_col.insert_one(assistant_msg)
    
    # Update session
    sessions_col = get_sessions_collection()
    await sessions_col.update_one(
        {"_id": ObjectId(session_id)},
        {"$set": {"updated_at": datetime.utcnow()}}
    )
    
    return AudioChatResponse(
        user_text=user_text,
        assistant_text=assistant_text,
        lang=lang,
        model_used=result["model_used"],
        session_id=session_id,
        audio_format="wav",
        audio_base64=audio_base64
    )
