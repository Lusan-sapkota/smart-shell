"""
Config Module - Handles loading and saving of configuration data.
"""

import os
import json
import base64
import binascii
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
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        console.print(f"[yellow]Warning: Could not load config file: {e}[/yellow]")
        return {}

def save_config(config):
    """Saves configuration to file."""
    os.makedirs(CONFIG_DIR, exist_ok=True)
    try:
        with open(CONFIG_FILE, "w") as f:
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

def get_sudo_password():
    """Gets the decoded sudo password from the config file."""
    config = load_config()
    encoded_pass = config.get("sudo_password_b64")
    if encoded_pass:
        try:
            return base64.b64decode(encoded_pass).decode('utf-8')
        except (binascii.Error, UnicodeDecodeError):
            return None
    return None

def save_sudo_password(password):
    """Saves the sudo password to the config file in base64 encoding."""
    config = load_config()
    encoded_pass = base64.b64encode(password.encode('utf-8')).decode('utf-8')
    config["sudo_password_b64"] = encoded_pass
    save_config(config) 