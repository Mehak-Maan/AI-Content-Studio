import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from ..models.database import get_db
from ..models.schemas import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectListResponse, SceneSchema
from ..services.project_service import project_service

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project_in: ProjectCreate, db: Session = Depends(get_db)):
    project = project_service.create_project(db, project_in)
    return project

@router.get("", response_model=ProjectListResponse)
def list_projects(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    projects = project_service.list_projects(db, skip, limit)
    total = project_service.count_projects(db)
    return {"total": total, "projects": projects}

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = project_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: str, project_update: ProjectUpdate, db: Session = Depends(get_db)):
    project = project_service.update_project(db, project_id, project_update)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: str, db: Session = Depends(get_db)):
    success = project_service.delete_project(db, project_id)
    if not success:
        raise HTTPException(status_code=404, detail="Project not found")
    return None

@router.get("/{project_id}/video")
def get_project_video(project_id: str, db: Session = Depends(get_db)):
    project = project_service.get_project(db, project_id)
    if not project or not project.final_video_path or not os.path.exists(project.final_video_path):
        raise HTTPException(status_code=404, detail="Video file not found or not yet generated")
    return FileResponse(
        project.final_video_path, 
        media_type="video/mp4", 
        filename=f"{project.id}_video.mp4",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache", "Expires": "0"}
    )

@router.get("/{project_id}/thumbnail")
def get_project_thumbnail(project_id: str, db: Session = Depends(get_db)):
    project = project_service.get_project(db, project_id)
    if not project or not project.thumbnail_path or not os.path.exists(project.thumbnail_path):
        # Fallback to default or 404
        raise HTTPException(status_code=404, detail="Thumbnail not found")
    return FileResponse(
        project.thumbnail_path, 
        media_type="image/jpeg",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )

@router.get("/{project_id}/scenes/{scene_id}/video")
def get_scene_video(project_id: str, scene_id: str, db: Session = Depends(get_db)):
    project = project_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    scene = next((s for s in project.scenes if s.id == scene_id), None)
    if not scene or not scene.video_path or not os.path.exists(scene.video_path):
        raise HTTPException(status_code=404, detail="Scene video not found")
    return FileResponse(
        scene.video_path, 
        media_type="video/mp4",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )

@router.get("/{project_id}/scenes/{scene_id}/thumbnail")
def get_scene_thumbnail(project_id: str, scene_id: str, db: Session = Depends(get_db)):
    project = project_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    scene = next((s for s in project.scenes if s.id == scene_id), None)
    if not scene or not scene.thumbnail_path or not os.path.exists(scene.thumbnail_path):
        raise HTTPException(status_code=404, detail="Scene thumbnail not found")
    return FileResponse(
        scene.thumbnail_path, 
        media_type="image/jpeg",
        headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
    )
