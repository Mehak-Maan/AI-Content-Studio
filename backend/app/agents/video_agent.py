import os
from typing import Dict, Any, List
from ..tools.video import get_video_provider
from ..services.storage_service import storage_service
from ..utils.logger import logger, broadcast_agent_log

class VideoGenerationAgent:
    """
    Video Generation Agent converts scene prompts into video clips using configured providers.
    """
    def __init__(self):
        self.video_provider = get_video_provider()

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        project_id = state.get("project_id", "")
        scenes = state.get("scenes", [])
        plan = state.get("production_plan", {})
        aspect_ratio = plan.get("aspect_ratio", "9:16")
        target_scene_number = state.get("target_scene_number") # For single-scene regeneration
        
        broadcast_agent_log("Video Generation Agent", f"Starting video clip generation for {len(scenes)} scenes...", "INFO", project_id)
        logger.info(f"[Video Agent] Generating video clips for project {project_id}")

        generated_videos: List[str] = list(state.get("generated_videos", []))
        # Ensure list is sized appropriately
        while len(generated_videos) < len(scenes):
            generated_videos.append("")

        for idx, scene in enumerate(scenes):
            scene_num = scene.get("scene_number", idx + 1)
            
            # If regenerating a single scene, skip others that already exist
            if target_scene_number is not None and scene_num != target_scene_number:
                continue

            prompt = scene.get("video_prompt") or scene.get("visual_prompt", "")
            duration = float(scene.get("duration", 5.0))
            style = scene.get("style", "cinematic")
            out_path = storage_service.get_scene_video_path(project_id, scene_num)

            # Reuse cached scene video if already generated and non-empty (saves API credits & time)
            if target_scene_number is None and os.path.exists(out_path) and os.path.getsize(out_path) > 10000:
                logger.info(f"[Video Agent] Reusing cached scene video for Scene {scene_num}: {out_path} ({os.path.getsize(out_path)} bytes)")
                broadcast_agent_log(
                    "Video Generation Agent", 
                    f"✓ Scene {scene_num} already exists on disk. Reusing clip.", 
                    "INFO", 
                    project_id
                )
                generated_videos[idx] = out_path
                continue

            broadcast_agent_log(
                "Video Generation Agent", 
                f"Generating scene {scene_num}/{len(scenes)} ({duration}s)...", 
                "INFO", 
                project_id
            )

            try:
                clip_path = await self.video_provider.generate_video(
                    prompt=prompt,
                    duration=duration,
                    aspect_ratio=aspect_ratio,
                    output_path=out_path,
                    style=style,
                    scene_number=scene_num,
                    total_scenes=len(scenes),
                    subtitle=scene.get("narration", scene.get("script_excerpt", "")),
                )
                generated_videos[idx] = clip_path
                broadcast_agent_log(
                    "Video Generation Agent", 
                    f"✓ Scene {scene_num} completed", 
                    "INFO", 
                    project_id
                )
            except Exception as e:
                logger.error(f"[Video Agent] Scene {scene_num} generation failed: {e}. Attempting fallback...")
                broadcast_agent_log(
                    "Video Generation Agent", 
                    f"⚠ Scene {scene_num} provider issue ({str(e)[:50]}), falling back...", 
                    "WARNING", 
                    project_id
                )
                try:
                    from ..tools.video.procedural_provider import ProceduralMotionVideoProvider
                    fallback_prov = ProceduralMotionVideoProvider()
                    clip_path = await fallback_prov.generate_video(
                        prompt=prompt,
                        duration=duration,
                        aspect_ratio=aspect_ratio,
                        output_path=out_path,
                        style=style,
                        scene_number=scene_num,
                        total_scenes=len(scenes),
                        subtitle=scene.get("narration", scene.get("script_excerpt", "")),
                    )
                    generated_videos[idx] = clip_path
                    broadcast_agent_log(
                        "Video Generation Agent", 
                        f"✓ Scene {scene_num} completed (via fallback)", 
                        "INFO", 
                        project_id
                    )
                except Exception as inner_e:
                    logger.error(f"[Video Agent] Scene {scene_num} fallback failed: {inner_e}")
                    raise inner_e

        # Filter non-empty paths
        valid_clips = [v for v in generated_videos if v and os.path.exists(v)]
        broadcast_agent_log("Video Generation Agent", f"All {len(valid_clips)} video scenes generated successfully.", "INFO", project_id)

        return {
            "generated_videos": valid_clips,
            "current_agent": "Video Generation Agent",
            "agent_status": {"video": "completed"}
        }
