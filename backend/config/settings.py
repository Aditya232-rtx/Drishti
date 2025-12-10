"""Application settings and configuration."""
from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "drishti_ai"
    MEMORI_MONGO_DB_NAME: str = "drishti_memori"
    
    # Base directory for all local data
    # Changed from Path.home() / "ai-data" to keep models in project directory
    BASE_DIR: Path = Path(__file__).parent.parent / "models"
    
    # Model directories
    @property
    def MODEL_DIR_LLM(self) -> Path:
        return self.BASE_DIR / "models" / "llm"
    
    @property
    def MODEL_DIR_WHISPER(self) -> Path:
        return self.BASE_DIR / "models" / "whisper"
    
    @property
    def MODEL_DIR_TTS(self) -> Path:
        return self.BASE_DIR / "models" / "tts"
    
    @property
    def SARVAM_MODEL_PATH(self) -> Path:
        return self.MODEL_DIR_LLM / "sarvam-1"
    
    @property
    def TTS_MODEL_PATH(self) -> Path:
        return self.MODEL_DIR_TTS / "indic-parler"
    
    # Data directories
    @property
    def UPLOADS_DIR(self) -> Path:
        return self.BASE_DIR / "uploads"
    
    @property
    def AUDIO_DIR(self) -> Path:
        return self.BASE_DIR / "audio"
    
    @property
    def LOGS_DIR(self) -> Path:
        return self.BASE_DIR / "logs"
    
    @property
    def MEMORI_DIR(self) -> Path:
        return self.BASE_DIR / "memori"
    
    # LLM Configuration
    LLAMA_OLLAMA_URL: str = "http://localhost:11434"
    LLAMA_MODEL_NAME: str = "llama3.1"
    
    # Whisper Configuration
    WHISPER_MODEL_SIZE: str = "small"
    WHISPER_DEVICE: str = "auto"
    
    # Text Processing
    MAX_CHUNK_SIZE: int = 1024
    MAX_CONTEXT_CHUNKS: int = 5
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
