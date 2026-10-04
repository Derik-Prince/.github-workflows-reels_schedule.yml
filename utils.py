import re
import json
import subprocess
from pathlib import Path

# Correct project root path
ROOT = Path(__file__).resolve().parent
PUBLIC = ROOT / "public"
PUBLIC.mkdir(parents=True, exist_ok=True)

def safe(name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_\-]+', '_', name)

def run(cmd):
    """Executes system shell/ffmpeg commands safely"""
    if isinstance(cmd, str):
        res = subprocess.run(cmd, shell=True, check=True)
    else:
        res = subprocess.run(cmd, check=True)
    return res

def load_products():
    config_file = ROOT / "config" / "products.json"
    if not config_file.exists():
        config_file = ROOT / "products.json"
        
    with open(config_file, "r", encoding="utf-8") as f:
        return json.load(f)
