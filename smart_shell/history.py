"""
History Module - Stores and shows generated commands.
"""

import os
import json
import uuid
from datetime import datetime
from rich.console import Console
from rich.prompt import Confirm
from rich.syntax import Syntax

from .utils import execute_command
from .safety import check_command_safety

console = Console()

HISTORY_DIR = os.path.expanduser("~/.local/share/smart-shell")
HISTORY_FILE = os.path.join(HISTORY_DIR, "history.json")

MAX_ENTRIES = 1000


def load_history():
    try:
        with open(HISTORY_FILE) as f:
            history = json.load(f)
        return history if isinstance(history, list) else []
    except (OSError, ValueError):
        return []


def write_history(history):
    os.makedirs(HISTORY_DIR, exist_ok=True)
    # Prompts can contain secrets: owner read/write only.
    fd = os.open(HISTORY_FILE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    os.fchmod(fd, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(history[-MAX_ENTRIES:], f, indent=2)


def save_to_history(prompt, command, executed=False):
    """Append an entry and return its id."""
    history_id = uuid.uuid4().hex
    history = load_history()
    history.append({
        "id": history_id,
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "command": command,
        "executed": executed,
        "success": None,
    })
    write_history(history)
    return history_id


def update_history_result(history_id, success):
    """Record whether an entry's command succeeded."""
    history = load_history()
    for entry in history:
        if entry.get("id") == history_id:
            entry["success"] = success
            write_history(history)
            return


def as_text(command):
    return " && ".join(command) if isinstance(command, list) else str(command)


def show_command_history():
    """Show the last 10 entries."""
    history = load_history()
    if not history:
        console.print("[yellow]No command history yet.[/yellow]")
        return
    console.print("[bold]Command History:[/bold]")
    for i, entry in enumerate(reversed(history[-10:]), 1):
        timestamp = datetime.fromisoformat(entry["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
        status = {True: "[green]✓[/green]", False: "[red]✗[/red]"}.get(entry.get("success"), "[yellow]?[/yellow]")
        if not entry.get("executed"):
            status = "[dim]dry run[/dim]"
        console.print(f"{i}. {status} [blue]{timestamp}[/blue]")
        console.print(f"   Prompt: {entry['prompt']}")
        console.print("   Command: ", end="")
        console.print(Syntax(as_text(entry["command"]), "bash", theme="monokai"))
        console.print("")


def show_last_command():
    """Show the last generated command."""
    history = load_history()
    if not history:
        console.print("[yellow]No command history yet.[/yellow]")
        return
    console.print(f"[blue]Prompt:[/blue] {history[-1]['prompt']}")
    console.print(Syntax(as_text(history[-1]["command"]), "bash", theme="monokai"))


def redo_last_command():
    """Re-run the last plan after a safety check and confirmation."""
    history = load_history()
    if not history:
        console.print("[yellow]No command history yet.[/yellow]")
        return
    command = history[-1]["command"]
    steps = command if isinstance(command, list) else [command]
    blocked = [c for c in steps if check_command_safety(c)["status"] == "blocked"]
    if blocked:
        console.print(f"[bold red]Refusing to re-run a blocked command:[/bold red] {blocked[0]}")
        return
    console.print(f"[blue]Re-running:[/blue] {as_text(command)}")
    if Confirm.ask("Run it?", default=True):
        execute_command(as_text(command))
