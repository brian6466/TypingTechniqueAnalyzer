import os
import json

CONFIG_PATH = "assets/keys.json"

def keys_exist():
    return os.path.exists(CONFIG_PATH) and os.path.getsize(CONFIG_PATH) > 0

def load_keys():
    if keys_exist():
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return None
