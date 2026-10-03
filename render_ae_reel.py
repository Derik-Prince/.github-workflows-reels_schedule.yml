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

IG_USER_ID = (os.getenv("IG_USER_ID") or "17841417494301577").strip()
ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")

with open("products.json", "r", encoding="utf-8") as f:
    PRODUCTS_LIST = json.load(f)

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

# 100% Policy-Safe Captions (ASCI & FTC Affiliate Rules Adherent)
LANG_CONFIG = {
    "te": {
        "voice": "te-IN-MohanNeural",
        "font": "Pragati Narrow",
        "hook": f"WAIT! SCROLL CHEYODDU! 🚨\nCOMMENT '{TRIGGER_KEYWORD}'",
        "script": f"Rey scroll cheyadam ventane aapandi! Ee deal chusara? {PRODUCT['title']} meedha straight {PRODUCT['discount']} drop paddadi! Original price {PRODUCT['mrp']}, ippudu kevalam {PRODUCT['deal_price']} ke dorukuthondi. Stock ventane aipothundi, direct link mee DM lo ravalante kindha '{TRIGGER_KEYWORD}' ani comment cheyyandi!",
        "caption": (
            f"🚨 STOP SCROLLING! UNREAL PRICE DROP! 🚨\n\n"
            f"⚡ {PRODUCT['title']}\n"
            f"🏷️ MRP: {PRODUCT['mrp']}\n"
            f"💥 Loot Price: {PRODUCT['deal_price']} ({PRODUCT['discount']})\n\n"
            f"👉 Link mee DM lo direct ga ravalante kindha \"{TRIGGER_KEYWORD}\" ani comment cheyyandi!\n\n"
            f"⚠️ (Legal Affiliate Disclosure: As an affiliate partner, we may earn an affiliate commission on qualifying purchases at no extra cost to you.)\n\n"
            f"#ad #affiliate #viralreels #telugureels #trendingreels #lootdeals #telugutech #amazonfinds #smartwatch #prucansales #trendingnow #explorepage #instadeals #reelsindia"
        )
    },
    "hi": {
        "voice": "hi-IN-MadhurNeural",
        "font": "Poppins-Black",
        "hook": f"RUKO! SCROLL BAND KARO! 🚨\nCOMMENT '{TRIGGER_KEYWORD}'",
        "script": f"Ek second dosto, scrolling turant roko! Aisa loot offer dubara nahi milega. {PRODUCT['title']} par flat {PRODUCT['discount']} ka massive drop aa chuka hai! {PRODUCT['mrp']} ka product sirf {PRODUCT['deal_price']} me mil raha hai. Limited units bache hain, buy link ke liye niche '{TRIGGER_KEYWORD}' turant comment karo!",
        "caption": (
            f"🚨 STOP SCROLLING! BIGGEST LOOT TODAY! 🚨\n\n"
            f"⚡ {PRODUCT['title']}\n"
            f"🏷️ MRP: {PRODUCT['mrp']}\n"
            f"💥 Deal Price: {PRODUCT['deal_price']} ({PRODUCT['discount']})\n\n"
            f"👉 Link ke liye niche \"{TRIGGER_KEYWORD}\" comment karein! DM me instant link aayega!\n\n"
            f"⚠️ (Affiliate Disclosure: Paid partnership / As an affiliate partner, we earn from qualifying purchases.)\n\n"
            f"#ad #affiliate #viralreels #hindideals #lootlootloot #amazonfinds #techdeals #trendingreels #viralvideos #prucansales #instadeals #explorepage #reelsindia"
        )
    },
    "en": {
        "voice": "en-IN-PrabhatNeural",
        "font": "Poppins-Black",
        "hook": f"WAIT! STOP SCROLLING! 🚨\nCOMMENT '{TRIGGER_KEYWORD}'",
        "script": f"Stop scrolling right now! This deal is literally insane. Massive price crash on {PRODUCT['title']} with flat {PRODUCT['discount']} discount! Selling for just {PRODUCT['deal_price']}, down from {PRODUCT['mrp']}. Stocks are disappearing fast, comment '{TRIGGER_KEYWORD}' right now to get the instant link directly in your DM!",
        "caption": (
            f"🚨 STOP SCROLLING! INSANE PRICE DROP! 🚨\n\n"
            f"⚡ {PRODUCT['title']}\n"
            f"🏷️ Original Price: {PRODUCT['mrp']}\n"
            f"💥 Steal Deal: {PRODUCT['deal_price']} ({PRODUCT['discount']})\n\n"
            f"👉 Comment \"{TRIGGER_KEYWORD}\" to get the link sent directly to your DM! 📩\n\n"
            f"⚠️ (Affiliate Disclosure: As an affiliate partner, we earn from qualifying purchases at no extra cost to you.)\n\n"
            f"#ad #affiliate #viral #trending #reelsviral #explorepage #stealdeals #techunboxing #amazonmusthaves #prucansales #dealsandsteals #trendingaudio #instareels"
        )
    }
}

async def generate_voiceover(text, voice_name, output_path):
    communicate = edge_tts.Communicate(text, voice_name, rate="+15%", pitch="+2Hz")
    await communicate.save(output_path)

def download_image(url, save_path):
    res = requests.get(url, stream=True)
    with open(save_path, 'wb') as f:
        f.write(res.content)

def build_cinematic_reel(lang, audio_path, image_path, output_video):
    cfg = LANG_CONFIG[lang]
    audio = AudioFileClip(audio_path)
    duration = audio.duration

    canvas = ColorClip(size=(1080, 1920), color=(10, 10, 12), duration=duration)

    img_clip = ImageClip(image_path).set_duration(duration)
    img_clip = img_clip.resize(height=1050)
    img_clip = img_clip.resize(lambda t: 1 + 0.08 * (t / duration))
    img_clip = img_clip.set_position(('center', 420))

    badge_bg = ColorClip(size=(640, 115), color=(255, 0, 70), duration=duration).set_position(('center', 160))
    badge_text = TextClip(f"🔥 {PRODUCT['discount']} LIMITED LOOT 🔥", fontsize=44, color='white', font='Poppins-Black', size=(640, 115), method='caption').set_position(('center', 160)).set_duration(duration)

    hook_text = TextClip(cfg["hook"], fontsize=48, color='#FFE600', font=cfg["font"], size=(980, None), method='caption').set_position(('center', 290)).set_duration(min(duration, 3.8))

    price_box = TextClip(f"PRICE: {PRODUCT['deal_price']}   MRP: {PRODUCT['mrp']}", fontsize=54, color='#00FFCC', font='Poppins-Black', size=(960, None), method='caption').set_position(('center', 1510)).set_duration(duration)

    cta_box = TextClip(f"👇 COMMENT '{TRIGGER_KEYWORD}' FOR DIRECT LINK 👇", fontsize=42, color='#FFFFFF', font='Poppins-Black', size=(960, None), method='caption').set_position(('center', 1660)).set_duration(duration)

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
        
    print(f"Reel container created: {creation_id}. Polling Meta video processing...")
    
    # Official Meta Transcode verification loop
    max_retries = 15
    for attempt in range(max_retries):
        time.sleep(10)
        status_url = f"https://graph.facebook.com/v26.0/{creation_id}?fields=status_code&access_token={ACCESS_TOKEN}"
        st_res = requests.get(status_url).json()
        status_code = st_res.get("status_code")
        print(f"Meta Transcode Status ({attempt+1}/{max_retries}): {status_code}")
        
        if status_code == "FINISHED":
            break
        elif status_code == "ERROR":
            print("Meta Transcoding Error:", st_res)
            sys.exit(1)
        elif attempt == max_retries - 1:
            print("Processing timeout reached.")

    pub = requests.post(f"{base_url}/media_publish", data={
        "creation_id": creation_id,
        "access_token": ACCESS_TOKEN
    }).json()
    
    post_id = pub.get("id")
    if post_id:
        print("🎉 SUCCESS! Reel is live on Instagram! Post ID:", post_id)
    else:
        print("Failed to publish Reel:", pub)
        sys.exit(1)

async def render_flow():
    with open("current_lang.txt", "w") as f:
        f.write(ACTIVE_LANG)
        
    audio_file = f"audio_{ACTIVE_LANG}.mp3"
    img_file = "product.jpg"
    video_file = f"reel_{ACTIVE_LANG}.mp4"

    download_image(PRODUCT["image_url"], img_file)
    await generate_voiceover(LANG_CONFIG[ACTIVE_LANG]["script"], LANG_CONFIG[ACTIVE_LANG]["voice"], audio_file)
    build_cinematic_reel(ACTIVE_LANG, audio_file, img_file, video_file)
    print(f"Video rendered successfully: {video_file}")

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
