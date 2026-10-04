import json, os, re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
(PUBLIC / "reels").mkdir(parents=True, exist_ok=True)
(PUBLIC / "audio").mkdir(parents=True, exist_ok=True)
(PUBLIC / "cache").mkdir(parents=True, exist_ok=True)

def load_products():
    with open(ROOT / "config" / "products.json", encoding="utf-8") as f:
        return json.load(f)

def run(cmd):
    p = subprocess.run(cmd, text=True, capture_output=True)
    if p.returncode:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{p.stderr}")
    return p.stdout

def safe(s):
    return re.sub(r"[^A-Za-z0-9_-]+", "_", str(s)).strip("_")[:80]
