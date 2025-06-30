#!/usr/bin/env python3
"""
Smart-Shell - An intelligent terminal assistant that converts natural language into executable Bash commands.
"""

import sys
import os
import click
import signal
import readline
import atexit
import json
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown
from rich.syntax import Syntax
from rich.table import Table

from shell_builder import generate_command, display_banner, list_supported_models
from safety import check_command_safety
from config import load_config, setup_config, ENV_API_KEY
from utils import execute_command, print_command_preview, reset_sudo_password

console = Console()

# History file for command storage
HISTORY_DIR = os.path.expanduser("~/.local/share/smart-shell")
HISTORY_FILE = os.path.join(HISTORY_DIR, "history.json")

@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--list-models", is_flag=True, help="List all supported AI models")
def cli(ctx, list_models):
    """Smart-Shell: Convert natural language to Bash commands using AI."""
    if list_models:
        display_models()
        return
        
    if ctx.invoked_subcommand is None:
        # Show help if no subcommand is provided
        display_banner()
        ctx.invoke(run, prompt=None, dry_run=False, model=None, interactive=True)

def display_models():
    """Display a list of supported models."""
    models = list_supported_models()
    
    display_banner()
    
    table = Table(title="Supported AI Models")
    table.add_column("Model Name", style="cyan")
    table.add_column("Speed", style="green")
    table.add_column("Capabilities", style="yellow")
    
    model_info = {
        "gemini-2.5-pro": ("Medium", "Most accurate, default model"),
        "gemini-2.5-flash": ("Fast", "Lower latency, good output"),
        "gemini-2.0-pro": ("Legacy", "Older version, fallback")
    }
    
    for model in models:
        speed, capabilities = model_info.get(model, ("Unknown", "Unknown"))
        table.add_row(model, speed, capabilities)
    
    console.print(table)
    console.print("\nUse the --model option to specify a model:")
    console.print("  smart-shell run --model gemini-2.5-flash \"list all files\"")

@cli.command()
@click.argument("prompt", nargs=-1)
@click.option("--dry-run", "-d", is_flag=True, help="Show command without executing")
@click.option("--model", "-m", help="Specify model to use (gemini-2.5-pro, gemini-2.5-flash, etc.)")
@click.option("--interactive", "-i", is_flag=True, help="Run in interactive mode")
@click.option("--yes", "-y", is_flag=True, help="Automatically confirm all prompts")
def run(prompt, dry_run, model, interactive, yes):
    """Convert natural language to Bash commands."""
    # Display banner
    display_banner()
    
    # Load configuration
    config = load_config()
    
    # Check for API key in environment or config
    api_key = os.environ.get(ENV_API_KEY) or config.get("api_key")
    if not api_key:
        console.print("[bold red]No API key found. Run 'smart-shell setup' to configure.[/bold red]")
        console.print(f"Alternatively, set the {ENV_API_KEY} environment variable.")
        return

    if interactive:
        run_interactive_mode(dry_run, model, api_key, config, yes)
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
    process_prompt(user_prompt, dry_run, model, api_key, config, yes)

def process_prompt(user_prompt, dry_run, model, api_key, config, auto_yes=False):
    """Process a single user prompt."""
    console.print(f"[bold blue]Prompt:[/bold blue] {user_prompt}")
    
    try:
        # Generate command
        console.print("[blue]Generating command...[/blue]")
        command = generate_command(user_prompt, api_key, model)
        
        # Check command safety
        safety_result = check_command_safety(command)
        
        if safety_result["status"] == "blocked":
            console.print(f"[bold red]⛔ BLOCKED:[/bold red] {command}")
            console.print(f"[red]Reason: {safety_result['reason']}[/red]")
            if "details" in safety_result:
                console.print(f"[red]Details: {safety_result['details']}[/red]")
            
            # Ask if user wants to edit the command
            if Prompt.ask("Would you like to edit the command?", choices=["y", "n"], default="y") == "y":
                edited_command = Prompt.ask("Enter modified command", default=command)
                if edited_command != command:
                    # Check safety of edited command
                    safety_result = check_command_safety(edited_command)
                    if safety_result["status"] == "blocked":
                        console.print(f"[bold red]⛔ Edited command is still blocked:[/bold red]")
                        console.print(f"[red]Reason: {safety_result['reason']}[/red]")
                        return False
                    command = edited_command
                    console.print("[green]Using edited command.[/green]")
                else:
                    return False
            else:
                return False
            
        # Print the command with preview
        print_command_preview(command, safety_result)
        
        # Execute or dry run
        if dry_run:
            console.print("[yellow]Dry run mode - command not executed[/yellow]")
            # Save to history even in dry run mode
            save_to_history(user_prompt, command, executed=False)
            return True
        else:
            if safety_result["status"] == "warning" and not auto_yes:
                confirm = Confirm.ask("Do you want to proceed?", default=False)
                if not confirm:
                    return False
            
            # Save to history before execution
            history_id = save_to_history(user_prompt, command, executed=True)
            
            # Execute the command
            success = execute_command(command)
            
            # Update history with execution result
            update_history_result(history_id, success)
            
            return success
            
    except KeyboardInterrupt:
        console.print("\n[yellow]Command generation interrupted.[/yellow]")
        return False
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {str(e)}")
        console.print("[yellow]If this is an API error, check your API key and internet connection.[/yellow]")
        return False

def run_interactive_mode(dry_run, model, api_key, config, auto_yes=False):
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
    
    # Welcome message
    console.print(Panel.fit(
        "Welcome to Smart-Shell interactive mode! Type your requests in natural language.\n"
        "Type 'exit', 'quit', or press Ctrl+C to exit.\n\n"
        "Special commands:\n"
        "  !history - Show command history\n"
        "  !clear - Clear the screen\n"
        "  !help - Show help\n"
        "  !model <model-name> - Change the model\n"
        "  !models - List available models",
        title="Smart-Shell Interactive Mode",
        border_style="green"
    ))
    
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        console.print("\n[green]Exiting Smart-Shell. Goodbye![/green]")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Main interactive loop
    current_model = model
    try:
        while True:
            # Get user input
            try:
                user_prompt = Prompt.ask("\n[bold blue]Smart-Shell[/bold blue]")
                readline.add_history(user_prompt)
            except EOFError:
                # Handle Ctrl+D
                console.print("\n[green]Exiting Smart-Shell. Goodbye![/green]")
                break
            
            # Check for exit commands
            if user_prompt.lower() in ["exit", "quit", "bye", "q"]:
                console.print("[green]Exiting Smart-Shell. Goodbye![/green]")
                break
            
            # Skip empty prompts
            if not user_prompt.strip():
                continue
                
            # Check for special commands
            if user_prompt.startswith("!"):
                current_model = handle_special_command(user_prompt, current_model)
                continue
                
            # Process the prompt
            process_prompt(user_prompt, dry_run, current_model, api_key, config, auto_yes)
            
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
        parts = cmd.split(" ", 1)
        if len(parts) > 1:
            new_model = parts[1].strip()
            console.print(f"[green]Changing model to: {new_model}[/green]")
            return new_model
    else:
        console.print(f"[yellow]Unknown special command: {command}[/yellow]")
    
    return current_model

def show_help():
    """Show help information in interactive mode."""
    help_text = """
    # Smart-Shell Help

    ## Basic Usage
    Type your request in natural language, and Smart-Shell will convert it to a Bash command.
    
    Examples:
    - "List all PDF files in the current directory"
    - "Find large files over 100MB"
    - "Create a backup of my project folder"
    
    ## Special Commands
    - `!history` - Show command history
    - `!clear` - Clear the screen
    - `!help` - Show this help
    - `!model <model-name>` - Change the AI model
    - `!models` - List available models
    
    ## Exiting
    Type `exit`, `quit`, `bye`, `q` or press Ctrl+C to exit.
    
    ## Safety
    Commands are checked for safety before execution:
    - 🟢 **Safe**: Commands that are considered safe to run
    - 🟡 **Warning**: Commands that might have unintended consequences (requires confirmation)
    - 🔴 **Blocked**: Commands that are potentially harmful (will not be executed)
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
    console.print("[bold]Smart-Shell v1.0.0[/bold]")
    console.print("An intelligent terminal assistant for Bash commands")
    console.print("Powered by Google Gemini")

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