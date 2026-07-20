import os

CONFIG_FILE = "config.yaml"

DEFAULT_CONFIG = {
    "token": "",
    "output": "discord_collectibles",
    "threads": 16,
    "retries": 3,
    "proxy": "",
    "export_json": ""
}

def load_config():
    """Load configuration from config.yaml if present."""
    config = DEFAULT_CONFIG.copy()
    if not os.path.exists(CONFIG_FILE):
        return config

    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if ":" in line:
                    key, val = line.split(":", 1)
                    key = key.strip()
                    val = val.strip().strip('"\'')
                    if key == "threads" and val.isdigit():
                        config["threads"] = int(val)
                    elif key == "retries" and val.isdigit():
                        config["retries"] = int(val)
                    elif key in config:
                        config[key] = val
    except Exception:
        pass
    return config

def save_config(config):
    """Save configuration into config.yaml file."""
    yaml_content = f"""# Discord Collectibles Scraper Configuration by MrX
token: "{config.get('token', '')}"
output: "{config.get('output', 'discord_collectibles')}"
threads: {config.get('threads', 16)}
retries: {config.get('retries', 3)}
proxy: "{config.get('proxy', '')}"
export_json: "{config.get('export_json', '')}"
"""
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(yaml_content)
    except Exception as e:
        print(f"[!] Could not save config.yaml: {e}")
