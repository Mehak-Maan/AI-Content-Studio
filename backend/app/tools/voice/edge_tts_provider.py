import os
import edge_tts
from typing import Optional, Dict, Any
from ...utils.logger import logger
from .base import VoiceProvider

class EdgeTTSVoiceProvider(VoiceProvider):
    """
    Microsoft Edge Neural TTS Provider.
    100% Free, crystal-clear studio quality, supports English, Urdu, Hindi, Spanish, French, etc.
    """

    VOICE_MAP = {
        "English": {
            "Professional": "en-US-ChristopherNeural",
            "Friendly": "en-US-EmmaNeural",
            "Energetic": "en-US-GuyNeural",
            "Narrator": "en-US-EricNeural",
            "Default": "en-US-ChristopherNeural"
        },
        "Urdu": {
            "Professional": "ur-PK-AsadNeural",
            "Friendly": "ur-PK-UzmaNeural",
            "Energetic": "ur-PK-AsadNeural",
            "Narrator": "ur-PK-UzmaNeural",
            "Default": "ur-PK-AsadNeural"
        },
        "Roman Urdu": {
            "Professional": "en-IN-PrabhatNeural",
            "Friendly": "en-IN-NeerjaNeural",
            "Energetic": "en-IN-PrabhatNeural",
            "Narrator": "en-IN-NeerjaNeural",
            "Default": "en-IN-PrabhatNeural"
        },
        "Hindi": {
            "Professional": "hi-IN-MadhurNeural",
            "Friendly": "hi-IN-SwaraNeural",
            "Energetic": "hi-IN-MadhurNeural",
            "Narrator": "hi-IN-SwaraNeural",
            "Default": "hi-IN-MadhurNeural"
        }
    }

    def _select_voice(self, language: str, voice_pref: str) -> str:
        lang_voices = self.VOICE_MAP.get(language, self.VOICE_MAP["English"])
        return lang_voices.get(voice_pref, lang_voices["Default"])

    async def generate_speech(
        self,
        text: str,
        output_path: str,
        voice: str = "Professional",
        language: str = "English",
        style: Optional[str] = None
    ) -> Dict[str, Any]:
        selected_voice = self._select_voice(language, voice)
        logger.info(f"[EdgeTTS] Generating speech with voice '{selected_voice}' for text ({len(text)} chars)...")

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        communicate = edge_tts.Communicate(text, selected_voice)
        sub_maker = edge_tts.SubMaker()
        
        with open(output_path, "wb") as file:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    file.write(chunk["data"])
                elif chunk["type"] == "WordBoundary":
                    sub_maker.feed(chunk)

        # Get audio duration using ffprobe or file estimation
        duration = 0.0
        try:
            import subprocess
            cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{output_path}"'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.stdout.strip():
                duration = float(result.stdout.strip())
        except Exception:
            # Fallback estimation: average 150 words per minute ~ 2.5 words per sec
            word_count = len(text.split())
            duration = max(3.0, word_count / 2.5)

        logger.info(f"[EdgeTTS] Speech generation completed. Duration: {duration:.2f}s -> {output_path}")

        return {
            "audio_path": output_path,
            "duration": duration,
            "subtitles_text": sub_maker.get_srt() if sub_maker else "",
            "voice_used": selected_voice
        }
