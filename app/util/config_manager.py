import os
import json

CONFIG_PATHS = {
    "keys": "app/assets/keys.json",
    "technique": "app/assets/technique.json"
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
