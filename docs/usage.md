# Usage Guide: Smart-Shell

This guide covers all special commands, system-level commands, and usage patterns for Smart-Shell, including both CLI and interactive modes.

---

## Quick Start

- **Interactive Mode:**
  ```sh
  smart-shell --interactive
  ```
- **One-off Command:**
  ```sh
  smart-shell run "list all PDF files in the current directory"
  ```
- **Help:**
  ```sh
  smart-shell --help
  ```

---

## Special Commands (Interactive Mode)

Type these at the Smart-Shell prompt (not in your system shell):

| Command                | Description                                      |
|------------------------|--------------------------------------------------|
| `!help`                | Show help message                                |
| `!history`             | Show command history                             |
| `!last`                | Show the last generated command                  |
| `!redo`                | Re-execute the last command                      |
| `!clear`               | Clear the screen                                 |
| `!models`              | List available AI models                         |
| `!models standard`     | List only free standard models                   |
| `!models premium`      | List only paid premium models                    |
| `!models <n>`          | List models with a limit of n                    |
| `!models web`          | Show additional model info from web              |
| `!model <model-name>`  | Switch to a different AI model                   |
| `!web`                 | Toggle web search for commands                   |
| `!update`              | Check for updates and install                    |
| `!errors`              | Show the error log                               |
| `!forget-sudo`         | Clear the session sudo password                  |
| `!creator`             | Show information about the creator               |
| `!docs`                | Show link to documentation                       |

- **Exit:** Type `exit`, `quit`, `bye`, `q`, or press Ctrl+C.

---

## System-Level CLI Commands

Run these in your system shell:

| Command                                 | Description                                  |
|------------------------------------------|----------------------------------------------|
| `smart-shell run <prompt>`               | Run a one-off natural language command       |
| `smart-shell --interactive`              | Start interactive mode                      |
| `smart-shell setup`                      | Configure API key and settings              |
| `smart-shell models`                     | List available models                       |
| `smart-shell history`                    | Show command history                        |
| `smart-shell --help` or `-h`             | Show CLI help                               |
| `smart-shell --version`                  | Show version information                    |

---

## Usage Patterns

- **Natural Language:**
  - Type requests like "Find large files over 100MB" or "Create a backup of my project folder".
- **Model Selection:**
  - Use `--model <model-name>` in CLI or `!model <model-name>` in interactive mode.
- **Web Search:**
  - Toggle with `!web` in interactive mode.
- **Safety:**
  - Commands are checked for safety before execution. High-risk commands require explicit confirmation.

---

## Safety System

- 🟢 **Safe:** Command is safe to run.
- 🟡 **Warning:** Might have unintended consequences (requires confirmation).
- 🔴 **Blocked:** Potentially harmful (requires explicit confirmation; will be executed if you confirm).

---

## Configuration

- To reconfigure, exit Smart-Shell and run:
  ```sh
  smart-shell setup
  ```

---

## Documentation

- Full docs: https://lusan-sapkota.github.io/smart-shell/

---

## Notes

- Premium models may incur costs or have stricter rate limits.
- All commands and features are available in both Bash and Zsh environments.
- For troubleshooting, use `!errors` or check the error log.

---

For more details, see the full documentation or use `!help` in interactive mode.
