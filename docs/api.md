# API Reference

## Main Modules

- `smart_shell.main`: Entry point, CLI logic, interactive mode, and special commands
- `smart_shell.ai_wrapper`: Handles AI model communication (Gemini)
- `smart_shell.safety`: Safety checks, command validation, and user confirmation logic
- `smart_shell.config`: Configuration, API key management, and model selection
- `smart_shell.shell_builder`: Bash/Zsh command construction and banner display
- `smart_shell.utils`: Utility functions (execution, logging, sudo, OS detection)
- `smart_shell.setup_logic`: Setup and installation logic

## Key Classes & Functions

### ai_wrapper.py
- `get_wrapper(api_key)`: Returns an AIWrapper instance for Gemini
- `AIWrapper.list_available_models()`: List supported Gemini models
- `AIWrapper.generate_command(prompt, model)`: Generate Bash/Zsh command from prompt

### safety.py
- `check_command_safety(command)`: Returns safety analysis with status ("safe", "medium", "high", "info_leak") and detailed reason
- Safety levels trigger appropriate confirmation prompts in the main application

### config.py
- `load_config()`: Loads config file
- `save_model(model)`: Saves selected model
- `get_current_model()`: Gets current model
- `ENV_API_KEY`: Environment variable for API key

### shell_builder.py
- `generate_command_plan(prompt, api_key, model, os_info)`: Returns a list of command(s) for a prompt
- `display_banner()`: Prints the Smart-Shell banner
- `BANNER`: Banner string

### utils.py
- `execute_command(command)`: Runs a shell command safely
- `print_plan_preview(plan, safety_results)`: Shows command plan with safety analysis
- `reset_sudo_password()`: Clears cached sudo password
- `log_error(error)`: Logs errors to file
- `get_os_info()`: Returns detailed OS information
- `detect_shell()`: Detects current shell (Bash or Zsh)
- `validate_sudo_password(password)`: Validates sudo credentials

### setup_logic.py
- `setup_config()`: Runs interactive setup wizard
- `setup_api_key(config)`: Handles API key configuration with validation
- `setup_sudo_password(config)`: Handles sudo password setup with security warnings
- `set_default_model(api_key, config)`: Interactive model selection during setup

## Special Commands

The interactive mode supports various special commands:

- `!help`: Show comprehensive help
- `!history`: Display command history
- `!last`: Show last generated command  
- `!redo`: Re-execute last command
- `!clear`: Clear the screen
- `!models`: List available AI models
- `!model <name>`: Switch AI model
- `!web`: Toggle web search integration
- `!update`: Check for and install updates from GitHub
- `!errors`: Show error log
- `!forget-sudo`: Clear cached sudo password
- `!creator`: Show creator information
- `!docs`: Show documentation link

---

For more, see the source code and inline docstrings. All modules are designed for Bash and Zsh compatibility, and safety checks always prompt for confirmation on high-risk commands.
