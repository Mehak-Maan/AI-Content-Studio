import os
import asyncio
import aiohttp
from typing import Optional
from ...utils.logger import logger
from .base import VideoProvider

class HuggingFaceVideoProvider(VideoProvider):
    """
    Hugging Face API-based text-to-video provider.
    Supports Models like zeroscope_v2_576w, cerspense/zeroscope_v2_576w, or CogVideoX.
    """
    def __init__(self, api_token: Optional[str] = None):
        from ...config.settings import settings
        self.api_token = api_token or getattr(settings, "HUGGINGFACE_API_KEY", os.getenv("HUGGINGFACE_API_KEY", ""))
        self.api_url = "https://router.huggingface.co/hf-inference/models/damo-vilab/text-to-video-ms-1.7b"

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
        if not self.api_token:
            raise ValueError("Hugging Face API key is missing. Please configure HUGGINGFACE_API_KEY.")

        headers = {"Authorization": f"Bearer {self.api_token}"}
        payload = {
            "inputs": f"{prompt}, {style}, 8k, cinematic lighting, master quality",
            "parameters": {
                "num_frames": int(duration * 16),
                "fps": 16
            }
        }

        logger.info(f"[HuggingFaceVideoProvider] Requesting video generation for prompt: {prompt[:60]}...")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=8)) as resp:
                    if resp.status == 200:
                        video_bytes = await resp.read()
                        with open(output_path, "wb") as f:
                            f.write(video_bytes)
                        return output_path
                    elif resp.status == 503:
                        data = await resp.json()
                        estimated_time = data.get("estimated_time", 20)
                        raise RuntimeError(f"Hugging Face model is loading (estimated {estimated_time}s). Free tier busy.")
                    elif resp.status == 429:
                        raise RuntimeError("Hugging Face rate limit/free quota reached.")
                    else:
                        err_text = await resp.text()
                        raise RuntimeError(f"Hugging Face video generation failed ({resp.status}): {err_text[:200]}")
        except Exception as e:
            import traceback
            logger.warning(f"[HuggingFaceVideoProvider] Hugging Face video generation unavailable ({e}). Traceback: {traceback.format_exc()}\nFalling back to procedural engine.")
            from .procedural_provider import ProceduralMotionVideoProvider
            fallback_provider = ProceduralMotionVideoProvider()
            return await fallback_provider.generate_video(
                prompt=prompt,
                duration=duration,
                aspect_ratio=aspect_ratio,
                output_path=output_path,
                style=style,
                scene_number=scene_number,
                total_scenes=total_scenes,
                subtitle=subtitle
            )
