import asyncio
from typing import Dict, Any
from ..tools.llm import get_llm_provider
from ..utils.logger import logger, broadcast_agent_log


class ManagerAgent:
    """
    Manager Agent — uses Groq/Gemini to create a fully unique, topic-aware
    production plan for each video. No hardcoded templates.
    """

    def __init__(self):
        self.llm = get_llm_provider()

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        project_id = state.get("project_id", "")
        prompt = state.get("user_prompt", "")
        settings_data = state.get("settings", {})

        req_duration = int(settings_data.get("duration", 30))
        req_aspect = settings_data.get("aspect_ratio", "9:16")
        req_type = settings_data.get("video_type", "instagram_reel")
        req_lang = settings_data.get("language", "English")
        music_pref = settings_data.get("music_preference", "Cinematic")
        voice_pref = settings_data.get("voice_preference", "Professional")
        visual_style = settings_data.get("visual_style", "modern cinematic")

        broadcast_agent_log("Manager Agent", "Analyzing prompt and creating production plan...", "INFO", project_id)
        logger.info(f"[Manager Agent] Planning project {project_id}: '{prompt[:60]}'")

        system_prompt = (
            "You are an expert AI Video Director and Executive Producer. "
            "Analyze the video request and create a precise, topic-specific production plan in JSON. "
            "The plan must be specific to the topic — avoid generic templates. "
            "Output ONLY valid JSON, no markdown."
        )

        user_input = (
            f"Create a production plan for this video:\n\n"
            f"USER REQUEST: {prompt}\n"
            f"TYPE: {req_type}\n"
            f"DURATION: {req_duration} seconds\n"
            f"ASPECT RATIO: {req_aspect}\n"
            f"LANGUAGE: {req_lang}\n"
            f"VOICE STYLE: {voice_pref}\n"
            f"VISUAL STYLE: {visual_style}\n"
            f"MUSIC MOOD: {music_pref}\n"
            f"CAPTIONS: {settings_data.get('captions_enabled', True)}\n\n"
            f"Return this JSON:\n"
            f'{{"title": "catchy title", "theme": "core topic in 3-5 words", '
            f'"video_type": "{req_type}", "duration": {req_duration}, "aspect_ratio": "{req_aspect}", '
            f'"language": "{req_lang}", "number_of_scenes": <int>, '
            f'"voice_required": true, "music_required": true, "captions_required": true, '
            f'"visual_style": "...", "music_preference": "{music_pref}"}}'
        )

        plan = None
        for attempt in range(1, 3):
            try:
                plan = await self.llm.generate_json(user_input, system_prompt)
                if plan.get("title"):
                    break
            except Exception as e:
                logger.warning(f"[Manager Agent] Attempt {attempt} failed: {e}")
                await asyncio.sleep(1)

        if not plan or not plan.get("title"):
            # Minimal topic-aware fallback
            logger.warning("[Manager Agent] LLM plan failed, using topic-aware fallback")
            plan = {
                "title": f"The World of {prompt[:30]}",
                "theme": prompt[:40],
                "video_type": req_type,
                "visual_style": visual_style,
                "music_preference": music_pref,
            }

        # Always enforce user settings
        plan["duration"] = req_duration
        plan["aspect_ratio"] = req_aspect
        plan["language"] = req_lang
        plan["voice_required"] = True
        plan["music_required"] = True
        plan["captions_required"] = settings_data.get("captions_enabled", True)
        if not plan.get("number_of_scenes") or plan["number_of_scenes"] < 2:
            plan["number_of_scenes"] = max(3, int(req_duration / 6))

        broadcast_agent_log(
            "Manager Agent",
            f"✓ Plan ready: '{plan.get('title')}' — {plan['number_of_scenes']} scenes, {req_duration}s, {req_aspect}",
            "INFO", project_id
        )

        return {
            "production_plan": plan,
            "current_agent": "Manager Agent",
            "agent_status": {"manager": "completed"}
        }
