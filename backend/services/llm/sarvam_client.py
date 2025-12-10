"""Sarvam-1 local LLM client."""
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
from typing import List, Dict
import torch
from backend.config.settings import get_settings


class SarvamClient:
    """Client for Sarvam-1 Indic LLM."""
    
    def __init__(self, model_dir: Path = None):
        """Initialize Sarvam-1 model.
        
        Args:
            model_dir: Path to Sarvam-1 model directory
        """
        settings = get_settings()
        self.model_dir = model_dir or settings.SARVAM_MODEL_PATH
        
        if not self.model_dir.exists():
            raise FileNotFoundError(
                f"Sarvam-1 model not found at {self.model_dir}. "
                "Run scripts/download_models.py first."
            )
        
        print(f"Loading Sarvam-1 from {self.model_dir}...")
        
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(str(self.model_dir))
        self.model = AutoModelForCausalLM.from_pretrained(
            str(self.model_dir),
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto",
            low_cpu_mem_usage=True
        )
        
        # Create pipeline
        self.pipe = pipeline(
            "text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
            max_new_tokens=512,
            do_sample=True,
            temperature=0.7,
            top_p=0.9
        )
        
        print("✅ Sarvam-1 loaded successfully")
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Generate response from Sarvam-1.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
        
        Returns:
            Assistant response text
        """
        # Flatten messages into a single prompt
        prompt = self._build_prompt(messages)
        
        # Generate
        outputs = self.pipe(prompt, return_full_text=False)
        
        if outputs and len(outputs) > 0:
            return outputs[0]["generated_text"].strip()
        
        return "I apologize, but I couldn't generate a response."
    
    def _build_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Build prompt from messages.
        
        Args:
            messages: List of message dicts
        
        Returns:
            Formatted prompt string
        """
        parts = []
        
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "system":
                parts.append(f"System: {content}")
            elif role == "user":
                parts.append(f"User: {content}")
            elif role == "assistant":
                parts.append(f"Assistant: {content}")
        
        parts.append("Assistant:")
        return "\n\n".join(parts)
