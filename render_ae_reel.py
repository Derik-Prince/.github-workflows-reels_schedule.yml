import os
import sys
import time
import json
import subprocess
import requests

IG_USER_ID = (os.getenv("IG_USER_ID") or "17841417494301577").strip()
ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
ELEVEN_KEY = os.getenv("ELEVENLABS_API_KEY")

with open("active_deal.json", "r", encoding="utf-8") as f:
    PRODUCT = json.load(f)

TRIGGER_KEYWORD = PRODUCT.get("keyword", "DEAL").upper()

# Natural Tanglish script (numbers read naturally)
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

def render_remotion_video():
    generate_natural_voice("public/audio_te.mp3") if os.path.exists("public") else generate_natural_voice("audio_te.mp3")
    print("Rendering Google-style video using Remotion...")
    os.makedirs("out", exist_ok=True)
    # Direct shell execution prevents npx argument swallowing
    cmd = "npx remotion render src/index.ts ReelComposition out/reel_te.mp4"
    subprocess.run(cmd, shell=True, check=True)

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
        render_remotion_video()
    elif "--publish-only" in sys.argv:
        video_url = os.getenv("VIDEO_PUBLIC_URL")
        post_reel_to_meta(video_url)
