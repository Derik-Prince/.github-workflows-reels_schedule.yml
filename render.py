from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import subprocess, math, os
from .utils import run

W,H=720,1280

def font(size, bold=False):
    candidates=[]
    if bold: candidates += ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]
    candidates += ["/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for p in candidates:
        if os.path.exists(p): return ImageFont.truetype(p,size)
    return ImageFont.load_default()

def card(text, path, accent=False):
    im=Image.new("RGB",(W,H),(22,22,24)); d=ImageDraw.Draw(im)
    # simple premium studio-style gradient approximation
    for y in range(H):
        c=int(22+30*y/H); d.line((0,y,W,y),fill=(c,c,c+4))
    f=font(52,True)
    words=text.split(); lines=[]; line=""
    for word in words:
        test=(line+" "+word).strip()
        if d.textbbox((0,0),test,font=f)[2] > 610 and line:
            lines.append(line); line=word
        else: line=test
    if line: lines.append(line)
    total=len(lines)*68; y=(H-total)//2
    for line in lines:
        box=d.textbbox((0,0),line,font=f); tw=box[2]
        x=(W-tw)//2
        d.rounded_rectangle((x-22,y-10,x+tw+22,y+55),radius=16,fill=(255,255,255))
        d.text((x,y),line,font=f,fill=(15,15,15)); y+=68
    im.save(path,quality=92)

def prepare_visuals(product, workdir):
    # If supplied images exist, use them. Otherwise generate clean text cards so the pipeline still runs.
    imgs=sorted(Path(workdir).glob("img_*"))
    if not imgs:
        p=Path(workdir)/"fallback.jpg"; card(product["title"],p); imgs=[p]
    return imgs

def make_segment(image, out, duration, motion=1):
    # Scale/crop to 720x1280, with a subtle zoom-in.
    frames=max(1,int(duration*30)); zoom0=1.0; zoom1=1.08 if motion else 1.0
    vf=(f"scale=720:1280:force_original_aspect_ratio=increase,crop=720:1280,"
        f"zoompan=z='min({zoom0}+({zoom1}-{zoom0})*on/{frames}, {zoom1})':d=1:s=720x1280:fps=30")
    run(["ffmpeg","-y","-loop","1","-i",str(image),"-t",str(duration),"-vf",vf,"-an","-c:v","libx264","-pix_fmt","yuv420p",str(out)])

def render(product, plan, voice, out, workdir):
    workdir=Path(workdir); out=Path(out); out.parent.mkdir(parents=True,exist_ok=True)
    imgs=prepare_visuals(product,workdir)
    segments=[]
    for i,s in enumerate(plan["scenes"]):
        p=workdir/f"seg_{i}.mp4"
        base=imgs[i % len(imgs)]
        make_segment(base,p,float(s.get("duration",3)))
        # overlay scene text; use drawtext and escape basic punctuation
        text=str(s.get("text","")).replace("'","\\'").replace(":","\\:")
        overlay=workdir/f"seg_text_{i}.mp4"
        vf=f"drawtext=text='{text}':fontcolor=white:fontsize=34:box=1:boxcolor=black@0.70:boxborderw=18:x=(w-text_w)/2:y=h-260"
        run(["ffmpeg","-y","-i",str(p),"-vf",vf,"-c:v","libx264","-pix_fmt","yuv420p","-an",str(overlay)])
        segments.append(overlay)
    concat=workdir/"concat.txt"
    concat.write_text("".join(f"file '{p.resolve()}'\n" for p in segments),encoding="utf-8")
    silent=workdir/"silent.mp4"
    run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(concat),"-c","copy",str(silent)])
    run(["ffmpeg","-y","-i",str(silent),"-i",str(voice),"-map","0:v:0","-map","1:a:0","-shortest","-c:v","copy","-c:a","aac","-b:a","128k","-movflags","+faststart",str(out)])
    return out
