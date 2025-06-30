# Changelog

All notable changes to Smart-Shell will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Interactive REPL mode that continues until user explicitly exits
- Command history tracking and viewing
- Special commands in interactive mode (!history, !clear, !help, !model)
- Automatic error recovery for common issues
- Support for sudo commands with password caching
- Command execution via temporary script files for better security
- Desktop entry for GUI launchers
- Support for multiple shells (bash, zsh)
- Comprehensive safety checks for commands
- Auto-installation of missing dependencies
- Better error handling and recovery
- Command-specific risk assessment

### Changed
- Improved installation script with error handling
- Enhanced safety checks with detailed analysis
- Better terminal output formatting
- Prioritize environment variables for API key storage
- Updated command-line interface with more options

### Fixed
- Invalid escape sequence in ASCII art banner
- Handling of sudo password prompts
- Path issues in command execution

## [1.0.0] - 2023-09-15

### Added
- Initial release of Smart-Shell
- Natural language to Bash command conversion
- Interactive mode with continuous command generation
- Safety checks for dangerous commands
- Command history tracking and viewing
- Secure API key management
- Multiple AI model support
- Tab completion for commands and options
- Desktop integration
- Installation script with multiple installation options
- Comprehensive documentation

## [1.1.0] - 2023-09-20

### Added
- Support for sudo commands with secure password handling
- Command editing when safety checks block execution
- Special commands in interactive mode (!history, !clear, !help, !model)
- Automatic fallback for unavailable models

### Changed
- Improved safety checks with more detailed analysis
- Enhanced error recovery for common issues
- Better formatting of command output

## [1.2.0] - 2023-10-01

### Added
- Support for multi-shell environments (bash, zsh)
- Command history persistence across sessions
- Auto-completion for file paths in prompts
- Dry run mode to preview commands without execution

### Fixed
- Issue with API key validation
- Command history not saving in some cases
- Error handling for network connectivity issues

## [1.3.0] - 2023-10-15

### Added
- Enhanced API key flexibility with support for any Gemini-compatible API key
- Improved model validation with graceful fallback to default model
- New `--list-models` flag to display available AI models
- Special command `!models` in interactive mode to list models

### Changed
- Updated model names to gemini-2.5-pro, gemini-2.5-flash, and gemini-2.0-pro
- Improved API wrapper with better error handling
- Enhanced documentation with API key and model information

### Fixed
- Issues with model selection and fallback
- Error handling for invalid API keys 