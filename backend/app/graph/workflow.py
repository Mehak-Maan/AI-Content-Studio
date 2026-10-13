from typing import Dict, Any
from langgraph.graph import StateGraph, END
from .state import VideoGenerationState
from ..agents.manager_agent import ManagerAgent
from ..agents.script_agent import ScriptAgent
from ..agents.scene_agent import SceneAgent
from ..agents.video_agent import VideoGenerationAgent
from ..agents.voice_agent import VoiceAgent
from ..agents.audio_agent import AudioAgent
from ..agents.subtitle_agent import SubtitleAgent
from ..agents.editor_agent import EditorAgent
from ..agents.reviewer_agent import ReviewerAgent
from ..utils.logger import logger

# Initialize agents
manager_agent = ManagerAgent()
script_agent = ScriptAgent()
scene_agent = SceneAgent()
video_agent = VideoGenerationAgent()
voice_agent = VoiceAgent()
audio_agent = AudioAgent()
subtitle_agent = SubtitleAgent()
editor_agent = EditorAgent()
reviewer_agent = ReviewerAgent()

# Node functions
async def run_manager(state: VideoGenerationState) -> Dict[str, Any]:
    return await manager_agent.execute(state)

async def run_script(state: VideoGenerationState) -> Dict[str, Any]:
    return await script_agent.execute(state)

async def run_scene(state: VideoGenerationState) -> Dict[str, Any]:
    return await scene_agent.execute(state)

async def run_video(state: VideoGenerationState) -> Dict[str, Any]:
    return await video_agent.execute(state)

async def run_voice(state: VideoGenerationState) -> Dict[str, Any]:
    return await voice_agent.execute(state)

async def run_audio(state: VideoGenerationState) -> Dict[str, Any]:
    return await audio_agent.execute(state)

async def run_subtitle(state: VideoGenerationState) -> Dict[str, Any]:
    return await subtitle_agent.execute(state)

async def run_editor(state: VideoGenerationState) -> Dict[str, Any]:
    return await editor_agent.execute(state)

async def run_reviewer(state: VideoGenerationState) -> Dict[str, Any]:
    return await reviewer_agent.execute(state)

# Conditional router from Reviewer
def route_review(state: VideoGenerationState) -> str:
    if state.get("retry_required", False):
        retry_agent = state.get("retry_agent", "editor")
        logger.info(f"[Workflow Router] Quality check failed. Routing retry back to: {retry_agent}")
        if retry_agent in ["video", "editor", "voice", "audio", "subtitle"]:
            return retry_agent
        return "editor"
    return END

def create_video_generation_graph():
    """Build and compile the multi-agent LangGraph orchestration graph."""
    graph = StateGraph(VideoGenerationState)

    # Register Nodes
    graph.add_node("manager", run_manager)
    graph.add_node("script", run_script)
    graph.add_node("scene", run_scene)
    graph.add_node("video", run_video)
    graph.add_node("voice", run_voice)
    graph.add_node("audio", run_audio)
    graph.add_node("subtitle", run_subtitle)
    graph.add_node("editor", run_editor)
    graph.add_node("reviewer", run_reviewer)

    # Set Entry Point
    graph.set_entry_point("manager")

    # Linear workflow edges
    graph.add_edge("manager", "script")
    graph.add_edge("script", "scene")
    graph.add_edge("scene", "video")
    graph.add_edge("video", "voice")
    graph.add_edge("voice", "audio")
    graph.add_edge("audio", "subtitle")
    graph.add_edge("subtitle", "editor")
    graph.add_edge("editor", "reviewer")

    # Conditional edge from reviewer
    graph.add_conditional_edges(
        "reviewer",
        route_review,
        {
            "video": "video",
            "voice": "voice",
            "audio": "audio",
            "subtitle": "subtitle",
            "editor": "editor",
            END: END
        }
    )

    return graph.compile()

video_orchestration_graph = create_video_generation_graph()
