import os
import json
import requests

IG_USER_ID = os.getenv("IG_USER_ID", "").strip()
ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN", "").strip()
API_VERSION = os.getenv("IG_API_VERSION", "v21.0").strip()

def check_and_reply_dms():
    if not IG_USER_ID or not ACCESS_TOKEN:
        print("Missing credentials for Auto DM.")
        return

    # Load active products and keywords
    with open("products.json", "r", encoding="utf-8") as f:
        products = json.load(f)

    keyword_map = {p["keyword"].upper(): p for p in products if p.get("active", True)}

    # Fetch recent reels
    url = f"https://graph.facebook.com/{API_VERSION}/{IG_USER_ID}/media?fields=id,caption,comments&access_token={ACCESS_TOKEN}"
    res = requests.get(url).json()
    media_list = res.get("data", [])

    processed_file = "processed_comments.txt"
    processed = set()
    if os.path.exists(processed_file):
        processed = set(open(processed_file, "r").read().splitlines())

    for media in media_list[:3]:
        media_id = media.get("id")
        comments_url = f"https://graph.facebook.com/{API_VERSION}/{media_id}/comments?access_token={ACCESS_TOKEN}"
        comments_res = requests.get(comments_url).json()

        for c in comments_res.get("data", []):
            cid = c.get("id")
            text = c.get("text", "").upper()
            username = c.get("from", {}).get("username", "")

            if cid in processed:
                continue

            for kw, prod in keyword_map.items():
                if kw in text:
                    # Message with Website Redirect Link
                    link = prod.get("website_url") or prod.get("affiliate_links", {}).get("amazon")
                    msg = (
                        f"Hey @{username}! 🔥\n"
                        f"Mee special loot deal link ikkada undi:\n👉 {link}\n\n"
                        f"Official verified direct link tho purchase cheyyandi. Limited stock deal!"
                    )
                    
                    # Send Private DM reply to comment
                    reply_url = f"https://graph.facebook.com/{API_VERSION}/{cid}/replies"
                    requests.post(reply_url, data={"message": f"Link sent to your DM, check inbox bro! 📩", "access_token": ACCESS_TOKEN})
                    print(f"Sent deal response for keyword '{kw}' to user: {username}")
                    processed.add(cid)

    with open(processed_file, "w") as f:
        f.write("\n".join(processed))

if __name__ == "__main__":
    check_and_reply_dms()
