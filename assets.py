import os
import requests
from pathlib import Path
from utils import safe

# Free high quality vertical stock clips matching product category
CATEGORY_BG_VIDEOS = {
    "smartwatch": "https://assets.mixkit.co/videos/preview/mixkit-hands-of-a-man-wearing-a-smartwatch-43287-large.mp4",
    "earbuds": "https://assets.mixkit.co/videos/preview/mixkit-young-man-wearing-wireless-earphones-43285-large.mp4",
    "watch": "https://assets.mixkit.co/videos/preview/mixkit-hands-of-a-man-wearing-a-smartwatch-43287-large.mp4"
}

FALLBACK_BG_VIDEO = "https://assets.mixkit.co/videos/preview/mixkit-hands-of-a-man-working-on-a-computer-43288-large.mp4"

def download_assets(product, workdir):
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    files = []

    # 1. Download Exact Product Image
    urls = product.get("image_urls", [])
    if not urls and product.get("image_url"):
        urls = [product.get("image_url")]

    for i, url in enumerate(urls):
        if not url:
            continue
        try:
            r = requests.get(url, timeout=25, headers={"User-Agent": "Mozilla/5.0"})
            r.raise_for_status()
            ext = ".png" if "png" in r.headers.get("content-type", "") else ".jpg"
            path = workdir / f"img_{i}{ext}"
            path.write_bytes(r.content)
            files.append(path)
            print(f"Downloaded asset for {product['id']}: {path.name}")
        except Exception as e:
            print("Image download error:", url, e)

    # 2. Download Category Matching Vertical Stock Background Video
    cat = str(product.get("category", "")).lower()
    bg_url = CATEGORY_BG_VIDEOS.get(cat, FALLBACK_BG_VIDEO)
    bg_video_path = workdir / "category_bg.mp4"

    try:
        r = requests.get(bg_url, timeout=35, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            bg_video_path.write_bytes(r.content)
            print(f"Downloaded realistic background clip for category: {cat}")
    except Exception as e:
        print("Background video fetch warning:", e)

    return files
