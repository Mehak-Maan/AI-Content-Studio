import os
import urllib.request
import urllib.error
import subprocess
import random
import hashlib
import asyncio
from typing import Optional
from ...utils.logger import logger
from .base import VideoProvider

# ─────────────────────────────────────────────────
# CINEMATIC MOTION TYPES - 8 unique motions
# ─────────────────────────────────────────────────
MOTION_PRESETS = [
    # 0 - Slow dramatic zoom in to center
    lambda w, h, f: f"scale={w}:{h},zoompan=z='min(zoom+0.0015,1.30)':d={f}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={w}x{h}:fps=24",
    # 1 - Slow zoom out from center
    lambda w, h, f: f"scale={w}:{h},zoompan=z='if(lte(zoom,1.0),1.30,max(1.001,zoom-0.0015))':d={f}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={w}x{h}:fps=24",
    # 2 - Pan left to right + slight zoom
    lambda w, h, f: f"scale={w}:{h},zoompan=z='1.15':d={f}:x='(iw-iw/zoom)*(on/{f})':y='ih/2-(ih/zoom/2)':s={w}x{h}:fps=24",
    # 3 - Pan right to left + slight zoom
    lambda w, h, f: f"scale={w}:{h},zoompan=z='1.15':d={f}:x='(iw-iw/zoom)*(1-on/{f})':y='ih/2-(ih/zoom/2)':s={w}x{h}:fps=24",
    # 4 - Pan bottom to top (tilt up)
    lambda w, h, f: f"scale={w}:{h},zoompan=z='1.15':d={f}:x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*(on/{f})':s={w}x{h}:fps=24",
    # 5 - Pan top to bottom (tilt down)
    lambda w, h, f: f"scale={w}:{h},zoompan=z='1.15':d={f}:x='iw/2-(iw/zoom/2)':y='(ih-ih/zoom)*(1-on/{f})':s={w}x{h}:fps=24",
    # 6 - Zoom in + pan diagonal (top-left to bottom-right)
    lambda w, h, f: f"scale={w}:{h},zoompan=z='min(zoom+0.001,1.25)':d={f}:x='(iw-iw/zoom)*(on/{f})':y='(ih-ih/zoom)*(on/{f})':s={w}x{h}:fps=24",
    # 7 - Zoom out + pan diagonal (bottom-right to top-left)
    lambda w, h, f: f"scale={w}:{h},zoompan=z='if(lte(zoom,1.0),1.25,max(1.001,zoom-0.001))':d={f}:x='(iw-iw/zoom)*(1-on/{f})':y='(ih-ih/zoom)*(1-on/{f})':s={w}x{h}:fps=24",
]

# ─────────────────────────────────────────────────
# IMAGE STYLE MODIFIERS for variety
# ─────────────────────────────────────────────────
STYLE_MODS = [
    "cinematic photography, golden hour lighting, bokeh, shallow depth of field",
    "dramatic film noir, high contrast shadows, moody atmosphere",
    "vibrant hyperrealistic, ultra sharp 8k, studio lighting, award winning",
    "cinematic wide angle, epic landscape, volumetric light rays",
    "dark moody aesthetic, neon rim light, cyberpunk atmosphere",
    "warm natural light, documentary style, authentic realistic",
    "architectural cinematic, birds eye view, dramatic perspective",
    "macro close-up, crystal clear detail, professional photography",
]


class AIMotionVideoProvider(VideoProvider):
    """
    AI-Powered Motion Video Generator.
    Uses Pollinations.ai for unique scene-specific imagery with varied
    cinematic camera motions (8 unique Ken Burns presets) and style modifiers.
    Auto-selects unique styles per scene to avoid repetition.
    Falls back to procedural engine if network is unavailable.
    """

    def __init__(self):
        from .procedural_provider import ProceduralMotionVideoProvider
        self.fallback = ProceduralMotionVideoProvider()

    def _get_dimensions(self, aspect_ratio: str):
        if aspect_ratio == "16:9":
            return 1280, 720
        elif aspect_ratio == "1:1":
            return 768, 768
        else:
            return 720, 1280  # 9:16 default

    def _get_unique_seed(self, prompt: str, scene_number: int) -> int:
        """Generate a deterministic-but-unique seed per scene so images don't repeat."""
        combined = f"{prompt[:80]}_{scene_number}_{random.randint(0, 9999)}"
        return int(hashlib.md5(combined.encode()).hexdigest()[:8], 16) % 999999

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
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        w, h = self._get_dimensions(aspect_ratio)
        temp_img = output_path.replace(".mp4", f"_scene_{scene_number}_raw.jpg")

        try:
            # Select unique style modifier per scene (cycles through 8 styles)
            style_mod = STYLE_MODS[(scene_number - 1) % len(STYLE_MODS)]

            # Build high-quality prompt — clean, specific, no repetition
            clean_prompt = prompt.replace("\n", " ").strip()
            # Inject scene-specific visual keywords to force uniqueness
            scene_keywords = [
                "establishing wide shot", "extreme close-up detail", 
                "medium shot portrait", "overhead aerial view",
                "side angle profile", "low angle looking up",
                "silhouette against light", "interior ambient light"
            ]
            angle_hint = scene_keywords[(scene_number - 1) % len(scene_keywords)]
            
            enhanced_prompt = (
                f"{clean_prompt}, {angle_hint}, {style_mod}, "
                f"professional photography, no watermark, no text, no logo"
            )
            
            import urllib.parse
            encoded = urllib.parse.quote(enhanced_prompt[:300])
            seed = self._get_unique_seed(prompt, scene_number)

            image_url = (
                f"https://image.pollinations.ai/prompt/{encoded}"
                f"?width={w}&height={h}&nologo=true&seed={seed}"
            )

            logger.info(f"[AIMotionVideoProvider] Scene {scene_number}/{total_scenes} — fetching AI image (seed={seed})...")

            loop = asyncio.get_event_loop()

            import time
            def _download_image():
                # Add a small random delay to avoid hitting rate limit simultaneously
                time.sleep(random.uniform(0.5, 2.5))
                for attempt in range(3):
                    try:
                        req = urllib.request.Request(
                            image_url,
                            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                        )
                        with urllib.request.urlopen(req, timeout=20) as resp:
                            data = resp.read()
                            if len(data) < 3000:
                                raise ValueError(f"Image too small ({len(data)} bytes) — likely an error")
                            with open(temp_img, "wb") as f:
                                f.write(data)
                        return len(data)
                    except urllib.error.HTTPError as he:
                        if attempt == 2:
                            raise
                        logger.warning(f"[AIMotionVideoProvider] Rate limited or error on scene {scene_number} (Attempt {attempt+1}): {he}. Retrying...")
                        time.sleep(3 + attempt * 2)
                    except Exception as e:
                        if attempt == 2:
                            raise
                        time.sleep(2)

            size = await loop.run_in_executor(None, _download_image)
            logger.info(f"[AIMotionVideoProvider] Scene {scene_number} image downloaded ({size} bytes)")

            # Select unique motion preset per scene
            fps = 24
            total_frames = max(fps, int(duration * fps))
            motion_idx = (scene_number - 1) % len(MOTION_PRESETS)
            vf = MOTION_PRESETS[motion_idx](w, h, total_frames)

            # Render cinematic video
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1",
                "-i", temp_img,
                "-vf", vf,
                "-t", str(duration),
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-preset", "fast",
                "-crf", "20",
                output_path
            ]

            res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if res.returncode != 0 or not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
                raise RuntimeError(f"FFmpeg render failed (code {res.returncode}): {res.stderr[-300:]}")

            # Save scene thumbnail
            thumb_path = (
                output_path
                .replace("\\scenes\\", "\\thumbnails\\")
                .replace("/scenes/", "/thumbnails/")
                .replace(".mp4", ".jpg")
            )
            dirname = os.path.dirname(output_path)
            if dirname:
                os.makedirs(dirname, exist_ok=True)
            if os.path.exists(temp_img):
                import shutil
                try:
                    shutil.copyfile(temp_img, thumb_path)
                except Exception:
                    pass

            file_size = os.path.getsize(output_path)
            logger.info(
                f"[AIMotionVideoProvider] Scene {scene_number} done — "
                f"motion={motion_idx}, style={style_mod[:30]}..., size={file_size // 1024}KB"
            )
            return output_path

        except Exception as e:
            import traceback
            logger.warning(f"[AIMotionVideoProvider] Scene {scene_number} failed ({type(e).__name__}: {e})\n{traceback.format_exc()}\nUsing procedural fallback.")
            return await self.fallback.generate_video(
                prompt=prompt,
                duration=duration,
                aspect_ratio=aspect_ratio,
                output_path=output_path,
                style=style,
                scene_number=scene_number,
                total_scenes=total_scenes,
                subtitle=subtitle
            )
        finally:
            if os.path.exists(temp_img):
                try:
                    os.remove(temp_img)
                except Exception:
                    pass
