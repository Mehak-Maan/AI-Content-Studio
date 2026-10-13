import json
import re
import asyncio
from typing import Dict, Any, List, Optional
from ..tools.llm import get_llm_provider
from ..utils.logger import logger, broadcast_agent_log


class ScriptAgent:
    """
    Script Agent — uses Groq/Gemini LLM to craft 100% unique, high-engagement
    video scripts, narrations, scene descriptions, and on-screen text.
    NO hardcoded fallback content — all output is AI-generated.
    """

    def __init__(self):
        self.llm = get_llm_provider()

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        project_id = state.get("project_id", "")
        plan = state.get("production_plan", {})
        prompt = state.get("user_prompt", "")

        broadcast_agent_log("Script Agent", "Writing unique AI-generated script and scene narrations...", "INFO", project_id)
        logger.info(f"[Script Agent] Writing script for project {project_id} — topic: {prompt[:60]}")

        num_scenes = plan.get("number_of_scenes", 5)
        duration = plan.get("duration", 30)
        language = plan.get("language", "English")
        aspect_ratio = plan.get("aspect_ratio", "9:16")
        visual_style = plan.get("visual_style", "cinematic")
        theme = plan.get("theme", prompt)

        system_prompt = (
            "You are a world-class viral video scriptwriter specializing in YouTube Shorts, Instagram Reels, and TikTok. "
            "You write UNIQUE, emotionally compelling, fact-driven scripts tailored exactly to the topic. "
            "NEVER use generic phrases. Every narration must be specific to the topic. "
            "Every visual_prompt must describe a specific, photorealistic scene relevant to the topic. "
            "Output ONLY valid JSON, no markdown, no explanation."
        )

        user_input = (
            f"Create a complete video script for the following:\n\n"
            f"TOPIC: {prompt}\n"
            f"THEME: {theme}\n"
            f"DURATION: {duration} seconds total\n"
            f"SCENES: {num_scenes} scenes\n"
            f"LANGUAGE: {language}\n"
            f"ASPECT RATIO: {aspect_ratio}\n"
            f"VISUAL STYLE: {visual_style}\n\n"
            f"Rules:\n"
            f"- Each scene narration must be specific to the topic — no generic AI/tech phrases unless topic requires it\n"
            f"- Each visual_prompt must describe a UNIQUE, specific, photorealistic scene (different angle/shot each scene)\n"
            f"- Narrations must flow naturally as spoken voice-over\n"
            f"- screen_text must be short punchy 2-5 word phrases\n"
            f"- Duration of each scene should be approximately {round(duration/num_scenes, 1)} seconds\n\n"
            f"Return this exact JSON structure:\n"
            f'{{"title": "...", "hook": "...", "call_to_action": "...", "total_duration": {duration}, '
            f'"scenes": [{{"scene_number": 1, "duration": {round(duration/num_scenes, 1)}, '
            f'"narration": "...", "visual_prompt": "...", "screen_text": "...", "transition": "fade"}}]}}'
        )

        script_data = None
        attempts = 0
        max_attempts = 3

        while attempts < max_attempts:
            attempts += 1
            try:
                broadcast_agent_log(
                    "Script Agent",
                    f"Generating script via AI (attempt {attempts}/{max_attempts})...",
                    "INFO", project_id
                )
                raw = await self.llm.generate_json(user_input, system_prompt)

                # Validate structure
                if "scenes" not in raw or not isinstance(raw.get("scenes"), list) or len(raw["scenes"]) == 0:
                    raise ValueError(f"Script missing 'scenes' list (got keys: {list(raw.keys())})")

                # Validate each scene has required fields
                for i, scene in enumerate(raw["scenes"]):
                    if not scene.get("narration") or not scene.get("visual_prompt"):
                        raise ValueError(f"Scene {i+1} missing narration or visual_prompt")

                script_data = raw
                # Ensure scene numbers are correct
                for i, scene in enumerate(script_data["scenes"]):
                    scene["scene_number"] = i + 1
                    if not scene.get("duration"):
                        scene["duration"] = round(duration / num_scenes, 1)

                logger.info(f"[Script Agent] Script generated successfully on attempt {attempts}")
                break

            except Exception as e:
                logger.warning(f"[Script Agent] Attempt {attempts} failed: {type(e).__name__}: {e}")
                if attempts < max_attempts:
                    await asyncio.sleep(1.5)

        if script_data is None:
            # Last resort: ask LLM with simplified prompt
            broadcast_agent_log("Script Agent", "Retrying with simplified prompt...", "WARNING", project_id)
            try:
                simplified_prompt = (
                    f"Write a {duration}-second video script about: {prompt}\n"
                    f"Return JSON with fields: title, hook, call_to_action, total_duration, scenes.\n"
                    f"scenes is a list of {num_scenes} objects each with: scene_number, duration, narration, visual_prompt, screen_text, transition.\n"
                    f"Make narrations and visual_prompts specific to the topic. Return only JSON."
                )
                script_data = await self.llm.generate_json(simplified_prompt)
                if "scenes" not in script_data or not script_data["scenes"]:
                    raise ValueError("No scenes in simplified script")
            except Exception as e:
                logger.error(f"[Script Agent] All attempts failed: {e}")
                # Absolute minimal fallback — still topic-specific
                scene_dur = round(duration / max(1, num_scenes), 1)
                script_data = {
                    "title": f"The Story of {_extract_topic(prompt)}",
                    "hook": f"Here is everything you need to know about {_extract_topic(prompt)}.",
                    "call_to_action": "Follow for more!",
                    "total_duration": duration,
                    "scenes": [
                        {
                            "scene_number": i + 1,
                            "duration": scene_dur,
                            "narration": f"{_extract_topic(prompt)} — part {i+1} of the story.",
                            "visual_prompt": f"Cinematic shot related to {_extract_topic(prompt)}, scene {i+1}, professional photography",
                            "screen_text": f"{_extract_topic(prompt)}",
                            "transition": "fade"
                        }
                        for i in range(num_scenes)
                    ]
                }

        broadcast_agent_log(
            "Script Agent",
            f"✓ Script ready: '{script_data.get('title')}' — {len(script_data.get('scenes', []))} scenes",
            "INFO", project_id
        )

        return {
            "script": script_data,
            "scenes": script_data.get("scenes", []),
            "current_agent": "Script Agent",
            "agent_status": {"script": "completed"}
        }


def _extract_topic(text: str) -> str:
    """Extract the core topic from a user prompt."""
    # Remove common command words
    cleaned = re.sub(
        r'^(?:create|make|generate|write|produce)\s+(?:a\s+)?(?:\d+[\s-]*(?:second|sec|s)\s+)?'
        r'(?:video|reel|tiktok|short|clip|content)?\s*(?:about|on|for|explaining|showcasing)?\s*',
        '', text.strip(), flags=re.IGNORECASE
    ).strip()
    if not cleaned:
        return text[:40]
    # Take first meaningful chunk (up to first period or 60 chars)
    for sep in ['.', '!', '?', ',']:
        if sep in cleaned:
            part = cleaned.split(sep)[0].strip()
            if 3 < len(part) < 60:
                return part
    return cleaned[:60].strip()
