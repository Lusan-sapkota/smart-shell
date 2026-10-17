"""
Shell Builder Module - Generates shell commands from natural language prompts.
"""

import os
import re
import json
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.box import ROUNDED, DOUBLE, HEAVY

console = Console()

BANNER = r"""
    _____                      _      _____ _          _ _                  
   / ____|                    | |    / ____| |        | | |                 
  | (___  _ __ ___   __ _ _ __| |_  | (___ | |__   ___| | |                 
   \___ \| '_ ` _ \ / _` | '__| __|  \___ \| '_ \ / _ \ | |                 
   ____) | | | | | | (_| | |  | |_   ____) | | | |  __/ | |                 
  |_____/|_| |_| |_|\__,_|_|   \__| |_____/|_| |_|\___|_|_|                 

  Natural Language → Bash/Zsh Commands
"""

# Retries when the model's reply is not valid JSON (network retries live in the client)
MAX_RETRIES = 2

def parse_plan(text):
    """Pull {"commands": [...]} out of a model reply, tolerating common small-model mistakes."""
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        raw = match.group(0)
        for candidate in (raw, re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', raw)):
            try:
                return json.loads(candidate)
            except json.JSONDecodeError:
                pass
    # Ignored the JSON instruction and answered with a ```bash block instead.
    fence = re.search(r'```(?:bash|sh|zsh|shell)?\n(.*?)```', text, re.DOTALL)
    if fence:
        commands = [l.strip() for l in fence.group(1).splitlines() if l.strip() and not l.strip().startswith("#")]
        if commands:
            return {"commands": commands}
    return None


def format_session_context(session, limit=5):
    """Earlier requests this session, so follow-ups like "same for /var/log" resolve."""
    lines = []
    for entry in session[-limit:]:
        lines.append(f"- Request: {entry['prompt']}\n  Commands: {' && '.join(entry['commands'])}\n  Result: {entry['result']}")
    return "Earlier in this session:\n" + "\n".join(lines) if lines else ""


def generate_command_plan(prompt, client, model, os_info=None, session=None):
    """Generates a sequence of shell commands (a plan) from a natural language prompt."""
    if os_info is None:
        os_info = {"name": "a generic Linux system", "id": "linux"}

    shell_type = os_info.get('shell', None)
    if not shell_type:
        shell_type = os.environ.get('SHELL', '/bin/bash')
        if 'zsh' in shell_type:
            shell_type = 'zsh'
        else:
            shell_type = 'bash'

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

    context = format_session_context(session or [])
    user_message = f"{context}\n\nNew request: {prompt}" if context else prompt

    last_error = None
    for _ in range(MAX_RETRIES + 1):
        raw_text = client.chat(model, system_prompt, user_message)
        if not raw_text:
            raise ValueError("The AI model returned an empty response. Please try rephrasing your request.")

        parsed_json = parse_plan(raw_text)
        if parsed_json is None:
            last_error = "The AI model did not return a usable plan."
            continue

        if "reason" in parsed_json and not parsed_json.get("commands"):
            raise Exception(f"Request blocked by AI for safety: {parsed_json['reason']}")

        commands = parsed_json.get("commands", [])
        if not isinstance(commands, list) or not all(isinstance(cmd, str) for cmd in commands):
            raise ValueError("The AI model returned an invalid command structure.")
        return commands

    raise Exception(f"Error generating command plan: {last_error}")

def explain_command(client, model, command):
    """Plain-English explanation of a shell command."""
    system = ("Explain what this shell command does, step by step, in plain language. "
              "Point out anything destructive or surprising. Be brief. No markdown headings.")
    return client.chat(model, system, command, max_tokens=800)


def display_banner():
    """Display the Smart-Shell banner with improved styling."""
    styled_banner = Text()
    lines = BANNER.strip().split('\n')
    
    for i, line in enumerate(lines):
        if i < 6:  # The ASCII art part
            styled_banner.append(line + "\n", style=f"bold bright_blue")
        else:  # The tagline
            styled_banner.append(line, style="bold cyan")
    
    panel = Panel(
        Align.center(styled_banner),
        box=DOUBLE,
        border_style="bright_blue",
        padding=(1, 2),
        title="[bold white]Smart-Shell[/bold white]",
        title_align="center",
        subtitle="[bold white]Any OpenAI-compatible model, local or cloud[/bold white]",
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
    welcome_content = f"""[bold blue]Detected shell:[/bold blue] [green]{shell_type}[/green]

[bold white]Welcome to Smart-Shell![/bold white]
Type your requests in natural language to convert them into shell commands.

[bold cyan]Special Commands:[/bold cyan]
  [cyan]!help[/cyan] - Show detailed help      [cyan]!history[/cyan] - Command history     [cyan]!models[/cyan] - List AI models
  [cyan]!clear[/cyan] - Clear screen          [cyan]!model <name>[/cyan] - Switch model   [cyan]!docs[/cyan] - Documentation
  [cyan]!last[/cyan] - Show last command      [cyan]!redo[/cyan] - Re-execute last       [cyan]!errors[/cyan] - Show error log
  [cyan]!forget-sudo[/cyan] - Clear sudo      [cyan]!creator[/cyan] - About creator       [cyan]!web[/cyan] - Toggle web search
  [cyan]!explain <cmd>[/cyan] - Explain a command  [cyan]!update[/cyan] - Check for updates

[bold green]Configuration Commands:[/bold green]
  [green]smart-shell setup[/green] - Configure provider   [green]smart-shell version[/green] - Show version
  [green]smart-shell --help[/green] - Show CLI help      [green]smart-shell models[/green] - List models

[bold yellow]Exit Commands:[/bold yellow] [cyan]exit[/cyan], [cyan]quit[/cyan], [cyan]bye[/cyan], [cyan]q[/cyan], or [cyan]Ctrl+C[/cyan]

[italic]Note: Commands are safety-checked before execution. Cloud providers may bill per request.
Configuration commands should be run outside Smart-Shell (exit first).[/italic]"""
    
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
    display_banner()
    display_welcome_message()
    console.print("[yellow]Shell Builder module - For testing only[/yellow]")
    console.print("Use 'smart-shell' command or main.py to run the application.")