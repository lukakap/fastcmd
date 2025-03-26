import os
import json
from pathlib import Path

CONFIG_DIR = Path.home() / ".fastcmd"
CONFIG_FILE = CONFIG_DIR / "config.json"

def save_api_key(api_key):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as file:
        json.dump({"OPENAI_API_KEY": api_key}, file)
    print("API key saved successfully.")

def load_api_key():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as file:
            data = json.load(file)
            return data.get("OPENAI_API_KEY")
    return None

def clear_api_key():
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
        print("API key cleared successfully.")
    else:
        print("No API key set.")

def get_api_key():
    api_key = os.getenv('OPENAI_API_KEY') or load_api_key()
    
    if api_key:
        return api_key
    
    api_key = input("Enter your OpenAI API key: ").strip()
    if not api_key:
        raise ValueError("API key cannot be empty.")
    
    save_api_key(api_key)
    return api_key
