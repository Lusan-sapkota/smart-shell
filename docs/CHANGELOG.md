# Changelog

All notable changes to Smart-Shell will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-10-17

### Added
- Support for any OpenAI-compatible chat API through one requests-based client, with presets for Gemini, OpenAI, DeepSeek, OpenRouter, Groq, Ollama and LM Studio, plus `custom` for any base URL.
- Fully offline use with local models via Ollama or LM Studio.
- `smart-shell setup` now picks a provider, confirms the base URL, checks the connection and offers the live model list.
- `SMART_SHELL_BASE_URL` environment variable, alongside `SMART_SHELL_API_KEY`.
- `blocked` safety level for commands that never run (`rm -rf /`, fork bombs, `mkfs` or `dd` onto disks, and similar).
- pytest suite in `tests/` and a CI workflow running it on Python 3.9 and 3.13.

### Changed
- Multi-step plans run in one shell joined with `&&` and stop at the first failure.
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
