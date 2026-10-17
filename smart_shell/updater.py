"""
Updater Module - Checks GitHub for new versions and updates in place.
"""

import os
import re
import sys
import subprocess
import importlib.metadata
from pathlib import Path
import requests
from rich.console import Console
from rich.prompt import Confirm

from .utils import log_error

console = Console()

def handle_update_command():
    """Handle the !update command to check for and install updates."""
    try:
        console.print("[blue]Checking for Smart-Shell updates...[/blue]")
        
        current_version = get_current_version()
        console.print(f"[blue]Current version: {current_version}[/blue]")
        
        latest_version = get_latest_github_version()
        if not latest_version:
            console.print("[yellow]Could not fetch latest version from GitHub.[/yellow]")
            console.print("[dim]Fallback: Try manual update with 'git pull' if in development mode.[/dim]")
            return
        
        console.print(f"[blue]Latest version: {latest_version}[/blue]")
        
        if compare_versions(current_version, latest_version) >= 0:
            console.print("[green]You're already using the latest version![/green]")
            return
        
        console.print(f"[yellow]New version available: {current_version} → {latest_version}[/yellow]")
        
        if not Confirm.ask("Do you want to update to the latest version?", choices=["y", "n"], default="y"):
            console.print("[yellow]Update cancelled.[/yellow]")
            return
        
        project_root = find_project_root()
        if project_root and (project_root / ".git").exists():
            console.print("[blue]Development environment detected. Updating via git...[/blue]")
            success = update_via_git(project_root)
        else:
            console.print("[blue]Installed package detected. Updating via pip...[/blue]")
            success = update_via_pip()
        
        if success:
            console.print("[green]Smart-Shell updated successfully![/green]")
            console.print("[bold yellow]Please restart Smart-Shell to use the new version.[/bold yellow]")
            console.print("[dim]Type 'exit' and run 'smart-shell' again.[/dim]")
        else:
            console.print("[red]Update failed. Please try manual update.[/red]")
            console.print("[yellow]Manual options:[/yellow]")
            console.print("  • Development: [blue]git pull && pip install -e .[/blue]")
            console.print("  • Installed: [blue]pip install --upgrade smart-shell[/blue]")
            
    except Exception as e:
        console.print(f"[red]Error during update: {e}[/red]")
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
            if not v or v == 'unknown':
                return [0, 0, 0]
            v = v.lstrip('v').split('.')
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
        
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if result.stdout.strip():
            console.print("[yellow]You have uncommitted changes. Stashing them...[/yellow]")
            subprocess.run(["git", "stash"], capture_output=True)
        
        console.print("[blue]Pulling latest changes...[/blue]")
        result = subprocess.run(["git", "pull", "origin", "main"], capture_output=True, text=True)
        
        if result.returncode != 0:
            console.print(f"[red]Git pull failed: {result.stderr}[/red]")
            return False
        
        console.print("[blue]Reinstalling package...[/blue]")
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
        console.print("[blue]Updating via pip...[/blue]")
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
