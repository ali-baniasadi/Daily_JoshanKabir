import json
import os
import sys
from pathlib import Path
from urllib import request, parse, error

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "joshan_kabir.json"
STATE_FILE = BASE_DIR / "state.json"

CHANNEL_ID = "@Daily_JoshanKabir"
FOOTER = "🆔 @Daily_JoshanKabir | دعای جوشن کبیر"


def load_json(path, default):
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, value):
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(value, f, ensure_ascii=False, indent=2)
        f.write("\n")
    tmp.replace(path)


def telegram(method, payload):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is not set.")

    url = f"https://api.telegram.org/bot{token}/{method}"
    body = parse.urlencode(payload).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=30) as response:
            result = json.loads(response.read().decode("utf-8"))
    except error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Telegram HTTP {exc.code}: {details}") from exc

    if not result.get("ok"):
        raise RuntimeError(f"Telegram API error: {result}")

    return result


def main():
    data = load_json(DATA_FILE, {})
    if len(data) != 100:
        raise RuntimeError(
            "data/joshan_kabir.json must contain exactly 100 sections. "
            "Run sync_data.py first."
        )

    state = load_json(
        STATE_FILE,
        {"current_section": 1, "completed": False},
    )

    if state.get("completed"):
        print("All 100 sections have already been published. Nothing to do.")
        return

    section_number = int(state.get("current_section", 1))
    if not 1 <= section_number <= 100:
        raise RuntimeError(f"Invalid current_section: {section_number}")

    section = data[str(section_number)]
    arabic = section["arabic"].strip()
    translation = section["translation"].strip()

    text = (
        f"🕊️ <b>فراز {section_number} از دعای جوشن کبیر</b>\n\n"
        f"{arabic}\n\n"
        f"🌱 <b>معنی:</b>\n"
        f"{translation}\n\n"
        f"{FOOTER}"
    )

    telegram(
        "sendMessage",
        {
            "chat_id": CHANNEL_ID,
            "text": text,
            "parse_mode": "HTML",
            "disable_web_page_preview": "true",
        },
    )

    next_section = section_number + 1
    if next_section > 100:
        state = {
            "current_section": 100,
            "completed": True,
        }
        print("Section 100 published. Sequence completed.")
    else:
        state = {
            "current_section": next_section,
            "completed": False,
        }
        print(f"Section {section_number} published. Next: {next_section}")

    save_json(STATE_FILE, state)


if __name__ == "__main__":
    main()
