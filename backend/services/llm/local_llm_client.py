"""Unified local LLM client combining Llama and Sarvam."""
from typing import Dict, List
from backend.services.llm.llama_client import LlamaClient
from backend.services.llm.sarvam_client import SarvamClient
from backend.services.llm.router import choose_model


# Shared system prompt for chat
SYSTEM_PROMPT = """You are Drishti AI, a helpful multilingual assistant supporting English and Indian languages (Hindi, Bengali, Marathi, Tamil, Telugu, Gujarati, Kannada, Malayalam, Odia, Punjabi).

Guidelines:
- Reply in the SAME LANGUAGE as the user unless they explicitly ask you to translate
- Keep responses concise and TTS-friendly (avoid overly long paragraphs)
- If the user asks to translate, output ONLY the translated text without explanation
- Be helpful, accurate, and culturally aware
- For code or technical topics, provide clear step-by-step explanations"""

TRANSLATION_PROMPT_TEMPLATE = """Translate the following text from {source_lang} to {target_lang}.
Output ONLY the translated text, nothing else.

Text: {text}

Translation:"""


class LocalLLMClient:
    """Unified LLM client with routing between Llama and Sarvam."""
    
    def __init__(self, llama_client: LlamaClient, sarvam_client: SarvamClient):
        """Initialize with both LLM clients.
        
        Args:
            llama_client: Llama 3.1 client instance
            sarvam_client: Sarvam-1 client instance
        """
        self.llama_client = llama_client
        self.sarvam_client = sarvam_client
    
    def chat(self, text: str, lang: str, context: str = "") -> Dict[str, str]:
        """Generate chat response with routing.
        
        Args:
            text: User message text
            lang: Detected language code
            context: Additional context (e.g., from documents)
        
        Returns:
            Dict with 'reply' and 'model_used'
        """
        # Choose model based on text and language
        model_choice = choose_model(text, lang)
        
        # Build messages
        system_content = SYSTEM_PROMPT
        if context:
            system_content += f"\n\nContext from uploaded documents:\n{context}"
        
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": text}
        ]
        
        # Route to appropriate model
        if model_choice == "light":
            reply = self.sarvam_client.chat(messages)
            model_used = "sarvam-1"
        else:
            reply = self.llama_client.chat(messages)
            model_used = "llama-3.1-8b"
        
        return {
            "reply": reply,
            "model_used": model_used
        }
    
    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text between languages.
        
        Args:
            text: Text to translate
            source_lang: Source language code
            target_lang: Target language code
        
        Returns:
            Translated text
        """
        prompt = TRANSLATION_PROMPT_TEMPLATE.format(
            source_lang=source_lang,
            target_lang=target_lang,
            text=text
        )
        
        messages = [
            {"role": "user", "content": prompt}
        ]
        
        # Prefer Sarvam for Indic translations
        indic_langs = {"hi", "bn", "mr", "ta", "te", "gu", "kn", "ml", "or", "pa"}
        if source_lang in indic_langs or target_lang in indic_langs:
            return self.sarvam_client.chat(messages)
        else:
            return self.llama_client.chat(messages)
