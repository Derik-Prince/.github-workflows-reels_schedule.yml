import os
import sys
import time
import json
import subprocess
import requests
from PIL import Image, ImageDraw, ImageFilter

IG_USER_ID = (os.getenv("IG_USER_ID") or "17841417494301577").strip()
ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
ELEVEN_KEY = os.getenv("ELEVENLABS_API_KEY")

with open("active_deal.json", "r", encoding="utf-8") as f:
    PRODUCT = json.load(f)

TRIGGER_KEYWORD = PRODUCT.get("keyword", "DEAL").upper()

VOICE_SCRIPT = (
    "Brooo! Check this out! "
    f"Deal price వచ్చి కేవలం {PRODUCT.get('deal_price', '999 rupees')} మాత్రమే! "
    "Wait wait wait, ఇది regular product కాదు భయ్యా, crazy price drop! "
    f"మార్కెట్ లో దీని actual MRP వచ్చి {PRODUCT.get('mrp', '2,999 rupees')} ఉండేది, "
    f"కానీ ఇవాళ ఏకంగా {PRODUCT.get('discount', '60 percent')} discount! "
    "Quality and looks super premium ఉన్నాయి! "
    "ఈ లిమిటెడ్ డీల్ ఎప్పుడైనా end అవ్వచ్చు. "
    f"కింద కామెంట్స్ లో {TRIGGER_KEYWORD} అని టైప్ చేయండి, "
    "official direct discount link instant గా మీ DM కి వస్తుంది!"
)

CAPTION = (
    f"⚡ Bro, Check this out! Deal Price {PRODUCT.get('deal_price', '₹999')} only!\n\n"
    f"🔥 Product: {PRODUCT.get('title', 'Smart Tech Gadget')}\n"
    f"🏷️ MRP: {PRODUCT.get('mrp', '₹2,999')}\n"
    f"💥 Deal: {PRODUCT.get('deal_price', '₹999')} ({PRODUCT.get('discount', 'Huge Discount')})\n\n"
    f"👉 Direct verified link kosam kindha \"{TRIGGER_KEYWORD}\" ani comment cheyyandi! Instant ga mee DM lo vasthundi! 📩\n\n"
    f"#ad #affiliate #telugutech #lootdeals #amazonfinds #reelsindia"
)

def generate_natural_voice(output_path):
    print("Generating natural voice via ElevenLabs...")
    url = "https://api.elevenlabs.io/v1/text-to-speech/pNInz6obpgDQGcFmaJgB"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVEN_KEY
    }
    data = {
        "text": VOICE_SCRIPT,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.32,
            "similarity_boost": 0.82,
            "style": 0.55,
            "use_speaker_boost": True
        }
    }
    res = requests.post(url, json=data, headers=headers)
    if res.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(res.content)
        print("Natural voice ready!")
    else:
        print(f"Fallback edge-tts: {res.text}")
        subprocess.run(["edge-tts", "--voice", "te-IN-MohanNeural", "--text", VOICE_SCRIPT, "--write-media", output_path], check=True)

def create_product_card_graphic(image_url, save_path):
    raw_img = "raw_download.jpg"
    try:
        subprocess.run(["curl", "-L", "-A", "Mozilla/5.0", "-o", raw_img, image_url], check=True)
        img = Image.open(raw_img).convert("RGBA")
    except Exception as e:
        img = Image.new("RGBA", (500, 500), (255, 255, 255, 255))

    img.thumbnail((620, 620), Image.Resampling.LANCZOS)
    
    card_w, card_h = 760, 760
    card = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)
    
    # White glossy card with neon border & rounded corners
    draw.rounded_rectangle([0, 0, card_w, card_h], radius=44, fill=(255, 255, 255, 250), outline=(0, 255, 102, 255), width=8)
    
    # Center product in card
    ox = (card_w - img.width) // 2
    oy = (card_h - img.height) // 2
    card.paste(img, (ox, oy), img)
    card.save(save_path, "PNG")

def render_motion_video():
    os.makedirs("out", exist_ok=True)
    audio_file = "audio_te.mp3"
    generate_natural_voice(audio_file)
    
    # Product card generation
    card_img = "product_card.png"
    img_url = PRODUCT.get("image_url") or "https://m.media-amazon.com/images/I/61SSVxTSs3L._SL1500_.jpg"
    create_product_card_graphic(img_url, card_img)
    
    deal_price = PRODUCT.get('deal_price', '₹999').replace(":", "")
    keyword = TRIGGER_KEYWORD
    
    print("Rendering Google-style motion graphics reel via FFmpeg...")
    # Clean, professional animated video with smooth spring-like slide-up, glowing gradients, deal tag and CTA
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
        "out/reel_te.mp4"
    ]
    subprocess.run(ffmpeg_cmd, check=True)
    print("Video rendered successfully!")

def post_reel_to_meta(video_url):
    base_url = f"https://graph.facebook.com/v26.0/{IG_USER_ID}"
    res = requests.post(f"{base_url}/media", data={
        "media_type": "REELS",
        "video_url": video_url,
        "caption": CAPTION,
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
    print("🎉 SUCCESS! Pro Google-Style Reel is Live! ID:", pub.get("id"))

if __name__ == "__main__":
    if "--render-only" in sys.argv:
        render_motion_video()
    elif "--publish-only" in sys.argv:
        video_url = os.getenv("VIDEO_PUBLIC_URL")
        post_reel_to_meta(video_url)
