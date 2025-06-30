#!/usr/bin/env python3
"""
Config Module - Handles API key and configuration management.
"""

import os
import json
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel

console = Console()

# Configuration paths
CONFIG_DIR = os.path.expanduser("~/.config/smart-shell")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# Environment variable for API key
ENV_API_KEY = "SMART_SHELL_API_KEY"

def load_config():
    """
    Load configuration from file.
    
    Returns:
        dict: Configuration dictionary
    """
    if not os.path.exists(CONFIG_FILE):
        return {}
        
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[yellow]Warning: Could not load config file: {str(e)}[/yellow]")
        return {}

def save_config(config):
    """
    Save configuration to file.
    
    Args:
        config (dict): Configuration dictionary
    """
    os.makedirs(CONFIG_DIR, exist_ok=True)
    
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config, f, indent=2)
    except Exception as e:
        console.print(f"[bold red]Error: Could not save config file: {str(e)}[/bold red]")

def setup_config():
    """Interactive configuration setup."""
    console.print(Panel.fit(
        "Welcome to Smart-Shell setup!\n"
        "This will guide you through setting up your API key and preferences.",
        title="Smart-Shell Setup",
        border_style="blue"
    ))
    
    # Load existing config
    config = load_config()
    
    # Check for existing API key in environment
    env_key = os.environ.get(ENV_API_KEY)
    if env_key:
        console.print(f"[green]API key found in {ENV_API_KEY} environment variable.[/green]")
        console.print("[yellow]Note: Environment variable takes precedence over config file.[/yellow]")
    
    # Get API key
    current_key = config.get("api_key", "")
    masked_key = "*" * len(current_key) if current_key else ""
    
    console.print("\n[bold]API Key Configuration[/bold]")
    console.print("Smart-Shell uses Google Gemini API for natural language processing.")
    console.print("You can get an API key from https://ai.google.dev/")
    console.print("[yellow]Note: Any valid Gemini-compatible API key will work.[/yellow]")
    
    if masked_key:
        console.print(f"Current API key: {masked_key}")
        
    api_key = Prompt.ask("Enter your Gemini API key", password=True, default=current_key)
    
    # Save config
    if api_key:
        config["api_key"] = api_key
        save_config(config)
        console.print("[green]API key saved successfully![/green]")
    else:
        console.print("[yellow]No API key provided. Using existing key if available.[/yellow]")
    
    # Show environment variable option
    console.print(f"\n[bold]Alternative: Environment Variable[/bold]")
    console.print(f"You can also set your API key using the {ENV_API_KEY} environment variable:")
    console.print(f"  export {ENV_API_KEY}=your-api-key-here")
    console.print("[yellow]This is recommended for better security.[/yellow]")
    
    console.print("\n[green]Setup complete! You can now use Smart-Shell.[/green]")
    console.print("Try: smart-shell run \"list all files in this directory\"") 