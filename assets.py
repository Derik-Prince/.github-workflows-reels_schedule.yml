import requests
from pathlib import Path
from .utils import safe

def download_assets(product, workdir):
    workdir = Path(workdir); workdir.mkdir(parents=True, exist_ok=True)
    files=[]
    for i, url in enumerate(product.get("image_urls", [])):
        if not url: continue
        try:
            r=requests.get(url, timeout=25, headers={"User-Agent":"Mozilla/5.0"}); r.raise_for_status()
            ext=".jpg"
            ctype=r.headers.get("content-type","")
            if "png" in ctype: ext=".png"
            path=workdir/f"img_{i}{ext}"; path.write_bytes(r.content); files.append(path)
        except Exception as e:
            print("image download failed", url, e)
    for i, url in enumerate(product.get("video_urls", [])):
        if not url: continue
        try:
            r=requests.get(url, timeout=60, headers={"User-Agent":"Mozilla/5.0"}); r.raise_for_status()
            path=workdir/f"video_{i}.mp4"; path.write_bytes(r.content); files.append(path)
        except Exception as e:
            print("video download failed", url, e)
    return files
