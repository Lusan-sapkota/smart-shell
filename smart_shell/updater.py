"""
Updater Module - Checks for new versions and upgrades with the tool it was installed by.
"""

import sys
import subprocess
import importlib.metadata
from pathlib import Path
import requests
from rich.console import Console
from rich.prompt import Confirm

from .utils import log_error

console = Console()

PACKAGE = "smart-shell-cli"


def handle_update_command():
    """Handle the !update command."""
    current = get_current_version()
    latest = get_latest_version()
    console.print(f"[blue]Current version: {current}[/blue]")
    if not latest:
        console.print("[yellow]Could not fetch the latest version.[/yellow]")
        return
    console.print(f"[blue]Latest version: {latest}[/blue]")
    if parse_version(current) >= parse_version(latest):
        console.print("[green]You're already using the latest version.[/green]")
        return

    command = upgrade_command()
    if command is None:
        console.print("[yellow]Running from a git checkout: update with 'git pull'.[/yellow]")
        return
    if not Confirm.ask(f"Update with '{' '.join(command)}'?", default=True):
        return
    if subprocess.run(command).returncode == 0:
        console.print("[green]Updated. Restart Smart-Shell to use the new version.[/green]")
    else:
        console.print(f"[red]Update failed. Try running it yourself: {' '.join(command)}[/red]")


def get_current_version():
    """Get the installed package version."""
    try:
        return importlib.metadata.version(PACKAGE)
    except importlib.metadata.PackageNotFoundError:
        return "unknown"


def get_latest_version():
    """Latest version on PyPI, falling back to the latest GitHub release."""
    sources = [
        (f"https://pypi.org/pypi/{PACKAGE}/json", lambda d: d["info"]["version"]),
        ("https://api.github.com/repos/Lusan-sapkota/smart-shell/releases/latest", lambda d: d["tag_name"].lstrip("v")),
    ]
    for url, pick in sources:
        try:
            response = requests.get(url, timeout=10)
            if response.ok:
                return pick(response.json())
        except Exception as e:
            log_error(f"Version check against {url} failed: {e}")
    return None


def parse_version(version):
    """'1.2.3' -> (1, 2, 3); anything unparsable sorts first."""
    try:
        return tuple(int(part) for part in version.lstrip("v").split("."))
    except (AttributeError, ValueError):
        return (0,)


def upgrade_command():
    """The upgrade command for how this copy was installed, or None for a git checkout."""
    if (Path(__file__).resolve().parent.parent / ".git").exists():
        return None
    if "/uv/tools/" in sys.prefix:
        return ["uv", "tool", "upgrade", PACKAGE]
    if "/pipx/venvs/" in sys.prefix:
        return ["pipx", "upgrade", PACKAGE]
    return [sys.executable, "-m", "pip", "install", "--upgrade", PACKAGE]
