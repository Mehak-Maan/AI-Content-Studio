import requests
import time

API_URL = "http://localhost:8000/api"

def run():
    payload = {
        "prompt": "Create a 30-second Instagram Reel explaining what AI agents are. Make it modern, energetic and suitable for social media. Use English narration, background music and subtitles.",
        "video_type": "instagram_reel",
        "duration": 30,
        "aspect_ratio": "9:16",
        "language": "English",
        "voice_preference": "Energetic",
        "visual_style": "modern cinematic",
        "music_preference": "Energetic",
        "captions_enabled": True
    }
    
    print("Creating project...")
    res = requests.post(f"{API_URL}/projects", json=payload)
    data = res.json()
    project_id = data["id"]
    print(f"Project created with ID: {project_id}")

    print("Triggering generation workflow...")
    gen_res = requests.post(f"{API_URL}/projects/{project_id}/generate")
    print("Generation status response:", gen_res.json())

    # Poll until completed
    while True:
        status_res = requests.get(f"{API_URL}/projects/{project_id}/status").json()
        status = status_res.get("status")
        progress = status_res.get("progress")
        agent = status_res.get("current_agent")
        print(f"[{agent}] Status: {status}, Progress: {progress}%")

        if status == "completed":
            print("\nGeneration completed successfully!")
            video_url = f"{API_URL}/projects/{project_id}/video"
            print(f"Final MP4 Video URL: {video_url}")
            break
        elif status == "failed":
            print("\nGeneration failed:", status_res.get("error_message"))
            break

        time.sleep(4)

if __name__ == "__main__":
    run()
