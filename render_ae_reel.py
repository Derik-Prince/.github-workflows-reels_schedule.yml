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

TRIGGER_KEYWORD = PRODUCT.get("keyword", "DEAL").upper()

# Humanized Conversational Scripts with Phonetic Clarity (Zero Robotic Accent)
LANG_CONFIG = {
    "te": {
        "voice": "te-IN-MohanNeural",
        "font": "Pragati Narrow",
        "rate": "+5%",
        "pitch": "+0Hz",
        "hook": f"ఒక్క నిమిషం! SCROLL CHEYODDU! 🚨\nకామెంట్ చేయండి '{TRIGGER_KEYWORD}'",
        # Pure natural Telugu conversational tone with spelled-out pricing to avoid robotic numbers
        "script": (
            f"ఒక్క సెకండ్ ఆగండి బ్రో! ఈ క్రేజీ డీల్ చూసారా? "
            f"మార్కెట్ లో బాగా ట్రెండ్ అవుతున్న స్మార్ట్ వాచ్ మీద ఏకంగా డెబ్బై శాతం భారీ డిస్కౌంట్ పడింది! "
            f"నాలుగు వేల తొమ్మిది వందలు ఉండే వాచ్, ఇప్పుడు ఆఫర్ లో కేవలం పదిహేను వందల రూపాయలకే వస్తోంది. "
            f"ప్రీమియం డిస్ప్లే, సూపర్ బ్యాటరీ లైఫ్ ఉంటుంది. "
            f"స్టాక్ అయిపోకముందే డైరెక్ట్ సీక్రెట్ లింక్ మీ ఇన్ బాక్స్ లో రావాలంటే, "
            f"కింద కామెంట్స్ లో వాచ్ అని టైప్ చేయండి! డైరెక్ట్ డీల్ లింక్ వెంటనే మీ ఇన్ బాక్స్ కి వస్తుంది!"
        ),
        "caption": (
            f"🚨 STOP SCROLLING! CRAZIEST TECH LOOT TODAY! 🚨\n\n"
            f"⚡ {PRODUCT['title']}\n"
            f"🏷️ MRP: {PRODUCT['mrp']}\n"
            f"💥 Deal Price: {PRODUCT['deal_price']} ({PRODUCT['discount']})\n\n"
            f"👉 డైరెక్ట్ బై లింక్ కోసం కింద \"{TRIGGER_KEYWORD}\" అని కామెంట్ చేయండి! Direct link instant ga mee DM lo vasthundi! 📩\n\n"
            f"⚠️ (Legal Affiliate Disclosure: As an Amazon/Affiliate associate, we earn from qualifying purchases at no extra cost to you.)\n\n"
            f"#ad #affiliate #telugureels #telugutech #lootdeals #techreels #smartwatch #amazonfinds #viralreels #explorepage #instadeals #trendingnow"
        )
    },
    "hi": {
        "voice": "hi-IN-MadhurNeural",
        "font": "Poppins-Black",
        "rate": "+6%",
        "pitch": "+0Hz",
        "hook": f"RUKO! SCROLL BAND KARO! 🚨\nCOMMENT '{TRIGGER_KEYWORD}'",
        # Fluent Hindi Creator Hinglish tone
        "script": (
            f"Rukiye dosto, ek second ke liye scroll band kijiye! Aaj ka sabse bada loot offer aa chuka hai. "
            f"Is premium smartwatch par pure sattar percent ka flat discount mil raha hai! "
            f"Paanch hazar wali watch abhi sale mein sirf pandrah sau rupaye mein mil rahi hai. "
            f"Aisa price drop baar baar nahi aata. "
            f"Agar aapko direct buy link chahiye, toh niche comment box mein watch comment kijiye, "
            f"turant aapke DM mein verified loot link bhej diya jayega!"
        ),
        "caption": (
            f"🚨 STOP SCROLLING! BIGGEST LOOT TODAY! 🚨\n\n"
            f"⚡ {PRODUCT['title']}\n"
            f"🏷️ MRP: {PRODUCT['mrp']}\n"
            f"💥 Deal Price: {PRODUCT['deal_price']} ({PRODUCT['discount']})\n\n"
            f"👉 Niche \"{TRIGGER_KEYWORD}\" comment karein! Instant link direct aapke DM mein aayega! 📩\n\n"
            f"⚠️ (Affiliate Disclosure: Paid partnership / As an affiliate associate, we earn from qualifying purchases.)\n\n"
            f"#ad #affiliate #hindideals #techdeals #lootlootloot #amazonfinds #smartwatch #viralreels #explorepage #reelsindia #trendingreels"
        )
    },
    "en": {
        "voice": "en-IN-PrabhatNeural",
        "font": "Poppins-Black",
        "rate": "+8%",
        "pitch": "+0Hz",
        "hook": f"WAIT! STOP SCROLLING! 🚨\nCOMMENT '{TRIGGER_KEYWORD}'",
        # Crisp Indian-English natural tech influencer voice
        "script": (
            f"Hold on! Stop scrolling right now! You definitely don't want to miss this insane price drop. "
            f"This best-selling smartwatch is currently running on a massive seventy percent discount! "
            f"Originally priced at five thousand rupees, it's now available for just fifteen hundred rupees during this flash sale. "
            f"Premium build, crisp display, and incredible battery life. "
            f"Stocks are selling out super fast, so comment watch right below, "
            f"and we will drop the direct official link straight to your inbox!"
        ),
        "caption": (
            f"🚨 STOP SCROLLING! UNREAL PRICE CRASH! 🚨\n\n"
            f"⚡ {PRODUCT['title']}\n"
            f"🏷️ MRP: {PRODUCT['mrp']}\n"
            f"💥 Steal Price: {PRODUCT['deal_price']} ({PRODUCT['discount']})\n\n"
            f"👉 Comment \"{TRIGGER_KEYWORD}\" right below to get the direct discounted link in your DM! 📩\n\n"
            f"⚠️ (Affiliate Disclosure: As an affiliate partner, we earn from qualifying purchases at no additional cost to you.)\n\n"
            f"#ad #affiliate #stealdeals #techtrends #amazonfinds #smartwatch #viral #explorepage #instareels #lootdeals #reelsindia"
        )
    }
}

async def generate_voiceover(text, voice_name, rate, pitch, output_path):
    communicate = edge_tts.Communicate(text, voice_name, rate=rate, pitch=pitch)
    await communicate.save(output_path)

def download_image(url, save_path):
    res = requests.get(url, stream=True, timeout=20)
    with open(save_path, 'wb') as f:
        f.write(res.content)

def build_cinematic_reel(lang, audio_path, image_path, output_video):
    cfg = LANG_CONFIG[lang]
    audio = AudioFileClip(audio_path)
    duration = audio.duration

    # Dark modern studio background canvas
    canvas = ColorClip(size=(1080, 1920), color=(12, 14, 20), duration=duration)

    # Dynamic camera zoom & pulse effect on product visual
    img_clip = ImageClip(image_path).set_duration(duration)
    img_clip = img_clip.resize(height=980)
    # Smooth continuous zoom-in for dynamic motion
    img_clip = img_clip.resize(lambda t: 1.0 + 0.05 * (t / max(duration, 1)))
    img_clip = img_clip.set_position(('center', 460))

    # Top Deal Badge Banner
    badge_bg = ColorClip(size=(720, 110), color=(255, 20, 80), duration=duration).set_position(('center', 150))
    badge_text = TextClip(
        f"🔥 {PRODUCT.get('discount', '70% OFF')} LIMITED DROP 🔥",
        fontsize=42,
        color='white',
        font='Poppins-Black',
        size=(720, 110),
        method='caption'
    ).set_position(('center', 150)).set_duration(duration)

    # Dynamic Hook Banner (Appears for first 4 seconds)
    hook_box = TextClip(
        cfg["hook"],
        fontsize=46,
        color='#FFE600',
        font=cfg["font"],
        size=(1000, None),
        method='caption'
    ).set_position(('center', 290)).set_duration(min(duration, 4.0))

    # Clean Modern Pricing Card
    price_tag = TextClip(
        f"DEAL: {PRODUCT.get('deal_price', '₹1,499')}  |  MRP: {PRODUCT.get('mrp', '₹4,999')}",
        fontsize=52,
        color='#00FFD1',
        font='Poppins-Black',
        size=(980, None),
        method='caption'
    ).set_position(('center', 1500)).set_duration(duration)

    # Bottom CTA Box
    cta_bar = ColorClip(size=(960, 130), color=(0, 100, 255), duration=duration).set_position(('center', 1650))
    cta_text = TextClip(
        f"👇 COMMENT '{TRIGGER_KEYWORD}' FOR DIRECT LINK 👇",
        fontsize=38,
        color='#FFFFFF',
        font='Poppins-Black',
        size=(940, 130),
        method='caption'
    ).set_position(('center', 1650)).set_duration(duration)

    final_video = CompositeVideoClip(
        [canvas, img_clip, badge_bg, badge_text, hook_box, price_tag, cta_bar, cta_text],
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
    print(f"Creating Reel container on Meta for account [{IG_USER_ID}]...")
    
    res = requests.post(f"{base_url}/media", data={
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
        "access_token": ACCESS_TOKEN
    }).json()
    
    creation_id = res.get("id")
    if not creation_id:
        print("Reel Container Creation Failed:", res)
        sys.exit(1)
        
    print(f"Container created ID: {creation_id}. Polling transcoding status...")
    
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
        print("🎉 SUCCESS! Pro-Quality Reel is Live! Post ID:", post_id)
    else:
        print("Publishing Failed:", pub)
        sys.exit(1)

async def render_flow():
    with open("current_lang.txt", "w") as f:
        f.write(ACTIVE_LANG)
        
    audio_file = f"audio_{ACTIVE_LANG}.mp3"
    img_file = "product.jpg"
    video_file = f"reel_{ACTIVE_LANG}.mp4"

    download_image(PRODUCT["image_url"], img_file)
    cfg = LANG_CONFIG[ACTIVE_LANG]
    await generate_voiceover(cfg["script"], cfg["voice"], cfg["rate"], cfg["pitch"], audio_file)
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
