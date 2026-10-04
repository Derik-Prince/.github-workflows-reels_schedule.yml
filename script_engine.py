import json, os, requests

VOICE_LABELS = {"te": "Telugu", "hi": "Hindi", "en": "English"}

FALLBACK = {
    "te": {
        "watch": "ఈ స్మార్ట్ వాచ్ మీద మంచి డీల్ వచ్చింది. ధర తగ్గినప్పుడు మిస్ అవ్వకండి. ఫీచర్స్ చూడండి, మీకు కావాల్సిన డీల్ అయితే వెంటనే చెక్ చేయండి. లింక్ కావాలంటే WATCH అని కామెంట్ చేయండి.",
        "earbuds": "ఈ వైర్లెస్ ఇయర్‌బడ్స్ మీద మంచి డీల్ కనిపిస్తోంది. క్లియర్ కాల్స్, తక్కువ లేటెన్సీ, మంచి బ్యాటరీ — రోజువారీ ఉపయోగానికి బాగుంటాయి. లింక్ కావాలంటే BUDS అని కామెంట్ చేయండి.",
        "default": "ఈ ప్రోడక్ట్ మీద మంచి డీల్ వచ్చింది. ధర, ఫీచర్స్ చూసి మీకు ఉపయోగపడితే చెక్ చేయండి. లింక్ కావాలంటే COMMENT చేయండి."
    },
    "hi": {
        "watch": "इस स्मार्टवॉच पर अच्छा डील मिल रहा है। फीचर्स और कीमत जरूर चेक करें। अगर आपको लिंक चाहिए तो WATCH कमेंट करें।",
        "earbuds": "इन वायरलेस ईयरबड्स पर बढ़िया डील दिख रही है। क्लियर कॉलिंग, लो लेटेंसी और अच्छी बैटरी मिलती है। लिंक चाहिए तो BUDS कमेंट करें।",
        "default": "इस प्रोडक्ट पर अच्छा डील मिल रहा है। कीमत और फीचर्स चेक करें। लिंक चाहिए तो कमेंट करें।"
    },
    "en": {
        "watch": "This smartwatch has a deal worth checking. Look at the features and the current price before it ends. Comment WATCH for the link.",
        "earbuds": "These wireless earbuds have a deal worth checking. You get clear calling, low latency and long battery life. Comment BUDS for the link.",
        "default": "This product has a deal worth checking. See the current price and key features. Comment for the link."
    }
}

def fallback(product, lang):
    cat = product.get("category", "default")
    text = FALLBACK.get(lang, FALLBACK["en"]).get(cat, FALLBACK.get(lang, FALLBACK["en"])["default"])
    return {"hook": product["title"], "voice": text, "scenes": [
        {"type":"hook", "duration":3, "text":product["title"]},
        {"type":"product", "duration":5, "text":"Key features"},
        {"type":"price", "duration":4, "text":f"{product['currency']}{product['current_price']:,}"},
        {"type":"features", "duration":5, "text":" • ".join(product.get("features", []))},
        {"type":"cta", "duration":4, "text":f"COMMENT {product['keyword']} FOR LINK"}
    ]}

def generate(product, lang):
    key = os.getenv("GEMINI_API_KEY")
    if not key:
        return fallback(product, lang)
    prompt = f'''Create a short social-commerce Reel plan in {VOICE_LABELS[lang]} for this product.
Product: {product['title']}
Category: {product.get('category')}
Price: {product['currency']}{product['current_price']}
Original: {product['currency']}{product.get('original_price')}
Discount: {product.get('discount_percent')}%
Features: {product.get('features')}
Keyword: {product['keyword']}

Return JSON only with keys hook, voice, scenes. voice must be natural spoken {VOICE_LABELS[lang]}, not a literal translation. scenes is 4-7 objects with type (hook/product/feature/price/cta), duration seconds and text. Do not invent specs, reviews, stock claims or guarantees.'''
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=" + key
    r = requests.post(url, json={"contents":[{"parts":[{"text":prompt}]}]}, timeout=45)
    r.raise_for_status()
    txt = r.json()["candidates"][0]["content"]["parts"][0]["text"]
    txt = txt.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(txt)
    except Exception:
        return fallback(product, lang)
