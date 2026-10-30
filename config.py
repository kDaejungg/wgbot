import os
import json
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

def load_settings():
    # A missing or empty settings.json should behave like "no settings yet", not crash.
    try:
        with open("settings.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_settings(data):
    with open("settings.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_about():
    with open("about.json", "r", encoding="utf-8") as f:
        return json.load(f)
