import argparse, os, json
from pathlib import Path
from dotenv import load_dotenv

# Direct imports for root directory execution
from deal_engine import select
from script_engine import generate
from voice import create as create_voice
from assets import download_assets
from render import render
from instagram import publish
from utils import ROOT, PUBLIC, safe

load_dotenv(ROOT/".env")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--language", choices=["te", "hi", "en"], required=True)
    ap.add_argument("--publish", action="store_true")
    args = ap.parse_args()
    lang = args.language

    product = select(lang)
    work = PUBLIC / "cache" / safe(product["id"] + "_" + lang)
    work.mkdir(parents=True, exist_ok=True)
    print("Selected:", product["id"], product["title"])

    plan = generate(product, lang)
    (work / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=2), encoding="utf-8")
    
    download_assets(product, work)
    voice = create_voice(plan["voice"], PUBLIC / "audio" / (safe(product["id"] + "_" + lang) + ".mp3"), lang)
    out = PUBLIC / "reels" / (safe(product["id"] + "_" + lang) + ".mp4")
    
    render(product, plan, voice, out, work)
    
    caption = f"{plan['hook']}\n\n🔥 {product['currency']}{product['current_price']:,} | {product.get('discount_percent', 0)}% OFF\n\nComment {product['keyword']} for link.\n\n#deals #offers #shopping #reels"
    
    if args.publish or os.getenv("PUBLISH_INSTAGRAM", "false").lower() == "true":
        base = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")
        if not base:
            raise RuntimeError("PUBLIC_BASE_URL is required for Instagram publishing")
        url = base + "/reels/" + out.name
        print("Publishing:", url)
        print(publish(url, caption))
        
    print("REEL:", out)

if __name__ == "__main__":
    main()
