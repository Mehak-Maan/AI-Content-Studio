from fastapi import APIRouter
from .project_routes import router as project_router
from .generation_routes import router as generation_router
from ..models.schemas import SettingsConfig, SettingsUpdate
from ..config.settings import settings

api_router = APIRouter()

@api_router.get("/settings", response_model=SettingsConfig, tags=["Settings"])
def get_settings():
    return {
        "gemini_api_key_set": bool(settings.GEMINI_API_KEY),
        "groq_api_key_set": bool(settings.GROQ_API_KEY),
        "openai_api_key_set": bool(settings.OPENAI_API_KEY),
        "huggingface_api_key_set": bool(settings.HUGGINGFACE_API_KEY),
        "elevenlabs_api_key_set": bool(settings.ELEVENLABS_API_KEY),
        "default_voice_provider": settings.DEFAULT_VOICE_PROVIDER,
        "max_retries": settings.MAX_RETRIES
    }

@api_router.post("/settings", response_model=SettingsConfig, tags=["Settings"])
def update_settings(payload: SettingsUpdate):
    if payload.gemini_api_key is not None:
        settings.GEMINI_API_KEY = payload.gemini_api_key
    if payload.groq_api_key is not None:
        settings.GROQ_API_KEY = payload.groq_api_key
    if payload.openai_api_key is not None:
        settings.OPENAI_API_KEY = payload.openai_api_key
    if payload.huggingface_api_key is not None:
        settings.HUGGINGFACE_API_KEY = payload.huggingface_api_key
    if payload.elevenlabs_api_key is not None:
        settings.ELEVENLABS_API_KEY = payload.elevenlabs_api_key
    if payload.default_voice_provider is not None:
        settings.DEFAULT_VOICE_PROVIDER = payload.default_voice_provider
    if payload.max_retries is not None:
        settings.MAX_RETRIES = payload.max_retries

    return get_settings()

api_router.include_router(project_router)
api_router.include_router(generation_router)
