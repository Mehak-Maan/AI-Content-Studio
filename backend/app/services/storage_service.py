import os
import shutil
from pathlib import Path
from ..config.settings import settings

class StorageService:
    def __init__(self, base_dir: str = settings.OUTPUT_DIR):
        self.base_dir = Path(base_dir)
        self.projects_dir = self.base_dir / "projects"
        os.makedirs(self.projects_dir, exist_ok=True)

    def get_project_dir(self, project_id: str) -> Path:
        p_dir = self.projects_dir / f"project_{project_id}"
        os.makedirs(p_dir, exist_ok=True)
        os.makedirs(p_dir / "scenes", exist_ok=True)
        os.makedirs(p_dir / "audio", exist_ok=True)
        os.makedirs(p_dir / "subtitles", exist_ok=True)
        os.makedirs(p_dir / "final", exist_ok=True)
        os.makedirs(p_dir / "thumbnails", exist_ok=True)
        return p_dir

    def get_scene_video_path(self, project_id: str, scene_number: int) -> str:
        p_dir = self.get_project_dir(project_id)
        return str(p_dir / "scenes" / f"scene_{scene_number:02d}.mp4")

    def get_scene_thumb_path(self, project_id: str, scene_number: int) -> str:
        p_dir = self.get_project_dir(project_id)
        return str(p_dir / "thumbnails" / f"scene_{scene_number:02d}.jpg")

    def get_voice_path(self, project_id: str) -> str:
        p_dir = self.get_project_dir(project_id)
        return str(p_dir / "audio" / "voice.mp3")

    def get_music_path(self, project_id: str) -> str:
        p_dir = self.get_project_dir(project_id)
        return str(p_dir / "audio" / "music.mp3")

    def get_final_audio_path(self, project_id: str) -> str:
        p_dir = self.get_project_dir(project_id)
        return str(p_dir / "audio" / "final_audio.mp3")

    def get_subtitle_path(self, project_id: str) -> str:
        p_dir = self.get_project_dir(project_id)
        return str(p_dir / "subtitles" / "captions.srt")

    def get_final_video_path(self, project_id: str) -> str:
        p_dir = self.get_project_dir(project_id)
        return str(p_dir / "final" / "final_video.mp4")

    def get_project_thumb_path(self, project_id: str) -> str:
        p_dir = self.get_project_dir(project_id)
        return str(p_dir / "thumbnails" / "poster.jpg")

    def delete_project_files(self, project_id: str):
        p_dir = self.projects_dir / f"project_{project_id}"
        if p_dir.exists():
            shutil.rmtree(p_dir, ignore_errors=True)

storage_service = StorageService()
