import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_settings():
    response = client.get("/api/settings")
    assert response.status_code == 200
    assert "default_voice_provider" in response.json()

def test_create_project():
    payload = {
        "prompt": "Create a 30s TikTok video about deep learning",
        "video_type": "TikTok",
        "duration": 30,
        "aspect_ratio": "9:16",
        "language": "English",
        "voice_preference": "Energetic",
        "visual_style": "modern cinematic",
        "music_preference": "Energetic",
        "captions_enabled": True
    }
    response = client.post("/api/projects", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["duration"] == 30

    # Get project
    proj_id = data["id"]
    get_res = client.get(f"/api/projects/{proj_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == proj_id

    # List projects
    list_res = client.get("/api/projects")
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 1
