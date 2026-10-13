import os
from pathlib import Path
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ROOT_DIR = BASE_DIR.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Content Studio"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # LLM Settings
    GEMINI_API_KEY: str = ""
    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    
    # Text-to-Video Settings
    HUGGINGFACE_API_KEY: str = ""
    FAL_KEY: str = ""
    REPLICATE_API_TOKEN: str = ""
    JSON2VIDEO_API_KEY: str = ""
    MAGIC_HOUR_API_KEY: str = ""
    
    # Text-to-Speech Settings
    ELEVENLABS_API_KEY: str = ""
    DEFAULT_VOICE_PROVIDER: str = "edge_tts"
    
    # Database
    DATABASE_URL: str = f"sqlite:///{BASE_DIR}/content_studio.db"
    
    # Storage & Outputs
    OUTPUT_DIR: str = str(BASE_DIR / "generated")
    MAX_RETRIES: int = 2
    LOG_LEVEL: str = "INFO"
    
    # Server & CORS
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:5173", "http://127.0.0.1:5173", "*"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["*"]

    model_config = SettingsConfigDict(
        env_file=[str(ROOT_DIR / ".env"), str(BASE_DIR / ".env"), ".env"],
        extra="ignore"
    )

settings = Settings()

# Ensure base generated directories exist
os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
for sub in ["videos", "audio", "scenes", "subtitles", "images", "projects", "temp"]:
    os.makedirs(os.path.join(settings.OUTPUT_DIR, sub), exist_ok=True)
