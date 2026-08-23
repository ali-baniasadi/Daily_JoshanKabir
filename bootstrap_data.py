"""
One-time dataset builder.

Source:
https://setare.com/fa/news/8699/...
The source page explicitly presents the full 100 sections with Persian translation.
This script downloads it once, extracts numbered Arabic/translation pairs, validates
1..100, and writes data/joshan_kabir.json.

Run:
    pip install -r requirements.txt
    python bootstrap_data.py
"""

import json, re, unicodedata
from pathlib import Path
import requests
from bs4 import BeautifulSoup

URL = "https://setare.com/fa/news/8699/%D9%85%D8%AA%D9%86-%D8%AF%D8%B9%D8%A7%DB%8C-%D8%AC%D9%88%D8%B4%D9%86-%DA%A9%D8%A8%DB%8C%D8%B1-%D8%A8%D9%87-%D9%87%D9%85%D8%B1%D8%A7%D9%87-%D9%81%D8%A7%DB%8C%D9%84-%D8%B5%D9%88%D8%AA%DB%8C-%D9%88-%D9%88%DB%8C%D8%AF%DB%8C%D9%88%DB%8C%DB%8C-%D8%A8%D8%B1%D8%A7%DB%8C-%D8%AF%D8%A7%D9%86%D9%84%D9%88%D8%AF/"
OUT = Path(__file__).resolve().parent / "data" / "joshan_kabir.json"

DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")

def num(s):
    s = s.translate(DIGITS)
    m = re.search(r"\d+", s)
    return int(m.group()) if m else None

def clean(s):
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def main():
    r = requests.get(URL, timeout=30, headers={"User-Agent":"Mozilla/5.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # Work from visible text blocks. Setare uses a numbered Arabic block followed
    # immediately by its numbered Persian translation.
    blocks = []
    for tag in soup.find_all(["p","div","li"]):
        t = clean(tag.get_text(" ", strip=True))
        if t:
            blocks.append(t)

    found = {}
    for i, t in enumerate(blocks):
        m = re.match(r"^[﴿(«【\[]\s*([۰-۹0-9٠-٩]+)\s*[﴾)»】\]]", t)
        if not m:
            continue
        n = num(m.group(1))
        if not n or not 1 <= n <= 100:
            continue

        arabic = re.sub(r"^[﴿(«【\[]\s*[۰-۹0-9٠-٩]+\s*[﴾)»】\]]\s*", "", t)
        translation = None

        # Find the next short block carrying the same section number.
        for nxt in blocks[i+1:i+5]:
            if re.match(r"^[﴿(«【\[]\s*"+str(n).translate(DIGITS)+r"\s*[﴾)»】\]]", nxt.translate(DIGITS)):
                translation = re.sub(r"^[﴿(«【\[]\s*[۰-۹0-9٠-٩]+\s*[﴾)»】\]]\s*", "", nxt)
                break

        if translation and n not in found:
            found[n] = {"number": n, "arabic": arabic, "translation": translation}

    missing = [n for n in range(1,101) if n not in found]
    if missing:
        raise RuntimeError(
            "Could not build the complete dataset. Missing: " +
            ", ".join(map(str, missing)) +
            ". No partial dataset was written."
        )

    data = [found[n] for n in range(1,101)]
    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    print(f"OK: wrote {len(data)} sections to {OUT}")

if __name__ == "__main__":
    main()
