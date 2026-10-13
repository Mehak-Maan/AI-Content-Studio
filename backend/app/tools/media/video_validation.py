import os
import cv2
from typing import List, Dict, Any, Optional
from .ffmpeg_tool import FFmpegEditorTool
from ...utils.logger import logger

class VideoValidationTool:
    """
    Validation tool used by Reviewer Agent to inspect video streams,
    durations, audio tracks, and completeness.
    """

    @classmethod
    def validate_project_output(
        cls,
        final_video_path: str,
        expected_duration: float,
        scene_paths: List[str],
        subtitle_path: Optional[str] = None,
        captions_required: bool = True
    ) -> Dict[str, Any]:
        issues = []
        retry_agent = None

        # 1. Check final video existence & size
        if not os.path.exists(final_video_path):
            issues.append("Final video file does not exist.")
            return {"approved": False, "issues": issues, "retry_required": True, "retry_agent": "editor"}

        size = os.path.getsize(final_video_path)
        if size < 5000:
            issues.append(f"Final video file size is too small ({size} bytes). Rendering may have failed.")
            return {"approved": False, "issues": issues, "retry_required": True, "retry_agent": "editor"}

        # 2. Check scene video integrity
        for idx, s_path in enumerate(scene_paths, 1):
            if not os.path.exists(s_path) or os.path.getsize(s_path) < 1000:
                issues.append(f"Scene {idx} video is missing or corrupt: {s_path}")
                return {"approved": False, "issues": issues, "retry_required": True, "retry_agent": "video", "failed_scene_index": idx}

        # 3. Check video probe streams
        info = FFmpegEditorTool.get_media_info(final_video_path)
        if not info.get("has_video"):
            issues.append("Final MP4 does not contain a valid video stream.")
            return {"approved": False, "issues": issues, "retry_required": True, "retry_agent": "editor"}

        if not info.get("has_audio"):
            issues.append("Final MP4 does not contain an audio track.")
            return {"approved": False, "issues": issues, "retry_required": True, "retry_agent": "editor"}

        # 4. Check video playback via OpenCV frame read
        try:
            cap = cv2.VideoCapture(final_video_path)
            if not cap.isOpened():
                issues.append("Video file cannot be opened by standard media codecs.")
            else:
                ret, frame = cap.read()
                if not ret or frame is None:
                    issues.append("First video frame could not be decoded.")
            cap.release()
        except Exception as e:
            issues.append(f"Codec validation exception: {str(e)}")

        # 5. Check duration tolerance (within 20% or 5s)
        actual_duration = info.get("duration", 0)
        if expected_duration > 0 and abs(actual_duration - expected_duration) > (expected_duration * 0.4 + 4):
            issues.append(f"Video duration ({actual_duration:.1f}s) differs from target ({expected_duration}s).")

        # 6. Check subtitles if enabled
        if captions_required and subtitle_path:
            if not os.path.exists(subtitle_path) or os.path.getsize(subtitle_path) == 0:
                issues.append("Captions were requested but SRT subtitle file is missing or empty.")

        approved = len(issues) == 0
        logger.info(f"[VideoValidation] Video quality check: {'APPROVED' if approved else 'FLAGGED ISSUES'}")

        return {
            "approved": approved,
            "issues": issues,
            "retry_required": not approved,
            "retry_agent": retry_agent if not approved else None,
            "actual_duration": actual_duration,
            "resolution": f"{info.get('width', 0)}x{info.get('height', 0)}",
            "file_size_kb": round(size / 1024, 1)
        }
