import os
import uuid
import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Callable
from sqlalchemy.orm import Session
from ..models.database import Project, Scene, GenerationJob, AgentExecution, GeneratedAsset, SessionLocal
from ..graph.workflow import video_orchestration_graph
from ..services.storage_service import storage_service
from ..tools.video import get_video_provider
from ..agents.editor_agent import EditorAgent
from ..agents.reviewer_agent import ReviewerAgent
from ..utils.logger import logger, broadcast_agent_log

# Event subscriber registry for WebSockets & SSE
_status_listeners: List[Callable[[Dict[str, Any]], None]] = []

def register_status_listener(callback: Callable[[Dict[str, Any]], None]):
    _status_listeners.append(callback)

def unregister_status_listener(callback: Callable[[Dict[str, Any]], None]):
    if callback in _status_listeners:
        _status_listeners.remove(callback)

def broadcast_generation_status(event: Dict[str, Any]):
    for listener in _status_listeners:
        try:
            listener(event)
        except Exception:
            pass

class GenerationService:
    @staticmethod
    def _update_progress(db: Session, project_id: str, agent: str, progress: int, status: str = "running", msg: str = ""):
        project = db.query(Project).filter(Project.id == project_id).first()
        if project:
            project.current_agent = agent
            project.progress = progress
            project.status = status
            db.commit()

        event = {
            "type": "progress",
            "project_id": project_id,
            "agent": agent,
            "progress": progress,
            "status": status,
            "message": msg or f"{agent} is running..."
        }
        broadcast_generation_status(event)

    @classmethod
    async def start_generation(cls, project_id: str):
        """Asynchronously execute full multi-agent video pipeline."""
        db = SessionLocal()
        try:
            project = db.query(Project).filter(Project.id == project_id).first()
            if not project:
                logger.error(f"[GenerationService] Project {project_id} not found.")
                return

            job = GenerationJob(id=str(uuid.uuid4())[:8], project_id=project_id, status="running")
            db.add(job)
            project.status = "running"
            db.commit()

            initial_state = {
                "project_id": project_id,
                "user_prompt": project.prompt,
                "settings": {
                    "video_type": project.video_type,
                    "duration": project.duration,
                    "aspect_ratio": project.aspect_ratio,
                    "language": project.language,
                    "voice_preference": project.voice_preference,
                    "visual_style": project.visual_style,
                    "music_preference": project.music_preference,
                    "captions_enabled": project.captions_enabled
                },
                "production_plan": {},
                "script": {},
                "scenes": [],
                "generated_videos": [],
                "retry_count": 0,
                "max_retries": 2,
                "retry_required": False
            }

            # Map progress per agent node
            agent_progress_map = {
                "manager": (10, "Manager Agent"),
                "script": (22, "Script Agent"),
                "scene": (35, "Scene Agent"),
                "video": (60, "Video Generation Agent"),
                "voice": (72, "Voice Agent"),
                "audio": (82, "Audio Agent"),
                "subtitle": (88, "Subtitle Agent"),
                "editor": (95, "Editor Agent"),
                "reviewer": (100, "Reviewer Agent")
            }

            current_state = initial_state
            
            # Stream execution through LangGraph
            async for output in video_orchestration_graph.astream(initial_state):
                for node_name, node_state in output.items():
                    current_state.update(node_state)
                    prog, agent_display = agent_progress_map.get(node_name, (50, node_name.title()))
                    cls._update_progress(db, project_id, agent_display, prog, "running", f"{agent_display} completed execution.")
                    
                    # Record agent execution in DB
                    agent_exec = AgentExecution(
                        id=str(uuid.uuid4())[:8],
                        project_id=project_id,
                        agent_name=agent_display,
                        status="completed",
                        output_summary=str(list(node_state.keys()))
                    )
                    db.add(agent_exec)
                    db.commit()

            # Save generated scenes & production data to database
            final_plan = current_state.get("production_plan", {})
            final_script = current_state.get("script", {})
            final_scenes = current_state.get("scenes", [])
            final_video = current_state.get("final_video")
            final_thumb = current_state.get("thumbnail_path")
            voice_file = current_state.get("voice_file")
            music_file = current_state.get("music_file")
            sub_file = current_state.get("subtitle_file")
            review_res = current_state.get("review_result", {})

            # Clean previous scenes if regenerating
            db.query(Scene).filter(Scene.project_id == project_id).delete()

            for s_data in final_scenes:
                s_num = s_data.get("scene_number", 1)
                scene_record = Scene(
                    id=f"{project_id}_scene_{s_num}",
                    project_id=project_id,
                    scene_number=s_num,
                    narration=s_data.get("narration", ""),
                    visual_prompt=s_data.get("visual_prompt", ""),
                    screen_text=s_data.get("screen_text"),
                    camera_movement=s_data.get("camera", "slow zoom"),
                    visual_style=s_data.get("style", "cinematic"),
                    transition=s_data.get("transition", "fade"),
                    duration=float(s_data.get("duration", 5.0)),
                    video_path=storage_service.get_scene_video_path(project_id, s_num),
                    thumbnail_path=storage_service.get_scene_thumb_path(project_id, s_num),
                    status="completed"
                )
                db.add(scene_record)

            # Update Project Record
            project.title = final_script.get("title", project.title)
            project.production_plan = final_plan
            project.script_data = final_script
            project.final_video_path = final_video
            project.thumbnail_path = final_thumb
            project.voice_path = voice_file
            project.music_path = music_file
            project.subtitle_path = sub_file
            project.review_data = review_res
            project.status = "completed"
            project.progress = 100
            project.current_agent = "Reviewer Agent"

            job.status = "completed"
            job.completed_at = datetime.now(timezone.utc)
            db.commit()

            event = {
                "type": "completed",
                "project_id": project_id,
                "agent": "Reviewer Agent",
                "progress": 100,
                "status": "completed",
                "final_video_url": f"/api/projects/{project_id}/video"
            }
            broadcast_generation_status(event)
            logger.info(f"[GenerationService] Project {project_id} workflow successfully completed!")

        except Exception as e:
            logger.error(f"[GenerationService] Pipeline failed for project {project_id}: {e}", exc_info=True)
            db.rollback()
            project = db.query(Project).filter(Project.id == project_id).first()
            if project:
                project.status = "failed"
                project.error_message = str(e)
                db.commit()
            
            event = {
                "type": "failed",
                "project_id": project_id,
                "status": "failed",
                "error_message": f"Generation pipeline encountered an error: {str(e)}"
            }
            broadcast_generation_status(event)
        finally:
            db.close()

    @classmethod
    async def regenerate_single_scene(cls, project_id: str, scene_id: str):
        """Regenerate only one scene and re-compile the final video."""
        db = SessionLocal()
        try:
            scene = db.query(Scene).filter(Scene.id == scene_id, Scene.project_id == project_id).first()
            project = db.query(Project).filter(Project.id == project_id).first()
            if not scene or not project:
                raise ValueError(f"Scene {scene_id} or Project {project_id} not found.")

            cls._update_progress(db, project_id, "Video Generation Agent", 30, "running", f"Regenerating Scene {scene.scene_number}...")
            
            video_provider = get_video_provider()
            out_path = storage_service.get_scene_video_path(project_id, scene.scene_number)
            
            await video_provider.generate_video(
                prompt=scene.visual_prompt,
                duration=scene.duration,
                aspect_ratio=project.aspect_ratio,
                output_path=out_path,
                style=scene.visual_style,
                scene_number=scene.scene_number
            )
            scene.status = "completed"
            db.commit()

            # Re-compile video with Editor Agent
            cls._update_progress(db, project_id, "Editor Agent", 75, "running", "Rebuilding final video with updated scene...")
            
            all_scenes = db.query(Scene).filter(Scene.project_id == project_id).order_by(Scene.scene_number).all()
            scene_paths = [s.video_path for s in all_scenes if s.video_path and os.path.exists(s.video_path)]
            
            editor = EditorAgent()
            state = {
                "project_id": project_id,
                "production_plan": project.production_plan or {"aspect_ratio": project.aspect_ratio, "captions_required": project.captions_enabled},
                "generated_videos": scene_paths,
                "voice_file": project.voice_path,
                "music_file": project.music_path,
                "subtitle_file": project.subtitle_path
            }
            editor_res = await editor.execute(state)
            
            # Review again
            cls._update_progress(db, project_id, "Reviewer Agent", 95, "running", "Reviewing updated video...")
            reviewer = ReviewerAgent()
            state["final_video"] = editor_res.get("final_video")
            review_res = await reviewer.execute(state)

            project.status = "completed"
            project.progress = 100
            project.final_video_path = editor_res.get("final_video")
            project.review_data = review_res.get("review_result")
            db.commit()

            event = {
                "type": "completed",
                "project_id": project_id,
                "agent": "Reviewer Agent",
                "progress": 100,
                "status": "completed",
                "final_video_url": f"/api/projects/{project_id}/video"
            }
            broadcast_generation_status(event)

        except Exception as e:
            logger.error(f"[GenerationService] Single scene regeneration failed: {e}")
            event = {
                "type": "failed",
                "project_id": project_id,
                "status": "failed",
                "error_message": f"Scene regeneration error: {str(e)}"
            }
            broadcast_generation_status(event)
        finally:
            db.close()

generation_service = GenerationService()
