import os
import asyncio
import math
import textwrap
import functools
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
from typing import Tuple, List
from ...utils.logger import logger
from .base import VideoProvider


# ─────────────────────────────────────────────────────
#  5 CINEMATIC COLOUR THEMES
# ─────────────────────────────────────────────────────
THEMES = [
    {   # Scene 1 – Deep Space / Neural Blue
        "name": "neural_blue",
        "bg": (5, 10, 25),    "accent": (0, 180, 255),  "sec": (80, 60, 220),
        "text": (200, 230, 255), "highlight": (255, 255, 255),
        "grid": (20, 35, 70),
    },
    {   # Scene 2 – Cyberpunk Emerald
        "name": "cyberpunk_green",
        "bg": (5, 18, 14),    "accent": (0, 255, 140),  "sec": (200, 255, 0),
        "text": (180, 255, 210), "highlight": (255, 255, 255),
        "grid": (10, 40, 25),
    },
    {   # Scene 3 – Royal Amethyst
        "name": "amethyst",
        "bg": (18, 8, 30),    "accent": (200, 60, 255), "sec": (100, 80, 255),
        "text": (240, 210, 255), "highlight": (255, 255, 255),
        "grid": (35, 15, 55),
    },
    {   # Scene 4 – Solar Gold / Dark
        "name": "solar_gold",
        "bg": (14, 10, 4),    "accent": (255, 180, 0),  "sec": (255, 100, 30),
        "text": (255, 240, 200), "highlight": (255, 255, 255),
        "grid": (40, 28, 8),
    },
    {   # Scene 5 – Arctic Teal
        "name": "arctic_teal",
        "bg": (6, 18, 24),    "accent": (0, 230, 210),  "sec": (60, 160, 255),
        "text": (200, 245, 255), "highlight": (255, 255, 255),
        "grid": (12, 36, 44),
    },
]


def _clamp(v): return max(0, min(255, int(v)))
def _ease(t): return t * t * (3.0 - 2.0 * t)


# ─────────────────────────────────────────────────────
#  FONT HELPERS
# ─────────────────────────────────────────────────────
@functools.lru_cache(maxsize=32)
def _load_font(size: int, bold: bool = False):
    """LRU-cached: fonts are loaded from disk once per process, not per frame."""
    candidates_bold = [
        "C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    candidates_regular = [
        "C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in (candidates_bold if bold else candidates_regular):
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


# ─────────────────────────────────────────────────────
#  FRAME DRAWING HELPERS (operate on RGB numpy arrays)
# ─────────────────────────────────────────────────────

def _draw_gradient_bg(img, theme, t, w, h):
    cx = w // 2 + int(math.sin(t * 0.4) * w * 0.08)
    cy = h // 2 + int(math.cos(t * 0.3) * h * 0.06)
    y_idx, x_idx = np.ogrid[:h, :w]
    dist = np.sqrt((x_idx - cx) ** 2 + (y_idx - cy) ** 2).astype(np.float32)
    glow = np.clip(1.0 - dist / (math.sqrt(w**2 + h**2) * 0.6), 0, 1) ** 1.4
    for c in range(3):
        blend = theme["bg"][c] + glow * (theme["sec"][c] - theme["bg"][c]) * 0.55
        img[:, :, c] = np.clip(blend, 0, 255).astype(np.uint8)


def _draw_grid(img, theme, t, w, h, spacing=55):
    gc = theme["grid"]
    off = int((t * 25) % spacing)
    for gy in range(off - spacing, h + spacing, spacing):
        cv2.line(img, (0, gy), (w, gy), gc, 1)
    for gx in range(0, w + spacing, spacing):
        cv2.line(img, (gx, 0), (gx, h), gc, 1)


def _draw_particles(img, theme, t, w, h, seed):
    """Vectorised particle network — O(n²) distance computed via numpy broadcasting."""
    rng = np.random.RandomState(seed)
    n = 32
    px = rng.uniform(0.08 * w, 0.92 * w, n)
    py = rng.uniform(0.08 * h, 0.92 * h, n)
    vx = rng.uniform(-1.0, 1.0, n)
    vy = rng.uniform(-1.0, 1.0, n)
    radii = rng.uniform(3, 9, n)
    cx = (px + vx * t * 28) % (0.84 * w) + 0.08 * w
    cy = (py + vy * t * 28) % (0.84 * h) + 0.08 * h

    # Vectorised pairwise distances via broadcasting
    dx = cx[:, None] - cx[None, :]          # (n, n)
    dy = cy[:, None] - cy[None, :]
    dists = np.sqrt(dx * dx + dy * dy)      # (n, n)

    # Upper triangle only, where distance < 160
    mask = np.triu(dists < 160, k=1)
    ii, jj = np.where(mask)
    for k in range(len(ii)):
        i, j = int(ii[k]), int(jj[k])
        d = dists[i, j]
        a = (1.0 - d / 160.0) * 0.7
        lc = tuple(_clamp(theme["sec"][c] * a) for c in range(3))
        cv2.line(img, (int(cx[i]), int(cy[i])), (int(cx[j]), int(cy[j])), lc, 1)

    # Nodes
    for i in range(n):
        r = int(radii[i] + math.sin(t * 2.8 + i) * 2)
        pt = (int(cx[i]), int(cy[i]))
        glow_c = tuple(_clamp(theme["accent"][c] * 0.35) for c in range(3))
        cv2.circle(img, pt, r + 5, glow_c, 1)
        cv2.circle(img, pt, r, theme["accent"], -1)
        cv2.circle(img, pt, max(1, r // 2), theme["highlight"], -1)


def _draw_wave_bars(img, theme, t, w, h):
    num = 28
    bw = w // (num + 4)
    max_bh = int(h * 0.18)
    base_y = int(h * 0.92)
    for i in range(num):
        phase = t * 3.5 + i * 0.45
        bh = int(max_bh * (0.35 + 0.65 * (0.5 + 0.5 * math.sin(phase))))
        bx = (w - num * (bw + 3)) // 2 + i * (bw + 3)
        a = 0.5 + 0.5 * math.sin(phase * 0.7)
        color = tuple(_clamp(theme["accent"][c] * a) for c in range(3))
        cv2.rectangle(img, (bx, base_y - bh), (bx + bw, base_y), color, -1)


def _draw_hud_corners(img, theme, w, h):
    s = min(w, h) // 12
    c = theme["accent"]
    pad = 18
    for (ox, oy, sx, sy) in [
        (pad, pad, 1, 1), (w - pad, pad, -1, 1),
        (pad, h - pad, 1, -1), (w - pad, h - pad, -1, -1),
    ]:
        cv2.line(img, (ox, oy), (ox + sx * s, oy), c, 2)
        cv2.line(img, (ox, oy), (ox, oy + sy * s), c, 2)


def _draw_scan_line(img, theme, t, w, h):
    y = int((t * 0.5 % 1.0) * h)
    overlay = img.copy()
    cv2.line(overlay, (0, y), (w, y), theme["accent"], 2)
    cv2.addWeighted(overlay, 0.25, img, 0.75, 0, img)


def _draw_center_ring(img, theme, t, w, h):
    r = int(min(w, h) * 0.10 + math.sin(t * 2.2) * 8)
    cx, cy = w // 2, h // 2
    cv2.circle(img, (cx, cy), r + 14,
               tuple(_clamp(theme["sec"][c] * 0.45) for c in range(3)), 2)
    cv2.circle(img, (cx, cy), r, theme["accent"], 2)


# ─────────────────────────────────────────────────────
#  PIL TEXT OVERLAY
# ─────────────────────────────────────────────────────

def _extract_title(prompt: str) -> str:
    prompt = prompt.strip()
    for sep in [".", "!", "?", ",", " - ", "–", ":"]:
        if sep in prompt:
            part = prompt.split(sep)[0].strip()
            if 3 < len(part) < 60:
                return part
    words = prompt.split()
    return " ".join(words[:7]) if len(words) > 7 else prompt


def _overlay_text(frame_bgr, title, subtitle, scene_num, total_scenes,
                  theme, progress, w, h):
    img_pil = Image.fromarray(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)

    title_sz = max(26, w // 18)
    sub_sz = max(16, w // 30)
    tag_sz = max(12, w // 48)
    f_title = _load_font(title_sz, bold=True)
    f_sub = _load_font(sub_sz)
    f_tag = _load_font(tag_sz)

    # Fade alpha
    if progress < 0.12:
        alpha = _ease(progress / 0.12)
    elif progress > 0.80:
        alpha = _ease((1.0 - progress) / 0.20)
    else:
        alpha = 1.0

    # Semi-transparent lower bar
    bar_h = int(h * 0.30)
    bar_top = h - bar_h - int(h * 0.04)
    overlay = img_pil.copy()
    ImageDraw.Draw(overlay).rectangle(
        [(0, bar_top), (w, h)], fill=theme["bg"])
    img_pil = Image.blend(img_pil, overlay, 0.58)
    draw = ImageDraw.Draw(img_pil)

    # Title lines
    lines = textwrap.wrap(title, width=max(16, w // title_sz + 2))
    y = bar_top + int(h * 0.025)
    acc = theme["accent"]
    for line in lines[:3]:
        bb = draw.textbbox((0, 0), line, font=f_title)
        lw = bb[2] - bb[0]
        lx = (w - lw) // 2
        draw.text((lx + 2, y + 2), line, font=f_title, fill=(0, 0, 0))
        draw.text((lx, y), line, font=f_title,
                  fill=(_clamp(acc[0] * 0.9 + 26), _clamp(acc[1] * 0.9 + 26), _clamp(acc[2] * 0.9 + 26)))
        y += (bb[3] - bb[1]) + int(h * 0.008)

    # Subtitle lines
    sub_lines = textwrap.wrap(subtitle[:120], width=max(22, w // sub_sz + 4))
    for line in sub_lines[:3]:
        bb = draw.textbbox((0, 0), line, font=f_sub)
        lw = bb[2] - bb[0]
        lx = (w - lw) // 2
        draw.text((lx + 1, y + 1), line, font=f_sub, fill=(0, 0, 0))
        draw.text((lx, y), line, font=f_sub, fill=theme["text"])
        y += (bb[3] - bb[1]) + int(h * 0.005)

    # Scene tag
    tag = f"SCENE {scene_num} / {total_scenes}"
    draw.text((26, 26), tag, font=f_tag, fill=acc)

    # Progress bar (bottom 5px)
    bar_y = h - 5
    draw.rectangle([(0, bar_y), (w, h)],
                   fill=(_clamp(theme["bg"][0] + 20),
                         _clamp(theme["bg"][1] + 20),
                         _clamp(theme["bg"][2] + 20)))
    draw.rectangle([(0, bar_y), (int(w * progress), h)], fill=acc)

    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)


# ─────────────────────────────────────────────────────
#  MAIN PROVIDER CLASS
# ─────────────────────────────────────────────────────

class ProceduralMotionVideoProvider(VideoProvider):
    """
    Production-quality cinematic video generator.
    Each scene gets a unique theme, animated background, particle network,
    wave bars, HUD overlays, and scene-aware text rendered via Pillow.
    """

    def _get_dimensions(self, aspect_ratio: str) -> Tuple[int, int]:
        if aspect_ratio == "9:16":
            return (720, 1280)
        elif aspect_ratio == "1:1":
            return (720, 720)
        else:
            return (1280, 720)

    async def generate_video(
        self,
        prompt: str,
        duration: float,
        aspect_ratio: str,
        output_path: str,
        style: str = "cinematic",
        scene_number: int = 1,
        total_scenes: int = 5,
        subtitle: str = "",
    ) -> str:
        w, h = self._get_dimensions(aspect_ratio)
        fps = 30
        total_frames = max(30, int(duration * fps))
        theme = THEMES[(scene_number - 1) % len(THEMES)]

        logger.info(
            f"[ProceduralVideo] Generating {duration:.1f}s clip "
            f"({w}×{h}, {total_frames} frames) scene {scene_number} "
            f"[{theme['name']}]..."
        )

        scene_title = _extract_title(prompt)
        scene_sub = subtitle if subtitle else prompt[:120]

        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        temp_out = output_path.replace(".mp4", "_temp.mp4")
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(temp_out, fourcc, fps, (w, h))

        for fi in range(total_frames):
            t = fi / fps
            progress = fi / total_frames

            img = np.zeros((h, w, 3), dtype=np.uint8)
            _draw_gradient_bg(img, theme, t, w, h)
            _draw_grid(img, theme, t, w, h)
            _draw_particles(img, theme, t, w, h, seed=scene_number * 13)
            _draw_wave_bars(img, theme, t, w, h)
            _draw_hud_corners(img, theme, w, h)
            _draw_scan_line(img, theme, t, w, h)
            _draw_center_ring(img, theme, t, w, h)

            frame_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            frame_bgr = _overlay_text(
                frame_bgr, scene_title, scene_sub,
                scene_number, total_scenes, theme, progress, w, h
            )
            writer.write(frame_bgr)

        writer.release()

        # Re-encode to H.264 / YUV420P – higher quality CRF 18
        os.system(
            f'ffmpeg -y -i "{temp_out}" '
            f'-c:v libx264 -pix_fmt yuv420p -preset fast -crf 18 '
            f'"{output_path}" >nul 2>&1'
        )
        if os.path.exists(temp_out):
            try:
                os.remove(temp_out)
            except Exception:
                pass

        # Thumbnail
        thumb_dir = os.path.join(os.path.dirname(output_path), "..", "thumbnails")
        os.makedirs(thumb_dir, exist_ok=True)
        thumb_path = os.path.join(thumb_dir, f"scene_{scene_number:02d}.jpg")
        if os.path.exists(output_path):
            os.system(
                f'ffmpeg -y -ss 00:00:01 -i "{output_path}" '
                f'-vframes 1 -q:v 2 "{thumb_path}" >nul 2>&1'
            )

        logger.info(f"[ProceduralVideo] Completed: {output_path}")
        return output_path
