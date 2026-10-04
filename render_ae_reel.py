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
    ColorClip, concatenate_videoclips
)

IG_USER_ID = (os.getenv("IG_USER_ID") or "17841417494301577").strip()
ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
PIXABAY_KEY = os.getenv("PIXABAY_API_KEY")

with open("active_deal.json", "r", encoding="utf-8") as f:
    PRODUCT = json.load(f)

target_input = os.getenv("TARGET_LANG")
if target_input in ["te", "hi", "en"]:
    ACTIVE_LANG = target_input
else:
    utc_hour = datetime.datetime.utcnow().hour
    if utc_hour == 1:
        ACTIVE_LANG = "te"
    elif utc_hour == 7:
        ACTIVE_LANG = "hi"
    elif utc_hour == 11:
        ACTIVE_LANG = "en"
    else:
        ACTIVE_LANG = "te"

TRIGGER_KEYWORD = PRODUCT.get("keyword", "DEAL").upper()

LANG_CONFIG = {
    "te": {
        "voice": "te-IN-MohanNeural",
        "font": "DejaVu-Sans-Bold",
        "rate": "+4%",
        "pitch": "+0Hz",
        "script": (
            f"గైస్, చెక్ దిస్ ఔట్! డీల్ ప్రైస్ కేవలం {PRODUCT['deal_price']} రూపాయలు! "
            f"ఇది నార్మల్ వాచ్ కాదు, సూపర్ ఆఫర్ ఇది! "
            f"మార్కెట్ లో యాక్చువల్ ప్రైస్ {PRODUCT['mrp']}, కానీ ఇప్పుడు భారీ ప్రైస్ డ్రాప్! "
            f"డిస్ప్లే చాలా బ్రైట్ గా ఉంది, స్మూత్ నెస్ సూపర్ ఉంది! "
            f"స్ట్రాప్ క్వాలిటీ మరియు బిల్డ్ కూడా ఇన్ క్రెడిబుల్ గా ఉంది. "
            f"డీల్ ప్రైస్ త్వరలోనే ఎండ్ అవుతుంది! ఇప్పుడే కింద కామెంట్స్ లో {TRIGGER_KEYWORD} అని టైప్ చేయండి, "
            f"డైరెక్ట్ బై లింక్ మీ ఇన్ బాక్స్ కి వస్తుంది!"
        ),
        "caption": (
            f"⚡ Guys, Check this out! Deal Price {PRODUCT['deal_price']} only!\n\n"
            f"🔥 Product: {PRODUCT['title']}\n"
            f"🏷️ MRP: {PRODUCT['mrp']}\n"
            f"💥 Deal Price: {PRODUCT['deal_price']} ({PRODUCT['discount']})\n\n"
            f"👉 Direct verified link kosam kindha \"{TRIGGER_KEYWORD}\" ani comment cheyyandi! Instant ga mee DM lo vasthundi! 📩\n\n"
            f"⚠️ (Legal Affiliate Disclosure: As an Amazon Associate, we earn from qualifying purchases at no extra cost to you.)\n\n"
            f"#ad #affiliate #telugureels #telugutech #smartwatch #amazonfinds #viralreels #explorepage #techdeals"
        )
    },
    "hi": {
        "voice": "hi-IN-MadhurNeural",
        "font": "DejaVu-Sans-Bold",
        "rate": "+5%",
        "pitch": "+0Hz",
        "script": (
            f"Dosto, check this out! Deal price sirf {PRODUCT['deal_price']} rupees! "
            f"Ye koi normal watch nahi, massive offer chal raha hai! "
            f"Market me iska actual price {PRODUCT['mrp']} hai, lekin abhi full discount! "
            f"Display kafi bright hai, smooth performance aur solid build quality! "
            f"Deal jaldi end hone wali hai! Abhi niche comment box me {TRIGGER_KEYWORD} comment kijiye, "
            f"direct loot link turant aapke DM me aa jayega!"
        ),
        "caption": (
            f"⚡ Guys, Check this out! Deal Price {PRODUCT['deal_price']} only!\n\n"
            f"🔥 Product: {PRODUCT['title']}\n"
            f"🏷️ MRP: {PRODUCT['mrp']}\n"
            f"💥 Deal Price: {PRODUCT['deal_price']} ({PRODUCT['discount']})\n\n"
            f"👉 Comment \"{TRIGGER_KEYWORD}\" below for direct link in your DM! 📩\n\n"
            f"⚠️ (Affiliate Disclosure: Paid partnership / As an affiliate partner, we earn from qualifying purchases.)\n\n"
            f"#ad #affiliate #techdeals #smartwatch #amazonfinds #viralreels #explorepage #reelsindia"
        )
    },
    "en": {
        "voice": "en-IN-PrabhatNeural",
        "font": "DejaVu-Sans-Bold",
        "rate": "+6%",
        "pitch": "+0Hz",
        "script": (
            f"Guys, check this out! Deal price is just {PRODUCT['deal_price']}! "
            f"This is not a regular watch, this is an incredible deal! "
            f"Actual price is {PRODUCT['mrp']}, but right now it is heavily discounted! "
            f"The display is super bright, touch smoothness is great, and strap quality feels premium! "
            f"Deal price ends soon! Comment {TRIGGER_KEYWORD} right below, "
            f"and we will drop the direct official link straight to your inbox!"
        ),
        "caption": (
            f"⚡ Guys, Check this out! Deal Price {PRODUCT['deal_price']} only!\n\n"
            f"🔥 Product: {PRODUCT['title']}\n"
            f"🏷️ MRP: {PRODUCT['mrp']}\n"
            f"💥 Deal Price: {PRODUCT['deal_price']} ({PRODUCT['discount']})\n\n"
            f"👉 Comment \"{TRIGGER_KEYWORD}\" below for the direct link! 📩\n\n"
            f"⚠️ (Affiliate Disclosure: As an affiliate partner, we earn from qualifying purchases at no additional cost to you.)\n\n"
            f"#ad #affiliate #stealdeals #techtrends #amazonfinds #viral #explorepage #instareels"
        )
    }
}

def download_file(url, save_path):
    cmd = [
        "curl", "-L", "-A",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "-o", save_path, url
    ]
    subprocess.run(cmd, check=True)

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
    download_file(video_url, save_path)

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

async def generate_voiceover(text, voice_name, rate, pitch, output_path):
    communicate = edge_tts.Communicate(text, voice_name, rate=rate, pitch=pitch)
    await communicate.save(output_path)

def build_pro_creator_reel(lang, audio_path, host_vid, broll_vid, output_video):
    cfg = LANG_CONFIG[lang]
    audio = AudioFileClip(audio_path)
    total_duration = audio.duration

    # 1. Multi-Cut Architecture: Host Intro (0-3.5s) -> B-Roll Middle -> Host Outro (Last 5s)
    intro_dur = min(3.5, total_duration * 0.25)
    outro_dur = min(5.0, total_duration * 0.30)
    broll_dur = max(1.0, total_duration - intro_dur - outro_dur)

    try:
        host_clip = VideoFileClip(host_vid)
        broll_clip = VideoFileClip(broll_vid)

        if host_clip.duration < (intro_dur + outro_dur):
            host_clip = concatenate_videoclips([host_clip] * 3)
        if broll_clip.duration < broll_dur:
            broll_clip = concatenate_videoclips([broll_clip] * 3)

        clip_intro = crop_to_vertical(host_clip.subclip(0, intro_dur))
        clip_broll = crop_to_vertical(broll_clip.subclip(0, broll_dur))
        clip_outro = crop_to_vertical(host_clip.subclip(intro_dur, intro_dur + outro_dur))

        merged_background = concatenate_videoclips([clip_intro, clip_broll, clip_outro]).set_duration(total_duration)
    except Exception as e:
        print(f"Fallback video stitching: {e}")
        merged_background = ColorClip(size=(1080, 1920), color=(18, 18, 22), duration=total_duration)

    # 2. Authentic Creator Minimal Overlays (Just like reference video)
    # Price Tag Reveal (Appears during B-Roll section)
    price_box_text = TextClip(
        f"Actual price\n{PRODUCT.get('mrp', '₹1,999*!')}",
        fontsize=64,
        color='white',
        font='DejaVu-Sans-Bold',
        stroke_color='black',
        stroke_width=2,
        align='center'
    ).set_start(intro_dur + 0.2).set_duration(3.5).set_position(('center', 620))

    deal_badge = TextClip(
        f"DEAL: {PRODUCT.get('deal_price', '₹999')}",
        fontsize=72,
        color='#00FF66',
        font='DejaVu-Sans-Bold',
        stroke_color='black',
        stroke_width=3,
        align='center'
    ).set_start(intro_dur + 3.8).set_duration(broll_dur - 3.8 if broll_dur > 4 else 2).set_position(('center', 620))

    # Outro Clean Action Text (Minimal Creator Style)
    cta_clean = TextClip(
        f"COMMENT '{TRIGGER_KEYWORD}'\nFOR LINK",
        fontsize=58,
        color='white',
        font='DejaVu-Sans-Bold',
        stroke_color='black',
        stroke_width=3,
        align='center'
    ).set_start(total_duration - outro_dur).set_duration(outro_dur).set_position(('center', 1450))

    # Bottom Right Creator Channel Tag
    handle_tag = TextClip(
        "@LootDealsOfficial",
        fontsize=32,
        color='white',
        font='DejaVu-Sans-Bold',
        stroke_color='black',
        stroke_width=2
    ).set_duration(total_duration).set_position((720, 1820))

    final_video = CompositeVideoClip([
        merged_background,
        price_box_text,
        deal_badge,
        cta_clean,
        handle_tag
    ], size=(1080, 1920)).set_duration(total_duration)

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
    
    print("🎉 SUCCESS! Pro-Creator Style Reel is Live! Post ID:", pub.get("id"))

async def render_flow():
    with open("current_lang.txt", "w") as f:
        f.write(ACTIVE_LANG)
        
    audio_file = f"audio_{ACTIVE_LANG}.mp3"
    host_vid = "host_reviewer.mp4"
    broll_vid = "product_broll.mp4"
    video_file = f"reel_{ACTIVE_LANG}.mp4"

    # High-quality verified reviewer human footage & product closeups
    host_fallback = "https://assets.mixkit.co/videos/preview/mixkit-young-man-talking-to-camera-in-a-studio-42686-large.mp4"
    broll_fallback = "https://assets.mixkit.co/videos/preview/mixkit-smartwatch-on-a-mans-wrist-touching-the-screen-41312-large.mp4"

    fetch_pixabay_video("man tech presenter studio", host_vid, host_fallback)
    fetch_pixabay_video(PRODUCT.get("keyword", "smartwatch") + " close up", broll_vid, broll_fallback)
    
    cfg = LANG_CONFIG[ACTIVE_LANG]
    await generate_voiceover(cfg["script"], cfg["voice"], cfg["rate"], cfg["pitch"], audio_file)
    build_pro_creator_reel(ACTIVE_LANG, audio_file, host_vid, broll_vid, video_file)

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
