import pytest
import os
import asyncio
from backend.app.agents.manager_agent import ManagerAgent
from backend.app.agents.script_agent import ScriptAgent
from backend.app.agents.scene_agent import SceneAgent
from backend.app.agents.voice_agent import VoiceAgent
from backend.app.agents.audio_agent import AudioAgent
from backend.app.agents.subtitle_agent import SubtitleAgent
from backend.app.agents.editor_agent import EditorAgent
from backend.app.agents.reviewer_agent import ReviewerAgent
from backend.app.tools.video.procedural_provider import ProceduralMotionVideoProvider
from backend.app.tools.media.ffmpeg_tool import FFmpegEditorTool
from backend.app.tools.media.video_validation import VideoValidationTool

@pytest.mark.asyncio
async def test_manager_agent():
    agent = ManagerAgent()
    state = {
        "project_id": "test_proj",
        "user_prompt": "Create a 15-second educational reel about AI agents.",
        "settings": {
            "duration": 15,
            "video_type": "instagram_reel",
            "aspect_ratio": "9:16",
            "language": "English"
        }
    }
    result = await agent.execute(state)
    assert "production_plan" in result
    plan = result["production_plan"]
    assert plan["duration"] == 15
    assert plan["aspect_ratio"] == "9:16"

@pytest.mark.asyncio
async def test_script_and_scene_agent():
    script_agent = ScriptAgent()
    state = {
        "project_id": "test_proj",
        "user_prompt": "Explain RAG architecture in simple terms.",
        "production_plan": {
            "duration": 15,
            "number_of_scenes": 3,
            "language": "English",
            "visual_style": "cinematic"
        }
    }
    script_res = await script_agent.execute(state)
    assert "script" in script_res
    assert len(script_res["scenes"]) >= 3

    scene_agent = SceneAgent()
    state["scenes"] = script_res["scenes"]
    scene_res = await scene_agent.execute(state)
    assert len(scene_res["scenes"]) >= 3
    assert "video_prompt" in scene_res["scenes"][0]

@pytest.mark.asyncio
async def test_procedural_video_provider(tmp_path):
    provider = ProceduralMotionVideoProvider()
    out_file = str(tmp_path / "test_scene.mp4")
    res_path = await provider.generate_video(
        prompt="Futuristic AI glowing core",
        duration=2.0,
        aspect_ratio="9:16",
        output_path=out_file,
        style="modern cinematic",
        scene_number=1
    )
    assert os.path.exists(res_path)
    assert os.path.getsize(res_path) > 1000

    info = FFmpegEditorTool.get_media_info(res_path)
    assert info["exists"] is True
    assert info["has_video"] is True
