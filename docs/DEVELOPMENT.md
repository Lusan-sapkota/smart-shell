# Smart-Shell Development Guide

This document provides guidelines for developers who want to contribute to or modify the Smart-Shell project.

## Project Structure

```
smart-shell/
├── main.py             # Main entry point and CLI interface
├── shell_builder.py    # Core functionality for generating commands
├── ai_wrapper.py       # Wrapper for AI model interactions
├── safety.py           # Safety checks for commands
├── config.py           # Configuration management
├── utils.py            # Utility functions
├── setup.py            # Package setup
├── install.sh          # Installation script
├── docs/               # Documentation
│   ├── DEVELOPMENT.md  # This file
│   └── SAFETY.md       # Safety documentation
└── examples/           # Example usage
```

## Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/Lusan-sapkota/smart-shell.git
   cd smart-shell
   ```

2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install in development mode:
   ```bash
   pip install -e .
   ```

4. Install development dependencies:
   ```bash
   pip install pytest black flake8
   ```

## Core Components

### Main (main.py)

The main module provides the command-line interface using Click. It handles:
- Command parsing and execution
- Interactive mode
- History tracking
- Configuration management

### Shell Builder (shell_builder.py)

This module is responsible for:
- Generating shell commands from natural language
- Managing model selection
- Formatting output

### AI Wrapper (ai_wrapper.py)

The AI wrapper provides a unified interface for interacting with AI models:
- Handles API authentication
- Manages model selection and fallbacks
- Processes prompts and responses

### Safety (safety.py)

The safety module implements checks to prevent dangerous commands:
- Pattern matching for risky commands
- Path validation
- Risk assessment

### Config (config.py)

Handles configuration management:
- Loading/saving configuration
- API key management
- User preferences

## API Key and Model Support

Smart-Shell is designed to work with Google Gemini models but supports any valid Gemini-compatible API key. This allows developers to use their own Google Cloud or AI Studio API credentials.

### API Key Management

API keys can be provided in two ways:
1. Environment variable: `SMART_SHELL_API_KEY` (recommended for security)
2. Config file: `~/.config/smart-shell/config.json`

The environment variable takes precedence over the config file.

### Model Support

Smart-Shell supports multiple Gemini models:
- `gemini-2.5-pro` (default): Most capable model with advanced reasoning
- `gemini-2.5-flash`: Faster model with good performance
- `gemini-2.0-pro`: Legacy model for compatibility

The model validation system in `shell_builder.py` ensures that:
1. If an invalid model is specified, it falls back to the default model
2. Users are informed when a fallback occurs
3. The system can be extended to support new models as they become available

### Adding Support for New Models

To add support for a new model:
1. Add the model name to the `SUPPORTED_MODELS` list in `shell_builder.py`
2. Update the model information in `display_models()` in `main.py`
3. Test the model with various prompts to ensure compatibility

## Adding New Features

When adding new features:

1. Create a branch for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Write tests for your feature in `test_smart_shell.py`

3. Implement your feature

4. Run tests:
   ```bash
   pytest
   ```

5. Format your code:
   ```bash
   black .
   flake8
   ```

6. Update documentation as needed

7. Submit a pull request

## Safety Guidelines

When modifying the safety system:

1. Never disable safety checks without careful consideration
2. Add tests for new safety rules
3. Consider edge cases and potential bypasses
4. Document changes in `docs/SAFETY.md`

## Release Process

1. Update version number in `setup.py`
2. Update `CHANGELOG.md` with changes
3. Run full test suite
4. Create a release tag
5. Build and publish package

## Extending to Other AI Providers

While Smart-Shell is currently optimized for Google Gemini models, it's designed to be extensible. To add support for other AI providers:

1. Create a new wrapper class in `ai_wrapper.py` that implements the same interface as `GeminiWrapper`
2. Update the `get_wrapper()` function to detect and use the appropriate wrapper
3. Add configuration options for the new provider
4. Update documentation and help text

Remember that different AI models may have different capabilities and limitations, so thorough testing is essential. 