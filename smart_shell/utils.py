"""
Utility functions for Smart-Shell
"""

import os
import json
import shutil
import time
import sys
import subprocess
import re
from typing import Dict, Any, Optional, Tuple
from rich.console import Console
from rich.markup import escape
from rich.table import Table
from rich.text import Text
from datetime import datetime

from .config import load_config

console = Console()

ERROR_LOG_DIR = os.path.expanduser("~/.local/share/smart-shell")
ERROR_LOG_FILE = os.path.join(ERROR_LOG_DIR, "error.log")

def get_os_info() -> Dict[str, str]:
    """Parses /etc/os-release to get Linux distribution information."""
    os_info = {"id": "unknown", "name": "Unknown Linux"}
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    value = value.strip('"')
                    if key == "ID":
                        os_info["id"] = value
                    elif key == "PRETTY_NAME":
                        os_info["name"] = value
    except FileNotFoundError:
        import platform
        os_info["id"] = platform.system().lower()
        os_info["name"] = platform.system()
    except Exception as e:
        log_error(f"Could not read /etc/os-release: {e}")

    return os_info

def reset_sudo_password():
    """Drop sudo's cached credentials so the next sudo asks again."""
    subprocess.run(["sudo", "-k"], check=False)

def detect_shell() -> str:
    """Detect the user's current shell (bash, zsh, etc)."""
    shell = os.environ.get("SHELL", "").lower()
    if "zsh" in shell:
        return "zsh"
    elif "bash" in shell:
        return "bash"
    elif shell:
        return shell.split("/")[-1]
    else:
        return "bash"  # Default fallback

def execute_command(command: str) -> Tuple[bool, str]:
    """Run a shell command with live output. Returns (success, tail of stderr)."""
    console.print(f"[bold green]Executing:[/bold green] {escape(command)}")
    console.print("─" * console.width)

    try:
        # sudo prompts on the terminal itself, so the password never passes through us.
        shell_type = detect_shell()
        shell_executable = f"/bin/{shell_type}" if shell_type in ("bash", "zsh") else "/bin/bash"
        # stdout goes straight to the terminal so output is live and prompts (apt's y/n) work.
        # stderr is echoed live too, keeping the tail for the error hints below.
        process = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE, executable=shell_executable)
        tail = b""
        try:
            for chunk in iter(lambda: os.read(process.stderr.fileno(), 4096), b""):
                sys.stderr.buffer.write(chunk)
                sys.stderr.flush()
                tail = (tail + chunk)[-4096:]
            process.wait()
        except KeyboardInterrupt:
            # Ctrl+C already reached the command (same process group); stop it, keep Smart-Shell running.
            process.kill()
            process.wait()
            console.print("\n[yellow]Interrupted.[/yellow]")
            return False, "interrupted by user"
        stderr_text = tail.decode(errors="replace")

        console.print("─" * console.width)

        if process.returncode != 0:
            if "incorrect password attempt" in stderr_text.lower():
                console.print("[bold red]✗ Incorrect sudo password.[/bold red]")
            elif "no such file or directory" in stderr_text.lower():
                console.print("[bold yellow]✗ Command failed because a file or directory it references does not exist.[/bold yellow]")
            elif "permission denied" in stderr_text.lower():
                console.print("[bold yellow]✗ Permission denied. Try running the command with 'sudo'.[/bold yellow]")
            elif "command not found" in stderr_text.lower():
                missing_command = extract_missing_command(stderr_text)
                if missing_command:
                    console.print(f"[bold yellow]✗ Command '{escape(missing_command)}' not found. You may need to install it.[/bold yellow]")
            else:
                console.print(f"[bold red]✗ Command failed with exit code {process.returncode}[/bold red]")
            return False, stderr_text
        else:
            console.print("[bold green]✓ Command executed successfully[/bold green]")
            return True, stderr_text

    except Exception as e:
        log_error(f"Failed to execute command '{command}': {e}")
        console.print(f"[bold red]Error during command execution: {escape(str(e))}[/bold red]")
        return False, str(e)

def extract_missing_command(error_text: str) -> Optional[str]:
    """Extract the missing command from an error message."""
    match = re.search(r"command not found:\s*(\w+)", error_text) or \
            re.search(r"(\w+):\s*command not found", error_text)
    if match:
        return match.group(1)
    return None


def print_plan_preview(command_plan: list[str], safety_results: list[dict[str, Any]]) -> None:
    """Prints a preview of the entire command plan in a table."""
    table = Table(title="[bold]Execution Plan[/bold]", show_header=True, header_style="bold magenta")
    table.add_column("Step", style="dim", width=5)
    table.add_column("Command", style="cyan")
    table.add_column("Safety Level", style="bold")
    table.add_column("Details")

    color_map = {"safe": "green", "info_leak": "blue", "medium": "yellow", "high": "red", "blocked": "bold red"}

    for i, (command, result) in enumerate(zip(command_plan, safety_results)):
        status = result.get("status", "safe")
        notes = result.get("notes", "No details.")
        color = color_map.get(status, "white")
        table.add_row(
            str(i + 1),
            Text(command),
            f"[{color}]{status.upper()}[/{color}]",
            notes
        )
    
    console.print(table)


NOTIFY_AFTER = 5  # seconds without input before a desktop notification is worth sending
_last_input = time.monotonic()


def mark_input() -> None:
    """Record that the user just typed something."""
    global _last_input
    _last_input = time.monotonic()


def notify(message: str) -> None:
    """Tell the user Smart-Shell is waiting, in whatever way their terminal supports."""
    if not sys.stdout.isatty() or load_config().get("notify") is False:
        return
    message = message.replace("\a", "").replace("\033", "")
    env = os.environ
    escape = ""
    if env.get("VTE_VERSION") or env.get("TERM_PROGRAM") in ("ghostty", "WezTerm"):
        escape = f"\033]777;notify;Smart-Shell;{message}\a"
    elif env.get("TERM_PROGRAM") == "iTerm.app" or env.get("WT_SESSION"):
        escape = f"\033]9;Smart-Shell: {message}\a"
    # The bell always: terminals flash, beep or mark the tab.
    sys.stdout.write("\a" + escape)
    sys.stdout.flush()
    if escape or time.monotonic() - _last_input < NOTIFY_AFTER or env.get("SSH_CONNECTION"):
        return
    # Konsole, kitty, Alacritty, xterm, Terminal.app...: no escape code, so use the desktop's notifier.
    if sys.platform == "darwin" and shutil.which("osascript"):
        command = ["osascript", "-e", f"display notification {json.dumps(message)} with title \"Smart-Shell\""]
    elif (env.get("DISPLAY") or env.get("WAYLAND_DISPLAY")) and shutil.which("notify-send"):
        command = ["notify-send", "--app-name=Smart-Shell", "--icon=utilities-terminal", "--expire-time=8000",
                   "Smart-Shell", message]
    else:
        return
    subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)


def log_error(error_message):
    """Logs an error message to the error log file."""
    try:
        os.makedirs(ERROR_LOG_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(ERROR_LOG_FILE, "a") as f:
            f.write(f"[{timestamp}] {error_message}\n")
    except Exception as e:
        console.print(f"[bold red]Failed to write to error log: {e}[/bold red]")