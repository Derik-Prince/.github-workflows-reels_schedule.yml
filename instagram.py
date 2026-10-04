import os, requests

def publish(video_url, caption):
    user=os.getenv("IG_USER_ID"); token=os.getenv("IG_ACCESS_TOKEN"); ver=os.getenv("IG_API_VERSION","v24.0")
    if not user or not token: raise RuntimeError("IG_USER_ID/IG_ACCESS_TOKEN missing")
    base=f"https://graph.facebook.com/{ver}"
    r=requests.post(f"{base}/{user}/media",data={"media_type":"REELS","video_url":video_url,"caption":caption,"access_token":token},timeout=45)
    r.raise_for_status(); creation=r.json()["id"]
    # Meta processing can take time. Poll briefly before publish.
    for _ in range(12):
        s=requests.get(f"{base}/{creation}",params={"fields":"status_code","access_token":token},timeout=30)
        s.raise_for_status(); status=s.json().get("status_code")
        if status == "FINISHED": break
        if status == "ERROR": raise RuntimeError(f"Instagram media processing failed: {s.text}")
        import time; time.sleep(5)
    p=requests.post(f"{base}/{user}/media_publish",data={"creation_id":creation,"access_token":token},timeout=45)
    p.raise_for_status(); return p.json()
