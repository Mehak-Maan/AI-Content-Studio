from typing import Dict, Any, List
from ..tools.llm import get_llm_provider
from ..utils.logger import logger, broadcast_agent_log

class SceneAgent:
    """
    Scene Agent analyzes each script scene, enriches visual prompts, camera movement,
    lighting, and style tokens optimized for text-to-video generation.
    """
    def __init__(self):
        self.llm = get_llm_provider()

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        project_id = state.get("project_id", "")
        scenes = state.get("scenes", [])
        plan = state.get("production_plan", {})
        visual_style = plan.get("visual_style", "modern cinematic")

        broadcast_agent_log("Scene Agent", f"Optimizing camera angles and visual prompts for {len(scenes)} scenes...", "INFO", project_id)
        logger.info(f"[Scene Agent] Processing {len(scenes)} scenes for project {project_id}")

        enriched_scenes = []
        for scene in scenes:
            scene_num = scene.get("scene_number", len(enriched_scenes) + 1)
            raw_prompt = scene.get("visual_prompt", "")
            duration = scene.get("duration", 5.0)

            # Cinematic camera movements list
            camera_moves = ["slow cinematic push-in", "smooth orbital tracking", "dynamic ascending pan", "macro focus pull", "steady dolly zoom"]
            camera = camera_moves[(scene_num - 1) % len(camera_moves)]

            # Enrich prompt with cinematic keywords
            enriched_prompt = f"{raw_prompt}, {visual_style}, ultra-detailed, volumetric atmospheric lighting, 8k render, masterpiece"
            
            enriched_scene = {
                **scene,
                "scene_number": scene_num,
                "video_prompt": enriched_prompt,
                "camera": camera,
                "style": visual_style,
                "duration": duration,
                "transition": scene.get("transition", "fade")
            }
            enriched_scenes.append(enriched_scene)

        broadcast_agent_log("Scene Agent", f"All {len(enriched_scenes)} scenes optimized for video generation.", "INFO", project_id)

        return {
            "scenes": enriched_scenes,
            "current_agent": "Scene Agent",
            "agent_status": {"scene": "completed"}
        }
