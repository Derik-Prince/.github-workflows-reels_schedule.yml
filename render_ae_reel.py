import os
import sys
import time
import json
import asyncio
import datetime
import requests
import edge_tts
from moviepy.editor import (
    VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip,
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

TRIGGER_KEYWORD = PRODUCT.get("keyword", "DEAL").upper()

LANG_CONFIG = {
    "te": {
        "voice": "te-IN-MohanNeural",
        "font": "Pragati Narrow",
        "rate": "+5%",
        "pitch": "+0Hz",
        "hook": f"WAIT! SCROLL CHEYODDU! 🚨\nCOMMENT '{TRIGGER_KEYWORD}'",
        "script": (
            f"ఒక్క సెకండ్ ఆగండి బ్రో! ఈ క్రేజీ డీల్ చూసారా? "
            f"స్మార్ట్ వాచ్ మీద ఏకంగా డెబ్బై శాతం భారీ డిస్కౌంట్ పడింది! "
            f"నాలుగు వేల తొమ్మిది వందలు ఉండే వాచ్, ఇప్పుడు కేవలం పదిహేను వందల రూపాయలకే వస్తోంది. "
            f"ప్రీమియం డిస్ప్లే, సూపర్ బ్యాటరీ లైఫ్ ఉంటుంది. "
            f"డైరెక్ట్ సీక్రెట్ లింక్ మీ ఇన్ బాక్స్ లో రావాలంటే, "
            f"కింద కామెంట్స్ లో వాచ్ అని టైప్ చేయండి!"
        ),
        "caption": (
            f"🚨 STOP SCROLLING! CRAZIEST TECH LOOT TODAY! 🚨\n\n"
            f"⚡ {PRODUCT['title']}\n"
            f"🏷️ MRP: {PRODUCT['mrp']}\n"
            f"💥 Deal Price: {PRODUCT['deal_price']} ({PRODUCT['discount']})\n\n"
            f"👉 Direct link mee DM lo ravalante kindha \"{TRIGGER_KEYWORD}\" ani comment cheyyandi! 📩\n\n"
            f"⚠️ (Legal Affiliate Disclosure: As an Amazon Associate, we earn from qualifying purchases at no extra cost to you.)\n\n"
            f"#ad #affiliate #telugureels #telugutech #lootdeals #techreels #smartwatch #amazonfinds #viralreels #explorepage #instadeals"
        )
    },
    "hi": {
        "voice": "hi-IN-MadhurNeural",
        "font": "Poppins-Black",
        "rate": "+6%",
        "pitch": "+0Hz",
        "hook": f"RUKO! SCROLL BAND KARO! 🚨\nCOMMENT '{TRIGGER_KEYWORD}'",
        "script": (
            f"Rukiye dosto, ek second ke liye scroll band kijiye! Aaj ka sabse bada loot offer aa chuka hai. "
            f"Is premium smartwatch par pure sattar percent ka flat discount mil raha hai! "
            f"Paanch hazar wali watch abhi sirf pandrah sau rupaye mein mil rahi hai. "
            f"Direct loot link ke liye niche watch comment kijiye, "
            f"turant aapke DM mein link aa jayega!"
        ),
        "caption": (
            f"🚨 STOP SCROLLING! BIGGEST LOOT TODAY! 🚨\n\n"
            f"⚡ {PRODUCT['title']}\n"
            f"🏷️ MRP: {PRODUCT['mrp']}\n"
            f"💥 Deal Price: {PRODUCT['deal_price']} ({PRODUCT['discount']})\n\n"
            f"👉 Niche \"{TRIGGER_KEYWORD}\" comment karein! Instant link DM me aayega! 📩\n\n"
            f"⚠️ (Affiliate Disclosure: Paid partnership / As an affiliate associate, we earn from qualifying purchases.)\n\n"
            f"#ad #affiliate #hindideals #techdeals #lootlootloot #amazonfinds #smartwatch #viralreels #explorepage #reelsindia"
        )
    },
    "en": {
        "voice": "en-IN-PrabhatNeural",
        "font": "Poppins-Black",
        "rate": "+8%",
        "pitch": "+0Hz",
        "hook": f"WAIT! STOP SCROLLING! 🚨\nCOMMENT '{TRIGGER_KEYWORD}'",
        "script": (
            f"Hold on! Stop scrolling right now! You definitely don't want to miss this deal. "
            f"This best selling smartwatch has a massive seventy percent discount! "
            f"Originally five thousand rupees, now selling for just fifteen hundred rupees. "
            f"Stocks are disappearing fast, comment watch below, "
            f"and we will send the direct link to your inbox!"
        ),
        "caption": (
            f"🚨 STOP SCROLLING! UNREAL PRICE CRASH! 🚨\n\n"
            f"⚡ {PRODUCT['title']}\n"
            f"🏷️ Original Price: {PRODUCT['mrp']}\n"
            f"💥 Steal Price: {PRODUCT['deal_price']} ({PRODUCT['discount']})\n\n"
            f"👉 Comment \"{TRIGGER_KEYWORD}\" right below to get direct link in your DM! 📩\n\n"
            f"⚠️ (Affiliate Disclosure: As an affiliate partner, we earn from qualifying purchases at no additional cost to you.)\n\n"
            f"#ad #affiliate #stealdeals #techtrends #amazonfinds #smartwatch #viral #explorepage #instareels #lootdeals"
        )
    }
}

async def generate_voiceover(text, voice_name, rate, pitch, output_path):
    communicate = edge_tts.Communicate(text, voice_name, rate=rate, pitch=pitch)
    await communicate.save(output_path)

def download_file(url, save_path):
    res = requests.get(url, stream=True, timeout=30)
    with open(save_path, 'wb') as f:
        for chunk in res.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

def build_cinematic_reel(lang, audio_path, raw_video_path, output_video):
    cfg = LANG_CONFIG[lang]
    audio = AudioFileClip(audio_path)
    duration = audio.duration

    # 1. Base Product Video Handling (Crop & Fit to 9:16 Vertical)
    source_clip = VideoFileClip(raw_video_path)
    
    # Loop source video if shorter than audio
    if source_clip.duration < duration:
        loops_needed = int(duration / source_clip.duration) + 1
        video_sequence = [source_clip] * loops_needed
        from moviepy.editor import concatenate_videoclips
        source_clip = concatenate_videoclips(video_sequence)
        
    source_clip = source_clip.subclip(0, duration)
    
    # Scale & Center crop to 1080x1920
    w, h = source_clip.size
    target_aspect = 1080 / 1920
    current_aspect = w / h
    
    if current_aspect > target_aspect:
        new_w = int(h * target_aspect)
        x_center = w / 2
        bg_video = source_clip.crop(x1=x_center - new_w / 2, x2=x_center + new_w / 2, y1=0, y2=h)
    else:
        new_h = int(w / target_aspect)
        y_center = h / 2
        bg_video = source_clip.crop(y1=y_center - new_h / 2, y2=y_center + new_h / 2, x1=0, x2=w)
        
    bg_video = bg_video.resize((1080, 1920))

    # Top & Bottom soft dark gradients for text readability
    top_vignette = ColorClip(size=(1080, 480), color=(0, 0, 0), duration=duration).set_opacity(0.45).set_position(('center', 0))
    bottom_vignette = ColorClip(size=(1080, 680), color=(0, 0, 0), duration=duration).set_opacity(0.55).set_position(('center', 1240))

    # Static Deal Badge Banner (Top)
    badge_bg = ColorClip(size=(720, 110), color=(255, 10, 84), duration=duration).set_position(('center', 140))
    badge_text = TextClip(
        f"🔥 {PRODUCT.get('discount', '70% OFF')} LIMITED DROP 🔥",
        fontsize=42,
        color='white',
        font='Poppins-Black',
        size=(720, 110),
        method='caption'
    ).set_position(('center', 140)).set_duration(duration)

    # 2. Dynamic 3-5 Words Synchronized Animated Subtitles (Typing / Flash Chunks)
    words = cfg["script"].split()
    chunk_size = 4
    word_chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    chunk_duration = duration / max(len(word_chunks), 1)

    animated_caption_clips = []
    for idx, chunk in enumerate(word_chunks):
        start_time = idx * chunk_duration
        current_dur = min(chunk_duration, duration - start_time)
        
        # Word Box Background
        bg_card = ColorClip(size=(980, 170), color=(10, 12, 16), duration=current_dur).set_opacity(0.85)
        
        caption_txt = TextClip(
            chunk,
            fontsize=46,
            color='#FFE600',
            font=cfg["font"],
            size=(940, 150),
            method='caption'
        ).set_duration(current_dur)
        
        chunk_composite = CompositeVideoClip([bg_card, caption_txt.set_position('center')], size=(980, 170))
        chunk_composite = chunk_composite.set_start(start_time).set_position(('center', 1330))
        animated_caption_clips.append(chunk_composite)

    # Persistent Bottom Action Bar
    cta_bar = ColorClip(size=(1000, 120), color=(0, 122, 255), duration=duration).set_position(('center', 1660))
    cta_text = TextClip(
        f"👇 COMMENT '{TRIGGER_KEYWORD}' FOR DIRECT LINK 👇",
        fontsize=38,
        color='#FFFFFF',
        font='Poppins-Black',
        size=(980, 120),
        method='caption'
    ).set_position(('center', 1660)).set_duration(duration)

    # Composite Layers Together
    elements = [
        bg_video, top_vignette, bottom_vignette,
        badge_bg, badge_text,
        *animated_caption_clips,
        cta_bar, cta_text
    ]

    final_video = CompositeVideoClip(elements, size=(1080, 1920)).set_duration(duration)
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
    print(f"Creating Reel container for video: {video_url}")
    
    res = requests.post(f"{base_url}/media", data={
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": ACCESS_TOKEN
    }).json()
    
    creation_id = res.get("id")
    if not creation_id:
        print("Container Creation Failed:", res)
        sys.exit(1)
        
    print(f"Container created ID: {creation_id}. Polling Meta transcode status...")
    
    max_retries = 18
    for attempt in range(max_retries):
        time.sleep(10)
        status_url = f"https://graph.facebook.com/v26.0/{creation_id}?fields=status_code&access_token={ACCESS_TOKEN}"
        st_res = requests.get(status_url).json()
        status_code = st_res.get("status_code")
        print(f"Meta Transcoding ({attempt+1}/{max_retries}): {status_code}")
        
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
        print("🎉 SUCCESS! Pro-Video Reel is Live! Post ID:", post_id)
    else:
        print("Publishing Failed:", pub)
        sys.exit(1)

async def render_flow():
    with open("current_lang.txt", "w") as f:
        f.write(ACTIVE_LANG)
        
    audio_file = f"audio_{ACTIVE_LANG}.mp3"
    raw_video = "source_product.mp4"
    video_file = f"reel_{ACTIVE_LANG}.mp4"

    # Download raw product review video clip
    download_file(PRODUCT["video_url"], raw_video)
    
    cfg = LANG_CONFIG[ACTIVE_LANG]
    await generate_voiceover(cfg["script"], cfg["voice"], cfg["rate"], cfg["pitch"], audio_file)
    build_cinematic_reel(ACTIVE_LANG, audio_file, raw_video, video_file)
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
