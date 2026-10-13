import asyncio
import json
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ..models.database import get_db, Project
from ..models.schemas import GenerationStatusResponse
from ..services.project_service import project_service
from ..services.generation_service import generation_service, register_status_listener, unregister_status_listener
from ..utils.logger import add_log_listener, remove_log_listener

router = APIRouter(tags=["Generation"])

@router.post("/projects/{project_id}/generate", response_model=GenerationStatusResponse)
async def generate_project_video(
    project_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    project = project_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.status == "running":
        return {
            "project_id": project.id,
            "status": project.status,
            "current_agent": project.current_agent,
            "progress": project.progress,
            "message": "Generation already in progress"
        }

    # Trigger background task
    background_tasks.add_task(generation_service.start_generation, project_id)

    return {
        "project_id": project.id,
        "status": "running",
        "current_agent": "Manager Agent",
        "progress": 5,
        "message": "Generation workflow queued"
    }

@router.get("/projects/{project_id}/status", response_model=GenerationStatusResponse)
def get_generation_status(project_id: str, db: Session = Depends(get_db)):
    project = project_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return {
        "project_id": project.id,
        "status": project.status,
        "current_agent": project.current_agent,
        "progress": project.progress,
        "error_message": project.error_message,
        "final_video_url": f"/api/projects/{project.id}/video" if project.status == "completed" else None
    }

@router.post("/projects/{project_id}/regenerate", response_model=GenerationStatusResponse)
async def regenerate_project(
    project_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    project = project_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    background_tasks.add_task(generation_service.start_generation, project_id)
    return {
        "project_id": project.id,
        "status": "running",
        "current_agent": "Manager Agent",
        "progress": 5,
        "message": "Regenerating entire video..."
    }

@router.post("/projects/{project_id}/scenes/{scene_id}/regenerate", response_model=GenerationStatusResponse)
async def regenerate_single_scene(
    project_id: str,
    scene_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    project = project_service.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    background_tasks.add_task(generation_service.regenerate_single_scene, project_id, scene_id)
    return {
        "project_id": project.id,
        "status": "running",
        "current_agent": "Video Generation Agent",
        "progress": 25,
        "message": f"Regenerating Scene {scene_id}..."
    }

# WebSocket connection for real-time progress and logs
@router.websocket("/ws/status")
async def websocket_status_endpoint(websocket: WebSocket):
    await websocket.accept()
    queue = asyncio.Queue()

    def status_callback(event):
        try:
            queue.put_nowait({"event": "status", "data": event})
        except Exception:
            pass

    def log_callback(log_entry):
        try:
            queue.put_nowait({"event": "log", "data": log_entry})
        except Exception:
            pass

    register_status_listener(status_callback)
    add_log_listener(log_callback)

    try:
        while True:
            # Send events as they arrive or heartbeat
            try:
                msg = await asyncio.wait_for(queue.get(), timeout=20.0)
                await websocket.send_text(json.dumps(msg))
            except asyncio.TimeoutError:
                await websocket.send_text(json.dumps({"event": "ping"}))
    except WebSocketDisconnect:
        pass
    finally:
        unregister_status_listener(status_callback)
        remove_log_listener(log_callback)

# Server-Sent Events endpoint
@router.get("/events/status")
async def sse_status_endpoint():
    queue = asyncio.Queue()

    def callback(event):
        try:
            queue.put_nowait(event)
        except Exception:
            pass

    register_status_listener(callback)

    async def event_generator():
        try:
            while True:
                event = await queue.get()
                yield f"data: {json.dumps(event)}\n\n"
        except asyncio.CancelledError:
            unregister_status_listener(callback)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
