#!/usr/bin/env python3
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

console = Console()

# Store sudo password securely in memory
_sudo_password = None

def get_sudo_password():
    """Get the sudo password from the user, storing it securely in memory."""
    global _sudo_password
    if _sudo_password is None:
        _sudo_password = Prompt.ask("Enter your sudo password (needed for privileged commands)", password=True)
    return _sudo_password

def reset_sudo_password():
    """Reset the stored sudo password."""
    global _sudo_password
    _sudo_password = None

def execute_command(command: str) -> bool:
    """
    Execute a shell command and display the output.
    
    Args:
        command (str): The command to execute
        
    Returns:
        bool: True if command executed successfully, False otherwise
    """
    try:
        console.print(f"[bold green]Executing:[/bold green] {command}")
        console.print("─" * console.width)
        
        # Check if command needs sudo
        needs_sudo = command.strip().startswith("sudo ")
        
        # Create a temporary script file
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.sh', delete=False) as script_file:
            script_path = script_file.name
            script_file.write("#!/bin/bash\n")
            script_file.write("set -e\n")  # Exit on error
            
            # If command needs sudo, modify it to use the stored password
            if needs_sudo:
                # Remove sudo from the command as we'll handle it differently
                actual_command = re.sub(r'^sudo\s+', '', command)
                script_file.write(actual_command)
            else:
                script_file.write(command)
            
            script_file.write("\n")
        
        # Make the script executable
        os.chmod(script_path, 0o755)
        
        # Execute the script
        if needs_sudo:
            # Get sudo password if needed
            sudo_password = get_sudo_password()
            
            # Use sudo with password via stdin
            process = subprocess.Popen(
                ["sudo", "-S", script_path],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=False,
                bufsize=1,
                universal_newlines=True
            )
            
            # Send password to stdin
            if process.stdin:
                process.stdin.write(sudo_password + "\n")
                process.stdin.flush()
        else:
            # Normal execution without sudo
            process = subprocess.Popen(
                [script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=False,
                bufsize=1,
                universal_newlines=True
            )
        
        # Stream output in real-time
        stdout_lines = []
        stderr_lines = []
        
        while True:
            stdout_line = process.stdout.readline() if process.stdout else ""
            stderr_line = process.stderr.readline() if process.stderr else ""
            
            if not stdout_line and not stderr_line and process.poll() is not None:
                break
                
            if stdout_line:
                stdout_lines.append(stdout_line)
                console.print(stdout_line.rstrip())
                
            if stderr_line:
                stderr_lines.append(stderr_line)
                # Don't show password prompt in stderr output
                if not "password for" in stderr_line:
                    console.print(f"[red]{stderr_line.rstrip()}[/red]")
                
        # Get the return code
        return_code = process.poll()
        
        # Clean up the temporary script
        os.unlink(script_path)
        
        console.print("─" * console.width)
        
        # Handle specific error cases
        if return_code != 0:
            stderr_text = "".join(stderr_lines)
            
            # Check for common errors and suggest solutions
            if "command not found" in stderr_text:
                missing_command = extract_missing_command(stderr_text)
                if missing_command:
                    console.print(f"[yellow]Command '{missing_command}' not found. Would you like to install it?[/yellow]")
                    if Prompt.ask("Attempt to install?", choices=["y", "n"], default="y") == "y":
                        package_name = suggest_package(missing_command)
                        if package_name:
                            console.print(f"[blue]Attempting to install {package_name}...[/blue]")
                            install_command = f"sudo apt-get update && sudo apt-get install -y {package_name}"
                            execute_command(install_command)
                            console.print(f"[green]Installation complete. Retrying original command...[/green]")
                            return execute_command(command)
            
            # Check for permission denied
            elif "permission denied" in stderr_text.lower():
                console.print("[yellow]Permission denied. Would you like to retry with sudo?[/yellow]")
                if Prompt.ask("Retry with sudo?", choices=["y", "n"], default="y") == "y":
                    if not command.strip().startswith("sudo "):
                        return execute_command(f"sudo {command}")
            
            # Check for incorrect sudo password
            elif "sorry, try again" in stderr_text.lower():
                console.print("[yellow]Incorrect sudo password. Please try again.[/yellow]")
                reset_sudo_password()
                return execute_command(command)
                
            console.print(f"[bold red]✗ Command failed with exit code {return_code}[/bold red]")
            return False
        else:
            console.print("[bold green]✓ Command executed successfully[/bold green]")
            return True
            
    except Exception as e:
        console.print(f"[bold red]Error executing command:[/bold red] {str(e)}")
        
        # Try to recover from common errors
        if "No such file or directory" in str(e):
            console.print("[yellow]Checking if this is a path issue...[/yellow]")
            parts = shlex.split(command)
            for part in parts:
                if os.path.sep in part and not os.path.exists(part):
                    console.print(f"[yellow]Path not found: {part}[/yellow]")
                    parent_dir = os.path.dirname(part)
                    if not os.path.exists(parent_dir):
                        console.print(f"[yellow]Parent directory doesn't exist. Create it?[/yellow]")
                        if Prompt.ask("Create directory?", choices=["y", "n"], default="y") == "y":
                            try:
                                os.makedirs(parent_dir, exist_ok=True)
                                console.print(f"[green]Created directory: {parent_dir}[/green]")
                                console.print("[green]Retrying command...[/green]")
                                return execute_command(command)
                            except Exception as create_err:
                                console.print(f"[red]Failed to create directory: {str(create_err)}[/red]")
        
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

def print_command_preview(command: str, safety_result: Dict[str, Any]) -> None:
    """Print a preview of the command with syntax highlighting and safety info."""
    # Create a table for command preview
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Label", style="bold")
    table.add_column("Content")
    
    # Add command with syntax highlighting
    syntax = Syntax(command, "bash", theme="monokai", line_numbers=False)
    table.add_row("Command:", syntax)
    
    # Add safety status with appropriate color
    status = safety_result["status"]
    if status == "safe":
        status_text = "[bold green]🟢 Safe[/bold green]"
    elif status == "warning":
        status_text = "[bold yellow]🟡 Warning[/bold yellow]"
    else:
        status_text = "[bold red]🔴 Blocked[/bold red]"
        
    table.add_row("Safety:", status_text)
    
    # Add notes if available
    if safety_result.get("notes"):
        table.add_row("Notes:", safety_result["notes"])
    
    # Display the table in a panel
    console.print(Panel(
        table,
        title="Command Preview",
        border_style="blue"
    ))
    
def format_help_text(text: str) -> None:
    """Format and display help text using Markdown."""
    md = Markdown(text)
    console.print(md)
    
def get_terminal_size() -> Dict[str, int]:
    """Get the size of the terminal."""
    return {
        "width": console.width,
        "height": console.height
    } 