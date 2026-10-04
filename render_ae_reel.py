import os
import sys
import time
import json
import subprocess
import requests
from PIL import Image, ImageDraw

IG_USER_ID = (os.getenv("IG_USER_ID") or "17841417494301577").strip()
ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
ELEVEN_KEY = os.getenv("ELEVENLABS_API_KEY")

with open("active_deal.json", "r", encoding="utf-8") as f:
    PRODUCT = json.load(f)

# Language strict separation: default 'te', can be passed via env
TARGET_LANG = os.getenv("TARGET_LANG", "te").strip().lower()
if TARGET_LANG not in ["te", "hi", "en"]:
    TARGET_LANG = "te"

TRIGGER_KEYWORD = PRODUCT.get("keyword", "DEAL").upper()

# 100% SEPARATE SCRIPTS PER LANGUAGE (NO MIXING)
SCRIPTS = {
    "te": {
        "voice_id": "pNInz6obpgDQGcFmaJgB",
        # Pure natural Telugu without Hindi mixing, numbers spelled out for clear pronunciation
        "script": (
            "బ్రో! ఒక్కసారి ఇది చూడండి! "
            "డీల్ ప్రైస్ కేవలం తొమ్మిది వందల తొంభై తొమ్మిది రూపాయలు మాత్రమే! "
            "ఆగండి ఆగండి, ఇది మామూలు ఆఫర్ కాదు, కళ్లు చెదిరే ప్రైస్ డ్రాప్! "
            "మార్కెట్ లో దీని అసలు రేటు రెండు వేల తొమ్మిది వందల రూపాయలు ఉండేది, "
            "కానీ ఈ రోజు ఏకంగా అరవై శాతం భారీ తగ్గింపు లభిస్తోంది! "
            "లుక్స్ మరియు క్వాలిటీ చాలా బాగున్నాయి. "
            "ఈ ఆఫర్ కొద్ది సమయం మాత్రమే ఉంటుంది. "
            f"కింద కామెంట్స్ లో {TRIGGER_KEYWORD} అని టైప్ చేయండి, "
            "డైరెక్ట్ బై లింక్ వెంటనే మీ ఇన్ బాక్స్ కి పంపిస్తాను!"
        ),
        "caption": (
            f"⚡ Bro, Check this out! Deal Price {PRODUCT.get('deal_price', '₹999')} only!\n\n"
            f"🔥 Product: {PRODUCT.get('title', 'Smart Tech Gadget')}\n"
            f"🏷️ MRP: {PRODUCT.get('mrp', '₹2,999')}\n"
            f"💥 Deal: {PRODUCT.get('deal_price', '₹999')} ({PRODUCT.get('discount', '60% OFF')})\n\n"
            f"👉 Direct verified link kosam kindha \"{TRIGGER_KEYWORD}\" ani comment cheyyandi! Instant ga mee DM lo vasthundi! 📩\n\n"
            f"#ad #affiliate #telugutech #lootdeals #amazonfinds #reelsindia"
        ),
        "tts_voice": "te-IN-MohanNeural"
    },
    "hi": {
        "voice_id": "pNInz6obpgDQGcFmaJgB",
        # Pure natural Hindi without Telugu words
        "script": (
            "भाई लोग! एक बार ये ऑफर जरूर देखिए! "
            "डील प्राइस सिर्फ नौ सौ निन्यानवे रुपये है! "
            "रुकिए रुकिए, ये कोई साधारण ऑफर नहीं, बहुत बड़ा प्राइस ड्रॉप है! "
            "मार्केट में इसका असली दाम दो हज़ार नौ सौ रुपये था, "
            "लेकिन आज सीधा साठ परसेंट का भारी डिस्काउंट मिल रहा है! "
            "इसकी क्वालिटी और लुक बेहद शानदार हैं। "
            "ये लिमिटेड टाइम लूट डील कभी भी खत्म हो सकती है। "
            f"नीचे कमेंट्स में {TRIGGER_KEYWORD} टाइप कीजिए, "
            "ऑफिशियल डायरेक्ट लिंक तुरंत आपके डीएम में आ जाएगा!"
        ),
        "caption": (
            f"⚡ लूट ऑफर! Deal Price {PRODUCT.get('deal_price', '₹999')} only!\n\n"
            f"🔥 Product: {PRODUCT.get('title', 'Smart Tech Gadget')}\n"
            f"🏷️ MRP: {PRODUCT.get('mrp', '₹2,999')}\n"
            f"💥 Deal: {PRODUCT.get('deal_price', '₹999')}\n\n"
            f"👉 लिंक के लिए नीचे \"{TRIGGER_KEYWORD}\" कमेंट करें! तुरंत DM आ जाएगा! 📩\n\n"
            f"#ad #affiliate #techdeals #lootdeals #amazonfinds #viralreels"
        ),
        "tts_voice": "hi-IN-MadhurNeural"
    },
    "en": {
        "voice_id": "pNInz6obpgDQGcFmaJgB",
        # Pure fluent English
        "script": (
            "Bro, check this out right now! "
            "The special deal price is just nine ninety-nine rupees! "
            "Wait, this is an incredible price drop! "
            "The actual retail price was two thousand nine hundred rupees, "
            "but today you get a massive sixty percent discount! "
            "The build quality and design look super premium. "
            "This limited-time offer might end anytime. "
            f"Comment {TRIGGER_KEYWORD} right below, "
            "and I will send the direct verified link straight to your DM!"
        ),
        "caption": (
            f"⚡ Massive Price Drop! Deal Price {PRODUCT.get('deal_price', '₹999')} only!\n\n"
            f"🔥 Product: {PRODUCT.get('title', 'Smart Tech Gadget')}\n"
            f"🏷️ MRP: {PRODUCT.get('mrp', '₹2,999')}\n"
            f"💥 Deal: {PRODUCT.get('deal_price', '₹999')}\n\n"
            f"👉 Comment \"{TRIGGER_KEYWORD}\" below for direct official link! 📩\n\n"
            f"#ad #affiliate #techdeals #smartgadgets #amazonfinds"
        ),
        "tts_voice": "en-IN-PrabhatNeural"
    }
}

ACTIVE_CONFIG = SCRIPTS[TARGET_LANG]

def generate_natural_voice(output_path):
    print(f"Generating voice for language [{TARGET_LANG.upper()}] via ElevenLabs...")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{ACTIVE_CONFIG['voice_id']}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVEN_KEY
    }
    data = {
        "text": ACTIVE_CONFIG["script"],
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.40,          # Kept stable so languages don't bleed/mix
            "similarity_boost": 0.85,
            "style": 0.35,             # Pure accent without language crossover
            "use_speaker_boost": True
        }
    }
    res = requests.post(url, json=data, headers=headers)
    if res.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(res.content)
        print("Pure voice generated successfully!")
    else:
        print(f"ElevenLabs fallback ({res.status_code}): Using Microsoft Edge TTS ({ACTIVE_CONFIG['tts_voice']})")
        subprocess.run([
            "edge-tts", 
            "--voice", ACTIVE_CONFIG["tts_voice"], 
            "--text", ACTIVE_CONFIG["script"], 
            "--write-media", output_path
        ], check=True)

def create_product_card_graphic(image_url, save_path):
    raw_img = "raw_download.jpg"
    try:
        subprocess.run(["curl", "-L", "-A", "Mozilla/5.0", "-o", raw_img, image_url], check=True)
        img = Image.open(raw_img).convert("RGBA")
    except Exception:
        img = Image.new("RGBA", (500, 500), (255, 255, 255, 255))

    img.thumbnail((620, 620), Image.Resampling.LANCZOS)
    
    card_w, card_h = 760, 760
    card = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)
    
    # Clean white card with neon accent outline
    draw.rounded_rectangle([0, 0, card_w, card_h], radius=44, fill=(255, 255, 255, 250), outline=(0, 255, 102, 255), width=8)
    
    ox = (card_w - img.width) // 2
    oy = (card_h - img.height) // 2
    card.paste(img, (ox, oy), img)
    card.save(save_path, "PNG")

def render_motion_video():
    os.makedirs("out", exist_ok=True)
    audio_file = f"audio_{TARGET_LANG}.mp3"
    generate_natural_voice(audio_file)
    
    card_img = "product_card.png"
    img_url = PRODUCT.get("image_url") or "https://m.media-amazon.com/images/I/61SSVxTSs3L._SL1500_.jpg"
    create_product_card_graphic(img_url, card_img)
    
    deal_price = PRODUCT.get('deal_price', '₹999').replace(":", "")
    keyword = TRIGGER_KEYWORD
    
    output_video = f"out/reel_{TARGET_LANG}.mp4"
    print(f"Rendering isolated [{TARGET_LANG.upper()}] Reel via FFmpeg...")
    
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "color=c=#0b0e14:s=1080x1920:d=16:r=30",
        "-loop", "1", "-i", card_img,
        "-i", audio_file,
        "-filter_complex",
        f"[1:v]scale=760:760[card];"
        f"[0:v][card]overlay=x=160:y='if(lt(t,1.2), 1920, if(lt(t,2.2), 1920-(1920-380)*(sin((t-1.2)*1.5708)), 380))':shortest=1[v1];"
        f"[v1]drawtext=text='DEAL: {deal_price}':fontcolor='#00FF66':fontsize=76:x=(w-text_w)/2:y=1220:box=1:boxcolor=black@0.6:boxborderw=18:enable='gte(t,2.0)'[v2];"
        f"[v2]drawtext=text='COMMENT \"{keyword}\" FOR LINK':fontcolor=white:fontsize=56:x=(w-text_w)/2:y=1600:box=1:boxcolor=black@0.7:boxborderw=24[vout]",
        "-map", "[vout]",
        "-map", "2:a",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "fast",
        "-shortest",
        output_video
    ]
    subprocess.run(ffmpeg_cmd, check=True)
    print("Video rendered successfully!")

def post_reel_to_meta(video_url):
    base_url = f"https://graph.facebook.com/v26.0/{IG_USER_ID}"
    res = requests.post(f"{base_url}/media", data={
        "media_type": "REELS",
        "video_url": video_url,
        "caption": ACTIVE_CONFIG["caption"],
        "access_token": ACCESS_TOKEN
    }).json()
    creation_id = res.get("id")
    if not creation_id:
        print("Meta Container Error:", res)
        sys.exit(1)
        
    for attempt in range(18):
        time.sleep(10)
        st_res = requests.get(f"{base_url}/{creation_id}?fields=status_code&access_token={ACCESS_TOKEN}").json()
        status_code = st_res.get("status_code")
        print(f"Meta Transcoding ({attempt+1}/18): {status_code}")
        if status_code == "FINISHED":
            break
        elif status_code == "ERROR":
            sys.exit(1)

    pub = requests.post(f"{base_url}/media_publish", data={
        "creation_id": creation_id,
        "access_token": ACCESS_TOKEN
    }).json()
    print("🎉 SUCCESS! Isolated Clean Reel is Live! ID:", pub.get("id"))

if __name__ == "__main__":
    if "--render-only" in sys.argv:
        render_motion_video()
    elif "--publish-only" in sys.argv:
        video_url = os.getenv("VIDEO_PUBLIC_URL")
        post_reel_to_meta(video_url)
