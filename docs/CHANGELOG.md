# Changelog

All notable changes to Smart-Shell will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.2.0] - 2026-10-17

### Added
- Every plan asks **yes / no / edit** before running, so you can change a command first. Edits are checked again.
- Fix on failure: after a failed command, Smart-Shell offers to send the command and its error output to the model and shows a corrected plan.
- Spinner showing the provider and model while the AI is working.
- `smart-shell "<prompt>"` works without the `run` subcommand.

### Changed
- Startup shows a two-line header instead of the ASCII banner and welcome panel.
- Safe and info-leak plans now ask before running (default yes) instead of running immediately.
- Local providers (Ollama, LM Studio) are listed first, and a fresh setup defaults to Ollama.
- Python 3.10 or newer is required (3.9 reached end of life).
- Shorter system prompt: small local models return valid JSON far more often, and the detected package manager (apt, dnf, pacman, zypper, apk, brew) is passed to the model.
- History is capped at 1000 entries and written with `0600` permissions.
- CI also runs `ruff`.
- Install docs lead with `pipx install smart-shell-cli` / `uv tool install smart-shell-cli`; the install script is the alternative. The script installs from PyPI.


### Fixed
- `!history` and `!last` printed an object name instead of the command.
- A corrupt history file no longer crashes `!history`, `!last` or saving.
- `!redo` checks single-string commands for blocked patterns too.
- The installer cleans up the launcher left by pre-1.1.0 installs.
- Startup failed with "Invalid argument" when the input history file was written by a different readline build (for example after moving to uv's Python). The old file is now kept as `readline_history.old`.

### Removed
- `!creator`, the `help` command (use `--help`), and the REPL check that refused any request mentioning `smart-shell` commands.

## [1.1.0] - 2026-10-17

### Added
- Support for any OpenAI-compatible chat API through one requests-based client, with presets for Gemini, OpenAI, DeepSeek, OpenRouter, Groq, Ollama and LM Studio, plus `custom` for any base URL.
- Fully offline use with local models via Ollama or LM Studio.
- `smart-shell setup` now picks a provider, confirms the base URL, checks the connection and offers the live model list.
- `SMART_SHELL_BASE_URL` environment variable, alongside `SMART_SHELL_API_KEY`.
- `blocked` safety level for commands that never run (`rm -rf /`, fork bombs, `mkfs` or `dd` onto disks, and similar).
- `--provider` and `--base-url` options to use another provider for one run. The saved API key is only sent to the server it was saved for.
- `!explain <command>` explains a command and shows its safety level.
- Follow-ups in interactive mode: recent requests are sent as context.
- `install.sh --uninstall`.
- Installation with uv (`uv tool install`), preferred by the installer when available.
- pytest suite in `tests/` and a CI workflow running it on Python 3.9 and 3.13.

### Changed
- Package renamed to `smart-shell-cli` (the `smart-shell` name on PyPI belongs to another project). The command is still `smart-shell`.
- Multi-step plans run in one shell joined with `&&` and stop at the first failure.
- Command output is shown live, so interactive prompts work.
- Replies from small local models that wrap JSON in code fences, use shell escapes inside JSON, or answer with a bash block are now parsed.
- `install.sh` rewritten: uv or pipx only, completion generated from the CLI itself.
- `!update` checks PyPI and upgrades with the tool that installed Smart-Shell; it no longer stashes changes or pulls in a git checkout.
- Safety rules catch `rm` recursive/force flags in any spelling and piping into a shell, with fewer false positives.
- Config is written with `0600` permissions. Old configs with only `api_key` are treated as Gemini.
- `!models` lists models straight from the provider.
- Dependencies reduced to `rich`, `click` and `requests`. Python 3.9 or newer is required.
- History and update logic moved out of `main.py` into `history.py` and `updater.py`.

### Removed
- Stored sudo password. `sudo` now prompts in the terminal, and any previously stored password is deleted from the config. `!forget-sudo` runs `sudo -k`.
- Model pricing info, premium/free warnings and `!models free|premium|legacy|refresh`.
- Mentions of a `!web` web search command, which never existed.
- `google-genai`, `google-api-core`, `pyyaml` and `toml` dependencies.
- System-wide and virtualenv options in `install.sh` (use `pip install -e .` for development).
- `examples/`, root `uninstall.sh` and `CHANGELOG.md`, `smart_shell/offline.py`, `smart_shell/model_info.py`, and the old `smart_shell/test_smart_shell.py`.

## [1.0.0] - 2025-06-30

### Added
- Interactive REPL mode that continues until user explicitly exits
- Command history tracking and viewing
- Special commands in interactive mode (!history, !clear, !help, !model)
- Automatic error recovery for common issues
- Support for sudo commands with password caching and secure handling
- Command execution via temporary script files for better security
- Desktop entry for GUI launchers
- Support for multiple shells (bash, zsh)
- Comprehensive safety checks for commands, including command-specific risk assessment
- Auto-installation of missing dependencies
- Better error handling and recovery
- Command-specific risk assessment
- Enhanced API key flexibility with support for any Gemini-compatible API key
- Improved model validation with graceful fallback to default model
- New `--list-models` flag to display available AI models
- Special command `!models` in interactive mode to list models
- Support for multi-shell environments (bash, zsh)
- Command history persistence across sessions
- Auto-completion for file paths in prompts
- Dry run mode to preview commands without execution
- Enhanced documentation with API key and model information
- Tab completion for commands and options
- Desktop integration
- Installation script with multiple installation options
- Comprehensive documentation

### Changed
- Improved installation script with error handling
- Enhanced safety checks with detailed analysis
- Better terminal output formatting
- Prioritize environment variables for API key storage
- Updated command-line interface with more options
- Improved safety checks with more detailed analysis
- Enhanced error recovery for common issues
- Better formatting of command output
- Updated model names to gemini-2.5-pro, gemini-2.5-flash, and gemini-2.0-pro
- Improved API wrapper with better error handling

### Fixed
- Invalid escape sequence in ASCII art banner
- Handling of sudo password prompts
- Path issues in command execution
- Issue with API key validation
- Command history not saving in some cases
- Error handling for network connectivity issues
- Issues with model selection and fallback
- Error handling for invalid API keys
