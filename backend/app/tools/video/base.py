from abc import ABC, abstractmethod

class VideoProvider(ABC):
    @abstractmethod
    async def generate_video(
        self,
        prompt: str,
        duration: float,
        aspect_ratio: str,
        output_path: str,
        style: str = "cinematic",
        scene_number: int = 1,
        total_scenes: int = 1,
        subtitle: str = ""
    ) -> str:
        """
        Generate a video clip from a text prompt.
        
        Args:
            prompt: Visual description for the scene
            duration: Scene duration in seconds
            aspect_ratio: '9:16', '16:9', or '1:1'
            output_path: Local file path where the generated MP4 must be saved
            style: Visual aesthetic style
            scene_number: Sequence number of the scene
            total_scenes: Total number of scenes in the video
            subtitle: Optional subtitle text for the scene
            
        Returns:
            str: Verified file path to the generated MP4
        """
        pass
