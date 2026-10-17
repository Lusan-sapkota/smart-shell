"""
Shell Builder Module - Generates shell commands from natural language prompts.
"""

import os
import re
import json
from rich.console import Console

console = Console()

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
