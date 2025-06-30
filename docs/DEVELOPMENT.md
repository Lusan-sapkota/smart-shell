# Smart-Shell Development Guide

This document provides guidelines for developers who want to contribute to or modify the Smart-Shell project.

## Manual Installation for Developers

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- git (for cloning the repository)

### Step 1: Clone the Repository

```bash
git clone https://github.com/Lusan-sapkota/smart-shell.git
cd smart-shell
```

### Step 2: Set Up Development Environment

Choose one of the following methods:

#### Method 1: Virtual Environment (Recommended for Development)

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

#### Method 2: User Installation

```bash
# Install for current user
pip install --user -e .
```

#### Method 3: System-wide Installation

```bash
# Install system-wide (requires admin/sudo)
sudo pip install -e .
```

### Step 3: Set Up Your API Key

You'll need a Google Gemini API key to use Smart-Shell:

1. Get your API key from [Google AI Studio](https://ai.google.dev/)
2. Set it as an environment variable (recommended):
   ```bash
   export SMART_SHELL_API_KEY=your-api-key-here
   ```
   
   Or configure it using the setup command:
   ```bash
   smart-shell setup
   ```

### Step 4: Verify Installation

Test your installation by running:

```bash
# Simple test
smart-shell run "list files in current directory" --dry-run

# Run in interactive mode
smart-shell
```

## Development Environment

After installing, set up your development environment:

1. Install development dependencies:
   ```bash
   pip install pytest black flake8
   ```

2. Run tests:
   ```bash
   pytest
   ```

3. Format code before committing:
   ```bash
   black .
   flake8
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
- Uses the google-genai package to interact with Google's Gemini models

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
- `gemini-2.5-flash` (default): Fast, capable model for most use cases
- `gemini-2.5-pro`: More advanced reasoning, but may be slower or have stricter limits
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

## Package Dependencies

Smart-Shell requires the following main dependencies:

- `google-genai>=1.0.0`: Google's Generative AI Python SDK
- `rich`: For enhanced terminal output
- `click`: For command-line interface
- `requests`: For API communication

Make sure to keep `requirements.txt` and `pyproject.toml` in sync when adding new dependencies.

## Troubleshooting Common Development Issues

### API Connection Issues
If you're having trouble connecting to the Gemini API:
- Check that your API key is valid and has appropriate permissions
- Verify your internet connection
- Ensure the Google Gemini API is available in your region

### Package Installation Problems
If you encounter issues installing Smart-Shell:
- Ensure your Python version is 3.8 or higher
- Try installing with `--break-system-packages` if using Python 3.11+
- Check that all dependencies are available in your environment

### Import Errors
If you see import errors when running Smart-Shell:
- Verify that you've installed the package in development mode (`pip install -e .`)
- Make sure your virtual environment is activated
- Check that all dependencies are installed

## Safety Guidelines

When modifying the safety system:

1. Never disable safety checks without careful consideration
2. Add tests for new safety rules
3. Consider edge cases and potential bypasses
4. Document changes in `docs/SAFETY.md`

## Release Process

1. Update version number in `setup.py` and `pyproject.toml`
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