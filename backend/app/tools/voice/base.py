from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any

class VoiceProvider(ABC):
    @abstractmethod
    async def generate_speech(
        self,
        text: str,
        output_path: str,
        voice: str = "Professional",
        language: str = "English",
        style: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate spoken audio MP3 from text.
        
        Args:
            text: Narration text to synthesize
            output_path: Destination file path for the MP3
            voice: Voice tone/name
            language: Target language
            style: Voice style/energy
            
        Returns:
            Dict containing:
                - "audio_path": file path
                - "duration": approximate audio duration in seconds
                - "word_timestamps": list of word boundaries if available
        """
        pass
