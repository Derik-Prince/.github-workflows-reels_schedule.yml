import os
import sys
import time
import json
import subprocess
import requests
import whisper
from PIL import Image, ImageDraw, ImageOps
from moviepy.editor import (
    VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip,
    ImageClip, ColorClip, concatenate_videoclips
)

IG_USER_ID = (os.getenv("IG_USER_ID") or "17841417494301577").strip()
ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
PIXABAY_KEY = os.getenv("PIXABAY_API_KEY")
ELEVEN_KEY = os.getenv("ELEVENLABS_API_KEY")

with open("active_deal.json", "r", encoding="utf-8") as f:
    PRODUCT = json.load(f)

target_input = os.getenv("TARGET_LANG")
ACTIVE_LANG = target_input if target_input in ["te", "hi", "en"] else "te"
TRIGGER_KEYWORD = PRODUCT.get("keyword", "DEAL").upper()

VOICE_SCRIPTS = {
    "te": {
        "voice_id": "pNInz6obpgDQGcFmaJgB",
        "script": (
            f"Brooo! Check this out! Deal price కేవలం {PRODUCT.get('deal_price', '₹999')} మాత్రమే! "
            f"Wait wait wait, ఇది regular watch కాదు భయ్యా, క్రేజీ స్టీల్ ఆఫర్! "
            f"మార్కెట్ లో {PRODUCT.get('mrp', '₹2,999')} ఉండేది, ఇవాళ డైరెక్ట్ {PRODUCT.get('discount', '60% OFF')} డ్రాప్! "
            f"డిస్ప్లే super bright ఉంది, touch insanely smooth! "
            f"ఈ ప్రైస్ డ్రాప్ లిమిటెడ్ టైమ్ మాత్రమే. కింద కామెంట్స్ లో {TRIGGER_KEYWORD} అని టైప్ చేయండి, "
            f"డైరెక్ట్ బై లింక్ ఇన్స్టంట్ గా మీ ఇన్ బాక్స్ కి వస్తుంది!"
        ),
        "caption": (
            f"⚡ Bro, Check this out! Deal Price {PRODUCT.get('deal_price', '₹999')} only!\n\n"
            f"🔥 Product: {PRODUCT.get('title', 'Smartwatch')}\n"
            f"🏷️ MRP: {PRODUCT.get('mrp', '₹2,999')}\n"
            f"💥 Deal Price: {PRODUCT.get('deal_price', '₹999')} ({PRODUCT.get('discount', 'Special Offer')})\n\n"
            f"👉 Direct verified link kosam kindha \"{TRIGGER_KEYWORD}\" ani comment cheyyandi! Instant ga mee DM lo vasthundi! 📩\n\n"
            f"⚠️ (Legal Affiliate Disclosure: As an Amazon Associate, we earn from qualifying purchases at no extra cost to you.)\n\n"
            f"#ad #affiliate #telugutech #amazondeals #smartwatch #reelsindia #lootdeals"
        )
    },
    "en": {
        "voice_id": "pNInz6obpgDQGcFmaJgB",
        "script": (
            f"Bro, check this out right now! Deal price is just {PRODUCT.get('deal_price', '₹999')}! "
            f"Wait, this is an absolute steal deal! "
            f"Original price was {PRODUCT.get('mrp', '₹2,999')}, but today we have a massive {PRODUCT.get('discount', '60% OFF')} price drop! "
            f"Super bright display and premium build! "
            f"Deal ends soon! Comment {TRIGGER_KEYWORD} below for direct official link straight to your DM!"
        ),
        "caption": f"⚡ Steal Deal: {PRODUCT.get('title', 'Smartwatch')} at {PRODUCT.get('deal_price', '₹999')}! Comment {TRIGGER_KEYWORD} for link."
    }
}

def generate_elevenlabs_voice(text, voice_id, output_path):
    print("Generating energetic voice via ElevenLabs...")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVEN_KEY
    }
    data = {
        "text": text,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.28,
            "similarity_boost": 0.80,
            "style": 0.58,
            "use_speaker_boost": True
        }
    }
    res = requests.post(url, json=data, headers=headers)
    if res.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(res.content)
        print("ElevenLabs voice generated!")
    else:
        print(f"ElevenLabs error ({res.status_code}), falling back to edge-tts.")
        subprocess.run(["edge-tts", "--voice", "te-IN-MohanNeural", "--text", text, "--write-media", output_path], check=True)

def get_word_timestamps(audio_path):
    print("Running Whisper for accurate word sync...")
    model = whisper.load_model("tiny")
    result = model.transcribe(audio_path, word_timestamps=True)
    words = []
    for segment in result.get("segments", []):
        for w in segment.get("words", []):
            words.append({
                "word": w.get("word", "").strip(),
                "start": w.get("start", 0.0),
                "end": w.get("end", 0.0)
            })
    return words

def fetch_presenter_video(save_path):
    # Fetch clean young influencer / creator talking clip
    video_url = None
    if PIXABAY_KEY:
        try:
            url = f"https://pixabay.com/api/videos/?key={PIXABAY_KEY}&q=young+man+talking+camera+blogger&video_type=film&per_page=6"
            res = requests.get(url, timeout=15).json()
            hits = res.get("hits", [])
            if hits:
                videos_obj = hits[0].get("videos", {})
                for q in ["large", "medium", "small"]:
                    if q in videos_obj and videos_obj[q].get("url"):
                        video_url = videos_obj[q]["url"]
                        break
        except Exception as e:
            print(f"Pixabay fetch error: {e}")
    if not video_url:
        video_url = "https://assets.mixkit.co/videos/preview/mixkit-young-man-talking-to-camera-in-a-studio-42686-large.mp4"
    subprocess.run(["curl", "-L", "-A", "Mozilla/5.0", "-o", save_path, video_url], check=True)

def prepare_product_card(image_url, save_path):
    try:
        raw_img_path = "raw_product.jpg"
        subprocess.run(["curl", "-L", "-A", "Mozilla/5.0", "-o", raw_img_path, image_url], check=True)
        img = Image.open(raw_img_path).convert("RGBA")
        
        # Resize maintaining aspect ratio to fit 480x480 box
        img.thumbnail((440, 440), Image.Resampling.LANCZOS)
        
        # Card canvas with rounded corners and white glossy background
        card_w, card_h = 520, 520
        card = Image.new("RGBA", (card_w, card_h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(card)
        
        # Rounded white background card
        draw.rounded_rectangle([0, 0, card_w, card_h], radius=32, fill=(255, 255, 255, 245), outline=(0, 255, 102, 255), width=6)
        
        # Paste centered image
        offset_x = (card_w - img.width) // 2
        offset_y = (card_h - img.height) // 2
        card.paste(img, (offset_x, offset_y), img)
        card.save(save_path, "PNG")
        return True
    except Exception as e:
        print(f"Product card error: {e}")
        return False

def crop_to_vertical(clip):
    w, h = clip.size
    target_aspect = 1080 / 1920
    if (w / h) > target_aspect:
        new_w = int(h * target_aspect)
        cropped = clip.crop(x1=(w - new_w)/2, x2=(w + new_w)/2, y1=0, y2=h)
    else:
        new_h = int(w / target_aspect)
        cropped = clip.crop(y1=(h - new_h)/2, y2=(h + new_h)/2, x1=0, x2=w)
    return cropped.resize((1080, 1920))

def build_ugc_product_reel(audio_path, host_vid, product_card_path, output_video):
    audio = AudioFileClip(audio_path)
    total_dur = audio.duration

    try:
        host = VideoFileClip(host_vid)
        while host.duration < total_dur:
            host = concatenate_videoclips([host, host])
        bg = crop_to_vertical(host.subclip(0, total_dur))
    except Exception as e:
        print(f"Fallback canvas: {e}")
        bg = ColorClip(size=(1080, 1920), color=(18, 18, 24), duration=total_dur)

    overlay_clips = [bg]

    # Amazon Product Floating Card (Visible throughout product explanation)
    card_start = 2.0
    card_dur = max(3.0, total_dur - card_start - 3.0)
    if os.path.exists(product_card_path):
        product_clip = (
            ImageClip(product_card_path)
            .set_start(card_start)
            .set_duration(card_dur)
            .set_position(('center', 240))
        )
        overlay_clips.append(product_clip)

    # Dynamic Price Badges
    deal_tag = TextClip(
        f"DEAL: {PRODUCT.get('deal_price', '₹999')}  ({PRODUCT.get('discount', '60% OFF')})",
        fontsize=62,
        color='#00FF66',
        font='DejaVu-Sans-Bold',
        stroke_color='black',
        stroke_width=4
    ).set_start(card_start).set_duration(card_dur).set_position(('center', 800))
    overlay_clips.append(deal_tag)

    mrp_tag = TextClip(
        f"MRP: {PRODUCT.get('mrp', '₹2,999')}",
        fontsize=46,
        color='#FF4444',
        font='DejaVu-Sans-Bold',
        stroke_color='black',
        stroke_width=2
    ).set_start(card_start).set_duration(card_dur).set_position(('center', 880))
    overlay_clips.append(mrp_tag)

    # Kinetic Synced Subtitles (Whisper AI)
    word_data = get_word_timestamps(audio_path)
    grouped = []
    for i in range(0, len(word_data), 3):
        group = word_data[i:i+3]
        if group:
            grouped.append({
                "text": " ".join([w["word"] for w in group]),
                "start": group[0]["start"],
                "end": group[-1]["end"]
            })

    for item in grouped:
        st = item["start"]
        dur = max(0.3, item["end"] - item["start"])
        if st + dur > total_dur:
            dur = total_dur - st
        if dur <= 0:
            continue

        txt = TextClip(
            item["text"],
            fontsize=56,
            color='yellow',
            font='DejaVu-Sans-Bold',
            stroke_color='black',
            stroke_width=3,
            size=(960, 180),
            method='caption'
        ).set_start(st).set_duration(dur).set_position(('center', 1380))
        overlay_clips.append(txt)

    # Outro Call to Action
    cta_clip = TextClip(
        f"COMMENT '{TRIGGER_KEYWORD}'\nFOR DIRECT LINK",
        fontsize=64,
        color='white',
        font='DejaVu-Sans-Bold',
        stroke_color='black',
        stroke_width=4,
        align='center'
    ).set_start(max(0, total_dur - 4.5)).set_duration(4.5).set_position(('center', 1150))
    overlay_clips.append(cta_clip)

    final = CompositeVideoClip(overlay_clips, size=(1080, 1920)).set_duration(total_dur)
    final = final.set_audio(audio)
    final.write_videofile(output_video, fps=30, codec="libx264", audio_codec="aac", threads=4, preset="fast")

def post_reel_to_meta(video_url, caption):
    base_url = f"https://graph.facebook.com/v26.0/{IG_USER_ID}"
    res = requests.post(f"{base_url}/media", data={
        "media_type": "REELS",
        "video_url": video_url,
        "caption": caption,
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
    print("🎉 SUCCESS! Pro UGC Reel is Live! ID:", pub.get("id"))

def render_flow():
    with open("current_lang.txt", "w") as f:
        f.write(ACTIVE_LANG)
        
    audio_file = f"audio_{ACTIVE_LANG}.mp3"
    host_vid = "host_creator.mp4"
    product_card = "product_card.png"
    video_file = f"reel_{ACTIVE_LANG}.mp4"

    cfg = VOICE_SCRIPTS.get(ACTIVE_LANG, VOICE_SCRIPTS["te"])
    generate_elevenlabs_voice(cfg["script"], cfg["voice_id"], audio_file)

    fetch_presenter_video(host_vid)

    image_url = PRODUCT.get("image_url") or "https://m.media-amazon.com/images/I/61SSVxTSs3L._SL1500_.jpg"
    prepare_product_card(image_url, product_card)

    build_ugc_product_reel(audio_file, host_vid, product_card, video_file)

def publish_flow():
    with open("current_lang.txt", "r") as f:
        lang = f.read().strip()
    video_url = os.getenv("VIDEO_PUBLIC_URL")
    caption = VOICE_SCRIPTS.get(lang, VOICE_SCRIPTS["te"])["caption"]
    post_reel_to_meta(video_url, caption)

if __name__ == "__main__":
    if "--render-only" in sys.argv:
        render_flow()
    elif "--publish-only" in sys.argv:
        publish_flow()
