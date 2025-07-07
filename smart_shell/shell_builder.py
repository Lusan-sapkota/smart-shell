"""
Shell Builder Module - Generates shell commands from natural language prompts.
"""

import os
import sys
import time
import re
import json
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.style import Style
from rich.align import Align
from rich.prompt import Confirm
from rich.table import Table
from rich.box import ROUNDED, DOUBLE, HEAVY
from rich.columns import Columns

# Import our AI wrapper
from .ai_wrapper import get_wrapper

console = Console()

# ASCII art banner
BANNER = r"""
    _____                      _      _____ _          _ _                  
   / ____|                    | |    / ____| |        | | |                 
  | (___  _ __ ___   __ _ _ __| |_  | (___ | |__   ___| | |                 
   \___ \| '_ ` _ \ / _` | '__| __|  \___ \| '_ \ / _ \ | |                 
   ____) | | | | | | (_| | |  | |_   ____) | | | |  __/ | |                 
  |_____/|_| |_| |_|\__,_|_|   \__| |_____/|_| |_|\___|_|_|                 

  Natural Language → Bash/Zsh Commands
"""

# Maximum number of retries for command generation
MAX_RETRIES = 3
# Delay between retries (in seconds)
RETRY_DELAY = 2

def generate_command_plan(prompt, api_key, model=None, os_info=None, shell_type=None, max_retries=MAX_RETRIES):
    """
    Generates a sequence of shell commands (a plan) from a natural language prompt.

    Args:
        prompt (str): Natural language prompt.
        api_key (str): API key for Gemini.
        model (str, optional): Model to use. Defaults to None.
        os_info (dict, optional): Information about the user's OS.
        shell_type (str, optional): The user's shell ("bash" or "zsh").
        max_retries (int, optional): Maximum number of retries. Defaults to MAX_RETRIES.

    Returns:
        list[str]: A list of shell commands.
    """
    if os_info is None:
        os_info = {"name": "a generic Linux system", "id": "linux"}

    # Detect shell type (bash or zsh) from os_info or environment
    shell_type = os_info.get('shell', None)
    if not shell_type:
        shell_type = os.environ.get('SHELL', '/bin/bash')
        if 'zsh' in shell_type:
            shell_type = 'zsh'
        else:
            shell_type = 'bash'

    # Enhanced system prompt for maximum intelligence and capability
    system_prompt = f"""
    You are Smart-Shell, an advanced Linux/Unix command-line intelligence system. You are NOT just a wrapper - you are a sophisticated tool that understands context, solves complex problems, and generates robust automation solutions.

    SYSTEM CONTEXT:
    - OS: {os_info.get('name', 'Linux system')} ({os_info.get('id', 'linux')})
    - Shell: {shell_type}
    - Package Manager: {'apt' if 'ubuntu' in os_info.get('id', '').lower() or 'debian' in os_info.get('id', '').lower() else 'auto-detect'}

    CORE INTELLIGENCE PRINCIPLES:
    1. MAXIMUM HELPFULNESS - Be resourceful, creative, and solution-oriented
    2. DEEP UNDERSTANDING - Interpret intent, context, and implicit requirements
    3. ROBUST ENGINEERING - Generate reliable, error-resistant commands
    4. COMPREHENSIVE SOLUTIONS - Handle complex multi-step workflows
    5. TOOL MASTERY - Utilize the full power of Unix/Linux ecosystem
    6. MODERN BEST PRACTICES - Use current techniques and optimizations
    7. ADAPTIVE INTELLIGENCE - Work across different environments and constraints

    ADVANCED CAPABILITIES (Utilize ALL of these):
    ✓ Complex file operations: find, grep, sed, awk, sort, uniq, cut, tr
    ✓ System administration: systemctl, ps, top, htop, netstat, ss, lsof
    ✓ Development workflows: git, docker, make, cmake, npm, pip, cargo
    ✓ Text processing: regex patterns, data extraction, formatting
    ✓ Network operations: curl, wget, ssh, scp, rsync, ping, traceroute
    ✓ Archive management: tar, gzip, zip, 7z with optimal compression
    ✓ Performance analysis: iostat, vmstat, sar, perf, strace
    ✓ Database operations: mysql, psql, sqlite3, redis-cli
    ✓ Web automation: API calls, scraping, data processing
    ✓ Process management: jobs, nohup, screen, tmux
    ✓ Security tools: chmod, chown, sudo, gpg, openssl
    ✓ Monitoring: watch, tail, journalctl, dmesg

    INTELLIGENCE ENHANCEMENT:
    - Generate multiple alternative approaches when beneficial
    - Handle edge cases and error conditions proactively
    - Use advanced shell features: process substitution, arrays, functions
    - Optimize for performance and resource efficiency
    - Chain commands intelligently with pipes and redirections
    - Include progress indicators for long operations
    - Provide fallback options for missing tools
    - Use modern command options and flags

    RESPONSE FORMAT: Always return valid JSON with "commands" array. Only use "reason" for genuinely unsafe operations.

    SAFETY: Block only truly destructive operations (rm -rf /, mkfs, dd to system devices). Be helpful, not restrictive.

    ADVANCED EXAMPLES:
    User: "analyze log files for errors in the last hour"
    Response: {{"commands": ["find /var/log -name '*.log' -newermt '1 hour ago' -exec grep -l -i 'error\\|fail\\|exception' {{}} \\; | head -10 | xargs -I {{}} sh -c 'echo \"=== {{}} ===\"; grep -i \"error\\|fail\\|exception\" \"{{}}\" | tail -5'"]}}

    User: "setup development environment for python project"
    Response: {{"commands": ["python3 -m venv venv", "source venv/bin/activate", "pip install --upgrade pip", "pip install black flake8 pytest", "echo 'venv/' >> .gitignore", "echo 'Development environment ready! Activate with: source venv/bin/activate'"]}}
    """

    retries = 0
    last_error = "Unknown error occurred"

    while retries <= max_retries:
        try:
            wrapper = get_wrapper(api_key)
            model_to_use = model if model else "models/gemini-2.5-flash"
            model_obj = wrapper.get_model(model_to_use)

            response = wrapper.generate_content(
                model_obj,
                [system_prompt, prompt],
                retry=True,
                temperature=0.3,  # Optimal balance of creativity and precision
                top_p=0.95,       # High diversity for comprehensive solutions
                top_k=60,         # More options for advanced command generation
                max_output_tokens=3000,  # Generous limit for complex multi-step operations
            )

            raw_text = None
            if response and hasattr(response, 'text') and response.text:
                raw_text = response.text.strip()
            
            if not raw_text:
                from .utils import log_error
                log_error(f"AI model returned an empty response. Full response object: {response}")
                raise ValueError("The AI model returned an empty response. This may be due to a safety filter or an unclear prompt. Please try rephrasing your request.")
            
            # Find the JSON part of the response
            json_match = re.search(r'\{.*\}', raw_text, re.DOTALL)
            if not json_match:
                raise ValueError("The AI model did not return a valid JSON object.")
            
            parsed_json = json.loads(json_match.group(0))

            if "reason" in parsed_json and not parsed_json.get("commands"):
                raise Exception(f"Request blocked by AI for safety: {parsed_json['reason']}")

            commands = parsed_json.get("commands", [])
            if not isinstance(commands, list) or not all(isinstance(cmd, str) for cmd in commands):
                raise ValueError("The AI model returned an invalid command structure.")
            
            return commands

        except json.JSONDecodeError:
            last_error = "Failed to decode the AI's response as JSON. Retrying..."
            retries += 1
            time.sleep(RETRY_DELAY)
        except Exception as e:
            last_error = str(e)
            error_msg = last_error.lower()
            if "quota" in error_msg or "rate limit" in error_msg or "network" in error_msg or "connection" in error_msg or "timeout" in error_msg or "internet" in error_msg:
                if retries >= max_retries:
                    break
                console.print(f"[yellow]Error: {last_error}[/yellow]")
                console.print(f"[yellow]Retrying ({retries+1}/{max_retries})...[/yellow]")
                time.sleep(RETRY_DELAY)
                retries += 1
            else:
                break

    raise Exception(f"Error generating command plan: {last_error}")

def display_banner():
    """Display the Smart-Shell banner with improved styling."""
    # Create a styled version of the banner with gradient colors
    styled_banner = Text()
    lines = BANNER.strip().split('\n')
    
    # Apply blue gradient to the ASCII art
    for i, line in enumerate(lines):
        if i < 6:  # The ASCII art part
            styled_banner.append(line + "\n", style=f"bold bright_blue")
        else:  # The tagline
            styled_banner.append(line, style="bold cyan")
    
    # Create a panel with double-line border and a professional look
    panel = Panel(
        Align.center(styled_banner),
        box=DOUBLE,
        border_style="bright_blue",
        padding=(1, 2),
        title="[bold white]Smart-Shell[/bold white]",
        title_align="center",
        subtitle="[bold white]Powered by Google Gemini[/bold white]",
        subtitle_align="center"
    )
    
    console.print(panel)

def create_command_section(title, commands):
    """Create a section of commands for the welcome message."""
    content = ""
    for cmd, desc in commands:
        content += f"  [bold cyan]{cmd}[/bold cyan] - {desc}\n"
    
    return Panel(
        content,
        title=f"[bold white]{title}[/bold white]",
        border_style="blue",
        box=ROUNDED,
        padding=(0, 1),
        expand=False
    )

def display_welcome_message(shell_type="bash"):
    """Display a welcome message with helpful information."""
    # Create a comprehensive welcome message in a single block
    welcome_content = f"""[bold blue]Detected shell:[/bold blue] [green]{shell_type}[/green]

[bold white]Welcome to Smart-Shell![/bold white]
Type your requests in natural language to convert them into shell commands.

[bold cyan]Special Commands:[/bold cyan]
  [cyan]!help[/cyan] - Show detailed help      [cyan]!history[/cyan] - Command history     [cyan]!models[/cyan] - List AI models
  [cyan]!clear[/cyan] - Clear screen          [cyan]!model <name>[/cyan] - Switch model   [cyan]!docs[/cyan] - Documentation
  [cyan]!last[/cyan] - Show last command      [cyan]!redo[/cyan] - Re-execute last       [cyan]!errors[/cyan] - Show error log
  [cyan]!forget-sudo[/cyan] - Clear sudo      [cyan]!creator[/cyan] - About creator       [cyan]!web[/cyan] - Toggle web search
  [cyan]!update[/cyan] - Check for updates

[bold green]Configuration Commands:[/bold green]
  [green]smart-shell setup[/green] - Configure API key    [green]smart-shell version[/green] - Show version
  [green]smart-shell --help[/green] - Show CLI help      [green]smart-shell models[/green] - List models

[bold yellow]Exit Commands:[/bold yellow] [cyan]exit[/cyan], [cyan]quit[/cyan], [cyan]bye[/cyan], [cyan]q[/cyan], or [cyan]Ctrl+C[/cyan]

[italic]Note: Commands are safety-checked before execution. Premium models may incur costs.
Configuration commands should be run outside Smart-Shell (exit first).[/italic]"""
    
    # Main welcome panel with all information in one block
    welcome_panel = Panel(
        welcome_content,
        title="[bold white]Smart Terminal Assistant[/bold white]",
        border_style="green",
        box=HEAVY,
        padding=(1, 2),
        expand=True
    )
    
    console.print(welcome_panel)

if __name__ == "__main__":
    # This allows the module to be run directly for testing
    display_banner()
    display_welcome_message()
    console.print("[yellow]Shell Builder module - For testing only[/yellow]")
    console.print("Use 'smart-shell' command or main.py to run the application.")