from .base import VoiceProvider
from .edge_tts_provider import EdgeTTSVoiceProvider
from .elevenlabs_provider import ElevenLabsVoiceProvider
from ...config.settings import settings

def get_voice_provider() -> VoiceProvider:
    if settings.DEFAULT_VOICE_PROVIDER == "elevenlabs" and settings.ELEVENLABS_API_KEY:
        return ElevenLabsVoiceProvider(settings.ELEVENLABS_API_KEY)
    # Default to 100% Free EdgeTTS Neural
    return EdgeTTSVoiceProvider()

__all__ = ["VoiceProvider", "EdgeTTSVoiceProvider", "ElevenLabsVoiceProvider", "get_voice_provider"]
