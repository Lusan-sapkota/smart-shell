"""
Utility functions for Smart-Shell
"""

import os
import subprocess
import sys
import tempfile
import getpass
import shlex
import re
from typing import Dict, Any, Optional, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.markdown import Markdown
from rich.prompt import Prompt
from datetime import datetime

# Import the new config functions
from .config import get_sudo_password

console = Console()

# In-memory storage for a sudo password provided for the current session
SESSION_SUDO_PASSWORD = None

# Error log file
ERROR_LOG_DIR = os.path.expanduser("~/.local/share/smart-shell")
ERROR_LOG_FILE = os.path.join(ERROR_LOG_DIR, "error.log")

def get_session_sudo_password():
    """Gets the sudo password for the current session."""
    return SESSION_SUDO_PASSWORD

def set_session_sudo_password(password):
    """Sets the sudo password for the current session."""
    global SESSION_SUDO_PASSWORD
    SESSION_SUDO_PASSWORD = password

def get_os_info() -> Dict[str, str]:
    """
    Parses /etc/os-release to get Linux distribution information.

    Returns:
        A dictionary containing the OS 'id' and 'name'.
    """
    os_info = {"id": "unknown", "name": "Unknown Linux"}
    try:
        with open("/etc/os-release") as f:
            for line in f:
                if "=" in line:
                    key, value = line.strip().split("=", 1)
                    # Remove quotes from value
                    value = value.strip('"')
                    if key == "ID":
                        os_info["id"] = value
                    elif key == "PRETTY_NAME":
                        os_info["name"] = value
    except FileNotFoundError:
        # For non-Linux systems or if the file is missing
        import platform
        os_info["id"] = platform.system().lower()
        os_info["name"] = platform.system()
    except Exception as e:
        log_error(f"Could not read /etc/os-release: {e}")

    return os_info

def validate_sudo_password(password: str) -> bool:
    """
    Validates the sudo password by running a harmless command.

    Args:
        password (str): The sudo password to validate.

    Returns:
        bool: True if the password is valid, False otherwise.
    """
    if not password:
        return False
    try:
        # Use sudo's -S flag to read password from stdin, and -v to validate the timestamp
        command = f"echo '{password}' | sudo -S -v"
        result = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            executable='/bin/bash'
        )
        # A return code of 0 means the password was accepted
        return result.returncode == 0
    except Exception as e:
        log_error(f"Sudo validation failed unexpectedly: {e}")
        return False

def reset_sudo_password():
    """Reset the stored sudo password."""
    # This function is kept for compatibility but session password is the primary mechanism now
    global SESSION_SUDO_PASSWORD
    SESSION_SUDO_PASSWORD = None

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

def execute_command(command: str) -> bool:
    """
    Execute a shell command, handling sudo and displaying output.
    
    Args:
        command (str): The command to execute.
        
    Returns:
        bool: True if command executed successfully, False otherwise.
    """
    console.print(f"[bold green]Executing:[/bold green] {command}")
    console.print("─" * console.width)

    try:
        # Determine if sudo is needed and prepare the command
        needs_sudo = command.strip().startswith("sudo")
        final_command = command
        shell_type = detect_shell()
        shell_executable = f"/bin/{shell_type}" if shell_type in ("bash", "zsh") else "/bin/bash"
        if needs_sudo:
            # First, try to get password from config file
            sudo_password = get_sudo_password()
            # If not in config, check session password
            if not sudo_password:
                sudo_password = get_session_sudo_password()
            # If still no password, prompt the user once for the session
            if not sudo_password:
                sudo_password = Prompt.ask("Enter your sudo password for this session", password=True)
                set_session_sudo_password(sudo_password)
            # Prepend the password to the command for sudo's -S flag
            final_command = f"echo '{sudo_password}' | sudo -S -p '' {command.replace('sudo', '', 1).strip()}"
        # We use shell=True here because we are now constructing a full shell command
        # with pipes for sudo. This is generally safe as the command has been vetted.
        process = subprocess.Popen(
            final_command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            executable=shell_executable # Use detected shell
        )

        # Stream output
        stdout_text, stderr_text = process.communicate()

        if stdout_text:
            console.print(stdout_text.strip())
        if stderr_text:
            # Don't show the "sudo: password" prompt in stderr
            if "sudo: password" not in stderr_text.lower() and "try again" not in stderr_text.lower():
                 console.print(f"[red]{stderr_text.strip()}[/red]")

        console.print("─" * console.width)

        if process.returncode != 0:
            if "incorrect password attempt" in stderr_text.lower():
                console.print("[bold red]✗ Incorrect sudo password.[/bold red]")
                reset_sudo_password() # Clear the incorrect session password
            elif "no such file or directory" in stderr_text.lower():
                console.print("[bold yellow]✗ Command failed because a file or directory it references does not exist.[/bold yellow]")
            elif "permission denied" in stderr_text.lower():
                console.print("[bold yellow]✗ Permission denied. Try running the command with 'sudo'.[/bold yellow]")
            elif "command not found" in stderr_text.lower():
                missing_command = extract_missing_command(stderr_text)
                if missing_command:
                    console.print(f"[bold yellow]✗ Command '{missing_command}' not found. You may need to install it.[/bold yellow]")
            else:
                console.print(f"[bold red]✗ Command failed with exit code {process.returncode}[/bold red]")
            return False
        else:
            console.print("[bold green]✓ Command executed successfully[/bold green]")
            return True

    except Exception as e:
        log_error(f"Failed to execute command '{command}': {e}")
        console.print(f"[bold red]Error during command execution: {e}[/bold red]")
        return False

def extract_missing_command(error_text: str) -> Optional[str]:
    """Extract the missing command from an error message."""
    match = re.search(r"command not found:\s*(\w+)", error_text) or \
            re.search(r"(\w+):\s*command not found", error_text)
    if match:
        return match.group(1)
    return None

def suggest_package(command: str) -> Optional[str]:
    """Suggest a package that might provide the missing command."""
    # Common command to package mappings
    command_map = {
        "curl": "curl",
        "wget": "wget",
        "git": "git",
        "pip": "python3-pip",
        "pip3": "python3-pip",
        "python": "python3",
        "python3": "python3",
        "node": "nodejs",
        "npm": "npm",
        "docker": "docker.io",
        "java": "default-jre",
        "javac": "default-jdk",
        "mvn": "maven",
        "gradle": "gradle",
        "vim": "vim",
        "nano": "nano",
        "zip": "zip",
        "unzip": "unzip",
        "tar": "tar",
        "ssh": "openssh-client",
        "scp": "openssh-client",
        "rsync": "rsync",
        "nc": "netcat",
        "nmap": "nmap",
        "convert": "imagemagick",
        "ffmpeg": "ffmpeg",
        "gcc": "build-essential",
        "make": "build-essential",
    }
    
    return command_map.get(command, command)

def print_plan_preview(command_plan: list[str], safety_results: list[dict[str, Any]]) -> None:
    """
    Prints a preview of the entire command plan in a table.

    Args:
        command_plan (list[str]): The list of commands to be executed.
        safety_results (list[dict[str, Any]]): The safety check results for each command.
    """
    table = Table(title="[bold]Execution Plan[/bold]", show_header=True, header_style="bold magenta")
    table.add_column("Step", style="dim", width=5)
    table.add_column("Command", style="cyan")
    table.add_column("Safety Level", style="bold")
    table.add_column("Details")

    color_map = {"safe": "green", "medium": "yellow", "high": "red"}

    for i, (command, result) in enumerate(zip(command_plan, safety_results)):
        status = result.get("status", "safe")
        notes = result.get("notes", "No details.")
        color = color_map.get(status, "white")
        table.add_row(
            str(i + 1),
            command,
            f"[{color}]{status.upper()}[/{color}]",
            notes
        )
    
    console.print(table)

def print_command_preview(command: str, safety_result: Dict[str, Any]) -> None:
    """Print a preview of the command with syntax highlighting and safety info."""
    status = safety_result.get("status", "safe")
    reason = safety_result.get("notes", "No notes.")
    
    color_map = {
        "safe": "green",
        "medium": "yellow",
        "high": "red"
    }
    color = color_map.get(status, "white")

    # Create a panel with the safety info
    preview_panel = Panel(
        f"[bold]Command:[/bold] [cyan]{command}[/cyan]\n"
        f"[bold]Safety Level:[/bold] [{color}]{status.upper()}[/{color}]\n"
        f"[bold]Details:[/bold] {reason}",
        title="Command Preview",
        border_style=color,
        expand=False
    )
    console.print(preview_panel)

def format_help_text(text: str) -> None:
    """DEPRECATED: No longer needed with rich text."""
    md = Markdown(text)
    console.print(md)
    
def get_terminal_size() -> Dict[str, int]:
    """Get the size of the terminal."""
    return {
        "width": console.width,
        "height": console.height
    }

def log_error(error_message):
    """Logs an error message to the error log file."""
    try:
        os.makedirs(ERROR_LOG_DIR, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(ERROR_LOG_FILE, "a") as f:
            f.write(f"[{timestamp}] {error_message}\n")
    except Exception as e:
        console.print(f"[bold red]Failed to write to error log: {e}[/bold red]")