import os
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG_PATHS = {
    "keys": os.path.join(BASE_DIR, "assets", "keys.json"),
    "technique": os.path.join(BASE_DIR, "assets", "technique.json"),
    "keymap": os.path.join(BASE_DIR, "assets", "keymap.json")
}

def config_exists(which):
    path = CONFIG_PATHS.get(which)
    return path and os.path.exists(path) and os.path.getsize(path) > 0

def load_config(name):
    path = CONFIG_PATHS.get(name)
    if path and config_exists(name):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load config '{name}': {e}")
    else:
        print(f"Config '{name}' not found or empty.")
    return {}

def save_config(name, data):
    path = CONFIG_PATHS.get(name)
    if not path:
        print(f"Unknown config name: {name}")
        return False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Failed to save config '{name}': {e}")
        return False
