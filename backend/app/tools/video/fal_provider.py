import os
import logging
import asyncio
import aiohttp
from typing import Optional
from .base import VideoProvider
from ...config.settings import settings

logger = logging.getLogger(__name__)

class FalAIVideoProvider(VideoProvider):
    """
    Video generation provider powered by Fal.ai (Wan 2.1 / LTX-Video).
    Generates genuine high-definition AI video clips.
    Falls back smoothly to AIMotionVideoProvider (Pollinations + FFmpeg) if credits expire or rate limits occur.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.FAL_KEY or os.environ.get("FAL_KEY", "")
        if self.api_key:
            os.environ["FAL_KEY"] = self.api_key

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
        out_dir = os.path.dirname(output_path)
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        if not self.api_key:
            logger.warning("[FalAIVideoProvider] No FAL_KEY found. Falling back to AI Motion provider.")
            return await self._fallback(prompt, duration, aspect_ratio, output_path, style, scene_number, total_scenes, subtitle)

        os.environ["FAL_KEY"] = self.api_key

        # Map aspect ratio for Fal AI
        fal_aspect = "16:9"
        if "9:16" in aspect_ratio:
            fal_aspect = "9:16"
        elif "1:1" in aspect_ratio:
            fal_aspect = "1:1"

        logger.info(f"[FalAIVideoProvider] Scene {scene_number}/{total_scenes}: Requesting video from Fal.ai (Wan 2.1) | Prompt: {prompt[:80]}...")

        try:
            import fal_client

            def _submit_fal():
                # Wan 2.1 text-to-video model on Fal.ai
                # High quality, fast generation
                res = fal_client.subscribe(
                    "fal-ai/wan/v2.1/text-to-video",
                    arguments={
                        "prompt": f"{prompt}, high quality, cinematic lighting, photorealistic, 4k",
                        "aspect_ratio": fal_aspect,
                    },
                    with_logs=False,
                )
                return res

            # Run synchronous fal subscription in async thread pool
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, _submit_fal)

            video_data = result.get("video") or {}
            video_url = video_data.get("url")

            if not video_url:
                raise RuntimeError(f"Fal.ai returned no video URL: {result}")

            logger.info(f"[FalAIVideoProvider] Downloading generated video from {video_url[:60]}...")
            async with aiohttp.ClientSession() as session:
                async with session.get(video_url, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                    if resp.status != 200:
                        raise RuntimeError(f"Failed to download video from Fal.ai URL: status {resp.status}")
                    video_bytes = await resp.read()
                    with open(output_path, "wb") as f:
                        f.write(video_bytes)

            logger.info(f"[FalAIVideoProvider] Successfully saved real AI video clip to {output_path} ({len(video_bytes)} bytes)")
            return output_path

        except Exception as e:
            logger.warning(f"[FalAIVideoProvider] Fal.ai generation failed ({e}). Falling back to AI Motion provider.")
            return await self._fallback(prompt, duration, aspect_ratio, output_path, style, scene_number, total_scenes, subtitle)

    async def _fallback(
        self,
        prompt: str,
        duration: float,
        aspect_ratio: str,
        output_path: str,
        style: str,
        scene_number: int,
        total_scenes: int,
        subtitle: str
    ) -> str:
        from .ai_motion_provider import AIMotionVideoProvider
        fallback = AIMotionVideoProvider()
        return await fallback.generate_video(
            prompt=prompt,
            duration=duration,
            aspect_ratio=aspect_ratio,
            output_path=output_path,
            style=style,
            scene_number=scene_number,
            total_scenes=total_scenes,
            subtitle=subtitle
        )
