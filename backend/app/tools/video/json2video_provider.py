import os
import time
import logging
import asyncio
import aiohttp
import requests
from typing import Optional
from urllib.parse import quote_plus
from .base import VideoProvider
from ...config.settings import settings

logger = logging.getLogger(__name__)

class JSON2VideoProvider(VideoProvider):
    """
    Cloud Video Rendering provider using JSON2Video API.
    Combines high-definition AI generated imagery with cloud zoom & pan motion rendering,
    text overlays, and transitions, returning a cloud-rendered MP4 video.
    Falls back smoothly to AIMotionVideoProvider (Pollinations + FFmpeg) if quota or error happens.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.JSON2VIDEO_API_KEY or os.environ.get("JSON2VIDEO_API_KEY", "")
        self.base_url = "https://api.json2video.com/v2/movies"

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
            logger.warning("[JSON2VideoProvider] No JSON2VIDEO_API_KEY found. Falling back.")
            return await self._fallback(prompt, duration, aspect_ratio, output_path, style, scene_number, total_scenes, subtitle)

        # Resolution format for JSON2Video
        # landscape (16:9), portrait (9:16), square (1:1)
        res = "landscape"
        width, height = 1280, 720
        if "9:16" in aspect_ratio:
            res = "portrait"
            width, height = 720, 1280
        elif "1:1" in aspect_ratio:
            res = "square"
            width, height = 1080, 1080

        # AI image URL using Pollinations
        encoded_prompt = quote_plus(f"{prompt}, {style}, cinematic lighting, photorealistic, 4k")
        # Unique seed per scene
        seed = (int(time.time() * 1000) + scene_number * 37) % 999999
        ai_image_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed={seed}"

        pan_directions = ["right", "left", "top", "bottom"]
        pan_dir = pan_directions[(scene_number - 1) % len(pan_directions)]
        zoom_val = 3 if scene_number % 2 == 1 else -3

        scene_elements = [
            {
                "type": "image",
                "src": ai_image_url,
                "duration": max(2.5, float(duration)),
                "zoom": zoom_val,
                "pan": pan_dir
            }
        ]

        if subtitle and subtitle.strip():
            scene_elements.append({
                "type": "text",
                "text": subtitle.strip()[:100],
                "position": "bottom-center",
                "font-family": "Montserrat",
                "font-size": 42 if res == "landscape" else 36,
                "font-color": "#FFFFFF",
                "background-color": "rgba(0,0,0,0.6)",
                "duration": max(2.5, float(duration))
            })

        payload = {
            "resolution": res,
            "quality": "high",
            "scenes": [
                {
                    "duration": max(2.5, float(duration)),
                    "background-color": "#000000",
                    "elements": scene_elements
                }
            ]
        }

        headers = {
            "x-api-key": self.api_key,
            "Content-Type": "application/json"
        }

        logger.info(f"[JSON2VideoProvider] Scene {scene_number}/{total_scenes}: Submitting cloud render to JSON2Video...")

        try:
            loop = asyncio.get_running_loop()

            def _submit_job():
                resp = requests.post(self.base_url, json=payload, headers=headers, timeout=20)
                return resp

            resp = await loop.run_in_executor(None, _submit_job)
            if resp.status_code not in (200, 201):
                raise RuntimeError(f"JSON2Video submit failed ({resp.status_code}): {resp.text}")

            data = resp.json()
            project_id = data.get("project")
            if not project_id:
                raise RuntimeError(f"No project ID returned: {data}")

            logger.info(f"[JSON2VideoProvider] Project {project_id} started. Polling status...")

            # Poll for completion (up to 90 seconds)
            video_url = None
            poll_url = f"{self.base_url}?project={project_id}"

            for _ in range(18):
                await asyncio.sleep(5)
                def _check_status():
                    return requests.get(poll_url, headers=headers, timeout=15)
                status_resp = await loop.run_in_executor(None, _check_status)
                if status_resp.status_code == 200:
                    status_data = status_resp.json()
                    proj_data = status_data.get("movie") or status_data.get("project") or {}
                    curr_status = proj_data.get("status")
                    if curr_status == "done":
                        video_url = proj_data.get("url")
                        break
                    elif curr_status == "error":
                        raise RuntimeError(f"JSON2Video cloud render error: {proj_data.get('message')}")
                    logger.debug(f"[JSON2VideoProvider] Status: {curr_status}...")

            if not video_url:
                raise TimeoutError("JSON2Video render timed out after 90 seconds.")

            logger.info(f"[JSON2VideoProvider] Downloading completed cloud video from {video_url[:60]}...")
            async with aiohttp.ClientSession() as session:
                async with session.get(video_url, timeout=aiohttp.ClientTimeout(total=60)) as dl_resp:
                    if dl_resp.status != 200:
                        raise RuntimeError(f"Failed to download cloud video: HTTP {dl_resp.status}")
                    content = await dl_resp.read()
                    with open(output_path, "wb") as f:
                        f.write(content)

            logger.info(f"[JSON2VideoProvider] Scene {scene_number} saved to {output_path} ({len(content)} bytes)")
            return output_path

        except Exception as e:
            logger.warning(f"[JSON2VideoProvider] Generation failed ({e}). Falling back to local AI motion provider.")
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
