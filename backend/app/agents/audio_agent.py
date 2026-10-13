from typing import Dict, Any
from ..tools.audio import get_audio_provider
from ..services.storage_service import storage_service
from ..utils.logger import logger, broadcast_agent_log

class AudioAgent:
    """
    Audio Agent generates atmospheric background music, controls volume balancing,
    and applies smooth dynamic fades.
    """
    def __init__(self):
        self.audio_provider = get_audio_provider()

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        project_id = state.get("project_id", "")
        plan = state.get("production_plan", {})
        music_pref = plan.get("music_preference") or state.get("settings", {}).get("music_preference", "Cinematic")
        
        if music_pref.lower() == "none" or not plan.get("music_required", True):
            broadcast_agent_log("Audio Agent", "Background music disabled.", "INFO", project_id)
            return {"music_file": None, "current_agent": "Audio Agent", "agent_status": {"audio": "skipped"}}

        broadcast_agent_log("Audio Agent", f"Generating {music_pref} background music track...", "INFO", project_id)
        logger.info(f"[Audio Agent] Generating music for project {project_id}")

        duration = float(plan.get("duration", 30))
        out_path = storage_service.get_music_path(project_id)

        try:
            music_path = await self.audio_provider.generate_music(
                style=music_pref,
                duration=duration + 2.0,  # extra margin for smooth tail fade
                output_path=out_path
            )

            broadcast_agent_log("Audio Agent", f"Background music track ready ({music_pref})", "INFO", project_id)

            return {
                "music_file": music_path,
                "current_agent": "Audio Agent",
                "agent_status": {"audio": "completed"}
            }
        except Exception as e:
            logger.error(f"[Audio Agent] Music generation error: {e}")
            broadcast_agent_log("Audio Agent", f"Audio track generation error: {str(e)}", "ERROR", project_id)
            raise e
