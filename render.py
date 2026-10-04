import os
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

def create_google_motion_overlays(product, workdir):
    workdir = Path(workdir)
    imgs = sorted(workdir.glob("img_*"))
    
    # 1. Floating Product Card
    if imgs and imgs[0].exists():
        try:
            pimg = Image.open(imgs[0]).convert("RGBA")
        except Exception:
            pimg = Image.new("RGBA", (500, 500), (255, 255, 255, 0))
    else:
        pimg = Image.new("RGBA", (500, 500), (255, 255, 255, 0))

    pimg.thumbnail((680, 680), Image.Resampling.LANCZOS)

    card_canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(card_canvas)

    # Frosted Glossy Card
    cw, ch = 840, 840
    cx, cy = (W - cw) // 2, 420
    d.rounded_rectangle([cx, cy, cx + cw, cy + ch], radius=50, fill=(255, 255, 255, 246), outline=(0, 230, 118, 255), width=8)

    # Center product
    px = cx + (cw - pimg.width) // 2
    py = cy + (ch - pimg.height) // 2
    card_canvas.paste(pimg, (px, py), pimg)
    card_path = workdir / "layer_card.png"
    card_canvas.save(card_path)

    # 2. Price Animation Layer (MRP Cut + Deal Banner)
    price_canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dp = ImageDraw.Draw(price_canvas)

    curr_p = f"{product.get('currency', '₹')}{product.get('current_price', 999):,}"
    orig_p = f"{product.get('currency', '₹')}{product.get('original_price', 2499):,}"
    disc = f"{product.get('discount_percent', 50)}% OFF"

    f_label = get_font(48, bold=False)
    f_orig = get_font(84, bold=True)
    f_deal = get_font(104, bold=True)

    # Top MRP badge
    dp.rounded_rectangle([180, 220, 900, 360], radius=24, fill=(15, 18, 22, 230))
    dp.text((220, 255), "Actual Price:", font=f_label, fill=(200, 200, 200))
    dp.text((560, 240), orig_p, font=f_orig, fill=(255, 80, 80))
    dp.line([540, 298, 880, 298], fill=(255, 60, 60), width=8)

    # Big Deal Price Banner
    dp.rounded_rectangle([140, 1280, 940, 1460], radius=32, fill=(0, 230, 118, 255))
    dp.text((180, 1315), f"DEAL: {curr_p}* ({disc})", font=f_deal, fill=(10, 24, 15))
    price_path = workdir / "layer_price.png"
    price_canvas.save(price_path)

    # 3. Features & Dynamic CTA Layer
    cta_canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dc = ImageDraw.Draw(cta_canvas)

    kw = str(product.get("keyword", "DEAL")).upper()
    f_cta = get_font(58, bold=True)
    f_feat = get_font(42, bold=True)

    features = product.get("features", [])
    if features:
        feat_text = " • ".join(features[:2])
        dc.rounded_rectangle([120, 1490, 960, 1570], radius=20, fill=(30, 35, 45, 230))
        dc.text((150, 1508), feat_text, font=f_feat, fill=(0, 230, 118))

    dc.rounded_rectangle([100, 1610, 980, 1760], radius=30, fill=(0, 0, 0, 245), outline=(255, 255, 255), width=5)
    dc.text((140, 1650), f"👉 COMMENT '{kw}' FOR DIRECT LINK", font=f_cta, fill=(255, 255, 255))
    cta_path = workdir / "layer_cta.png"
    cta_canvas.save(cta_path)

    return card_path, price_path, cta_path

def render(product, plan, voice, out, workdir):
    workdir = Path(workdir)
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)

    card_p, price_p, cta_p = create_google_motion_overlays(product, workdir)

    bg_video = workdir / "category_bg.mp4"
    if bg_video.exists():
        bg_input = ["-stream_loop", "-1", "-i", str(bg_video)]
        bg_filter = "[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=10:5[bg];"
    else:
        bg_input = ["-f", "lavfi", "-i", "color=c=#0f131a:s=1080x1920:r=30"]
        bg_filter = "[0:v]null[bg];"

    filter_complex = (
        f"{bg_filter}"
        f"[1:v]scale=1080:1920[p_card];"
        f"[2:v]scale=1080:1920[p_price];"
        f"[3:v]scale=1080:1920[p_cta];"
        # Smooth bounce slide-up for product card
        f"[bg][p_card]overlay=x=0:y='if(lt(t,0.4), 1920, if(lt(t,1.2), 1920-(1920)*(sin((t-0.4)*1.96)), 0))'[v1];"
        # Strikethrough Price tag appears at 1.4s
        f"[v1][p_price]overlay=x=0:y=0:enable='gte(t,1.4)'[v2];"
        # CTA and features appear at 2.6s
        f"[v2][p_cta]overlay=x=0:y=0:enable='gte(t,2.6)'[vout]"
    )

    cmd = [
        "ffmpeg", "-y",
        *bg_input,
        "-loop", "1", "-i", str(card_p),
        "-loop", "1", "-i", str(price_p),
        "-loop", "1", "-i", str(cta_p),
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
    print("Google-style dynamic UGC reel ready:", out)
    return out
