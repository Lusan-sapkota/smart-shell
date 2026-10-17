"""
Config Module - Handles loading and saving of configuration data.
"""

import os
import json
from rich.console import Console

console = Console()

# Configuration paths
CONFIG_DIR = os.path.expanduser("~/.config/smart-shell")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")
ENV_API_KEY = "SMART_SHELL_API_KEY"

def load_config():
    """Loads configuration from file."""
    if not os.path.exists(CONFIG_FILE):
        return {}
    try:
        with open(CONFIG_FILE, "r") as f:
            config = json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        console.print(f"[yellow]Warning: Could not load config file: {e}[/yellow]")
        return {}
    # Older versions stored the sudo password here; scrub it.
    if config.pop("sudo_password_b64", None) is not None:
        save_config(config)
    return config

def save_config(config):
    """Saves configuration to file."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    try:
        # Holds the API key: owner read/write only.
        fd = os.open(CONFIG_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
        os.chmod(CONFIG_FILE, 0o600)
        with os.fdopen(fd, "w") as f:
            json.dump(config, f, indent=2)
    except IOError as e:
        console.print(f"[bold red]Error: Could not save config file: {e}[/bold red]")

def get_current_model():
    """Gets the current default model from the config file."""
    config = load_config()
    return config.get("default_model", "models/gemini-2.5-flash")

def save_model(model_name):
    """Saves the selected model to the config file."""
    config = load_config()
    config["default_model"] = model_name
    save_config(config)
