"""
Setup Logic Module - Handles all interactive setup for Smart-Shell.
"""

import os
import base64
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

# Import necessary functions from other modules
from .ai_wrapper import validate_api_key, get_wrapper
from .utils import validate_sudo_password, log_error
from .config import load_config, save_config

console = Console()
ENV_API_KEY = "SMART_SHELL_API_KEY"

def setup_config():
    """Interactive configuration setup for API key and sudo password."""
    console.print(Panel.fit(
        "Welcome to Smart-Shell setup!\\n"
        "This will guide you through setting up your API key and sudo password.",
        title="Smart-Shell Setup",
        border_style="blue"
    ))
    
    config = load_config()
    
    if not setup_api_key(config):
        console.print("[red]API key setup is required. Exiting setup.[/red]")
        return
        
    setup_sudo_password(config)
    
    api_key = os.environ.get(ENV_API_KEY) or config.get("api_key")
    if api_key:
        set_default_model(api_key, config)

    save_config(config)
    console.print(f"\\n[bold]Reminder:[/bold] You can also set your API key via the {ENV_API_KEY} environment variable.")
    console.print("\\n[green]Setup complete![/green]")

def setup_api_key(config):
    """Handles the API key part of the setup."""
    env_key = os.environ.get(ENV_API_KEY)
    if env_key:
        console.print(f"[green]API key found in {ENV_API_KEY} environment variable.[/green]")
    
    current_key = config.get("api_key", "")
    console.print("\\n[bold]API Key Configuration[/bold]")
    
    if current_key:
        masked_key = f"****{current_key[-4:]}"
        console.print(f"An API key is already configured ({masked_key}).")
        if not Confirm.ask("Do you want to change it?", default=False):
            return True
    
    while True:
        api_key = Prompt.ask("Enter your Gemini API key", password=True)
        if not api_key:
            continue
        console.print("[blue]Validating API key...[/blue]")
        is_valid, message = validate_api_key(api_key)
        
        if is_valid:
            console.print(f"[green]✓ {message}[/green]")
            config["api_key"] = api_key
            return True
        else:
            console.print(f"[bold red]✗ Validation failed: {message}[/bold red]")
            if not Confirm.ask("Do you want to try again?", default=True):
                return False

def setup_sudo_password(config):
    """Handles the sudo password part of the setup."""
    console.print("\\n[bold]Sudo Password Configuration (Optional)[/bold]")
    has_existing_password = "sudo_password_b64" in config and config["sudo_password_b64"]

    warning_panel = Panel(
        "[bold yellow]Warning:[/bold yellow] Storing your sudo password allows Smart-Shell to run commands with root privileges without asking. It's stored encoded, not encrypted.",
        title="[red]Security Warning[/red]", border_style="red"
    )
    console.print(warning_panel)

    prompt_text = "A sudo password is saved. Do you want to change or remove it?" if has_existing_password else "Do you want to configure a sudo password now?"
    if not Confirm.ask(prompt_text, default=False):
        if not has_existing_password: console.print("[yellow]Sudo password setup skipped.[/yellow]")
        return
        
    while True:
        password = Prompt.ask("Enter your new sudo password (leave blank to remove)", password=True)
        if not password:
            if "sudo_password_b64" in config: del config["sudo_password_b64"]
            console.print("[green]Sudo password has been removed.[/green]")
            break
        
        console.print("[blue]Validating sudo password...[/blue]")
        if validate_sudo_password(password):
            encoded_pass = base64.b64encode(password.encode('utf-8')).decode('utf-8')
            config["sudo_password_b64"] = encoded_pass
            console.print("[green]✓ Sudo password validated and saved.[/green]")
            break
        else:
            console.print("[bold red]✗ Incorrect sudo password.[/bold red]")
            if not Confirm.ask("Do you want to try again?", default=True):
                break

def set_default_model(api_key, config):
    """Asks the user to select a default model and saves it to the config."""
    if not Confirm.ask("\\nWould you like to set a default model now?", default=True):
        return

    try:
        wrapper = get_wrapper(api_key)
        models = wrapper.list_available_models()
        if not models:
            console.print("[red]Could not retrieve any models from the API.[/red]")
            return

        model_choices = [name.replace('models/', '') for name in models]
        console.print("\\nPlease select a default model from the list below:")
        for i, model_name in enumerate(model_choices, 1):
            console.print(f"  [cyan]{i}[/cyan]: {model_name}")

        choice = Prompt.ask("Enter the number of your choice", choices=[str(i) for i in range(1, len(model_choices) + 1)], show_choices=False)
        selected_model_name = models[int(choice) - 1]
        config["default_model"] = selected_model_name
        console.print(f"[green]'{selected_model_name}' has been set as your default model.[/green]")
    except Exception as e:
        console.print(f"[bold red]Could not set default model: {e}[/bold red]")
        log_error(f"Failed during default model setup: {e}") 