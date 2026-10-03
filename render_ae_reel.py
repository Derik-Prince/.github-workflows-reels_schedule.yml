import os
import sys
import time
import json
import asyncio
import datetime
import requests
import edge_tts
from moviepy.editor import (
    ImageClip, AudioFileClip, CompositeVideoClip, TextClip,
    ColorClip
)

IG_USER_ID = os.getenv("IG_USER_ID")
ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")

with open("products.json", "r", encoding="utf-8") as f:
    PRODUCTS_LIST = json.load(f)

# Eeroju active product (First item)
PRODUCT = PRODUCTS_LIST[0]

target_input = os.getenv("TARGET_LANG")
if target_input in ["te", "hi", "en"]:
    ACTIVE_LANG = target_input
else:
    utc_hour = datetime.datetime.utcnow().hour
    if utc_hour == 1:
        ACTIVE_LANG = "te"   # 7:00 AM IST
    elif utc_hour == 7:
        ACTIVE_LANG = "hi"   # 1:00 PM IST
    elif utc_hour == 11:
        ACTIVE_LANG = "en"   # 5:00 PM IST
    else:
        ACTIVE_LANG = "te"

TRIGGER_KEYWORD = PRODUCT["keyword"].upper()

LANG_CONFIG = {
    "te": {
        "voice": "te-IN-MohanNeural",
        "font": "Pragati Narrow",
        "hook": f"WAIT! COMMENT '{TRIGGER_KEYWORD}' FOR LINK!",
        "script": f"Rey aagandi! Ee deal chusara? {PRODUCT['title']} meedha straight {PRODUCT['discount']} discount undi! Kevalam {PRODUCT['deal_price']} ke vasthondi. Direct buy link mee DM lo direct ga ravalante kinda '{TRIGGER_KEYWORD}' ani comment cheyyandi!",
        "caption": f"🔥 UNREAL DEAL ALERT! 🔥\n\n{PRODUCT['title']}\nOffer Price: {PRODUCT['deal_price']} (MRP: {PRODUCT['mrp']})\nDiscount: {PRODUCT['discount']}\n\n👉 Comment \"{TRIGGER_KEYWORD}\" to get the link in your DM! 📩\n\n#prucansales #telugudeals #lootdeals #offers"
    },
    "hi": {
        "voice": "hi-IN-MadhurNeural",
        "font": "Poppins-Black",
        "hook": f"RUKO! COMMENT '{TRIGGER_KEYWORD}' FOR LINK!",
        "script": f"Rukiye dosto! Loot offer aa chuka hai! {PRODUCT['title']} par flat {PRODUCT['discount']} chal raha hai. Buy link ke liye niche '{TRIGGER_KEYWORD}' comment karein!",
        "caption": f"🔥 CRAZY DISCOUNT TODAY! 🔥\n\n{PRODUCT['title']}\nDeal Price: {PRODUCT['deal_price']} (MRP: {PRODUCT['mrp']})\nDiscount: {PRODUCT['discount']}\n\n👉 Comment \"{TRIGGER_KEYWORD}\" for direct link in your DM! 📩\n\n#deals #prucansales #amazonoffers #bestprice"
    },
    "en": {
        "voice": "en-IN-PrabhatNeural",
        "font": "Poppins-Black",
        "hook": f"STOP! COMMENT '{TRIGGER_KEYWORD}' FOR LINK!",
        "script": f"Stop scrolling right now! Huge price drop on {PRODUCT['title']}. Get it now for {PRODUCT['deal_price']} at {PRODUCT['discount']}. Comment '{TRIGGER_KEYWORD}' right now to get the link sent directly to your DM!",
        "caption": f"🔥 MASSIVE PRICE DROP ALERT! 🔥\n\n{PRODUCT['title']}\nDeal Price: {PRODUCT['deal_price']} (MRP: {PRODUCT['mrp']})\nDiscount: {PRODUCT['discount']}\n\n👉 Comment \"{TRIGGER_KEYWORD}\" to get the link in DM! 📩\n\n#deals #prucansales #techdeals #stealdeals"
    }
}

async def generate_voiceover(text, voice_name, output_path):
    communicate = edge_tts.Communicate(text, voice_name, rate="+10%")
    await communicate.save(output_path)

def download_image(url, save_path):
    res = requests.get(url, stream=True)
    with open(save_path, 'wb') as f:
        f.write(res.content)

def build_cinematic_reel(lang, audio_path, image_path, output_video):
    cfg = LANG_CONFIG[lang]
    audio = AudioFileClip(audio_path)
    duration = audio.duration

    canvas = ColorClip(size=(1080, 1920), color=(12, 12, 14), duration=duration)

    img_clip = ImageClip(image_path).set_duration(duration)
    img_clip = img_clip.resize(height=1000)
    img_clip = img_clip.resize(lambda t: 1 + 0.04 * (t / duration))
    img_clip = img_clip.set_position(('center', 420))

    badge_bg = ColorClip(size=(600, 110), color=(255, 30, 80), duration=duration).set_position(('center', 180))
    badge_text = TextClip(f"⚡ {PRODUCT['discount']} ⚡", fontsize=60, color='white', font='Poppins-Black', size=(600, 110), method='caption').set_position(('center', 180)).set_duration(duration)

    hook_text = TextClip(cfg["hook"], fontsize=48, color='yellow', font=cfg["font"], size=(980, None), method='caption').set_position(('center', 320)).set_duration(min(duration, 3.5))

    price_box = TextClip(f"PRICE: {PRODUCT['deal_price']}  |  MRP: {PRODUCT['mrp']}", fontsize=54, color='#00FFAA', font='Poppins-Black', size=(950, None), method='caption').set_position(('center', 1520)).set_duration(duration)

    cta_box = TextClip(f"👉 COMMENT '{TRIGGER_KEYWORD}' FOR LINK 👈", fontsize=40, color='white', font='Poppins-Black', size=(950, None), method='caption').set_position(('center', 1660)).set_duration(duration)

    final_video = CompositeVideoClip(
        [canvas, img_clip, badge_bg, badge_text, hook_text, price_box, cta_box],
        size=(1080, 1920)
    ).set_duration(duration)

    final_video = final_video.set_audio(audio)
    final_video.write_videofile(output_video, fps=30, codec="libx264", audio_codec="aac", threads=4, preset="fast")

def post_reel_to_meta(video_url, caption):
    base_url = f"https://graph.facebook.com/v26.0/{IG_USER_ID}"
    print(f"Creating Reel container for: {video_url}")
    
    res = requests.post(f"{base_url}/media", data={
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": ACCESS_TOKEN
    }).json()
    
    creation_id = res.get("id")
    if not creation_id:
        print("Reel Creation Failed:", res)
        sys.exit(1)
        
    print(f"Processing Reel... Container ID: {creation_id}")
    time.sleep(45)
    
    pub = requests.post(f"{base_url}/media_publish", data={
        "creation_id": creation_id,
        "access_token": ACCESS_TOKEN
    }).json()
    print("Reel successfully published! Live ID:", pub.get("id"))

async def render_flow():
    with open("current_lang.txt", "w") as f:
        f.write(ACTIVE_LANG)
        
    audio_file = f"audio_{ACTIVE_LANG}.mp3"
    img_file = "product.jpg"
    video_file = f"reel_{ACTIVE_LANG}.mp4"

    download_image(PRODUCT["image_url"], img_file)
    await generate_voiceover(LANG_CONFIG[ACTIVE_LANG]["script"], LANG_CONFIG[ACTIVE_LANG]["voice"], audio_file)
    build_cinematic_reel(ACTIVE_LANG, audio_file, img_file, video_file)
    print(f"Done rendering: {video_file}")

def publish_flow():
    with open("current_lang.txt", "r") as f:
        lang = f.read().strip()
    video_url = os.getenv("VIDEO_PUBLIC_URL")
    caption = LANG_CONFIG[lang]["caption"]
    post_reel_to_meta(video_url, caption)

if __name__ == "__main__":
    if "--render-only" in sys.argv:
        asyncio.run(render_flow())
    elif "--publish-only" in sys.argv:
        publish_flow()
