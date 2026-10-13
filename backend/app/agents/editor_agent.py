from typing import Dict, Any
from ..tools.media import FFmpegEditorTool
from ..services.storage_service import storage_service
from ..utils.logger import logger, broadcast_agent_log

class EditorAgent:
    """
    Editor Agent uses FFmpeg to concatenate scenes, balance and mix audio tracks,
    burn subtitles, and render the final MP4 video.
    """
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        project_id = state.get("project_id", "")
        plan = state.get("production_plan", {})
        aspect_ratio = plan.get("aspect_ratio", "9:16")
        captions_required = plan.get("captions_required", True)

        scene_videos = state.get("generated_videos", [])
        voice_file = state.get("voice_file")
        music_file = state.get("music_file")
        subtitle_file = state.get("subtitle_file")

        broadcast_agent_log("Editor Agent", "Stitching scene clips, balancing audio, and rendering final MP4...", "INFO", project_id)
        logger.info(f"[Editor Agent] Rendering project {project_id} ({len(scene_videos)} scenes)")

        if not scene_videos:
            raise ValueError("Cannot render video: No scene clips provided.")

        out_path = storage_service.get_final_video_path(project_id)
        poster_path = storage_service.get_project_thumb_path(project_id)

        try:
            final_path = FFmpegEditorTool.build_final_video(
                scene_paths=scene_videos,
                voice_path=voice_file,
                music_path=music_file,
                subtitle_path=subtitle_file,
                output_path=out_path,
                aspect_ratio=aspect_ratio,
                captions_enabled=captions_required
            )

            broadcast_agent_log("Editor Agent", f"Final video rendered successfully: {final_path}", "INFO", project_id)

            return {
                "final_video": final_path,
                "thumbnail_path": poster_path,
                "current_agent": "Editor Agent",
                "agent_status": {"editor": "completed"}
            }
        except Exception as e:
            logger.error(f"[Editor Agent] FFmpeg rendering error: {e}")
            broadcast_agent_log("Editor Agent", f"Video rendering error: {str(e)}", "ERROR", project_id)
            raise e
