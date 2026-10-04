import os
import requests
import subprocess
from pathlib import Path
from utils import safe

def download_assets(product, workdir):
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    files = []
    
    # 1. Collect all product image URLs (both single image_url and image_urls list)
    urls = []
    if product.get("image_url"):
        urls.append(product["image_url"])
    if product.get("image_urls"):
        urls.extend([u for u in product["image_urls"] if u and u not in urls])
        
    # Fallback to high-res smartwatch image if none provided
    if not urls:
        urls.append("https://m.media-amazon.com/images/I/61SSVxTSs3L._SL1500_.jpg")

    for i, url in enumerate(urls):
        try:
            r = requests.get(url, timeout=25, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            ext = ".png" if "png" in r.headers.get("content-type", "") else ".jpg"
            path = workdir / f"img_{i}{ext}"
            path.write_bytes(r.content)
            files.append(path)
            print(f"Downloaded product asset: {path.name}")
        except Exception as e:
            print("Image download failed:", url, e)

    # 2. Tech desk background video download for realistic studio backdrop
    bg_video_path = workdir / "studio_bg.mp4"
    bg_video_url = "https://assets.mixkit.co/videos/preview/mixkit-hands-of-a-man-working-on-a-computer-43288-large.mp4"
    if not bg_video_path.exists():
        try:
            r = requests.get(bg_video_url, timeout=40, headers={"User-Agent": "Mozilla/5.0"})
            if r.status_code == 200:
                bg_video_path.write_bytes(r.content)
                print("Downloaded studio background clip.")
        except Exception as e:
            print("Background video download fallback:", e)

    return files
