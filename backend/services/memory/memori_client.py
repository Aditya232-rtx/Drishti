"""Memori integration with MongoDB backend."""
from typing import Dict
from pymongo import MongoClient
from memori import Memori
from backend.services.llm.local_llm_client import LocalLLMClient
from backend.config.settings import get_settings


class MemoriWrapper:
    """Wrapper for Memori with MongoDB backend for conversation storage."""
    
    def __init__(self, mongo_uri: str, memori_db_name: str, llm_client: LocalLLMClient):
        """Initialize Memori with MongoDB backend.
        
        Args:
            mongo_uri: MongoDB connection URI
            memori_db_name: Database name for Memori storage
            llm_client: LocalLLMClient instance for LLM calls
        """
        self.llm_client = llm_client
        self.mongo_uri = mongo_uri
        self.memori_db_name = memori_db_name
        
        print(f"Initializing Memori with MongoDB backend: {memori_db_name}")
        
        # Initialize MongoDB connection
        self.mongo_client = MongoClient(mongo_uri)
        self.db = self.mongo_client[memori_db_name]
        
        # Initialize Memori with MongoDB using lambda pattern
        # We won't register an LLM since we have custom local models
        # Instead, we'll use Memori for conversation/memory storage
        self.memori = Memori(conn=lambda: self.db)
        
        # Build storage schema
        self.memori.config.storage.build()
        
        print("✅ Memori initialized with MongoDB storage")
    
    def chat(self, user_id: str, session_id: str, text: str, lang: str) -> Dict[str, str]:
        """Chat with memory-enabled LLM.
        
        Args:
            user_id: User identifier
            session_id: Session identifier
            text: User message text
            lang: Language code
        
        Returns:
            Dict with 'reply', 'model_used', and 'session_id'
        """
        # Set attribution for this interaction
        self.memori.attribution(
            entity_id=user_id,
            process_id="drishti-ai"
        )
        
        # Set session
        self.memori.set_session(session_id)
        
        # Get conversation history from Memori
        # Note: Since we're not using Memori's LLM integration,
        # we'll store messages manually and call our LLM directly
        
        # Call our local LLM
        result = self.llm_client.chat(text=text, lang=lang)
        
        # Store user message in Memori
        try:
            # Use Memori's storage to save the interaction
            # This will help build up conversation context over time
            from datetime import datetime
            
            # Store in Memori's database for future context
            messages_col = self.db["messages"]
            messages_col.insert_one({
                "entity_id": user_id,
                "process_id": "drishti-ai",
                "session_id": session_id,
                "user_message": text,
                "assistant_message": result["reply"],
                "model_used": result["model_used"],
                "timestamp": datetime.utcnow()
            })
        except Exception as e:
            print(f"⚠️  Memori storage error: {e}")
        
        result["session_id"] = session_id
        return result



# Global instance
_memori_wrapper: MemoriWrapper = None


def get_memori_wrapper(llm_client: LocalLLMClient = None) -> MemoriWrapper:
    """Get or create Memori wrapper instance.
    
    Args:
        llm_client: LocalLLMClient instance (required for first call)
    
    Returns:
        MemoriWrapper instance
    """
    global _memori_wrapper
    if _memori_wrapper is None:
        if llm_client is None:
            raise ValueError("llm_client required for first initialization")
        
        settings = get_settings()
        _memori_wrapper = MemoriWrapper(
            mongo_uri=settings.MONGO_URI,
            memori_db_name=settings.MEMORI_MONGO_DB_NAME,
            llm_client=llm_client
        )
    return _memori_wrapper
