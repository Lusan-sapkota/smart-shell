"""
Setup Logic Module - Handles all interactive setup for Smart-Shell.
"""

from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel

from .ai_wrapper import PROVIDERS, ENV_BASE_URL, AIClient, AIError
from .config import load_config, save_config, ENV_API_KEY

console = Console()

def setup_config():
    """Interactive configuration setup for provider, API key and default model."""
    console.print(Panel.fit(
        "Welcome to Smart-Shell setup!\n"
        "Pick an AI provider (cloud or local), then a default model.",
        title="Smart-Shell Setup",
        border_style="blue"
    ))

    config = load_config()
    client = setup_provider(config)
    if not client:
        console.print("[red]Provider setup did not complete. Nothing saved.[/red]")
        return

    set_default_model(client, config)
    save_config(config)
    console.print(f"\n[bold]Reminder:[/bold] {ENV_API_KEY} and {ENV_BASE_URL} override the saved key and URL.")
    console.print("\n[green]Setup complete![/green]")

def setup_provider(config):
    """Ask for provider, base URL and API key; return a working client or None."""
    names = list(PROVIDERS) + ["custom"]
    console.print("\n[bold]Providers:[/bold]")
    for i, name in enumerate(names, 1):
        where = "local" if name in ("ollama", "lmstudio") else "any OpenAI-compatible URL" if name == "custom" else "cloud"
        console.print(f"  [cyan]{i}[/cyan]: {name} [dim]({where})[/dim]")
    # Configs from before multi-provider support are Gemini.
    current = config.get("provider", "gemini" if config.get("api_key") else None)
    default = str(names.index(current) + 1) if current in names else "1"
    provider = names[int(Prompt.ask("Choose a provider", choices=[str(i) for i in range(1, len(names) + 1)],
                                    default=default, show_choices=False)) - 1]

    if provider == "custom":
        base_url = Prompt.ask("Base URL (e.g. http://localhost:8080/v1)", default=config.get("base_url") or None)
        needs_key = Confirm.ask("Does it need an API key?", default=False)
    else:
        base_url, _, needs_key = PROVIDERS[provider]
        base_url = Prompt.ask("Base URL", default=base_url)

    # Only offer to keep the saved key if it belongs to this provider.
    kept = config.get("api_key") if current == provider else None
    while True:
        api_key = None
        if needs_key:
            hint = f" (enter to keep ****{kept[-4:]})" if kept else ""
            api_key = Prompt.ask(f"API key for {provider}{hint}", password=True, default=kept or "", show_default=False)
            if not api_key:
                continue

        client = AIClient(base_url, api_key)
        console.print("[blue]Checking connection...[/blue]")
        try:
            client.list_models()
        except AIError as e:
            console.print(f"[bold red]✗ {e}[/bold red]")
            if provider == "ollama":
                console.print("[yellow]Is Ollama running? Start it with: ollama serve[/yellow]")
            if not Confirm.ask("Try again?", default=True):
                return None
            continue

        console.print("[green]✓ Connected.[/green]")
        config["provider"] = provider
        config["base_url"] = base_url
        if api_key:
            config["api_key"] = api_key
        else:
            config.pop("api_key", None)
        return client

def set_default_model(client, config):
    """Asks the user to select a default model and saves it to the config."""
    config.pop("default_model", None)
    try:
        models = client.list_models()
    except AIError as e:
        console.print(f"[bold red]Could not list models: {e}[/bold red]")
        return
    if not models:
        console.print("[yellow]No models available. For Ollama, pull one: ollama pull qwen2.5-coder[/yellow]")
        return

    console.print("\n[bold blue]Available Models:[/bold blue]")
    for i, name in enumerate(models, 1):
        console.print(f"  [cyan]{i}[/cyan]: {name}")
    preferred = PROVIDERS.get(config["provider"], (None, None, None))[1]
    default = str(models.index(preferred) + 1) if preferred in models else "1"
    choice = Prompt.ask("Default model", choices=[str(i) for i in range(1, len(models) + 1)],
                        default=default, show_choices=False)
    config["default_model"] = models[int(choice) - 1]
    console.print(f"[green]✓ '{config['default_model']}' is now your default model.[/green]")
