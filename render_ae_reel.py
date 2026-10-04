import os
import sys
import time
import json
import subprocess
import requests
import whisper
from moviepy.editor import (
    VideoFileClip, AudioFileClip, CompositeVideoClip, TextClip,
    ColorClip, concatenate_videoclips
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
        "voice_id": "pNInz6obpgDQGcFmaJgB", # High-energy natural conversational voice
        "script": (
            f"Guys! Check this out! Deal price కేవలం {PRODUCT['deal_price']} మాత్రమే! "
            f"ఇది నార్మల్ వాచ్ కాదు! యాక్చువల్ ప్రైస్ {PRODUCT['mrp']}, కానీ ఇవాళ క్రేజీ ప్రైస్ డ్రాప్! "
            f"డిస్ప్లే చాలా బ్రైట్ గా ఉంది, టచ్ స్మూత్ గా ఉంది! "
            f"డీల్ ప్రైస్ త్వరలోనే ఎండ్ అవుతుంది. కామెంట్స్ లో {TRIGGER_KEYWORD} అని టైప్ చేయండి, "
            f"డైరెక్ట్ బై లింక్ మీ ఇన్ బాక్స్ కి వస్తుంది!"
        ),
        "caption": (
            f"⚡ Guys, Check this out! Deal Price {PRODUCT['deal_price']} only!\n\n"
            f"🔥 Product: {PRODUCT['title']}\n"
            f"🏷️ Actual Price: {PRODUCT['mrp']}\n"
            f"💥 Deal Price: {PRODUCT['deal_price']} ({PRODUCT['discount']})\n\n"
            f"👉 Direct verified link kosam kindha \"{TRIGGER_KEYWORD}\" ani comment cheyyandi! Instant ga mee DM lo vasthundi! 📩\n\n"
            f"#ad #affiliate #telugutech #smartwatch #amazonfinds #reelsindia"
        )
    },
    "en": {
        "voice_id": "pNInz6obpgDQGcFmaJgB",
        "script": (
            f"Guys, check this out! Deal price is just {PRODUCT['deal_price']}! "
            f"This is not a regular watch, original price is {PRODUCT['mrp']}, but right now it's heavily discounted! "
            f"The display is super bright and touch is smooth! "
            f"Deal ends soon! Comment {TRIGGER_KEYWORD} right below for the direct link!"
        ),
        "caption": f"Deal Alert: {PRODUCT['title']} at {PRODUCT['deal_price']}! Comment {TRIGGER_KEYWORD} for link."
    }
}

def generate_elevenlabs_voice(text, voice_id, output_path):
    print("Generating ultra-human voice via ElevenLabs...")
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
            "stability": 0.45,
            "similarity_boost": 0.85,
            "style": 0.35,
            "use_speaker_boost": True
        }
    }
    res = requests.post(url, json=data, headers=headers)
    if res.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(res.content)
        print("ElevenLabs voice generated successfully!")
    else:
        print(f"ElevenLabs error ({res.status_code}): {res.text}. Falling back to edge-tts.")
        subprocess.run(["edge-tts", "--voice", "te-IN-MohanNeural", "--text", text, "--write-media", output_path], check=True)

def get_word_timestamps(audio_path):
    print("Transcribing with Whisper for millisecond word-sync...")
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

def fetch_pixabay_video(query, save_path, fallback_url):
    video_url = None
    if PIXABAY_KEY:
        try:
            url = f"https://pixabay.com/api/videos/?key={PIXABAY_KEY}&q={requests.utils.quote(query)}&video_type=film&per_page=5"
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
        video_url = fallback_url
    subprocess.run(["curl", "-L", "-A", "Mozilla/5.0", "-o", save_path, video_url], check=True)

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

def build_pro_synced_reel(audio_path, host_vid, broll_vid, output_video):
    audio = AudioFileClip(audio_path)
    total_dur = audio.duration

    intro_dur = min(3.2, total_dur * 0.25)
    outro_dur = min(4.5, total_dur * 0.28)
    broll_dur = max(1.0, total_dur - intro_dur - outro_dur)

    try:
        host = VideoFileClip(host_vid)
        broll = VideoFileClip(broll_vid)
        if host.duration < (intro_dur + outro_dur):
            host = concatenate_videoclips([host] * 3)
        if broll.duration < broll_dur:
            broll = concatenate_videoclips([broll] * 3)

        c1 = crop_to_vertical(host.subclip(0, intro_dur))
        c2 = crop_to_vertical(broll.subclip(0, broll_dur))
        c3 = crop_to_vertical(host.subclip(intro_dur, intro_dur + outro_dur))
        merged_bg = concatenate_videoclips([c1, c2, c3]).set_duration(total_dur)
    except Exception as e:
        print(f"Fallback bg: {e}")
        merged_bg = ColorClip(size=(1080, 1920), color=(18, 18, 22), duration=total_dur)

    # Word-by-word synced kinetic subtitles
    word_data = get_word_timestamps(audio_path)
    caption_clips = []
    
    # Group words into 3-word dynamic punches
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
            fontsize=52,
            color='white',
            font='DejaVu-Sans-Bold',
            stroke_color='black',
            stroke_width=3,
            size=(960, 160),
            method='caption'
        ).set_start(st).set_duration(dur).set_position(('center', 1350))
        caption_clips.append(txt)

    # Price graphic matching creator style
    price_tag = TextClip(
        f"Actual price\n{PRODUCT.get('mrp', '₹1,999*!')}",
        fontsize=64,
        color='white',
        font='DejaVu-Sans-Bold',
        stroke_color='black',
        stroke_width=2,
        align='center'
    ).set_start(intro_dur + 0.1).set_duration(3.2).set_position(('center', 600))

    deal_badge = TextClip(
        f"DEAL: {PRODUCT.get('deal_price', '₹999')}",
        fontsize=74,
        color='#00FF66',
        font='DejaVu-Sans-Bold',
        stroke_color='black',
        stroke_width=3,
        align='center'
    ).set_start(intro_dur + 3.4).set_duration(max(1.5, broll_dur - 3.4)).set_position(('center', 600))

    cta_clean = TextClip(
        f"COMMENT '{TRIGGER_KEYWORD}'\nFOR LINK",
        fontsize=58,
        color='white',
        font='DejaVu-Sans-Bold',
        stroke_color='black',
        stroke_width=3,
        align='center'
    ).set_start(total_dur - outro_dur).set_duration(outro_dur).set_position(('center', 1450))

    final = CompositeVideoClip([
        merged_bg,
        *caption_clips,
        price_tag,
        deal_badge,
        cta_clean
    ], size=(1080, 1920)).set_duration(total_dur)

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
    print("🎉 SUCCESS! Pro-Creator Synced Reel is Live! ID:", pub.get("id"))

def render_flow():
    with open("current_lang.txt", "w") as f:
        f.write(ACTIVE_LANG)
        
    audio_file = f"audio_{ACTIVE_LANG}.mp3"
    host_vid = "host_reviewer.mp4"
    broll_vid = "product_broll.mp4"
    video_file = f"reel_{ACTIVE_LANG}.mp4"

    cfg = VOICE_SCRIPTS.get(ACTIVE_LANG, VOICE_SCRIPTS["te"])
    generate_elevenlabs_voice(cfg["script"], cfg["voice_id"], audio_file)

    host_fb = "https://assets.mixkit.co/videos/preview/mixkit-young-man-talking-to-camera-in-a-studio-42686-large.mp4"
    broll_fb = "https://assets.mixkit.co/videos/preview/mixkit-smartwatch-on-a-mans-wrist-touching-the-screen-41312-large.mp4"
    fetch_pixabay_video("man reviewer studio", host_vid, host_fb)
    fetch_pixabay_video(PRODUCT.get("keyword", "smartwatch") + " close up", broll_vid, broll_fb)

    build_pro_synced_reel(audio_file, host_vid, broll_vid, video_file)

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
