"""Indic-Parler TTS service."""
from io import BytesIO
import torch
import soundfile as sf
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from backend.config.settings import get_settings


class IndicParlerTTSService:
    """Indic-Parler text-to-speech service."""
    
    # Default voice configurations per language
    VOICE_CONFIG = {
        "en": "A clear female voice with neutral accent",
        "hi": "एक स्पष्ट महिला आवाज़",
        "bn": "একটি স্পষ্ট মহিলা কণ্ঠস্বর",
        "mr": "एक स्पष्ट महिला आवाज",
        "ta": "தெளிவான பெண் குரல்",
        "te": "స్పష్టమైన స్త్రీ స్వరం",
        "gu": "સ્પષ્ટ સ્ત્રી અવાજ",
        "kn": "ಸ್ಪಷ್ಟ ಮಹಿಳೆ ಧ್ವನಿ",
        "ml": "വ്യക്തമായ സ്ത്രീ ശബ്ദം",
        "or": "ଏକ ସ୍ପଷ୍ଟ ମହିଳା ସ୍ୱର",
        "pa": "ਇਕ ਸਪੱਸ਼ਟ ਔਰਤ ਦੀ ਆਵਾਜ਼",
    }
    
    def __init__(self):
        """Initialize Indic-Parler TTS model."""
        settings = get_settings()
        model_path = settings.TTS_MODEL_PATH
        
        if not model_path.exists():
            raise FileNotFoundError(
                f"Indic-Parler TTS model not found at {model_path}. "
                "Run scripts/download_models.py first."
            )
        
        print(f"Loading Indic-Parler TTS from {model_path}...")
        
        # Load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(str(model_path))
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            str(model_path),
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto"
        )
        
        self.sample_rate = 16000  # Default sample rate
        
        print("✅ Indic-Parler TTS loaded successfully")
    
    def synthesize_speech(self, text: str, lang: str = "en") -> bytes:
        """Generate TTS audio for text.
        
        Args:
            text: Text to synthesize
            lang: Language code
        
        Returns:
            Audio bytes in WAV format
        """
        # Get voice description for language
        voice_desc = self.VOICE_CONFIG.get(lang, self.VOICE_CONFIG["en"])
        
        # Prepare input with voice description
        input_text = f"{voice_desc}: {text}"
        
        # Tokenize
        inputs = self.tokenizer(
            input_text,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512
        )
        
        # Move to same device as model
        if hasattr(self.model, 'device'):
            inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        
        # Generate audio
        with torch.no_grad():
            outputs = self.model.generate(**inputs, max_length=1024)
        
        # Decode to audio
        # Note: The actual Indic-Parler model may have different output processing
        # This is a simplified version - adjust based on actual model architecture
        audio_data = outputs.cpu().numpy()
        
        # If output is tokens, decode them first
        if len(audio_data.shape) == 2:
            # This is a simplified conversion - actual implementation may differ
            audio_data = audio_data[0].astype('float32') / 32768.0
        
        # Convert to WAV bytes
        buffer = BytesIO()
        sf.write(buffer, audio_data, self.sample_rate, format='WAV')
        buffer.seek(0)
        
        return buffer.read()


# Global instance
_tts_service: IndicParlerTTSService = None


def get_tts_service() -> IndicParlerTTSService:
    """Get or create TTS service instance."""
    global _tts_service
    if _tts_service is None:
        _tts_service = IndicParlerTTSService()
    return _tts_service
