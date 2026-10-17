"""
History Module - Stores and shows generated commands.
"""

import os
import json
from datetime import datetime
from rich.console import Console
from rich.prompt import Confirm
from rich.syntax import Syntax

from .utils import execute_command
from .safety import check_command_safety

console = Console()

HISTORY_DIR = os.path.expanduser("~/.local/share/smart-shell")
HISTORY_FILE = os.path.join(HISTORY_DIR, "history.json")

def save_to_history(prompt, command, executed=False):
    """Save a command to history."""
    os.makedirs(HISTORY_DIR, exist_ok=True)
    
    history_id = datetime.now().strftime("%Y%m%d%H%M%S")
    
    entry = {
        "id": history_id,
        "timestamp": datetime.now().isoformat(),
        "prompt": prompt,
        "command": command,
        "executed": executed,
        "success": None  # Will be updated after execution
    }
    
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                history = json.load(f)
        except:
            history = []
    
    history.append(entry)
    
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)
    
    return history_id

def update_history_result(history_id, success):
    """Update the success status of a history entry."""
    if not os.path.exists(HISTORY_FILE):
        return
    
    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)
    
    for entry in history:
        if entry["id"] == history_id:
            entry["success"] = success
            break
    
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)

def show_command_history():
    """Show the command history."""
    if not os.path.exists(HISTORY_FILE):
        console.print("[yellow]No command history found.[/yellow]")
        return
    
    with open(HISTORY_FILE, "r") as f:
        history = json.load(f)
    
    if not history:
        console.print("[yellow]Command history is empty.[/yellow]")
        return
    
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
        
        if isinstance(command, list):
            blocked = [c for c in command if check_command_safety(c)["status"] == "blocked"]
            if blocked:
                console.print(f"[bold red]Refusing to re-run a blocked command:[/bold red] {blocked[0]}")
                return
            command_to_execute = " && ".join(command)
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
