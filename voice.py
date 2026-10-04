import asyncio, os
from pathlib import Path
import edge_tts

VOICES = {
    "te": "te-IN-ShrutiNeural",
    "hi": "hi-IN-SwaraNeural",
    "en": "en-IN-NeerjaNeural"
}

async def _make(text, out, lang):
    communicate = edge_tts.Communicate(text, VOICES.get(lang, VOICES["en"]), rate="+5%", volume="+0%")
    await communicate.save(str(out))

def create(text, out, lang):
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    asyncio.run(_make(text, out, lang))
    return out
