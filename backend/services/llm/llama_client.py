"""Llama 3.1 client via Ollama HTTP API."""
import httpx
from typing import List, Dict
from backend.config.settings import get_settings


class LlamaClient:
    """Client for Llama 3.1 via Ollama."""
    
    def __init__(self, base_url: str = None, model_name: str = None):
        """Initialize Llama client.
        
        Args:
            base_url: Ollama API URL
            model_name: Model name in Ollama
        """
        settings = get_settings()
        self.base_url = base_url or settings.LLAMA_OLLAMA_URL
        self.model_name = model_name or settings.LLAMA_MODEL_NAME
        self.chat_url = f"{self.base_url}/api/chat"
    
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """Send chat request to Llama via Ollama.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
        
        Returns:
            Assistant response text
        
        Raises:
            Exception: If Ollama is unreachable or returns error
        """
        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature
            }
        }
        
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(self.chat_url, json=payload)
                response.raise_for_status()
                
                data = response.json()
                return data.get("message", {}).get("content", "").strip()
        
        except httpx.ConnectError:
            raise Exception(
                f"Failed to connect to Ollama at {self.base_url}. "
                "Ensure Ollama is running and llama3.1 model is pulled."
            )
        except httpx.HTTPStatusError as e:
            raise Exception(f"Ollama API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            raise Exception(f"Llama client error: {str(e)}")
