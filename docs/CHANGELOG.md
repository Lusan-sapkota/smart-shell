# Changelog

All notable changes to Smart-Shell will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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