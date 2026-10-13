import os
import pytest
import asyncio
from backend.app.models.database import SessionLocal, Project
from backend.app.services.project_service import project_service
from backend.app.services.generation_service import generation_service
from backend.app.models.schemas import ProjectCreate
from backend.app.tools.media.ffmpeg_tool import FFmpegEditorTool

@pytest.mark.asyncio
async def test_end_to_end_video_generation():
    db = SessionLocal()
    # Create test project
    proj_in = ProjectCreate(
        prompt="Create a 15-second educational video explaining what RAG is.",
        video_type="educational_video",
        duration=15,
        aspect_ratio="9:16",
        language="English",
        voice_preference="Professional",
        visual_style="modern cinematic",
        music_preference="Technology",
        captions_enabled=True
    )
    project = project_service.create_project(db, proj_in)
    project_id = project.id
    db.close()

    # Run full generation pipeline
    await generation_service.start_generation(project_id)

    db = SessionLocal()
    updated_project = db.query(Project).filter(Project.id == project_id).first()
    
    assert updated_project is not None
    assert updated_project.status == "completed"
    assert updated_project.final_video_path is not None
    assert os.path.exists(updated_project.final_video_path)
    
    # Verify video properties with FFmpeg
    info = FFmpegEditorTool.get_media_info(updated_project.final_video_path)
    assert info["exists"] is True
    assert info["has_video"] is True
    assert info["has_audio"] is True
    assert info["duration"] > 5.0

    # Test single scene regeneration
    first_scene = updated_project.scenes[0]
    await generation_service.regenerate_single_scene(project_id, first_scene.id)
    
    db.refresh(updated_project)
    assert updated_project.status == "completed"
    assert os.path.exists(updated_project.final_video_path)
    
    db.close()
