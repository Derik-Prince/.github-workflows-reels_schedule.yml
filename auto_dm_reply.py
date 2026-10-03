import os
import json
import requests

IG_USER_ID = os.getenv("IG_USER_ID")
ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")

with open("products.json", "r", encoding="utf-8") as f:
    PRODUCTS_LIST = json.load(f)

# Keyword ki aa specific product ni match chesthundhi
KEYWORD_PRODUCT_MAP = {p["keyword"].upper(): p for p in PRODUCTS_LIST}

def get_recent_reels():
    url = f"https://graph.facebook.com/v26.0/{IG_USER_ID}/media?fields=id,caption&limit=5&access_token={ACCESS_TOKEN}"
    res = requests.get(url).json()
    return res.get("data", [])

def check_and_send_dms(media_id):
    comments_url = f"https://graph.facebook.com/v26.0/{media_id}/comments?fields=id,text,from,username&access_token={ACCESS_TOKEN}"
    res = requests.get(comments_url).json()
    comments = res.get("data", [])

    for comment in comments:
        comment_id = comment["id"]
        comment_text = comment.get("text", "").upper().strip()
        username = comment.get("username", "there")

        for keyword, prod in KEYWORD_PRODUCT_MAP.items():
            if keyword in comment_text:
                print(f"Matched keyword '{keyword}' from @{username}")

                # 1. 100% Free Meta Official Private Reply (DM Send)
                dm_url = f"https://graph.facebook.com/v26.0/{IG_USER_ID}/messages"
                dm_payload = {
                    "recipient": {"comment_id": comment_id},
                    "message": {
                        "text": f"Hey @{username}! 🔥\n\nNuvvu adigina '{prod['title']}' deal link idhi:\n👉 {prod['affiliate_link']}\n\nFast ga chudu bro, stock limit lo undi!"
                    },
                    "access_token": ACCESS_TOKEN
                }
                dm_res = requests.post(dm_url, json=dm_payload).json()
                print("DM Status:", dm_res)

                # 2. Public comment ki reply
                reply_url = f"https://graph.facebook.com/v26.0/{comment_id}/replies"
                requests.post(reply_url, data={
                    "message": f"@{username} Bro, check your DM for the deal link! 📩",
                    "access_token": ACCESS_TOKEN
                })
                break

if __name__ == "__main__":
    reels = get_recent_reels()
    if reels:
        for reel in reels:
            print(f"Scanning Reel ID: {reel['id']}")
            check_and_send_dms(reel["id"])
    else:
        print("Reels dhorakaledhu.")
