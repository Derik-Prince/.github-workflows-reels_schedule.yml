import os
import time
import requests

IG_USER_ID = os.getenv("IG_USER_ID", "").strip()
ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN", "").strip()
API_VERSION = os.getenv("IG_API_VERSION", "v21.0").strip()

def publish(video_url: str, caption: str):
    if not IG_USER_ID or not ACCESS_TOKEN:
        raise RuntimeError("IG_USER_ID or IG_ACCESS_TOKEN is missing in environment variables.")

    base_url = f"https://graph.facebook.com/{API_VERSION}/{IG_USER_ID}"
    
    print(f"Step 1: Creating Instagram Reel Container for: {video_url}")
    create_payload = {
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": ACCESS_TOKEN
    }
    
    r = requests.post(f"{base_url}/media", data=create_payload)
    res = r.json()
    
    creation_id = res.get("id")
    if not creation_id:
        raise RuntimeError(f"Failed to create reel container: {res}")
        
    print(f"Container created successfully. ID: {creation_id}")
    print("Step 2: Waiting for Meta servers to process and transcode video...")

    # Wait and Poll status until Meta finishes processing the video
    max_retries = 24  # Wait up to 2 minutes
    ready = False
    
    for i in range(max_retries):
        time.sleep(6)
        status_url = f"https://graph.facebook.com/{API_VERSION}/{creation_id}"
        st_res = requests.get(status_url, params={"fields": "status_code,status", "access_token": ACCESS_TOKEN}).json()
        status_code = st_res.get("status_code")
        print(f"Polling ({i+1}/{max_retries}) - Processing Status: {status_code}")
        
        if status_code == "FINISHED":
            ready = True
            break
        elif status_code == "ERROR":
            raise RuntimeError(f"Meta media processing failed on server: {st_res}")
            
    if not ready:
        raise TimeoutError("Meta video processing timed out before finishing.")

    print("Step 3: Video is READY! Publishing Reel to Instagram feed...")
    publish_payload = {
        "creation_id": creation_id,
        "access_token": ACCESS_TOKEN
    }
    
    p = requests.post(f"{base_url}/media_publish", data=publish_payload)
    if not p.ok:
        raise RuntimeError(f"Publish failed: {p.text}")
        
    pub_res = p.json()
    print("🎉 SUCCESS! Reel is officially LIVE on Instagram! ID:", pub_res.get("id"))
    return pub_res
