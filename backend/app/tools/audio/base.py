from abc import ABC, abstractmethod

class AudioProvider(ABC):
    @abstractmethod
    async def generate_music(
        self,
        style: str,
        duration: float,
        output_path: str
    ) -> str:
        """
        Generate background music audio file.
        
        Args:
            style: Music vibe ('Cinematic', 'Energetic', 'Calm', 'Technology', 'None')
            duration: Required audio duration in seconds
            output_path: File path to save generated MP3
            
        Returns:
            str: Path to output audio file
        """
        pass
