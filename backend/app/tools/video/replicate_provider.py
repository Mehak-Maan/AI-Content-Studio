import os
import logging
import asyncio
import aiohttp
from typing import Optional
from .base import VideoProvider
from ...config.settings import settings

logger = logging.getLogger(__name__)

class ReplicateVideoProvider(VideoProvider):
    """
    Video generation provider powered by Replicate (e.g., LTX-Video / Wan 2.1).
    Generates authentic AI video clips.
    Gracefully falls back to AIMotionVideoProvider if credits are exhausted or an error occurs.
    """

    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token or settings.REPLICATE_API_TOKEN or os.environ.get("REPLICATE_API_TOKEN", "")
        if self.api_token:
            os.environ["REPLICATE_API_TOKEN"] = self.api_token

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

        if not self.api_token:
            logger.warning("[ReplicateVideoProvider] No REPLICATE_API_TOKEN found. Falling back to AI Motion provider.")
            return await self._fallback(prompt, duration, aspect_ratio, output_path, style, scene_number, total_scenes, subtitle)

        os.environ["REPLICATE_API_TOKEN"] = self.api_token

        logger.info(f"[ReplicateVideoProvider] Scene {scene_number}/{total_scenes}: Calling Replicate LTX-Video | Prompt: {prompt[:80]}...")

        try:
            import replicate

            def _run_replicate():
                client = replicate.Client(api_token=self.api_token)
                output = client.run(
                    "lightricks/ltx-video:8c47da666861d081eeb4d1261853087de23923a268a69b63febdf5dc1dee08e4",
                    input={
                        "prompt": f"{prompt}, cinematic lighting, photorealistic, 4k",
                        "negative_prompt": "low quality, blurry, distorted",
                    }
                )
                return output

            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(None, _run_replicate)

            # Replicate output is typically a FileOutput object or URL string
            video_url = str(result)
            if hasattr(result, "url"):
                video_url = result.url

            if not video_url or not str(video_url).startswith("http"):
                raise RuntimeError(f"Unexpected Replicate output: {result}")

            logger.info(f"[ReplicateVideoProvider] Downloading generated video from {video_url[:60]}...")
            async with aiohttp.ClientSession() as session:
                async with session.get(video_url, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                    if resp.status != 200:
                        raise RuntimeError(f"Failed to download video from Replicate URL: status {resp.status}")
                    video_bytes = await resp.read()
                    with open(output_path, "wb") as f:
                        f.write(video_bytes)

            logger.info(f"[ReplicateVideoProvider] Successfully saved Replicate video to {output_path} ({len(video_bytes)} bytes)")
            return output_path

        except Exception as e:
            logger.warning(f"[ReplicateVideoProvider] Replicate generation failed ({e}). Falling back to AI Motion provider.")
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
