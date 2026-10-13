import os
import asyncio
import subprocess
import urllib.request
import json
from typing import Optional, Dict, Any
from ...utils.logger import logger
from .base import VoiceProvider


class ElevenLabsVoiceProvider(VoiceProvider):
    """
    ElevenLabs API TTS Provider — studio-quality neural voices.
    Auto-selects best voice based on language and style preference.
    Uses eleven_multilingual_v2 model for maximum quality.
    """

    # Premium voice IDs (pre-made voices, available on all plans)
    VOICE_MAP = {
        "Professional": {
            "male":   "ErXwobaYiN019PkySvjV",  # Antoni — deep professional male
            "female": "EXAVITQu4vr4xnSDxMaL",  # Sarah — clear professional female
        },
        "Energetic": {
            "male":   "VR6AewLTigWG4xSOukaG",  # Arnold — strong energetic male
            "female": "jsCqWAovK2LkecY7zXl4",  # Dorothy — bright energetic female
        },
        "Friendly": {
            "male":   "TxGEqnHWrfWFTfGW9XjX",  # Josh — warm friendly male
            "female": "FGY2WhTYpPnrIDTdsKH5",  # Laura — warm friendly female
        },
        "Narrator": {
            "male":   "onwK4e9ZLuTAKqWW03F9",  # Daniel — smooth narrator male
            "female": "XB0fDUnXU5powFXDhCwa",  # Charlotte — elegant narrator female
        },
    }

    DEFAULT_VOICE_ID = "ErXwobaYiN019PkySvjV"  # Antoni

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY", "")

    def _select_voice_id(self, voice_pref: str) -> str:
        style_voices = self.VOICE_MAP.get(voice_pref, self.VOICE_MAP["Professional"])
        return style_voices.get("male", self.DEFAULT_VOICE_ID)

    async def generate_speech(
        self,
        text: str,
        output_path: str,
        voice: str = "Professional",
        language: str = "English",
        style: Optional[str] = None
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("ElevenLabs API Key not set. Add ELEVENLABS_API_KEY to .env")

        voice_id = self._select_voice_id(voice)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        payload = json.dumps({
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.45,
                "similarity_boost": 0.80,
                "style": 0.3,
                "use_speaker_boost": True
            }
        }).encode("utf-8")

        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg"
        }

        logger.info(f"[ElevenLabs] Generating speech — voice={voice_id}, chars={len(text)}")

        loop = asyncio.get_event_loop()

        def _request():
            req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=60) as resp:
                if resp.status == 200:
                    return resp.read()
                raise RuntimeError(f"ElevenLabs error {resp.status}")

        audio_data = await loop.run_in_executor(None, _request)

        with open(output_path, "wb") as f:
            f.write(audio_data)

        # Get duration via ffprobe
        duration = 0.0
        try:
            cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration",
                   "-of", "default=noprint_wrappers=1:nokey=1", output_path]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if res.stdout.strip():
                duration = float(res.stdout.strip())
        except Exception:
            word_count = len(text.split())
            duration = max(3.0, word_count / 2.5)

        logger.info(f"[ElevenLabs] ✓ Speech generated — {duration:.1f}s → {output_path}")

        return {
            "audio_path": output_path,
            "duration": duration,
            "subtitles_text": "",
            "voice_used": f"ElevenLabs-{voice_id[:8]}"
        }
