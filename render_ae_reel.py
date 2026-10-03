import os
import sys
import time
import json
import asyncio
import datetime
import subprocess
import requests
import edge_tts
from moviepy.editor import (
    VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip,
    ColorClip
)

IG_USER_ID = (os.getenv("IG_USER_ID") or "17841417494301577").strip()
ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")

# Auto-Generated Deal Load
with open("active_deal.json", "r", encoding="utf-8") as f:
    PRODUCT = json.load(f)

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

TRIGGER_KEYWORD = PRODUCT.get("keyword", "DEAL").upper()

LANG_CONFIG = {
    "te": {
        "voice": "te-IN-MohanNeural",
        "font": "Pragati Narrow",
        "rate": "+6%",
        "pitch": "+0Hz",
        "hook": f"WAIT! SCROLL CHEYODDU! 🚨\nకామెంట్ చేయండి '{TRIGGER_KEYWORD}'",
        "script": (
            f"ఒక్క సెకండ్ ఆగండి బ్రో! ఈ రోజు క్రేజీ లూట్ ఆఫర్ వచ్చేసింది! "
            f"{PRODUCT['title']} మీద ఏకంగా {PRODUCT['discount']} భారీ ప్రైస్ డ్రాప్ పడింది! "
            f"మార్కెట్ లో {PRODUCT['mrp']} ఉండేది, ఇప్పుడు కేవలం {PRODUCT['deal_price']} రూపాయలకే దొరుకుతోంది! "
            f"ఈ ఆఫర్ స్టాక్ ఉన్నంత వరకే ఉంటుంది. "
            f"డైరెక్ట్ సీక్రెట్ బై లింక్ మీ ఇన్ బాక్స్ కి రావాలంటే, "
            f"వెంటనే కింద కామెంట్స్ లో {TRIGGER_KEYWORD} అని కామెంట్ చేయండి!"
        ),
        "caption": (
            f"🚨 MASSIVE TECH LOOT TODAY! 🚨\n\n"
            f"⚡ {PRODUCT['title']}\n"
            f"🏷️ MRP: {PRODUCT['mrp']}\n"
            f"💥 Deal Price: {PRODUCT['deal_price']} ({PRODUCT['discount']})\n\n"
            f"👉 Direct verified link kosam kindha \"{TRIGGER_KEYWORD}\" అని comment cheyyandi! Instant ga mee DM lo vasthundi! 📩\n\n"
            f"⚠️ (Legal Affiliate Disclosure: As an Amazon Associate, we earn from qualifying purchases at no additional cost to you.)\n\n"
            f"#ad #affiliate #telugureels #telugutech #lootdeals #amazonfinds #techgadgets #viralreels #explorepage #instadeals"
        )
    },
    "hi": {
        "voice": "hi-IN-MadhurNeural",
        "font": "Poppins-Black",
        "rate": "+6%",
        "pitch": "+0Hz",
        "hook": f"RUKO! SCROLL BAND KARO! 🚨\nCOMMENT '{TRIGGER_KEYWORD}'",
        "script": (
            f"Rukiye dosto, ek second ke liye scroll band kijiye! Aaj ka sabse bada loot deal live ho chuka hai! "
            f"{PRODUCT['title']} par pure {PRODUCT['discount']} ka heavy discount mil raha hai! "
            f"{PRODUCT['mrp']} ka product abhi sale me sirf {PRODUCT['deal_price']} me mil raha hai! "
            f"Stock limited hai, agar direct buy link chahiye, "
            f"toh niche comment box me {TRIGGER_KEYWORD} comment kijiye! Instant DM link aa jayega!"
        ),
        "caption": (
            f"🚨 STOP SCROLLING! BIGGEST LOOT TODAY! 🚨\n\n"
            f"⚡ {PRODUCT['title']}\n"
            f"🏷️ MRP: {PRODUCT['mrp']}\n"
            f"💥 Deal Price: {PRODUCT['deal_price']} ({PRODUCT['discount']})\n\n"
            f"👉 Niche \"{TRIGGER_KEYWORD}\" comment karein! Instant link DM me aayega! 📩\n\n"
            f"⚠️ (Affiliate Disclosure: Paid partnership / As an affiliate partner, we earn from qualifying purchases.)\n\n"
            f"#ad #affiliate #hindideals #techdeals #lootlootloot #amazonfinds #viralreels #explorepage #reelsindia"
        )
    },
    "en": {
        "voice": "en-IN-PrabhatNeural",
        "font": "Poppins-Black",
        "rate": "+8%",
        "pitch": "+0Hz",
        "hook": f"WAIT! STOP SCROLLING! 🚨\nCOMMENT '{TRIGGER_KEYWORD}'",
        "script": (
            f"Hold on! Stop scrolling right now! You definitely don't want to miss this steal deal! "
            f"The popular {PRODUCT['title']} is currently running at a massive {PRODUCT['discount']} discount! "
            f"Original price is {PRODUCT['mrp']}, but right now it's up for just {PRODUCT['deal_price']}! "
            f"Units are flying off the shelves super fast. "
            f"Comment {TRIGGER_KEYWORD} right below to get the official verified link in your DM!"
        ),
        "caption": (
            f"🚨 STOP SCROLLING! CRAZY PRICE DROP! 🚨\n\n"
            f"⚡ {PRODUCT['title']}\n"
            f"🏷️ Original Price: {PRODUCT['mrp']}\n"
            f"💥 Steal Price: {PRODUCT['deal_price']} ({PRODUCT['discount']})\n\n"
            f"👉 Comment \"{TRIGGER_KEYWORD}\" right below to get direct link in your DM! 📩\n\n"
            f"⚠️ (Affiliate Disclosure: As an affiliate partner, we earn from qualifying purchases at no extra cost to you.)\n\n"
            f"#ad #affiliate #stealdeals #techtrends #amazonfinds #viral #explorepage #instareels #lootdeals"
        )
    }
}

async def generate_voiceover(text, voice_name, rate, pitch, output_path):
    communicate = edge_tts.Communicate(text, voice_name, rate=rate, pitch=pitch)
    await communicate.save(output_path)

def download_video_file(url, save_path):
    # Curl with browser user-agent avoids bot blocks
    cmd = [
        "curl", "-L", "-A",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "-o", save_path, url
    ]
    subprocess.run(cmd, check=True)

def build_cinematic_reel(lang, audio_path, raw_video_path, output_video):
    cfg = LANG_CONFIG[lang]
    audio = AudioFileClip(audio_path)
    duration = audio.duration

    try:
        source_clip = VideoFileClip(raw_video_path)
        if source_clip.duration < duration:
            loops_needed = int(duration / source_clip.duration) + 1
            from moviepy.editor import concatenate_videoclips
            source_clip = concatenate_videoclips([source_clip] * loops_needed)
        source_clip = source_clip.subclip(0, duration)
        
        # 9:16 Vertical Smart Crop
        w, h = source_clip.size
        target_aspect = 1080 / 1920
        if (w / h) > target_aspect:
            new_w = int(h * target_aspect)
            bg_video = source_clip.crop(x1=(w - new_w)/2, x2=(w + new_w)/2, y1=0, y2=h)
        else:
            new_h = int(w / target_aspect)
            bg_video = source_clip.crop(y1=(h - new_h)/2, y2=(h + new_h)/2, x1=0, x2=w)
        bg_video = bg_video.resize((1080, 1920))
    except Exception as e:
        print(f"Fallback to studio canvas due to video read error: {e}")
        bg_video = ColorClip(size=(1080, 1920), color=(14, 16, 22), duration=duration)

    # Gradients for text contrast
    top_vignette = ColorClip(size=(1080, 480), color=(0, 0, 0), duration=duration).set_opacity(0.45).set_position(('center', 0))
    bottom_vignette = ColorClip(size=(1080, 680), color=(0, 0, 0), duration=duration).set_opacity(0.60).set_position(('center', 1240))

    # Top Deal Badge Banner
    badge_bg = ColorClip(size=(740, 110), color=(255, 10, 84), duration=duration).set_position(('center', 140))
    badge_text = TextClip(
        f"🔥 {PRODUCT.get('discount', 'LIMITED DEAL')} FLASH SALE 🔥",
        fontsize=42,
        color='white',
        font='Poppins-Black',
        size=(740, 110),
        method='caption'
    ).set_position(('center', 140)).set_duration(duration)

    # Dynamic 3-5 Words Synced Captions (Alex Hormozi Style)
    words = cfg["script"].split()
    chunk_size = 4
    word_chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    chunk_duration = duration / max(len(word_chunks), 1)

    animated_caption_clips = []
    for idx, chunk in enumerate(word_chunks):
        st = idx * chunk_duration
        cdur = min(chunk_duration, duration - st)
        bg_card = ColorClip(size=(980, 160), color=(10, 12, 16), duration=cdur).set_opacity(0.85)
        caption_txt = TextClip(
            chunk,
            fontsize=46,
            color='#FFE600',
            font=cfg["font"],
            size=(940, 140),
            method='caption'
        ).set_duration(cdur)
        chunk_composite = CompositeVideoClip([bg_card, caption_txt.set_position('center')], size=(980, 160))
        chunk_composite = chunk_composite.set_start(st).set_position(('center', 1330))
        animated_caption_clips.append(chunk_composite)

    # Action Bar (CTA)
    cta_bar = ColorClip(size=(1000, 120), color=(0, 122, 255), duration=duration).set_position(('center', 1660))
    cta_text = TextClip(
        f"👇 COMMENT '{TRIGGER_KEYWORD}' FOR DIRECT LINK 👇",
        fontsize=38,
        color='#FFFFFF',
        font='Poppins-Black',
        size=(980, 120),
        method='caption'
    ).set_position(('center', 1660)).set_duration(duration)

    final_video = CompositeVideoClip([
        bg_video, top_vignette, bottom_vignette,
        badge_bg, badge_text,
        *animated_caption_clips,
        cta_bar, cta_text
    ], size=(1080, 1920)).set_duration(duration)

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
        print("Container Failed:", res)
        sys.exit(1)
        
    for attempt in range(18):
        time.sleep(10)
        status_url = f"https://graph.facebook.com/v26.0/{creation_id}?fields=status_code&access_token={ACCESS_TOKEN}"
        st_res = requests.get(status_url).json()
        status_code = st_res.get("status_code")
        print(f"Meta Transcoding ({attempt+1}/18): {status_code}")
        if status_code == "FINISHED":
            break
        elif status_code == "ERROR":
            print("Transcoding Error:", st_res)
            sys.exit(1)

    pub = requests.post(f"{base_url}/media_publish", data={
        "creation_id": creation_id,
        "access_token": ACCESS_TOKEN
    }).json()
    
    print("🎉 SUCCESS! Pro-Video Reel is Live! Post ID:", pub.get("id"))

async def render_flow():
    with open("current_lang.txt", "w") as f:
        f.write(ACTIVE_LANG)
        
    audio_file = f"audio_{ACTIVE_LANG}.mp3"
    raw_video = "source_video.mp4"
    video_file = f"reel_{ACTIVE_LANG}.mp4"

    download_video_file(PRODUCT["video_url"], raw_video)
    cfg = LANG_CONFIG[ACTIVE_LANG]
    await generate_voiceover(cfg["script"], cfg["voice"], cfg["rate"], cfg["pitch"], audio_file)
    build_cinematic_reel(ACTIVE_LANG, audio_file, raw_video, video_file)

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
