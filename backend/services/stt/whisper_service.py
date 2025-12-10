"""Whisper STT service using faster-whisper."""
from dataclasses import dataclass
from io import BytesIO
import soundfile as sf
import numpy as np
from faster_whisper import WhisperModel
from backend.config.settings import get_settings


@dataclass
class STTResult:
    """STT transcription result."""
    text: str
    lang: str


class WhisperService:
    """Whisper speech-to-text service."""
    
    def __init__(self):
        """Initialize Whisper model."""
        settings = get_settings()
        
        print(f"Loading Whisper model '{settings.WHISPER_MODEL_SIZE}'...")
        
        self.model = WhisperModel(
            settings.WHISPER_MODEL_SIZE,
            download_root=str(settings.MODEL_DIR_WHISPER),
            device=settings.WHISPER_DEVICE,
            compute_type="int8"
        )
        
        print("✅ Whisper model loaded successfully")
    
    def transcribe_audio(self, audio_bytes: bytes) -> STTResult:
        """Transcribe audio to text.
        
        Args:
            audio_bytes: Audio file bytes (WAV, MP3, WEBM, etc.)
        
        Returns:
            STTResult with text and detected language
        """
        # Load audio using soundfile
        try:
            audio_data, sample_rate = sf.read(BytesIO(audio_bytes))
            
            # Convert to mono if stereo
            if len(audio_data.shape) > 1:
                audio_data = audio_data.mean(axis=1)
            
            # Ensure float32
            audio_data = audio_data.astype(np.float32)
            
        except Exception as e:
            raise ValueError(f"Failed to load audio: {str(e)}")
        
        # Transcribe
        segments, info = self.model.transcribe(
            audio_data,
            beam_size=5,
            language=None,  # Auto-detect
            task="transcribe"
        )
        
        # Collect all segments
        text_parts = []
        for segment in segments:
            text_parts.append(segment.text)
        
        full_text = " ".join(text_parts).strip()
        detected_lang = info.language if hasattr(info, 'language') else "en"
        
        return STTResult(
            text=full_text,
            lang=detected_lang
        )


# Global instance
_whisper_service: WhisperService = None


def get_whisper_service() -> WhisperService:
    """Get or create Whisper service instance."""
    global _whisper_service
    if _whisper_service is None:
        _whisper_service = WhisperService()
    return _whisper_service
