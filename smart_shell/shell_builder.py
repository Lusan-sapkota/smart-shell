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

    # System prompt to instruct the model to act as a planner
    system_prompt = f"""
    You are an expert Linux Task Planner. Your task is to convert a user's natural language request into a sequence of shell commands that will accomplish the goal.

    The user is running: {os_info.get('name', 'a generic Linux system')}.
    The OS ID is: {os_info.get('id', 'linux')}.
    The user's shell is: {shell_type}.
    You MUST generate commands that are compatible with the user's shell. If the shell is 'zsh', use zsh-specific syntax or features when appropriate. If the shell is 'bash', use bash syntax. For common commands, use POSIX-compatible syntax unless the user requests something shell-specific.
    You MUST use the correct package manager for this system (e.g., 'apt' for 'ubuntu', 'pacman' for 'arch').

    Guidelines:
    1.  Your response MUST be a valid JSON object.
    2.  The JSON object must have a single key: "commands".
    3.  The value of "commands" must be an array of strings. Each string is a single, executable shell command.
    4.  Break down complex tasks into multiple steps. For simple tasks, the array will have one command.
    5.  Do not include explanations, comments, or any text outside of the JSON object.
    6.  If the request is dangerous, respond with an empty commands array and add a "reason" key explaining the danger.

    Examples:
    User: "list all running processes"
    Response: {{"commands": ["ps aux"]}}

    User: "update my system" (on Ubuntu)
    Response: {{"commands": ["sudo apt update", "sudo apt upgrade -y"]}}

    User: "install brave browser" (on Debian/Ubuntu)
    Response: {{"commands": ["sudo apt install curl", "sudo curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg", "echo \\\"deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg] https://brave-browser-apt-release.s3.brave.com/ stable main\\\" | sudo tee /etc/apt/sources.list.d/brave-browser-release.list", "sudo apt update", "sudo apt install brave-browser"]}}
    
    User: "Delete all files on my computer"
    Response: {{"commands": [], "reason": "This is an extremely dangerous request that could cause irreversible data loss."}}
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
                temperature=0.1,
                top_p=0.8,
                top_k=40,
                max_output_tokens=1000,
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
    # Main welcome panel
    welcome_panel = Panel(
        f"[bold blue]Detected shell:[/bold blue] [green]{shell_type}[/green]\n\n"
        "[bold white]Welcome to Smart-Shell![/bold white]\n"
        "Type your requests in natural language to convert them into shell commands.\n"
        "Type [bold cyan]exit[/bold cyan], [bold cyan]quit[/bold cyan], or press [bold cyan]Ctrl+C[/bold cyan] to exit.",
        title="[bold white]Smart Terminal Assistant[/bold white]",
        border_style="green",
        box=HEAVY,
        padding=(1, 2),
        expand=True
    )
    
    # Special commands section
    special_commands = [
        ("!help", "Show this help message"),
        ("!history", "Show command history"),
        ("!last", "Show the last generated command"),
        ("!redo", "Re-execute the last command"),
        ("!clear", "Clear the screen"),
        ("!models", "List available AI models"),
        ("!model <name>", "Switch to a different AI model"),
        ("!web", "Toggle web search for commands"),
        ("!update", "Check for updates and install"),
        ("!errors", "Show the error log"),
        ("!forget-sudo", "Clear the session sudo password"),
        ("!creator", "Show information about the creator"),
        ("!docs", "Show link to documentation")
    ]
    
    special_commands_panel = create_command_section("Special Commands", special_commands)
    
    # Configuration commands section
    config_commands = [
        ("smart-shell setup", "Configure API key and settings"),
        ("smart-shell models", "List available models from command line"),
        ("smart-shell version", "Show version information"),
        ("smart-shell --help", "Show all available options")
    ]
    
    config_panel = create_command_section("Configuration Commands", config_commands)
    
    # Notes panel
    notes_panel = Panel(
        "[italic]Note: Premium models may incur costs or have stricter rate limits.[/italic]\n"
        "[italic]To reconfigure settings, first exit Smart-Shell with 'exit' or Ctrl+C.[/italic]",
        title="[bold white]Notes[/bold white]",
        border_style="blue",
        box=ROUNDED,
        padding=(0, 1),
        expand=False
    )
    
    # Display everything in a structured layout
    console.print(welcome_panel)
    
    # Create a two-column layout for commands
    columns = Columns([special_commands_panel, config_panel], equal=True, expand=True)
    console.print(columns)
    console.print(notes_panel)

if __name__ == "__main__":
    # This allows the module to be run directly for testing
    display_banner()
    display_welcome_message()
    console.print("[yellow]Shell Builder module - For testing only[/yellow]")
    console.print("Use 'smart-shell' command or main.py to run the application.")