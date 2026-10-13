import uuid
from typing import List, Optional
from sqlalchemy.orm import Session
from ..models.database import Project, Scene, GenerationJob, AgentExecution, GeneratedAsset
from ..models.schemas import ProjectCreate, ProjectUpdate
from ..services.storage_service import storage_service

class ProjectService:
    @staticmethod
    def create_project(db: Session, project_in: ProjectCreate) -> Project:
        project_id = str(uuid.uuid4())[:8]
        project = Project(
            id=project_id,
            title=f"Video - {project_in.prompt[:25]}",
            prompt=project_in.prompt,
            video_type=project_in.video_type,
            duration=project_in.duration,
            aspect_ratio=project_in.aspect_ratio,
            language=project_in.language,
            voice_preference=project_in.voice_preference,
            visual_style=project_in.visual_style,
            music_preference=project_in.music_preference,
            captions_enabled=project_in.captions_enabled,
            status="draft",
            progress=0
        )
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def get_project(db: Session, project_id: str) -> Optional[Project]:
        return db.query(Project).filter(Project.id == project_id).first()

    @staticmethod
    def list_projects(db: Session, skip: int = 0, limit: int = 50) -> List[Project]:
        return db.query(Project).order_by(Project.created_at.desc()).offset(skip).limit(limit).all()

    @staticmethod
    def count_projects(db: Session) -> int:
        return db.query(Project).count()

    @staticmethod
    def update_project(db: Session, project_id: str, project_update: ProjectUpdate) -> Optional[Project]:
        project = ProjectService.get_project(db, project_id)
        if not project:
            return None
        
        update_data = project_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(project, field, value)
        
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def delete_project(db: Session, project_id: str) -> bool:
        project = ProjectService.get_project(db, project_id)
        if not project:
            return False
        
        storage_service.delete_project_files(project_id)
        db.delete(project)
        db.commit()
        return True

project_service = ProjectService()
