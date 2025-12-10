"""Health check endpoint."""
from fastapi import APIRouter, Depends
from backend.config.settings import Settings, get_settings
from backend.db.mongo import MongoDB
from backend.services.llm.llama_client import LlamaClient
import httpx


router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
async def health_check(settings: Settings = Depends(get_settings)):
    """Check health of all services.
    
    Returns:
        Health status of all services
    """
    status = {
        "mongodb": "unknown",
        "ollama_llama": "unknown",
        "sarvam": "unknown",
        "whisper": "unknown",
        "tts": "unknown",
        "memori": "unknown"
    }
    
    # Check MongoDB
    try:
        if MongoDB.client:
            await MongoDB.client.admin.command('ping')
            status["mongodb"] = "✅ connected"
        else:
            status["mongodb"] = "❌ not initialized"
    except Exception as e:
        status["mongodb"] = f"❌ error: {str(e)}"
    
    # Check Ollama (Llama)
    try:
        llama_client = LlamaClient()
        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{llama_client.base_url}/api/tags")
            if response.status_code == 200:
                status["ollama_llama"] = "✅ reachable"
            else:
                status["ollama_llama"] = f"❌ status {response.status_code}"
    except Exception as e:
        status["ollama_llama"] = f"❌ unreachable: {str(e)}"
    
    # Check Sarvam model path
    try:
        if settings.SARVAM_MODEL_PATH.exists():
            status["sarvam"] = "✅ model present"
        else:
            status["sarvam"] = "❌ model not found"
    except Exception as e:
        status["sarvam"] = f"❌ error: {str(e)}"
    
    # Check Whisper model path
    try:
        if settings.MODEL_DIR_WHISPER.exists():
            status["whisper"] = "✅ model directory exists"
        else:
            status["whisper"] = "❌ model directory not found"
    except Exception as e:
        status["whisper"] = f"❌ error: {str(e)}"
    
    # Check TTS model path
    try:
        if settings.TTS_MODEL_PATH.exists():
            status["tts"] = "✅ model present"
        else:
            status["tts"] = "❌ model not found"
    except Exception as e:
        status["tts"] = f"❌ error: {str(e)}"
    
    # Check Memori (via MongoDB)
    try:
        if MongoDB.client:
            memori_db = MongoDB.client[settings.MEMORI_MONGO_DB_NAME]
            collections = await memori_db.list_collection_names()
            status["memori"] = f"✅ MongoDB backend ready ({len(collections)} collections)"
        else:
            status["memori"] = "❌ MongoDB not initialized"
    except Exception as e:
        status["memori"] = f"❌ error: {str(e)}"
    
    return {
        "status": "operational",
        "services": status
    }
