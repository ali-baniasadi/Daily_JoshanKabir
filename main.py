import json, os
from pathlib import Path
import requests

BASE = Path(__file__).resolve().parent
DATA = BASE / "data" / "joshan_kabir.json"
STATE = BASE / "state.json"
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHANNEL = "@Daily_JoshanKabir"
FOOTER = "🆔 @Daily_JoshanKabir | دعای جوشن کبیر"

def load_data():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    if len(data) != 100 or [x["number"] for x in data] != list(range(1,101)):
        raise RuntimeError("Dataset must contain sections 1..100 in order.")
    for x in data:
        if not x.get("arabic") or not x.get("translation"):
            raise RuntimeError(f"Section {x.get('number')} is incomplete.")
    return data

def load_state():
    if not STATE.exists():
        STATE.write_text('{"current_fraz": 1}\n', encoding="utf-8")
    n = int(json.loads(STATE.read_text(encoding="utf-8"))["current_fraz"])
    if not 1 <= n <= 100:
        raise RuntimeError(f"Invalid current_fraz: {n}")
    return n

def save_state(n):
    STATE.write_text(json.dumps({"current_fraz": n}, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

def send(text):
    if not TOKEN:
        raise RuntimeError("Missing TELEGRAM_BOT_TOKEN.")
    r = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        json={"chat_id": CHANNEL, "text": text, "parse_mode": "HTML",
              "disable_web_page_preview": True},
        timeout=30,
    )
    r.raise_for_status()
    if not r.json().get("ok"):
        raise RuntimeError(r.text)

def main():
    data = load_data()
    n = load_state()
    s = data[n-1]
    text = (
        f"🕊️ <b>فراز {n} از دعای جوشن کبیر</b>\n\n"
        f"<b>{s['arabic']}</b>\n\n"
        f"🌱 <b>معنی:</b>\n{s['translation']}\n\n{FOOTER}"
    )
    send(text)
    if n < 100:
        save_state(n+1)
        print(f"Sent section {n}; next={n+1}")
    else:
        print("Sent section 100; sequence complete.")

if __name__ == "__main__":
    main()
