from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

# Project schemas
class ProjectCreate(BaseModel):
    prompt: str = Field(..., description="Prompt describing the desired video")
    video_type: str = Field(default="instagram_reel", description="Platform/type format")
    duration: int = Field(default=30, description="Target duration in seconds")
    aspect_ratio: str = Field(default="9:16", description="Aspect ratio like 9:16, 16:9, 1:1")
    language: str = Field(default="English", description="Target language")
    voice_preference: str = Field(default="Professional", description="Voice tone/style")
    visual_style: str = Field(default="modern cinematic", description="Visual aesthetic")
    music_preference: str = Field(default="Cinematic", description="Background music vibe")
    captions_enabled: bool = Field(default=True, description="Whether to generate subtitles")

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    prompt: Optional[str] = None
    video_type: Optional[str] = None
    duration: Optional[int] = None
    aspect_ratio: Optional[str] = None
    language: Optional[str] = None
    voice_preference: Optional[str] = None
    visual_style: Optional[str] = None
    music_preference: Optional[str] = None
    captions_enabled: Optional[bool] = None

class SceneSchema(BaseModel):
    id: str
    project_id: str
    scene_number: int
    narration: str
    visual_prompt: str
    screen_text: Optional[str] = None
    camera_movement: Optional[str] = "slow zoom"
    visual_style: Optional[str] = "cinematic"
    transition: Optional[str] = "fade"
    duration: float
    video_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    audio_path: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SceneUpdate(BaseModel):
    narration: Optional[str] = None
    visual_prompt: Optional[str] = None
    screen_text: Optional[str] = None
    duration: Optional[float] = None
    visual_style: Optional[str] = None
    camera_movement: Optional[str] = None

class ProjectResponse(BaseModel):
    id: str
    title: str
    prompt: str
    video_type: str
    duration: int
    aspect_ratio: str
    language: str
    voice_preference: str
    visual_style: str
    music_preference: str
    captions_enabled: bool
    status: str
    current_agent: Optional[str] = None
    progress: int
    error_message: Optional[str] = None
    production_plan: Optional[Dict[str, Any]] = None
    script_data: Optional[Dict[str, Any]] = None
    voice_path: Optional[str] = None
    music_path: Optional[str] = None
    subtitle_path: Optional[str] = None
    final_video_path: Optional[str] = None
    thumbnail_path: Optional[str] = None
    review_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    scenes: List[SceneSchema] = []

    model_config = ConfigDict(from_attributes=True)

class ProjectListResponse(BaseModel):
    total: int
    projects: List[ProjectResponse]

class GenerationStatusResponse(BaseModel):
    project_id: str
    status: str
    current_agent: Optional[str] = None
    progress: int
    message: Optional[str] = None
    error_message: Optional[str] = None
    final_video_url: Optional[str] = None

class SettingsConfig(BaseModel):
    gemini_api_key_set: bool
    groq_api_key_set: bool
    openai_api_key_set: bool
    huggingface_api_key_set: bool
    elevenlabs_api_key_set: bool
    default_voice_provider: str
    max_retries: int

class SettingsUpdate(BaseModel):
    gemini_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    huggingface_api_key: Optional[str] = None
    elevenlabs_api_key: Optional[str] = None
    default_voice_provider: Optional[str] = None
    max_retries: Optional[int] = None
