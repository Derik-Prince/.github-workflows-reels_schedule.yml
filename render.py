import os
import math
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from utils import run

W, H = 1080, 1920

def get_font(size, bold=True):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()

def create_product_showcase_cards(product, workdir):
    """Generates high-contrast UGC styled product cards like the reference reel"""
    workdir = Path(workdir)
    imgs = sorted(workdir.glob("img_*"))
    
    raw_img_path = imgs[0] if imgs else None
    if raw_img_path and raw_img_path.exists():
        try:
            pimg = Image.open(raw_img_path).convert("RGBA")
        except Exception:
            pimg = Image.new("RGBA", (600, 600), (255, 255, 255, 0))
    else:
        pimg = Image.new("RGBA", (600, 600), (255, 255, 255, 0))
        
    pimg.thumbnail((700, 700), Image.Resampling.LANCZOS)

    # 1. Main Floating Card with Product & Glowing Ring
    card1 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d1 = ImageDraw.Draw(card1)
    
    # Rounded Card Frame
    box_w, box_h = 820, 820
    bx, by = (W - box_w) // 2, 420
    d1.rounded_rectangle([bx, by, bx + box_w, by + box_h], radius=48, fill=(255, 255, 255, 245), outline=(0, 230, 118, 255), width=8)
    
    # Paste product in card center
    px = bx + (box_w - pimg.width) // 2
    py = by + (box_h - pimg.height) // 2
    card1.paste(pimg, (px, py), pimg)
    
    card1_path = workdir / "card_main.png"
    card1.save(card1_path)

    # 2. Price Tag Kinetic Card (Actual MRP with Strikethrough + Deal Price)
    card2 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d2 = ImageDraw.Draw(card2)
    
    curr_price = f"{product.get('currency', '₹')}{product.get('current_price', 999):,}"
    orig_price = f"{product.get('currency', '₹')}{product.get('original_price', 2999):,}"
    
    # MRP Tag
    f_sub = get_font(52, bold=False)
    f_price = get_font(96, bold=True)
    f_deal = get_font(110, bold=True)
    
    # "Actual Price"
    d2.rounded_rectangle([180, 240, 900, 360], radius=24, fill=(15, 15, 18, 220))
    d2.text((220, 270), "Actual Price:", font=f_sub, fill=(200, 200, 200))
    d2.text((580, 252), orig_price, font=f_price, fill=(255, 75, 75))
    # Red Strikethrough line
    d2.line([565, 310, 880, 310], fill=(255, 50, 50), width=8)

    # Big Deal Price Badge
    d2.rounded_rectangle([140, 1280, 940, 1470], radius=32, fill=(0, 230, 118, 255))
    d2.text((180, 1315), f"DEAL: {curr_price}*", font=f_deal, fill=(10, 20, 15))
    
    card2_path = workdir / "card_price.png"
    card2.save(card2_path)

    # 3. Dynamic Feature Badges & CTA
    card3 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d3 = ImageDraw.Draw(card3)
    
    kw = str(product.get("keyword", "DEAL")).upper()
    f_cta = get_font(58, bold=True)
    d3.rounded_rectangle([100, 1530, 980, 1690], radius=30, fill=(0, 0, 0, 230), outline=(255, 255, 255), width=4)
    d3.text((140, 1570), f"👉 COMMENT '{kw}' FOR LINK", font=f_cta, fill=(255, 255, 255))

    card3_path = workdir / "card_cta.png"
    card3.save(card3_path)

    return card1_path, card2_path, card3_path

def render(product, plan, voice, out, workdir):
    workdir = Path(workdir)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)

    print("Generating UGC kinetic graphics overlays...")
    card_main, card_price, card_cta = create_product_showcase_cards(product, workdir)

    # Background: Use studio video if downloaded, or dark gradient studio loop
    bg_video = workdir / "studio_bg.mp4"
    if bg_video.exists():
        bg_input = ["-stream_loop", "-1", "-i", str(bg_video)]
        bg_filter = "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=12:6[bg];"
    else:
        bg_input = ["-f", "lavfi", "-i", "color=c=#14171d:s=1080x1920:r=30"]
        bg_filter = "[0:v]null[bg];"

    print("Compositing smooth kinetic cuts and overlays via FFmpeg...")
    # Multi-layer composition matching UGC reel style
    filter_complex = (
        f"{bg_filter}"
        f"[1:v]scale=1080:1920[p_card];"
        f"[2:v]scale=1080:1920[p_price];"
        f"[3:v]scale=1080:1920[p_cta];"
        # Floating product entry with gentle spring scale
        f"[bg][p_card]overlay=x=0:y='if(lt(t,0.5), 1920, if(lt(t,1.2), 1920-(1920)*(sin((t-0.5)*2.24)), 0))'[v1];"
        # Actual price & deal price badges pop-up
        f"[v1][p_price]overlay=x=0:y=0:enable='gte(t,1.4)'[v2];"
        # CTA button pulsing from bottom
        f"[v2][p_cta]overlay=x=0:y=0:enable='gte(t,2.8)'[vout]"
    )

    cmd = [
        "ffmpeg", "-y",
        *bg_input,
        "-loop", "1", "-i", str(card_main),
        "-loop", "1", "-i", str(card_price),
        "-loop", "1", "-i", str(card_cta),
        "-i", str(voice),
        "-filter_complex", filter_complex,
        "-map", "[vout]",
        "-map", "4:a",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-preset", "faster",
        "-shortest",
        "-movflags", "+faststart",
        str(out)
    ]
    
    run(cmd)
    print("Kinetic UGC Tech Reel Render Completed:", out)
    return out
