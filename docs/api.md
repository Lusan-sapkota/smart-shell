# API Reference

## Main Modules

- `smart_shell.main`: Entry point and CLI logic
- `smart_shell.ai_wrapper`: Handles AI model communication
- `smart_shell.safety`: Safety checks and command validation
- `smart_shell.config`: Configuration and API key management
- `smart_shell.shell_builder`: Bash/Zsh command construction
- `smart_shell.utils`: Utility functions
- `smart_shell.setup_logic`: Setup and installation logic

## Key Classes & Functions

### ai_wrapper.py
- `AIWrapper`: Main class for interacting with Gemini models
- `AIWrapper.generate_command(prompt, model)`: Generate Bash/Zsh command from prompt

### safety.py
- `SafetyChecker`: Class for command safety analysis
- `SafetyChecker.check(command)`: Returns safety level and reason

### config.py
- `ConfigManager`: Handles config file and environment variables
- `ConfigManager.get_api_key()`: Returns API key

### shell_builder.py
- `ShellBuilder`: Converts structured command to Bash/Zsh

---

For more, see the source code and inline docstrings.
