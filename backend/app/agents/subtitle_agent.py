from typing import Dict, Any
from ..tools.subtitles import SubtitleTool
from ..services.storage_service import storage_service
from ..utils.logger import logger, broadcast_agent_log

class SubtitleAgent:
    """
    Subtitle Agent creates synchronized subtitles in SRT format from narration and scene cues.
    """
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        project_id = state.get("project_id", "")
        plan = state.get("production_plan", {})
        scenes = state.get("scenes", [])
        captions_enabled = plan.get("captions_required", True)
        
        if not captions_enabled:
            broadcast_agent_log("Subtitle Agent", "Captions not requested. Skipping subtitle generation.", "INFO", project_id)
            return {"subtitle_file": None, "current_agent": "Subtitle Agent", "agent_status": {"subtitle": "skipped"}}

        broadcast_agent_log("Subtitle Agent", "Generating synchronized SRT subtitle cues...", "INFO", project_id)
        logger.info(f"[Subtitle Agent] Generating subtitles for project {project_id}")

        out_path = storage_service.get_subtitle_path(project_id)
        word_subs = state.get("word_subtitles", "")

        try:
            srt_path = SubtitleTool.generate_srt(
                scenes=scenes,
                output_path=out_path,
                srt_text_override=word_subs
            )

            broadcast_agent_log("Subtitle Agent", "Subtitles generated and synchronized successfully.", "INFO", project_id)

            return {
                "subtitle_file": srt_path,
                "current_agent": "Subtitle Agent",
                "agent_status": {"subtitle": "completed"}
            }
        except Exception as e:
            logger.error(f"[Subtitle Agent] Subtitle generation error: {e}")
            broadcast_agent_log("Subtitle Agent", f"Subtitle generation warning: {str(e)}", "WARNING", project_id)
            return {
                "subtitle_file": None,
                "current_agent": "Subtitle Agent",
                "agent_status": {"subtitle": "warning"}
            }
