"""
Smart-Shell - An intelligent terminal assistant that converts natural language into executable Bash/Zsh commands.
"""

import sys
import os
import click
import signal
import readline
import atexit
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown

from .shell_builder import generate_command_plan, explain_command
from .safety import check_command_safety
from .setup_logic import setup_config
from .config import load_config, ENV_API_KEY
from .utils import execute_command, print_plan_preview, reset_sudo_password, ERROR_LOG_FILE, get_os_info, detect_shell
from .ai_wrapper import PROVIDERS, get_client, resolve_model, is_configured, override_provider, AIError
from .history import HISTORY_DIR, save_to_history, update_history_result, show_command_history, show_last_command, redo_last_command
from .updater import handle_update_command, get_current_version

console = Console()

class DefaultRunGroup(click.Group):
    """Treat `smart-shell "do something"` as `smart-shell run "do something"`."""

    GROUP_OPTIONS = {"--provider": 2, "--base-url": 2}

    def parse_args(self, ctx, args):
        i = 0
        while i < len(args) and args[i].split("=")[0] in self.GROUP_OPTIONS:
            i += 1 if "=" in args[i] else self.GROUP_OPTIONS[args[i]]
        rest = args[i:]
        if rest and rest[0] not in self.commands and rest[0] not in ("--help", "--list-models"):
            args = ["run"] + args
        return super().parse_args(ctx, args)


@click.group(cls=DefaultRunGroup, invoke_without_command=True)
@click.pass_context
@click.option("--list-models", is_flag=True, help="List all supported AI models")
@click.option("--provider", type=click.Choice(list(PROVIDERS) + ["custom"]), help="Use this provider instead of the saved one")
@click.option("--base-url", help="Use this OpenAI-compatible base URL instead of the saved one")
def cli(ctx, list_models, provider, base_url):
    """Smart-Shell: Convert natural language to Bash or Zsh commands using AI."""
    if list_models:
        display_models()
        return
        
    if ctx.invoked_subcommand is None:
        ctx.invoke(run, prompt=None, dry_run=False, model=None, interactive=True, provider=provider, base_url=base_url)

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
@click.option("--provider", type=click.Choice(list(PROVIDERS) + ["custom"]), help="Use this provider instead of the saved one")
@click.option("--base-url", help="Use this OpenAI-compatible base URL instead of the saved one")
def run(prompt, dry_run, model, interactive, yes, provider, base_url):
    """Convert natural language to Bash or Zsh commands."""
    try:
        config = override_provider(load_config(), provider, base_url)
    except AIError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        return

    if not is_configured(config):
        console.print("[bold red]No AI provider configured. Run 'smart-shell setup' to configure.[/bold red]")
        console.print(f"Alternatively, set the {ENV_API_KEY} environment variable for Gemini.")
        return
    client = get_client(config)

    shell_type = detect_shell()
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

    user_prompt = " ".join(prompt)
    process_prompt(user_prompt, dry_run, model, client, config, yes)

RISK_ORDER = ["safe", "info_leak", "medium", "high", "blocked"]


def process_prompt(user_prompt, dry_run, model, client, config, auto_yes=False, session=None):
    """Generate a plan for the prompt, then review and run it."""
    console.print(f"\n[bold blue]Prompt:[/bold blue] {user_prompt}")
    try:
        model = resolve_model(client, model, config)
        with console.status(f"Thinking ({config.get('provider', 'gemini')}:{model})..."):
            plan = generate_command_plan(user_prompt, client, model, os_info=get_os_info(), session=session)
    except KeyboardInterrupt:
        console.print("\n[yellow]Command generation interrupted.[/yellow]")
        return False
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        console.print("[yellow]If this is an API error, check 'smart-shell setup' and that the provider is reachable.[/yellow]")
        return False

    if not plan:
        console.print("[yellow]The AI returned an empty plan. Try rephrasing the request.[/yellow]")
        return False
    entry = {"prompt": user_prompt, "commands": plan, "result": "not run"}
    if session is not None:
        session.append(entry)
    return review_and_run(user_prompt, plan, dry_run, auto_yes, client, model, entry)


def review_and_run(user_prompt, plan, dry_run, auto_yes, client, model, entry):
    """Preview, confirm (yes / no / edit), run, and offer an AI fix if it fails."""
    while True:
        results = [check_command_safety(cmd) for cmd in plan]
        print_plan_preview(plan, results)
        worst = max((r["status"] for r in results), key=RISK_ORDER.index)

        if dry_run:
            console.print("[yellow]Dry run: nothing was executed.[/yellow]")
            save_to_history(user_prompt, plan, executed=False)
            return True

        if worst == "blocked":
            console.print("[bold red]Blocked: this plan will not run.[/bold red] You can edit it or cancel.")
            choice = "n" if auto_yes else Prompt.ask(r"\[e]dit or \[n]o", choices=["e", "n"], default="n")
        elif auto_yes:
            choice = "y"
        else:
            if worst in ("high", "medium"):
                color = "red" if worst == "high" else "yellow"
                for cmd, r in zip(plan, results):
                    if r["status"] == worst:
                        console.print(f"[{color}]{worst.upper()} risk:[/{color}] {cmd}  [dim]({r['notes']})[/dim]")
            default = "n" if worst in ("high", "medium") else "y"
            choice = Prompt.ask(r"Run it? \[y]es / \[n]o / \[e]dit", choices=["y", "n", "e"], default=default, show_choices=False)

        if choice == "n":
            console.print("[yellow]Cancelled.[/yellow]")
            return False
        if choice == "e":
            edited = Prompt.ask("Command", default=" && ".join(plan)).strip()
            if edited:
                plan = [edited]
            continue

        history_id = save_to_history(user_prompt, plan, executed=True)
        # Run the whole plan in one shell so cd/source carry over; stop at the first failure.
        command = " && ".join(plan)
        success, error_tail = execute_command(command)
        update_history_result(history_id, success)
        entry.update(commands=plan, result="succeeded" if success else "failed")
        if success or auto_yes or not Confirm.ask("Ask the AI to fix it?", default=True):
            return success

        fix_request = (f"This command failed:\n{command}\n\nLast lines of its error output:\n"
                       f"{error_tail.strip()[-1500:] or '(none)'}\n\nOriginal request: {user_prompt}\n"
                       "Return a corrected plan.")
        try:
            with console.status(f"Working on a fix ({model})..."):
                plan = generate_command_plan(fix_request, client, model, os_info=get_os_info())
        except Exception as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
            return False
        if not plan:
            console.print("[yellow]The AI did not suggest a fix.[/yellow]")
            return False


def run_interactive_mode(dry_run, model, client, config, auto_yes=False, shell_type="bash"):
    """Run Smart-Shell in interactive mode until user exits."""
    os.makedirs(HISTORY_DIR, exist_ok=True)
    
    readline_history_file = os.path.join(HISTORY_DIR, "readline_history")
    try:
        readline.read_history_file(readline_history_file)
    except FileNotFoundError:
        pass
    
    atexit.register(readline.write_history_file, readline_history_file)
    
    
    def signal_handler(sig, frame):
        console.print("\n[green]Exiting Smart-Shell. Goodbye![/green]")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        current_model = resolve_model(client, model, config)
    except AIError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        return
    console.print(f"[bold cyan]Smart-Shell[/bold cyan] v{get_current_version()}  "
                  f"[dim]{config.get('provider', 'gemini')}:{current_model}  {shell_type}[/dim]")
    console.print("[dim]Describe what you want to do. !help for commands, exit to quit.[/dim]")
    session = []
    try:
        while True:
            try:
                display_model = current_model.removeprefix('models/')
                
                def get_protected_input():
                    try:
                        prompt_text = f"\nSmart-Shell ({display_model}): "
                        line = input(prompt_text)
                        return line.rstrip()
                    except KeyboardInterrupt:
                        raise
                    except EOFError:
                        raise
                
                user_prompt = get_protected_input()
                
                if user_prompt:  # Only add non-empty prompts to history
                    readline.add_history(user_prompt)
            except EOFError:
                console.print("\n[green]Exiting Smart-Shell. Goodbye![/green]")
                break
            
            if user_prompt.lower() in ["exit", "quit", "bye", "q"]:
                console.print("[green]Exiting Smart-Shell. Goodbye![/green]")
                break
            
            if not user_prompt or not user_prompt.strip():
                continue
            
            smart_shell_commands = [
                "smart-shell setup", "smart-shell --setup", "smart-shell config",
                "smart-shell version", "smart-shell --version", "smart-shell -v",
                "smart-shell models", "smart-shell --models", "smart-shell --list-models",
                "smart-shell help", "smart-shell --help", "smart-shell -h",
                "smart-shell history", "smart-shell --history"
            ]
            
            user_prompt_lower = user_prompt.lower().strip()
            if any(cmd in user_prompt_lower for cmd in smart_shell_commands):
                console.print(f"[yellow]The command '{user_prompt}' should be run outside Smart-Shell.[/yellow]")
                console.print("[yellow]Please exit Smart-Shell first (type 'exit' or press Ctrl+C) and then run this command.[/yellow]")
                continue
                
            if user_prompt.startswith("!"):
                current_model = handle_special_command(user_prompt, current_model, client)
                continue
                
            process_prompt(user_prompt, dry_run, current_model, client, config, auto_yes, session)
            
    except Exception as e:
        console.print(f"\n[bold red]Error in interactive mode:[/bold red] {str(e)}")
        console.print("[green]Exiting Smart-Shell.[/green]")
        return

def handle_special_command(command, current_model, client):
    """Handle special commands in interactive mode."""
    cmd = command.lower().strip()
    
    if cmd == "!history":
        show_command_history()
    elif cmd == "!clear":
        os.system("clear" if os.name == "posix" else "cls")
    elif cmd == "!help":
        show_help()
    elif cmd == "!models":
        display_models()
    elif cmd.startswith("!model "):
        # Keep the original case: model ids like Qwen/Qwen2.5 are case-sensitive.
        new_model = command.strip().split(" ", 1)[1].strip()
        console.print(f"[green]✓ Switched to model: {new_model}[/green]")
        return new_model
    elif cmd.startswith("!explain "):
        target = command.strip().split(" ", 1)[1].strip()
        safety = check_command_safety(target)
        console.print(f"[bold]Safety level:[/bold] {safety['status'].upper()} ({safety['notes']})")
        try:
            console.print(explain_command(client, current_model, target))
        except AIError as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
    elif cmd == "!forget-sudo":
        reset_sudo_password()
        console.print("[green]Sudo credentials cleared.[/green]")
    elif cmd == "!docs":
        console.print("[bold blue]Documentation:[/bold blue] https://smart-shell.lusansapkota.com.np/")
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
- `!explain <command>` - Explain what a command does
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
Every step is checked before execution:
- **Blocked**: never runs (e.g. `rm -rf /`, fork bombs, formatting disks); you can only edit it
- **High**: destructive, asks y/n (e.g. `rm -rf dir`, piping into a shell)
- **Medium**: changes the system, asks y/n (e.g. `sudo`, package installs, `kill`)
- **Info leak**: may print secrets, flagged in the preview
- **Safe**: runs directly

## CLI Usage
- `smart-shell` - Start interactive mode
- `smart-shell run <prompt>` - Run a one-off command (`-d` dry run, `-m <model>`, `-y` skip prompts)
- `smart-shell setup` - Configure provider, API key and model
- `smart-shell models` - List available models
- `smart-shell history` - Show command history
- `smart-shell version` - Show version information

For more, see the documentation or run `smart-shell --help`.
"""
    md = Markdown(help_text)
    console.print(Panel(md, title="Smart-Shell Help", border_style="blue"))

@cli.command()
def setup():
    """Setup API key and configuration."""
    setup_config()

@cli.command()
def version():
    """Show version information."""
    console.print(f"Smart-Shell v{get_current_version()}")

@click.command('help', context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
def cli_help():
    """Show CLI help information."""
    click.echo(cli.get_help(click.Context(cli)))

cli.add_command(cli_help)

@cli.command()
def history():
    """Show command history."""
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

def show_error_log():
    """Show the error log."""
    if not os.path.exists(ERROR_LOG_FILE):
        console.print("[green]No errors logged yet![/green]")
        return
    
    try:
        with open(ERROR_LOG_FILE, "r") as f:
            logs = f.read().strip()
        
        if not logs:
            console.print("[green]Error log is empty![/green]")
            return
        
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
