import os
import sys
import json
import requests

IG_USER_ID = (os.getenv("IG_USER_ID") or "17841417494301577").strip()
ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")

with open("products.json", "r", encoding="utf-8") as f:
    PRODUCTS_LIST = json.load(f)

PRODUCT = PRODUCTS_LIST[0]
TRIGGER_KEYWORD = PRODUCT.get("keyword", "WATCH").strip().upper()
AFFILIATE_LINK = PRODUCT.get("affiliate_link", "https://amzn.to/example")

def get_recent_media():
    url = f"https://graph.facebook.com/v26.0/{IG_USER_ID}/media?fields=id,caption&limit=5&access_token={ACCESS_TOKEN}"
    res = requests.get(url).json()
    return res.get("data", [])

def get_comments_for_media(media_id):
    url = f"https://graph.facebook.com/v26.0/{media_id}/comments?fields=id,text,from,timestamp&access_token={ACCESS_TOKEN}"
    res = requests.get(url).json()
    return res.get("data", [])

def send_private_reply(comment_id, message_text):
    # Meta Instagram Graph API endpoint for replying directly to a comment via DM
    url = f"https://graph.facebook.com/v26.0/{IG_USER_ID}/messages"
    payload = {
        "recipient": {"comment_id": comment_id},
        "message": {"text": message_text},
        "access_token": ACCESS_TOKEN
    }
    res = requests.post(url, json=payload).json()
    return res

def process_automated_dms():
    print(f"Checking recent posts for trigger keyword: '{TRIGGER_KEYWORD}'...")
    media_list = get_recent_media()
    
    if not media_list:
        print("No recent media posts found.")
        return

    processed_file = "processed_comments.txt"
    processed_ids = set()
    if os.path.exists(processed_file):
        with open(processed_file, "r") as f:
            processed_ids = set(line.strip() for line in f)

    new_processed = []

    for media in media_list:
        media_id = media["id"]
        comments = get_comments_for_media(media_id)
        
        for comment in comments:
            c_id = comment["id"]
            c_text = comment.get("text", "").strip().upper()
            
            if c_id in processed_ids:
                continue
                
            if TRIGGER_KEYWORD in c_text:
                print(f"Keyword matched in comment: '{comment.get('text')}' by {comment.get('from', {}).get('username')}")
                
                dm_body = (
                    f"Hello! 👋 Here is your direct discount link for the {PRODUCT['title']}:\n\n"
                    f"🔗 Buy Link: {AFFILIATE_LINK}\n\n"
                    f"(Limited stock deal. Affiliate partnership disclosure included.)"
                )
                
                result = send_private_reply(c_id, dm_body)
                print(f"DM Response for comment {c_id}:", result)
                new_processed.append(c_id)

    if new_processed:
        with open(processed_file, "a") as f:
            for item in new_processed:
                f.write(f"{item}\n")
        print(f"Successfully replied to {len(new_processed)} new comments!")
    else:
        print("No new comments matching the keyword.")

if __name__ == "__main__":
    process_automated_dms()
