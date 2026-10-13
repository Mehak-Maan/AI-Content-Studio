import os
import shutil
import logging
import asyncio
from typing import Optional
from .base import VideoProvider
from ...config.settings import settings

logger = logging.getLogger(__name__)

class MagicHourVideoProvider(VideoProvider):
    """
    Video generation provider powered by MagicHour.ai (Text-to-Video).
    Generates authentic AI-rendered video clips.
    Falls back smoothly to JSON2Video or AIMotionVideoProvider if error occurs.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.MAGIC_HOUR_API_KEY or os.environ.get("MAGIC_HOUR_API_KEY", "")

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
            logger.warning("[MagicHourVideoProvider] No MAGIC_HOUR_API_KEY found. Falling back.")
            return await self._fallback(prompt, duration, aspect_ratio, output_path, style, scene_number, total_scenes, subtitle)

        # Map aspect ratio
        ar = "16:9"
        if "9:16" in aspect_ratio:
            ar = "9:16"
        elif "1:1" in aspect_ratio:
            ar = "1:1"

        # Ensure clip_duration is integer (MagicHour API requirement) and budgeted for multi-scene generation
        clip_duration = int(round(min(4.0, max(3.0, float(duration)))))

        logger.info(f"[MagicHourVideoProvider] Scene {scene_number}/{total_scenes}: Requesting video from MagicHour.ai | Prompt: {prompt[:80]}...")

        try:
            from magic_hour import Client
            temp_download_dir = os.path.join(os.path.dirname(output_path), f"mh_temp_{scene_number}")
            os.makedirs(temp_download_dir, exist_ok=True)

            client = Client(token=self.api_key)

            def _generate():
                res = client.v1.text_to_video.generate(
                    name=f"Scene_{scene_number}",
                    end_seconds=clip_duration,
                    aspect_ratio=ar,
                    resolution="480p",
                    style={
                        "prompt": f"{prompt}, {style}, cinematic lighting, photorealistic"
                    },
                    wait_for_completion=True,
                    download_outputs=True,
                    download_directory=temp_download_dir
                )
                return res

            loop = asyncio.get_running_loop()
            response = await loop.run_in_executor(None, _generate)

            downloaded_paths = getattr(response, "downloaded_paths", None) or []
            if not downloaded_paths:
                # Search temp directory
                files = [os.path.join(temp_download_dir, f) for f in os.listdir(temp_download_dir) if f.endswith(".mp4")]
                if files:
                    downloaded_paths = files

            if not downloaded_paths:
                raise RuntimeError(f"MagicHour video generation finished without output files. Response: {response}")

            downloaded_file = downloaded_paths[0]
            shutil.copyfile(downloaded_file, output_path)
            shutil.rmtree(temp_download_dir, ignore_errors=True)

            logger.info(f"[MagicHourVideoProvider] Scene {scene_number} successfully saved to {output_path} ({os.path.getsize(output_path)} bytes)")
            return output_path

        except Exception as e:
            logger.warning(f"[MagicHourVideoProvider] Generation failed ({e}). Falling back.")
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
        logger.info(f"[MagicHourVideoProvider] Using Procedural fallback for Scene {scene_number}")
        from .procedural_provider import ProceduralMotionVideoProvider
        return await ProceduralMotionVideoProvider().generate_video(
            prompt=prompt,
            duration=duration,
            aspect_ratio=aspect_ratio,
            output_path=output_path,
            style=style,
            scene_number=scene_number,
            total_scenes=total_scenes,
            subtitle=subtitle
        )
