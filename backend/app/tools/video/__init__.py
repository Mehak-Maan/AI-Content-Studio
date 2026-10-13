from .base import VideoProvider
from .huggingface_provider import HuggingFaceVideoProvider
from .procedural_provider import ProceduralMotionVideoProvider
from .ai_motion_provider import AIMotionVideoProvider
from .fal_provider import FalAIVideoProvider
from .replicate_provider import ReplicateVideoProvider
from .json2video_provider import JSON2VideoProvider
from .magichour_provider import MagicHourVideoProvider
from ...config.settings import settings

def get_video_provider() -> VideoProvider:
    if settings.MAGIC_HOUR_API_KEY:
        return MagicHourVideoProvider()
    return ProceduralMotionVideoProvider()

__all__ = [
    "VideoProvider",
    "MagicHourVideoProvider",
    "JSON2VideoProvider",
    "ReplicateVideoProvider",
    "FalAIVideoProvider",
    "AIMotionVideoProvider",
    "HuggingFaceVideoProvider",
    "ProceduralMotionVideoProvider",
    "get_video_provider"
]
