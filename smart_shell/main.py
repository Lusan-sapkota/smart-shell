"""
Smart-Shell - An intelligent terminal assistant that converts natural language into executable Bash/Zsh commands.
"""

import sys
import os
import click
from html import escape
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.markdown import Markdown

from .shell_builder import generate_command_plan, explain_command
from .safety import check_command_safety
from .setup_logic import setup_config
from .config import load_config, save_config, ENV_API_KEY
from .utils import execute_command, notify, print_plan_preview, reset_sudo_password, ERROR_LOG_FILE, get_os_info, detect_shell
from .ai_wrapper import PROVIDERS, get_client, resolve_model, is_configured, override_provider, AIError
from .history import HISTORY_DIR, save_to_history, update_history_result, show_command_history, show_last_command, redo_last_command
from .updater import handle_update_command, get_current_version
from .ui import COMMANDS, MODES, make_reader

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
    console.print("\nSwitch for one run with [cyan]--model <name>[/cyan] or in interactive mode with [cyan]/model <name>[/cyan].")

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


def process_prompt(user_prompt, dry_run, model, client, config, auto_yes=False, session=None, auto_safe=False):
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
    return review_and_run(user_prompt, plan, dry_run, auto_yes, client, model, entry, auto_safe)


def review_and_run(user_prompt, plan, dry_run, auto_yes, client, model, entry, auto_safe=False):
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
            if not auto_yes:
                notify("A blocked plan is waiting: edit or cancel")
            choice = "n" if auto_yes else Prompt.ask(r"\[e]dit or \[n]o", choices=["e", "n"], default="n")
        elif auto_yes:
            choice = "y"
        elif auto_safe and worst == "safe":
            console.print("[dim]Auto mode: running a safe plan without asking.[/dim]")
            choice = "y"
        else:
            if worst in ("high", "medium"):
                color = "red" if worst == "high" else "yellow"
                for cmd, r in zip(plan, results):
                    if r["status"] == worst:
                        console.print(f"[{color}]{worst.upper()} risk:[/{color}] {cmd}  [dim]({r['notes']})[/dim]")
            default = "n" if worst in ("high", "medium") else "y"
            notify(f"Waiting for you: run {plan[0][:60]}{' ...' if len(plan) > 1 else ''}?")
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
        if not success and not auto_yes:
            notify("A command failed: ask the AI to fix it?")
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
    """Run Smart-Shell in interactive mode until the user exits."""
    os.makedirs(HISTORY_DIR, exist_ok=True)
    try:
        current_model = resolve_model(client, model, config)
    except AIError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        return

    state = {"model": current_model, "mode": "plan" if dry_run else "ask"}
    provider = config.get("provider", "gemini")

    def status():
        cwd = os.getcwd().replace(os.path.expanduser("~"), "~", 1)
        return (f" <mode-{state['mode']}>{state['mode']} mode</mode-{state['mode']}> · "
                f"{escape(provider)}:{escape(state['model'])} · {shell_type} · {escape(cwd)}"
                f"   <key>Shift+Tab</key> mode · <key>/</key> commands · <key>Ctrl+D</key> quit")

    def cycle_mode():
        names = list(MODES)
        state["mode"] = names[(names.index(state["mode"]) + 1) % len(names)]

    read = make_reader(os.path.join(HISTORY_DIR, "input_history"), client.list_models, status, cycle_mode)
    console.print(f"[bold cyan]Smart-Shell[/bold cyan] v{get_current_version()}  "
                  f"[dim]{provider}:{current_model}  {shell_type}[/dim]", highlight=False)
    console.print("[dim]Describe what you want to do. Type / for commands.[/dim]", highlight=False)

    session = []
    while True:
        try:
            user_prompt = read().strip()
        except EOFError:
            break
        if not user_prompt:
            continue
        if user_prompt.lower() in ("exit", "quit", "bye", "q", "/exit", "/quit"):
            break
        if user_prompt[0] in "/!":
            handle_special_command(user_prompt, state, client)
            continue
        try:
            process_prompt(user_prompt, state["mode"] == "plan", state["model"], client, config, auto_yes, session,
                           auto_safe=state["mode"] == "auto")
        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted.[/yellow]")
    console.print("[green]Goodbye![/green]")


def handle_special_command(command, state, client):
    """Handle a /command (the older !command spelling still works)."""
    name, _, arg = command.strip().partition(" ")
    name = "/" + name[1:].lower()
    arg = arg.strip()

    if name == "/history":
        show_command_history()
    elif name == "/clear":
        os.system("clear")
    elif name == "/help":
        show_help()
    elif name == "/models":
        display_models()
    elif name == "/model":
        if not arg:
            console.print(f"Current model: {state['model']}. Use /model <name>; /models lists them.")
            return
        # Keep the original case: model ids like Qwen/Qwen2.5 are case-sensitive.
        state["model"] = arg
        console.print(f"[green]✓ Switched to model: {arg}[/green]")
    elif name == "/mode":
        if arg not in MODES:
            console.print(f"Mode is [bold]{state['mode']}[/bold]. Use /mode " + "|".join(MODES) + " or Shift+Tab.")
            for mode, description in MODES.items():
                console.print(f"  [cyan]{mode}[/cyan]  {description}")
            return
        state["mode"] = arg
        console.print(f"[green]✓ {arg} mode:[/green] {MODES[arg]}")
    elif name == "/explain" and arg:
        safety = check_command_safety(arg)
        console.print(f"[bold]Safety level:[/bold] {safety['status'].upper()} ({safety['notes']})")
        try:
            with console.status("Explaining..."):
                text = explain_command(client, state["model"], arg)
            console.print(text)
        except AIError as e:
            console.print(f"[bold red]Error:[/bold red] {e}")
    elif name == "/notify":
        config = load_config()
        config["notify"] = config.get("notify") is False
        save_config(config)
        console.print(f"Notifications {'on' if config['notify'] else 'off'} (bell and desktop notification when Smart-Shell waits for you).")
    elif name == "/forget-sudo":
        reset_sudo_password()
        console.print("[green]Sudo credentials cleared.[/green]")
    elif name == "/docs":
        console.print("[bold blue]Documentation:[/bold blue] https://smart-shell.lusansapkota.com.np/")
    elif name == "/update":
        handle_update_command()
    elif name == "/last":
        show_last_command()
    elif name == "/redo":
        redo_last_command()
    elif name == "/errors":
        show_error_log()
    else:
        console.print(f"[yellow]Unknown command: {command}. Type / to see commands.[/yellow]")


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

## Commands
{{commands}}

## Keys
- `Tab` or arrow keys - pick from the / command menu
- `Esc` then `Enter` - new line in your request
- `Up` / `Ctrl+R` - previous requests / search them
- `Ctrl+C` - clear the line; `Ctrl+D` or `/exit` - quit

## Safety
Every step is checked before execution:
- **Blocked**: never runs (e.g. `rm -rf /`, fork bombs, formatting disks); edit or cancel
- **High**: destructive, defaults to no (e.g. `rm -rf dir`, piping into a shell)
- **Medium**: changes the system, defaults to no (e.g. `sudo`, package installs, `kill`)
- **Info leak**: may print secrets, defaults to yes
- **Safe**: defaults to yes

Every plan asks yes / no / edit before running. If it fails, you can ask the AI to fix it.

## CLI Usage
- `smart-shell` - Start interactive mode
- `smart-shell "<prompt>"` - Run a one-off request (`-d` dry run, `-m <model>`, `-y` skip prompts)
- `smart-shell setup` - Configure provider, API key and model
- `smart-shell models` - List available models
- `smart-shell history` - Show command history
- `smart-shell version` - Show version information

For more, see the documentation or run `smart-shell --help`.
"""
    md = Markdown(help_text.replace("{commands}", "\n".join(f"- `{c}` - {d}" for c, d in COMMANDS.items())))
    console.print(Panel(md, title="Smart-Shell Help", border_style="blue"))

@cli.command()
def setup():
    """Setup API key and configuration."""
    setup_config()

@cli.command()
def version():
    """Show version information."""
    console.print(f"Smart-Shell v{get_current_version()}")

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
