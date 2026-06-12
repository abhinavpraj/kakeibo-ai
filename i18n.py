import json
from pathlib import Path

LOCALES_DIR = Path(__file__).parent / "locales"


def load_language(lang):
    with open(LOCALES_DIR / f"{lang}.json", encoding="utf-8") as f:
        return json.load(f)
