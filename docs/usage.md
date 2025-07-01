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
| `!models free`         | List only free models                            |
| `!models premium`      | List only premium models                         |
| `!models legacy`       | List only legacy models                          |
| `!models refresh`      | Refresh model info from web sources             |
| `!model <model-name>`  | Switch to a different AI model (with cost warning)|
| `!web`                 | Toggle web search for commands                   |
| `!update`              | Check for updates from GitHub and install       |
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
| `smart-shell version` or `--version`     | Show version information                    |
| `smart-shell --dry-run` or `-d`          | Show command without executing              |
| `smart-shell --yes` or `-y`              | Auto-confirm all prompts                    |

---

## Advanced Features

- **Protected Prompt:** When typing, backspacing won't delete the "Smart-Shell (model):" prefix.
- **Smart Command Detection:** If you try to run Smart-Shell commands inside Smart-Shell, it will guide you to exit first.
- **Robust Update System:** `!update` checks GitHub for the latest version and updates automatically.
- **Enhanced AI:** More resilient command generation with better error handling.
- **Y/N Confirmations:** All confirmations accept both `y`/`yes` and `n`/`no` in any case.

---

## Safety System

Smart-Shell includes a comprehensive safety system with confirmation prompts:

- 🟢 **Safe:** Command is safe to run (executed automatically).
- 🟡 **Medium Risk:** Commands like `sudo` operations (requires y/n confirmation).
- 🔴 **High Risk:** Dangerous commands like `rm -rf` (requires y/n confirmation).

All medium and high-risk commands require explicit user confirmation before execution. You can respond with `y`/`yes` or `n`/`no` (case insensitive).

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
