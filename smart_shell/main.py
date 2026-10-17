"""
Smart-Shell - An intelligent terminal assistant that converts natural language into executable Bash/Zsh commands.
"""

import sys
import os
import re
import importlib.metadata
import click
import signal
import readline
import atexit
import json
import subprocess
import requests
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table

from .shell_builder import generate_command_plan, display_banner
from .safety import check_command_safety
from .setup_logic import setup_config
from .config import load_config, ENV_API_KEY
from .utils import execute_command, print_plan_preview, reset_sudo_password, log_error, ERROR_LOG_FILE, get_os_info, detect_shell
from .ai_wrapper import get_client, resolve_model, is_configured, AIError

console = Console()

# History file for command storage
HISTORY_DIR = os.path.expanduser("~/.local/share/smart-shell")
HISTORY_FILE = os.path.join(HISTORY_DIR, "history.json")

@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--list-models", is_flag=True, help="List all supported AI models")
def cli(ctx, list_models):
    """Smart-Shell: Convert natural language to Bash or Zsh commands using AI."""
    if list_models:
        display_models()
        return
        
    if ctx.invoked_subcommand is None:
        # No need to show banner again, just invoke the run command
        ctx.invoke(run, prompt=None, dry_run=False, model=None, interactive=True)

def display_models():
    """List the models the configured provider offers."""
    if not is_configured():
        console.print("[bold red]No provider configured. Run 'smart-shell setup'.[/bold red]")
        return
    config = load_config()
    try:
        models = get_client(config).list_models()
    except AIError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        return
    current = config.get("default_model", "")
    console.print(f"\n[bold blue]Models from {config.get('provider', 'gemini')}:[/bold blue]")
    for name in models:
        marker = "[green]*[/green]" if name == current.removeprefix("models/") else " "
        console.print(f" {marker} {name}")
    console.print("\nSwitch for one run with [cyan]--model <name>[/cyan] or in interactive mode with [cyan]!model <name>[/cyan].")

@cli.command()
@click.argument("prompt", nargs=-1)
@click.option("--dry-run", "-d", is_flag=True, help="Show command without executing")
@click.option("--model", "-m", help="Specify model to use for this command")
@click.option("--interactive", "-i", is_flag=True, help="Run in interactive mode")
@click.option("yes", "-y", is_flag=True, help="Automatically confirm all prompts")
def run(prompt, dry_run, model, interactive, yes):
    """Convert natural language to Bash or Zsh commands."""
    # Don't display banner again - it's already shown in the main CLI function
    
    # Load configuration
    config = load_config()
    
    if not is_configured(config):
        console.print("[bold red]No AI provider configured. Run 'smart-shell setup' to configure.[/bold red]")
        console.print(f"Alternatively, set the {ENV_API_KEY} environment variable for Gemini.")
        return
    client = get_client(config)

    # Detect shell type
    shell_type = detect_shell()
    # Only show detected shell in non-interactive mode
    if not interactive:
        console.print(f"[bold blue]Detected shell:[/bold blue] {shell_type}")
    
    if interactive:
        run_interactive_mode(dry_run, model, client, config, yes, shell_type)
        return
    
    if not prompt:
        console.print(Panel.fit(
            "Please provide a prompt describing what you want to do.",
            title="Smart-Shell",
            border_style="blue"
        ))
        return

    # Generate command from natural language
    user_prompt = " ".join(prompt)
    process_prompt(user_prompt, dry_run, model, client, config, yes)

def process_prompt(user_prompt, dry_run, model, client, config, auto_yes=False):
    """Process a single user prompt."""
    console.print(f"\n[bold blue]Prompt:[/bold blue] {user_prompt}")
    
    try:
        # Generate a command plan (list of commands)
        console.print("[blue]Generating execution plan...[/blue]")
        command_plan = generate_command_plan(user_prompt, client, resolve_model(client, model, config), os_info=get_os_info())

        if not command_plan:
            console.print("[yellow]The AI returned an empty plan. This could be due to a safety block or an impossible request. Please try again.[/yellow]")
            return

        safety_results = [check_command_safety(cmd) for cmd in command_plan]
        
        # Display the plan preview
        print_plan_preview(command_plan, safety_results)
        
        # Check if any command in the plan is risky
        blocked_commands = [cmd for cmd, safety in zip(command_plan, safety_results) if safety["status"] == "blocked"]
        if blocked_commands:
            console.print("[bold red]⛔ BLOCKED:[/bold red]")
            for cmd in blocked_commands:
                console.print(f"   {cmd}")
            
            # Ask if user wants to edit the command
            if Prompt.ask("Would you like to edit the command?", choices=["y", "n"], default="y") == "y":
                edited_command = Prompt.ask("Enter modified command", default=blocked_commands[0])
                if edited_command != blocked_commands[0]:
                    # Check safety of edited command
                    safety_result = check_command_safety(edited_command)
                    if safety_result["status"] == "blocked":
                        console.print(f"[bold red]⛔ Edited command is still blocked:[/bold red]")
                        console.print(f"[red]Reason: {safety_result['reason']}[/red]")
                        return False
                    command_plan = [edited_command]
                    console.print("[green]Using edited command.[/green]")
                else:
                    return False
            else:
                return False
            
        # Execute or dry run
        if dry_run:
            console.print("[yellow]Dry run mode - command not executed[/yellow]")
            # Save to history even in dry run mode
            save_to_history(user_prompt, command_plan, executed=False)
            return True
        else:
            # Check for HIGH and MEDIUM risk commands and ask for confirmation
            high_risk_commands = [cmd for cmd, safety in zip(command_plan, safety_results) if safety["status"] == "high"]
            medium_risk_commands = [cmd for cmd, safety in zip(command_plan, safety_results) if safety["status"] == "medium"]
            
            if high_risk_commands and not auto_yes:
                console.print(f"[bold red]⚠️  HIGH RISK COMMAND DETECTED![/bold red]")
                for cmd, safety in zip(command_plan, safety_results):
                    if safety["status"] == "high":
                        console.print(f"[red]Command:[/red] {cmd}")
                        console.print(f"[red]Risk:[/red] {safety['notes']}")
                
                if not Confirm.ask("This command has HIGH RISK. Do you want to proceed?", choices=["y", "n"], default="n"):
                    console.print("[yellow]Command execution cancelled for safety.[/yellow]")
                    return False
            
            elif medium_risk_commands and not auto_yes:
                console.print(f"[bold yellow]⚠️  MEDIUM RISK COMMAND DETECTED![/bold yellow]")
                for cmd, safety in zip(command_plan, safety_results):
                    if safety["status"] == "medium":
                        console.print(f"[yellow]Command:[/yellow] {cmd}")
                        console.print(f"[yellow]Risk:[/yellow] {safety['notes']}")
                
                if not Confirm.ask("This command has MEDIUM RISK. Do you want to proceed?", choices=["y", "n"], default="n"):
                    console.print("[yellow]Command execution cancelled for safety.[/yellow]")
                    return False
            
            # Save to history before execution
            history_id = save_to_history(user_prompt, command_plan, executed=True)
            
            # Run the whole plan in one shell so cd/source carry over; stop at the first failure.
            success = execute_command(" && ".join(command_plan))
            
            # Update history with execution result
            update_history_result(history_id, success)
            
            return success
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Command generation interrupted.[/yellow]")
        return False
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        console.print("[yellow]If this is an API error, check 'smart-shell setup' and that the provider is reachable.[/yellow]")
        return False

def run_interactive_mode(dry_run, model, client, config, auto_yes=False, shell_type="bash"):
    """Run Smart-Shell in interactive mode until user exits."""
    # Set up history directory
    os.makedirs(HISTORY_DIR, exist_ok=True)
    
    # Set up readline history
    readline_history_file = os.path.join(HISTORY_DIR, "readline_history")
    try:
        readline.read_history_file(readline_history_file)
    except FileNotFoundError:
        pass
    
    # Save readline history on exit
    atexit.register(readline.write_history_file, readline_history_file)
    
    # Display the banner and welcome message
    from .shell_builder import display_banner, display_welcome_message
    display_banner()
    display_welcome_message(shell_type)
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        console.print("\n[green]Exiting Smart-Shell. Goodbye![/green]")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Main interactive loop
    try:
        current_model = resolve_model(client, model, config)
    except AIError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        return
    try:
        while True:
            # Get user input with enhanced prompt showing current model
            try:
                # Extract model name for display (remove 'models/' prefix if present)
                display_model = current_model.removeprefix('models/')
                
                # Create a truly protected prompt using a custom approach
                def get_protected_input():
                    # Use input() with the prompt parameter to make it non-deletable
                    try:
                        # Create the prompt string without Rich formatting for input()
                        prompt_text = f"\nSmart-Shell ({display_model}): "
                        line = input(prompt_text)
                        # Only strip trailing whitespace, preserve intentional leading spaces and line breaks
                        return line.rstrip()
                    except KeyboardInterrupt:
                        raise
                    except EOFError:
                        raise
                
                user_prompt = get_protected_input()
                
                if user_prompt:  # Only add non-empty prompts to history
                    readline.add_history(user_prompt)
            except EOFError:
                # Handle Ctrl+D
                console.print("\n[green]Exiting Smart-Shell. Goodbye![/green]")
                break
            
            # Check for exit commands
            if user_prompt.lower() in ["exit", "quit", "bye", "q"]:
                console.print("[green]Exiting Smart-Shell. Goodbye![/green]")
                break
            
            # Skip empty prompts (check if there's any non-whitespace content)
            if not user_prompt or not user_prompt.strip():
                continue
            
            # Check for Smart-Shell CLI commands that should be run outside
            smart_shell_commands = [
                "smart-shell setup", "smart-shell --setup", "smart-shell config",
                "smart-shell version", "smart-shell --version", "smart-shell -v",
                "smart-shell models", "smart-shell --models", "smart-shell --list-models",
                "smart-shell help", "smart-shell --help", "smart-shell -h",
                "smart-shell history", "smart-shell --history"
            ]
            
            user_prompt_lower = user_prompt.lower().strip()
            if any(cmd in user_prompt_lower for cmd in smart_shell_commands):
                console.print(f"[yellow]💡 The command '{user_prompt}' should be run outside Smart-Shell.[/yellow]")
                console.print("[yellow]Please exit Smart-Shell first (type 'exit' or press Ctrl+C) and then run this command.[/yellow]")
                continue
                
            # Check for special commands
            if user_prompt.startswith("!"):
                current_model = handle_special_command(user_prompt, current_model)
                continue
                
            # Process the prompt
            process_prompt(user_prompt, dry_run, current_model, client, config, auto_yes)
            
    except Exception as e:
        console.print(f"\n[bold red]Error in interactive mode:[/bold red] {str(e)}")
        console.print("[green]Exiting Smart-Shell.[/green]")
        return

def handle_special_command(command, current_model):
    """Handle special commands in interactive mode."""
    cmd = command.lower().strip()
    
    if cmd == "!history":
        show_command_history()
    elif cmd == "!clear":
        os.system("clear" if os.name == "posix" else "cls")
        display_banner()
    elif cmd == "!help":
        show_help()
    elif cmd == "!models":
        display_models()
    elif cmd.startswith("!model "):
        # Keep the original case: model ids like Qwen/Qwen2.5 are case-sensitive.
        new_model = command.strip().split(" ", 1)[1].strip()
        console.print(f"[green]✓ Switched to model: {new_model}[/green]")
        return new_model
    elif cmd == "!forget-sudo":
        reset_sudo_password()
        console.print("[green]Sudo credentials cleared.[/green]")
    elif cmd == "!docs":
        console.print("[bold blue]Documentation:[/bold blue] https://lusan-sapkota.github.io/smart-shell/")
    elif cmd == "!update":
        handle_update_command()
    elif cmd == "!creator":
        show_creator_info()
    elif cmd == "!last":
        show_last_command()
    elif cmd == "!redo":
        redo_last_command()
    elif cmd == "!errors":
        show_error_log()
    else:
        console.print(f"[yellow]Unknown special command: {command}[/yellow]")
    
    return current_model

def show_help():
    """Show help information in interactive mode."""
    shell_type = detect_shell()
    help_text = f"""
# Smart-Shell Help

## Basic Usage
Type your request in natural language, and Smart-Shell will convert it to a {shell_type.capitalize()} command.

Examples:
- "List all PDF files in the current directory"
- "Find large files over 100MB"
- "Create a backup of my project folder"

## Special Commands (Interactive Mode)
- `!history` - Show command history
- `!clear` - Clear the screen
- `!help` - Show this help
- `!model <model-name>` - Change the AI model
- `!models` - List available models
- `!last` - Show the last generated command
- `!redo` - Re-execute the last command
- `!update` - Check for updates and install
- `!errors` - Show the error log
- `!forget-sudo` - Clear cached sudo credentials
- `!creator` - Show information about the creator
- `!docs` - Show link to documentation

## Exiting
Type `exit`, `quit`, `bye`, `q` or press Ctrl+C to exit.

## Safety
Commands are checked for safety before execution:
- 🟢 **Safe**: Commands that are considered safe to run
- 🟡 **Warning**: Commands that might have unintended consequences (requires confirmation)
- 🔴 **Blocked**: Commands that are potentially harmful (will not be executed)

## CLI Usage
- `smart-shell --help` or `smart-shell -h` — Show CLI help
- `smart-shell --version` — Show version information
- `smart-shell run <prompt>` — Run a one-off natural language command
- `smart-shell --interactive` — Start interactive mode
- `smart-shell setup` — Configure provider, API key and model
- `smart-shell models` — List available models
- `smart-shell history` — Show command history

For more, see the documentation or run `smart-shell --help`.
"""
    md = Markdown(help_text)
    console.print(Panel(md, title="Smart-Shell Help", border_style="blue"))

def save_to_history(prompt, command, executed=False):
    """
    Save a command to history.
    
    Args:
        prompt (str): The user's natural language prompt
        command (str): The generated command
        executed (bool): Whether the command was executed
        
    Returns:
        str: The ID of the history entry
    """
    os.makedirs(HISTORY_DIR, exist_ok=True)
    
    # Generate a unique ID
    history_id = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Create history entry
    entry = {
        "id": history_id,
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "command": command,
        "executed": executed,
        "success": None  # Will be updated after execution
    }
    
    # Load existing history
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        except:
            history = []
    
    # Add new entry
    history.append(entry)
    
    # Save history
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)
    
    return history_id

def update_history_result(history_id, success):
    """
    Update the success status of a history entry.
    
    Args:
        history_id (str): The ID of the history entry
        success (bool): Whether the command executed successfully
    """
    if not os.path.exists(HISTORY_FILE):
        return
    
    # Load history
    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)
    
    # Update entry
    for entry in history:
        if entry["id"] == history_id:
            entry["success"] = success
            break
    
    # Save history
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def show_command_history():
    """Show the command history."""
    if not os.path.exists(HISTORY_FILE):
        console.print("[yellow]No command history found.[/yellow]")
        return
    
    # Load history
    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)
    
    if not history:
        console.print("[yellow]Command history is empty.[/yellow]")
        return
    
    # Display history
    console.print("[bold]Command History:[/bold]")
    for i, entry in enumerate(reversed(history[-10:])):  # Show last 10 entries
        timestamp = datetime.fromisoformat(entry["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
        status = ""
        if entry["executed"]:
            if entry["success"] is True:
                status = "[green]✓[/green]"
            elif entry["success"] is False:
                status = "[red]✗[/red]"
            else:
                status = "[yellow]?[/yellow]"
        
        console.print(f"{i+1}. {status} [blue]{timestamp}[/blue]")
        console.print(f"   Prompt: {entry['prompt']}")
        syntax = Syntax(entry["command"], "bash", theme="monokai", line_numbers=False)
        console.print(f"   Command: {syntax}")
        console.print("")

@cli.command()
def setup():
    """Setup API key and configuration."""
    display_banner()
    setup_config()

@cli.command()
def version():
    """Show version information."""
    display_banner()
    console.print(f"[bold]Smart-Shell v{get_current_version()}[/bold]")
    console.print("An intelligent terminal assistant for Bash or Zsh commands")
    console.print("Works with Gemini, OpenAI, DeepSeek, Ollama and any OpenAI-compatible API")

@click.command('help', context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
def cli_help():
    """Show CLI help information."""
    click.echo(cli.get_help(click.Context(cli)))

cli.add_command(cli_help)

@cli.command()
def history():
    """Show command history."""
    display_banner()
    show_command_history()

@cli.command()
def models():
    """List all supported AI models."""
    display_models()

def main():
    """Entry point for the application."""
    try:
        cli()
    except KeyboardInterrupt:
        console.print("\n[green]Exiting Smart-Shell. Goodbye![/green]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

def handle_update_command():
    """Handle the !update command to check for and install updates."""
    try:
        console.print("[blue]🔍 Checking for Smart-Shell updates...[/blue]")
        
        # Get current version from pyproject.toml
        current_version = get_current_version()
        console.print(f"[blue]📦 Current version: {current_version}[/blue]")
        
        # Get latest version from GitHub
        latest_version = get_latest_github_version()
        if not latest_version:
            console.print("[yellow]⚠️  Could not fetch latest version from GitHub.[/yellow]")
            console.print("[dim]Fallback: Try manual update with 'git pull' if in development mode.[/dim]")
            return
        
        console.print(f"[blue]🌟 Latest version: {latest_version}[/blue]")
        
        # Compare versions
        if compare_versions(current_version, latest_version) >= 0:
            console.print("[green]✅ You're already using the latest version![/green]")
            return
        
        console.print(f"[yellow]🆕 New version available: {current_version} → {latest_version}[/yellow]")
        
        # Ask for confirmation
        if not Confirm.ask("Do you want to update to the latest version?", choices=["y", "n"], default="y"):
            console.print("[yellow]Update cancelled.[/yellow]")
            return
        
        # Determine update method
        project_root = find_project_root()
        if project_root and (project_root / ".git").exists():
            # Development environment - use git
            console.print("[blue]🔄 Development environment detected. Updating via git...[/blue]")
            success = update_via_git(project_root)
        else:
            # Installed package - use pip
            console.print("[blue]🔄 Installed package detected. Updating via pip...[/blue]")
            success = update_via_pip()
        
        if success:
            console.print("[green]✅ Smart-Shell updated successfully![/green]")
            console.print("[bold yellow]🔄 Please restart Smart-Shell to use the new version.[/bold yellow]")
            console.print("[dim]Type 'exit' and run 'smart-shell' again.[/dim]")
        else:
            console.print("[red]❌ Update failed. Please try manual update.[/red]")
            console.print("[yellow]Manual options:[/yellow]")
            console.print("  • Development: [blue]git pull && pip install -e .[/blue]")
            console.print("  • Installed: [blue]pip install --upgrade smart-shell[/blue]")
            
    except Exception as e:
        console.print(f"[red]❌ Error during update: {e}[/red]")
        log_error(f"Update error: {e}")

def get_current_version():
    """Get the installed package version."""
    try:
        return importlib.metadata.version("smart-shell")
    except importlib.metadata.PackageNotFoundError:
        return "unknown"

def get_latest_github_version():
    """Get the latest version from GitHub releases."""
    try:
        url = "https://api.github.com/repos/Lusan-sapkota/smart-shell/releases/latest"
        headers = {"Accept": "application/vnd.github.v3+json"}
        
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            release_data = response.json()
            return release_data.get('tag_name', '').lstrip('v')
        
        # Fallback: check pyproject.toml from main branch
        url = "https://raw.githubusercontent.com/Lusan-sapkota/smart-shell/main/pyproject.toml"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            match = re.search(r'^version\s*=\s*"([^"]+)"', response.text, re.M)
            return match.group(1) if match else None
        
        return None
    except Exception as e:
        log_error(f"Error fetching GitHub version: {e}")
        return None

def compare_versions(version1, version2):
    """Compare two version strings. Returns: -1 if v1 < v2, 0 if equal, 1 if v1 > v2."""
    try:
        def normalize_version(v):
            # Handle 'unknown' or empty versions
            if not v or v == 'unknown':
                return [0, 0, 0]
            # Remove 'v' prefix if present and split by dots
            v = v.lstrip('v').split('.')
            # Convert to integers, pad to 3 elements
            return [int(x) for x in v] + [0] * (3 - len(v))
        
        v1_parts = normalize_version(version1)
        v2_parts = normalize_version(version2)
        
        for i in range(3):
            if v1_parts[i] < v2_parts[i]:
                return -1
            elif v1_parts[i] > v2_parts[i]:
                return 1
        
        return 0
    except Exception:
        return 0  # Assume equal if comparison fails

def find_project_root():
    """Find the project root directory by looking for pyproject.toml."""
    try:
        current_dir = Path(__file__).parent
        for _ in range(5):  # Look up to 5 levels up
            if (current_dir / "pyproject.toml").exists():
                return current_dir
            parent = current_dir.parent
            if parent == current_dir:  # Reached filesystem root
                break
            current_dir = parent
        return None
    except Exception:
        return None

def update_via_git(project_root):
    """Update using git pull for development environment."""
    try:
        os.chdir(project_root)
        
        # Check if there are uncommitted changes
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if result.stdout.strip():
            console.print("[yellow]⚠️  You have uncommitted changes. Stashing them...[/yellow]")
            subprocess.run(["git", "stash"], capture_output=True)
        
        # Pull latest changes
        console.print("[blue]📥 Pulling latest changes...[/blue]")
        result = subprocess.run(["git", "pull", "origin", "main"], capture_output=True, text=True)
        
        if result.returncode != 0:
            console.print(f"[red]Git pull failed: {result.stderr}[/red]")
            return False
        
        # Reinstall in development mode
        console.print("[blue]🔧 Reinstalling package...[/blue]")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-e", "."], capture_output=True, text=True)
        
        if result.returncode != 0:
            console.print(f"[red]Package reinstall failed: {result.stderr}[/red]")
            return False
        
        return True
        
    except Exception as e:
        console.print(f"[red]Git update failed: {e}[/red]")
        return False

def update_via_pip():
    """Update using pip for installed package."""
    try:
        console.print("[blue]📥 Updating via pip...[/blue]")
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "--upgrade", 
            "git+https://github.com/Lusan-sapkota/smart-shell.git"
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            console.print(f"[red]Pip update failed: {result.stderr}[/red]")
            return False
        
        return True
        
    except Exception as e:
        console.print(f"[red]Pip update failed: {e}[/red]")
        return False

def show_creator_info():
    """Show information about the creator."""
    creator_panel = Panel(
        """[bold cyan]Smart-Shell[/bold cyan] was created by [bold]Lusan Sapkota[/bold]

[yellow]About the Creator:[/yellow]
• Developer passionate about AI and automation
• Focused on making terminal interactions more intuitive
• Believes in the power of natural language interfaces

[blue]Connect:[/blue]
• GitHub: [link]https://github.com/lusan-sapkota[/link]
• Project: [link]https://github.com/lusan-sapkota/smart-shell[/link]

[green]Smart-Shell makes the terminal accessible to everyone![/green]""",
        title="[bold white]Creator Information[/bold white]",
        border_style="cyan",
        padding=(1, 2)
    )
    console.print(creator_panel)

def show_last_command():
    """Show the last generated command from history."""
    if not os.path.exists(HISTORY_FILE):
        console.print("[yellow]No command history found.[/yellow]")
        return
    
    try:
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
        
        if not history:
            console.print("[yellow]Command history is empty.[/yellow]")
            return
        
        last_entry = history[-1]
        console.print(f"[bold]Last Command:[/bold]")
        console.print(f"[blue]Prompt:[/blue] {last_entry['prompt']}")
        
        # Handle both string and list commands
        command = last_entry['command']
        if isinstance(command, list):
            for i, cmd in enumerate(command, 1):
                syntax = Syntax(cmd, "bash", theme="monokai", line_numbers=False)
                console.print(f"[blue]Command {i}:[/blue] {syntax}")
        else:
            syntax = Syntax(command, "bash", theme="monokai", line_numbers=False)
            console.print(f"[blue]Command:[/blue] {syntax}")
            
    except Exception as e:
        console.print(f"[red]Error reading command history: {e}[/red]")

def redo_last_command():
    """Re-execute the last command from history."""
    if not os.path.exists(HISTORY_FILE):
        console.print("[yellow]No command history found.[/yellow]")
        return
    
    try:
        with open(HISTORY_FILE, "r") as f:
            history = json.load(f)
        
        if not history:
            console.print("[yellow]Command history is empty.[/yellow]")
            return
        
        last_entry = history[-1]
        command = last_entry['command']
        
        # Handle both string and list commands
        if isinstance(command, list):
            if len(command) > 1:
                console.print("[yellow]Last command was a multi-step plan. Executing first command only.[/yellow]")
            command_to_execute = command[0] if command else ""
        else:
            command_to_execute = command
        
        if not command_to_execute:
            console.print("[yellow]No valid command to re-execute.[/yellow]")
            return
        
        console.print(f"[blue]Re-executing:[/blue] {command_to_execute}")
        
        if Confirm.ask("Do you want to execute this command?", choices=["y", "n"], default="y"):
            success = execute_command(command_to_execute)
            if success:
                console.print("[green]✓ Command executed successfully.[/green]")
            else:
                console.print("[red]✗ Command execution failed.[/red]")
        
    except Exception as e:
        console.print(f"[red]Error re-executing command: {e}[/red]")

def show_error_log():
    """Show the error log."""
    if not os.path.exists(ERROR_LOG_FILE):
        console.print("[green]No errors logged yet! 🎉[/green]")
        return
    
    try:
        with open(ERROR_LOG_FILE, "r") as f:
            logs = f.read().strip()
        
        if not logs:
            console.print("[green]Error log is empty! 🎉[/green]")
            return
        
        # Show last 10 lines
        lines = logs.split('\n')
        recent_lines = lines[-10:] if len(lines) > 10 else lines
        
        console.print("[bold]Recent Error Log (last 10 entries):[/bold]")
        for line in recent_lines:
            if line.strip():
                console.print(f"[red]{line}[/red]")
        
        if len(lines) > 10:
            console.print(f"\n[dim]... and {len(lines) - 10} more entries in {ERROR_LOG_FILE}[/dim]")
            
    except Exception as e:
        console.print(f"[red]Error reading error log: {e}[/red]")
