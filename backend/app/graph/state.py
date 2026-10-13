from typing import TypedDict, List, Dict, Any, Optional

class VideoGenerationState(TypedDict, total=False):
    project_id: str
    user_prompt: str
    settings: Dict[str, Any]
    production_plan: Dict[str, Any]
    script: Dict[str, Any]
    scenes: List[Dict[str, Any]]
    generated_videos: List[str]
    voice_file: Optional[str]
    voice_duration: Optional[float]
    word_subtitles: Optional[str]
    music_file: Optional[str]
    subtitle_file: Optional[str]
    final_video: Optional[str]
    thumbnail_path: Optional[str]
    current_agent: str
    agent_status: Dict[str, str]
    errors: List[str]
    retry_count: int
    max_retries: int
    retry_required: bool
    retry_agent: Optional[str]
    target_scene_number: Optional[int]
    review_result: Dict[str, Any]
