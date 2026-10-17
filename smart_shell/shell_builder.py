"""
Shell Builder Module - Generates shell commands from natural language prompts.
"""

import os
import shutil
import re
import json
from rich.console import Console

console = Console()

# Retries when the model's reply is not valid JSON (network retries live in the client)
MAX_RETRIES = 2

def parse_plan(text):
    """Pull {"commands": [...]} out of a model reply, tolerating common small-model mistakes."""
    start = text.find("{")
    if start != -1:
        raw = text[start:]
        for candidate in (raw, re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', raw)):
            try:
                # raw_decode stops at the end of the object, so prose after the JSON is fine.
                parsed, _ = json.JSONDecoder().raw_decode(candidate)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                pass
    # Ignored the JSON instruction and answered with a ```bash block instead.
    fence = re.search(r'```(?:bash|sh|zsh|shell)?\n(.*?)```', text, re.DOTALL)
    if fence:
        commands = [line.strip() for line in fence.group(1).splitlines() if line.strip() and not line.strip().startswith("#")]
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

    system_prompt = f"""You turn a request into shell commands for this machine.
OS: {os_info.get('name', 'Linux')}. Shell: {shell_type}. Package manager: {detect_package_manager()}.

Reply with JSON only, no prose and no code fences:
{{"commands": ["command 1", "command 2"]}}

Rules:
- Use as few commands as needed; they run in order in one shell, stopping at the first failure.
- Match the request exactly (counts, sizes, file types, paths).
- Prefer common tools that are installed by default.
- If the request cannot be done safely, reply {{"commands": [], "reason": "why"}}.

Examples:
Request: show the 3 most recent git commits
{{"commands": ["git log -3 --oneline"]}}
Request: find .log files over 10MB in /var/log
{{"commands": ["find /var/log -name '*.log' -size +10M"]}}
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
        return [cmd.strip() for cmd in commands if cmd.strip()]

    raise Exception(f"Error generating command plan: {last_error}")

def detect_package_manager():
    """First package manager found on PATH."""
    for tool in ("apt", "dnf", "pacman", "zypper", "apk", "brew"):
        if shutil.which(tool):
            return tool
    return "unknown"


def explain_command(client, model, command):
    """Plain-English explanation of a shell command."""
    system = ("Explain what this shell command does, step by step, in plain language. "
              "Point out anything destructive or surprising. Be brief. No markdown headings.")
    return client.chat(model, system, command, max_tokens=800)
