import json, os
from datetime import datetime, timezone
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
    st = json.loads(STATE.read_text(encoding="utf-8"))
    n = int(st["current_fraz"])
    if not 1 <= n <= 100:
        raise RuntimeError(f"Invalid current_fraz: {n}")
    return n, st.get("last_sent")

def save_state(n, last_sent):
    STATE.write_text(json.dumps({"current_fraz": n, "last_sent": last_sent}, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")

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
    n, last_sent = load_state()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    # Several early cron triggers exist to beat GitHub's schedule delays;
    # only the first one of the day may send. Manual runs set FORCE_SEND=1.
    if last_sent == today and os.environ.get("FORCE_SEND") != "1":
        print(f"Already sent today ({today}); skipping.")
        return
    s = data[n-1]
    text = (
        f"🕊️ <b>فراز {n} از دعای جوشن کبیر</b>\n\n"
        f"<b>{s['arabic']}</b>\n\n"
        f"🌱 <b>معنی:</b>\n{s['translation']}\n\n{FOOTER}"
    )
    send(text)
    if n < 100:
        save_state(n+1, today)
        print(f"Sent section {n}; next={n+1}")
    else:
        save_state(n, today)
        print("Sent section 100; sequence complete.")

if __name__ == "__main__":
    main()
