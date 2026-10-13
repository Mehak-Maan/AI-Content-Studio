from typing import Dict, Any
from ..tools.media import VideoValidationTool
from ..utils.logger import logger, broadcast_agent_log

class ReviewerAgent:
    """
    Reviewer Agent inspects the generated final video, validates media streams,
    durations, audio levels, scene counts, and triggers conditional retries if needed.
    """
    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        project_id = state.get("project_id", "")
        plan = state.get("production_plan", {})
        expected_duration = float(plan.get("duration", 30))
        captions_required = plan.get("captions_required", True)

        final_video = state.get("final_video", "")
        scene_videos = state.get("generated_videos", [])
        subtitle_file = state.get("subtitle_file")
        retry_count = state.get("retry_count", 0)
        max_retries = state.get("max_retries", 2)

        broadcast_agent_log("Reviewer Agent", "Conducting quality assurance and media stream validation...", "INFO", project_id)
        logger.info(f"[Reviewer Agent] Validating final video for project {project_id}")

        validation = VideoValidationTool.validate_project_output(
            final_video_path=final_video,
            expected_duration=expected_duration,
            scene_paths=scene_videos,
            subtitle_path=subtitle_file,
            captions_required=captions_required
        )

        approved = validation.get("approved", False)
        issues = validation.get("issues", [])

        if approved:
            broadcast_agent_log(
                "Reviewer Agent", 
                f"✓ Quality QA Passed! Video approved ({validation.get('actual_duration', 0):.1f}s, {validation.get('resolution')}, {validation.get('file_size_kb')} KB)", 
                "INFO", 
                project_id
            )
            return {
                "review_result": validation,
                "retry_required": False,
                "current_agent": "Reviewer Agent",
                "agent_status": {"reviewer": "approved"}
            }
        else:
            can_retry = retry_count < max_retries
            broadcast_agent_log(
                "Reviewer Agent", 
                f"⚠ Quality QA flagged {len(issues)} issue(s): {', '.join(issues)}. Retry attempt: {retry_count + 1}/{max_retries}", 
                "WARNING", 
                project_id
            )
            return {
                "review_result": validation,
                "retry_required": can_retry,
                "retry_count": retry_count + 1,
                "retry_agent": validation.get("retry_agent", "editor"),
                "current_agent": "Reviewer Agent",
                "agent_status": {"reviewer": "retrying" if can_retry else "failed"}
            }
