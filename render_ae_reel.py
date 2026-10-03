import os
import sys
import time
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

PRODUCT = {
    "title": "Noise Smart Watch Ultra",
    "deal_price": "₹1,499",
    "mrp": "₹4,999",
    "discount": "70% OFF",
    "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=1080"
}

LANG_CONFIG = {
    "te": {
        "voice": "te-IN-MohanNeural",
        "font": "Pragati Narrow",
        "hook": "WAIT! EE LOOT DEAL MISS AVVADDU!",
        "script": f"Rey aagandi! Ee deal chusara? {PRODUCT['title']} meedha straight 70% off nadusthondi! Original MRP {PRODUCT['mrp']}, ippudu kevalam {PRODUCT['deal_price']} ke vasthondi. Stock thondaraga aipothundi, buy link bio lo undi ventane order cheyyandi!",
        "caption": f"🔥 UNREAL DEAL ALERT! 🔥\n\n{PRODUCT['title']}\nOffer Price: {PRODUCT['deal_price']} (MRP: {PRODUCT['mrp']})\nDiscount: {PRODUCT['discount']}\n\n👉 Bio lo link undi grab cheyandi!\n#prucansales #telugudeals #lootdeals #offers"
    },
    "hi": {
        "voice": "hi-IN-MadhurNeural",
        "font": "Poppins-Black",
        "hook": "RUKO! YEH DEAL MISS MAT KARNA!",
        "script": f"Rukiye dosto! Loot offer aa chuka hai! {PRODUCT['title']} par flat 70% discount chal raha hai. {PRODUCT['mrp']} ka product sirf {PRODUCT['deal_price']} me mil raha hai. Link bio me hai, abhi order karein!",
        "caption": f"🔥 CRAZY DISCOUNT TODAY! 🔥\n\n{PRODUCT['title']}\nDeal Price: {PRODUCT['deal_price']} (MRP: {PRODUCT['mrp']})\nDiscount: {PRODUCT['discount']}\n\n👉 Link in Bio!\n#deals #prucansales #amazonoffers #bestprice"
    },
    "en": {
        "voice": "en-IN-PrabhatNeural",
        "font": "Poppins-Black",
        "hook": "STOP SCROLLING! HUGE DROP!",
        "script": f"Stop scrolling right now! Huge price drop on {PRODUCT['title']}. It is currently selling at flat 70% discount for just {PRODUCT['deal_price']}, down from {PRODUCT['mrp']}. Limited stock available, link in bio!",
        "caption": f"🔥 MASSIVE PRICE DROP ALERT! 🔥\n\n{PRODUCT['title']}\nDeal Price: {PRODUCT['deal_price']} (MRP: {PRODUCT['mrp']})\nDiscount: {PRODUCT['discount']}\n\n👉 Click link in Bio to buy now!\n#deals #prucansales #techdeals #stealdeals"
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

    hook_text = TextClip(cfg["hook"], fontsize=54, color='yellow', font=cfg["font"], size=(980, None), method='caption').set_position(('center', 320)).set_duration(min(duration, 3.5))

    price_box = TextClip(f"PRICE: {PRODUCT['deal_price']}  |  MRP: {PRODUCT['mrp']}", fontsize=54, color='#00FFAA', font='Poppins-Black', size=(950, None), method='caption').set_position(('center', 1520)).set_duration(duration)

    cta_box = TextClip("👉 CHECK LINK IN BIO TO BUY 👈", fontsize=44, color='white', font='Poppins-Black', size=(900, None), method='caption').set_position(('center', 1660)).set_duration(duration)

    final_video = CompositeVideoClip(
        [canvas, img_clip, badge_bg, badge_text, hook_text, price_box, cta_box],
        size=(1080, 1920)
    ).set_duration(duration)

    final_video = final_video.set_audio(audio)
    final_video.write_videofile(
        output_video,
        fps=30,
        codec="libx264",
        audio_codec="aac",
        threads=4,
        preset="fast"
    )

def post_reel_to_meta(video_url, caption):
    base_url = f"https://graph.facebook.com/v26.0/{IG_USER_ID}"
    print(f"Creating Reel container for URL: {video_url}")
    
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
        
    print(f"Container created ID: {creation_id}. Waiting for Meta transcode...")
    time.sleep(40)
    
    pub = requests.post(f"{base_url}/media_publish", data={
        "creation_id": creation_id,
        "access_token": ACCESS_TOKEN
    }).json()
    print("Reel Live ID:", pub.get("id"))

async def render_flow():
    with open("current_lang.txt", "w") as f:
        f.write(ACTIVE_LANG)
        
    audio_file = f"audio_{ACTIVE_LANG}.mp3"
    img_file = "product.jpg"
    video_file = f"reel_{ACTIVE_LANG}.mp4"

    download_image(PRODUCT["image_url"], img_file)
    await generate_voiceover(LANG_CONFIG[ACTIVE_LANG]["script"], LANG_CONFIG[ACTIVE_LANG]["voice"], audio_file)
    build_cinematic_reel(ACTIVE_LANG, audio_file, img_file, video_file)
    print(f"Rendering Finished: {video_file}")

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
