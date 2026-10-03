import os
import json
import random
import requests
from bs4 import BeautifulSoup

# Fallback verified high-converting viral catalog
CURATED_DEALS = [
    {
        "keyword": "WATCH",
        "title": "Noise ColorFit Pulse 2 Max Smartwatch",
        "mrp": "₹5,999",
        "deal_price": "₹1,299",
        "discount": "78% OFF",
        "video_url": "https://assets.mixkit.co/videos/preview/mixkit-smartwatch-on-a-mans-wrist-touching-the-screen-41312-large.mp4",
        "affiliate_tag": "affil_watch"
    },
    {
        "keyword": "BUDS",
        "title": "boAt Airdopes 141 ANC Earbuds",
        "mrp": "₹4,490",
        "deal_price": "₹999",
        "discount": "77% OFF",
        "video_url": "https://assets.mixkit.co/videos/preview/mixkit-hands-holding-a-pair-of-wireless-earphones-41584-large.mp4",
        "affiliate_tag": "affil_buds"
    },
    {
        "keyword": "POWER",
        "title": "Ambrane 20000mAh Ultra-Fast Power Bank",
        "mrp": "₹2,999",
        "deal_price": "₹1,199",
        "discount": "60% OFF",
        "video_url": "https://assets.mixkit.co/videos/preview/mixkit-man-charging-his-smartphone-with-a-powerbank-41580-large.mp4",
        "affiliate_tag": "affil_power"
    },
    {
        "keyword": "SPEAKER",
        "title": "Zebronics RGB Wireless Bluetooth Speaker",
        "mrp": "₹1,999",
        "deal_price": "₹699",
        "discount": "65% OFF",
        "video_url": "https://assets.mixkit.co/videos/preview/mixkit-top-shot-of-a-dj-controlling-music-equipment-42354-large.mp4",
        "affiliate_tag": "affil_speaker"
    },
    {
        "keyword": "LIGHT",
        "title": "Smart RGB Ambient Corner Floor Lamp",
        "mrp": "₹3,499",
        "deal_price": "₹999",
        "discount": "71% OFF",
        "video_url": "https://assets.mixkit.co/videos/preview/mixkit-multicolored-lights-moving-in-the-dark-41712-large.mp4",
        "affiliate_tag": "affil_light"
    }
]

def fetch_or_rotate_deal():
    tag_id = os.getenv("AMAZON_AFFILIATE_TAG") or "prucansales-21"
    index_file = "current_deal_index.txt"
    curr_idx = 0
    if os.path.exists(index_file):
        try:
            with open(index_file, "r") as f:
                curr_idx = int(f.read().strip())
        except Exception:
            curr_idx = 0

    deal = CURATED_DEALS[curr_idx % len(CURATED_DEALS)]
    deal["affiliate_link"] = f"https://www.amazon.in/dp/B0B53CNJ2C?tag={tag_id}"

    # Next run kosam index increment
    with open(index_file, "w") as f:
        f.write(str((curr_idx + 1) % len(CURATED_DEALS)))

    with open("active_deal.json", "w", encoding="utf-8") as f:
        json.dump(deal, f, indent=2)

    print(f"🔥 Auto-Selected Deal for Today: {deal['title']} ({deal['discount']})")

if __name__ == "__main__":
    fetch_or_rotate_deal()
