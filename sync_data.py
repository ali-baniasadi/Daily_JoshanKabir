import json
import re
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

SOURCE_URL = (
    "https://www.maood.ir/"
    "%D8%AF%D8%B9%D8%A7%D9%87%D8%A7-%D9%88-%D8%B2%DB%8C%D8%A7%D8%B1%D8%A7%D8%AA/"
    "%D8%AF%D8%B9%D8%A7%D9%87%D8%A7%DB%8C-%D9%85%D8%A7%D9%87-%D9%85%D8%A8%D8%A7%D8%B1%DA%A9-%D8%B1%D9%85%D8%B6%D8%A7%D9%86/"
    "446-%D8%AF%D8%B9%D8%A7%DB%8C-%D8%AC%D9%88%D8%B4%D9%86-%DA%A9%D8%A8%DB%8C%D8%B1.html"
)

ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "data" / "joshan_kabir.json"

ARABIC_MARKER = re.compile(r"﴿\s*([0-9۰-۹]+)\s*﴾")
PAREN_NUMBER = re.compile(r"^\s*[\(（]\s*[0-9۰-۹]+\s*[\)）]\s*")


def fa_to_en_digits(value):
    return value.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789"))


def clean(text):
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def fetch_source():
    req = Request(
        SOURCE_URL,
        headers={
            "User-Agent": "Mozilla/5.0 (compatible; DailyJoshanKabirBot/1.0)"
        },
    )
    try:
        with urlopen(req, timeout=30) as response:
            raw = response.read()
    except (HTTPError, URLError) as exc:
        raise RuntimeError(f"Could not download source page: {exc}") from exc

    return raw.decode("utf-8", errors="replace")


def html_to_lines(html):
    # BeautifulSoup is deliberately used only for parsing the public page.
    try:
        from bs4 import BeautifulSoup
    except ImportError as exc:
        raise RuntimeError(
            "beautifulsoup4 is required. Run: pip install -r requirements.txt"
        ) from exc

    soup = BeautifulSoup(html, "html.parser")

    # Remove navigation/scripts/styles so the parser sees the article text.
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()

    # Prefer the article/content area when available.
    container = (
        soup.find("div", class_=re.compile(r"item-page|article|content", re.I))
        or soup.find("article")
        or soup.body
    )
    if container is None:
        raise RuntimeError("Could not find page content.")

    raw_lines = container.get_text("\n").splitlines()
    return [clean(line) for line in raw_lines if clean(line)]


def parse_sections(lines):
    sections = {}

    for i, line in enumerate(lines):
        marker = ARABIC_MARKER.search(line)
        if not marker:
            continue

        number = int(fa_to_en_digits(marker.group(1)))
        if not 1 <= number <= 100:
            continue

        # The marker and Arabic text are normally on the same line.
        arabic = line[marker.end():].strip()

        # If Arabic text is empty, take the next non-empty line.
        j = i + 1
        if not arabic and j < len(lines):
            arabic = lines[j]
            j += 1

        # The next line is the Persian translation. Some source versions
        # prefix it with (۱), while others don't.
        translation = ""
        while j < len(lines):
            candidate = lines[j]
            if ARABIC_MARKER.search(candidate):
                break
            if candidate:
                translation = PAREN_NUMBER.sub("", candidate).strip()
                if translation:
                    break
            j += 1

        if arabic and translation:
            sections[str(number)] = {
                "arabic": clean(arabic),
                "translation": clean(translation),
            }

    return sections


def validate(sections):
    missing = [str(i) for i in range(1, 101) if str(i) not in sections]
    if missing:
        raise RuntimeError(
            "Could not parse all 100 sections. Missing: " + ", ".join(missing)
        )

    for i in range(1, 101):
        item = sections[str(i)]
        if len(item["arabic"]) < 20 or len(item["translation"]) < 10:
            raise RuntimeError(f"Section {i} looks incomplete.")

    return True


def main():
    html = fetch_source()
    lines = html_to_lines(html)
    sections = parse_sections(lines)
    validate(sections)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", encoding="utf-8") as f:
        json.dump(sections, f, ensure_ascii=False, indent=2)
        f.write("\n")

    print(f"Saved {len(sections)} sections to {OUTPUT}")


if __name__ == "__main__":
    main()
