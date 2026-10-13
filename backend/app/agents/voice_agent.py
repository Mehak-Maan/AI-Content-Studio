from typing import Dict, Any
from ..tools.voice import get_voice_provider
from ..services.storage_service import storage_service
from ..utils.logger import logger, broadcast_agent_log

class VoiceAgent:
    """
    Voice Agent synthesizes the voiceover narration track from script scenes.
    """
    def __init__(self):
        self.voice_provider = get_voice_provider()

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        project_id = state.get("project_id", "")
        plan = state.get("production_plan", {})
        scenes = state.get("scenes", [])
        
        if not plan.get("voice_required", True):
            broadcast_agent_log("Voice Agent", "Voice narration not required for this project.", "INFO", project_id)
            return {"voice_file": None, "current_agent": "Voice Agent", "agent_status": {"voice": "skipped"}}

        broadcast_agent_log("Voice Agent", "Synthesizing AI voice-over narration...", "INFO", project_id)
        logger.info(f"[Voice Agent] Generating voice for project {project_id}")

        # Combine narrations into cohesive speech with short natural pauses
        full_narration = " ".join([s.get("narration", "").strip() for s in scenes if s.get("narration")])
        if not full_narration:
            full_narration = plan.get("theme", "Welcome to AI Content Studio.")

        language = plan.get("language", "English")
        voice_pref = state.get("settings", {}).get("voice_preference", "Professional")
        out_path = storage_service.get_voice_path(project_id)

        try:
            result = await self.voice_provider.generate_speech(
                text=full_narration,
                output_path=out_path,
                voice=voice_pref,
                language=language
            )
            
            voice_file = result.get("audio_path")
            duration = result.get("duration", 0.0)
            subtitles_text = result.get("subtitles_text", "")

            broadcast_agent_log(
                "Voice Agent", 
                f"Voice-over narration generated successfully ({duration:.1f}s, {result.get('voice_used')})", 
                "INFO", 
                project_id
            )

            return {
                "voice_file": voice_file,
                "voice_duration": duration,
                "word_subtitles": subtitles_text,
                "current_agent": "Voice Agent",
                "agent_status": {"voice": "completed"}
            }
        except Exception as e:
            logger.error(f"[Voice Agent] Voice generation error: {e}")
            broadcast_agent_log("Voice Agent", f"Voice generation error: {str(e)}", "ERROR", project_id)
            raise e
