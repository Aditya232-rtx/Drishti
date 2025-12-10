"""Main FastAPI application entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config.settings import get_settings
from backend.db.mongo import MongoDB
from backend.services.llm.llama_client import LlamaClient
from backend.services.llm.sarvam_client import SarvamClient
from backend.services.llm.local_llm_client import LocalLLMClient
from backend.services.memory.memori_client import get_memori_wrapper
from backend.api import routes_health, routes_chat, routes_files, routes_translate


# Global service instances
llm_client: LocalLLMClient = None
memori_wrapper = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global llm_client, memori_wrapper
    
    settings = get_settings()
    
    print("🚀 Starting Drishti AI Backend...")
    
    # Ensure directories exist
    settings.BASE_DIR.mkdir(parents=True, exist_ok=True)
    settings.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    settings.AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    settings.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    settings.MEMORI_DIR.mkdir(parents=True, exist_ok=True)
    
    # Connect to MongoDB
    await MongoDB.connect()
    
    # Initialize LLM clients
    print("Initializing LLM clients...")
    llama_client_instance = LlamaClient()
    sarvam_client_instance = SarvamClient()
    llm_client = LocalLLMClient(llama_client_instance, sarvam_client_instance)
    print("✅ LLM clients initialized")
    
    # Initialize Memori with MongoDB backend
    memori_wrapper = get_memori_wrapper(llm_client)
    
    # Inject dependencies into routes
    routes_chat.set_memori_wrapper(memori_wrapper)
    routes_translate.set_llm_client(llm_client)
    
    print("✅ Drishti AI Backend ready!")
    
    yield
    
    # Cleanup
    print("\n🛑 Shutting down Drishti AI Backend...")
    await MongoDB.disconnect()
    print("👋 Goodbye!")


# Create FastAPI app
app = FastAPI(
    title="Drishti AI",
    description="Local-first AI assistant with chat, voice, files, and translation",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(routes_health.router)
app.include_router(routes_chat.router)
app.include_router(routes_files.router)
app.include_router(routes_translate.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Drishti AI",
        "version": "1.0.0",
        "docs": "/docs"
    }
