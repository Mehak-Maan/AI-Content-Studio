import os
from datetime import datetime, timezone
from sqlalchemy import (
    create_engine, Column, String, Integer, Float, Boolean, 
    Text, DateTime, ForeignKey, JSON
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from ..config.settings import settings

engine = create_engine(
    settings.DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_utc_now():
    return datetime.now(timezone.utc)

class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, nullable=False, default="Untitled Video")
    prompt = Column(Text, nullable=False)
    video_type = Column(String, default="instagram_reel")
    duration = Column(Integer, default=30)
    aspect_ratio = Column(String, default="9:16")
    language = Column(String, default="English")
    voice_preference = Column(String, default="Professional")
    visual_style = Column(String, default="modern cinematic")
    music_preference = Column(String, default="Cinematic")
    captions_enabled = Column(Boolean, default=True)
    
    # State tracking
    status = Column(String, default="draft")  # draft, pending, running, completed, failed
    current_agent = Column(String, nullable=True)
    progress = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    
    # Generated asset paths and JSON blobs
    production_plan = Column(JSON, nullable=True)
    script_data = Column(JSON, nullable=True)
    voice_path = Column(String, nullable=True)
    music_path = Column(String, nullable=True)
    subtitle_path = Column(String, nullable=True)
    final_video_path = Column(String, nullable=True)
    thumbnail_path = Column(String, nullable=True)
    review_data = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    # Relationships
    scenes = relationship("Scene", back_populates="project", cascade="all, delete-orphan", order_by="Scene.scene_number")
    generation_jobs = relationship("GenerationJob", back_populates="project", cascade="all, delete-orphan")
    agent_executions = relationship("AgentExecution", back_populates="project", cascade="all, delete-orphan")
    assets = relationship("GeneratedAsset", back_populates="project", cascade="all, delete-orphan")

class Scene(Base):
    __tablename__ = "scenes"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    scene_number = Column(Integer, nullable=False)
    narration = Column(Text, nullable=False)
    visual_prompt = Column(Text, nullable=False)
    screen_text = Column(String, nullable=True)
    camera_movement = Column(String, default="slow zoom")
    visual_style = Column(String, default="cinematic")
    transition = Column(String, default="fade")
    duration = Column(Float, default=5.0)
    
    # Generated media
    video_path = Column(String, nullable=True)
    thumbnail_path = Column(String, nullable=True)
    audio_path = Column(String, nullable=True)
    status = Column(String, default="pending")
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=get_utc_now)
    updated_at = Column(DateTime, default=get_utc_now, onupdate=get_utc_now)

    project = relationship("Project", back_populates="scenes")

class GenerationJob(Base):
    __tablename__ = "generation_jobs"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    status = Column(String, default="queued")
    retry_count = Column(Integer, default=0)
    error_log = Column(Text, nullable=True)
    started_at = Column(DateTime, default=get_utc_now)
    completed_at = Column(DateTime, nullable=True)

    project = relationship("Project", back_populates="generation_jobs")

class AgentExecution(Base):
    __tablename__ = "agent_executions"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    agent_name = Column(String, nullable=False)
    status = Column(String, default="running")
    input_summary = Column(Text, nullable=True)
    output_summary = Column(Text, nullable=True)
    execution_time_seconds = Column(Float, default=0.0)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)

    project = relationship("Project", back_populates="agent_executions")

class GeneratedAsset(Base):
    __tablename__ = "generated_assets"

    id = Column(String, primary_key=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=False)
    asset_type = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size_bytes = Column(Integer, default=0)
    duration_seconds = Column(Float, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=get_utc_now)

    project = relationship("Project", back_populates="assets")

def init_db():
    Base.metadata.create_all(bind=engine)

# Auto initialize schema tables
init_db()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
