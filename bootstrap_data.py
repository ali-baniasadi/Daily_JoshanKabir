"""
One-time dataset builder for Daily Joshan Kabir.

The original Setare page now contains the Persian translation only through
section 56, so the old parser cannot build sections 57..100. This version
uses a source that currently contains all 100 sections with Persian
translation and parses the page by numbered section markers instead of
depending on a particular HTML layout.
"""

import json
import re
import unicodedata
from pathlib import Path

import requests
from bs4 import BeautifulSoup

URL = "https://nasim.app/library/mafatih-novin/%D8%AF%D8%B9%D8%A7%DB%8C-%D8%AC%D9%88%D8%B4%D9%86-%DA%A9%D8%A8%DB%8C%D8%B1-2"
OUT = Path(__file__).resolve().parent / "data" / "joshan_kabir.json"

DIGITS = str.maketrans(
    "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
    "01234567890123456789",
)


def num(s):
    s = s.translate(DIGITS)
    m = re.search(r"\d+", s)
    return int(m.group()) if m else None


def clean(s):
    s = unicodedata.normalize("NFKC", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


MARKER_RE = re.compile(
    r"^\s*[﴿(«【\[]\s*([۰-۹0-9٠-٩]{1,3})\s*[﴾)»】\]]\s*(.*)$"
)


def main():
    r = requests.get(
        URL,
        timeout=60,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/131 Safari/537.36"
            )
        },
    )
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    # Use visible text lines. This source splits Arabic and translation
    # across several HTML elements, so looking for adjacent <p>/<div> tags
    # is unreliable.
    raw_lines = soup.get_text("\n").splitlines()
    lines = [clean(x) for x in raw_lines if clean(x)]

    sections = {}
    current = None
    mode = None

    for line in lines:
        m = MARKER_RE.match(line)
        if m:
            n = num(m.group(1))
            content = clean(m.group(2))

            if n is None or not 1 <= n <= 100:
                continue

            # The first marker for a section is the Arabic text.
            # The second marker with the same number starts its translation.
            if n != current:
                current = n
                mode = "arabic"
                sections.setdefault(n, {"arabic": [], "translation": []})
                if content:
                    sections[n]["arabic"].append(content)
            else:
                mode = "translation"
                if content:
                    sections[n]["translation"].append(content)

            continue

        if current is None or mode is None:
            continue

        sections[current][mode].append(line)

        # Section 100 ends with the standard closing sentence. Stop there so
        # page UI/navigation text is never included in the dataset.
        if (
            current == 100
            and mode == "translation"
            and line.startswith("تسبیح")
        ):
            break

    found = {}

    for n in range(1, 101):
        item = sections.get(n)
        if not item:
            continue

        arabic = clean(" ".join(item["arabic"]))
        translation = clean(" ".join(item["translation"]))

        if arabic and translation:
            found[n] = {
                "number": n,
                "arabic": arabic,
                "translation": translation,
            }

    missing = [n for n in range(1, 101) if n not in found]

    if missing:
        raise RuntimeError(
            "Could not build the complete dataset. Missing: "
            + ", ".join(map(str, missing))
            + ". No partial dataset was written."
        )

    data = [found[n] for n in range(1, 101)]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"OK: wrote {len(data)} sections to {OUT}")


if __name__ == "__main__":
    main()
