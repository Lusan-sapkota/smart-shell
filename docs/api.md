# API Reference

An overview of the modules in `smart_shell/`. See the source for details.

## Modules

| Module | Purpose |
|--------|---------|
| `main` | Click CLI (`run`, `setup`, `models`, `history`, `version`, `help`), the interactive REPL and `!` commands |
| `ai_wrapper` | `AIClient` for OpenAI-compatible APIs and the provider presets |
| `setup_logic` | The `smart-shell setup` wizard |
| `shell_builder` | System prompt, plan parsing, banner and welcome message |
| `safety` | Command risk classification |
| `history` | Command history in `~/.local/share/smart-shell/history.json` |
| `updater` | `!update`: version check against GitHub, update via git or pip |
| `utils` | Command execution, OS and shell detection, previews, error log |
| `config` | Load and save `~/.config/smart-shell/config.json` |

## ai_wrapper.py

- `PROVIDERS`: `name -> (base_url, default_model or None, needs_api_key)` for gemini, openai, deepseek, openrouter, groq, ollama, lmstudio.
- `AIClient(base_url, api_key=None)`
    - `list_models()`: sorted model ids from `GET /models`.
    - `chat(model, system, user, temperature=0.3, max_tokens=3000)`: text from `POST /chat/completions`, with `<think>` blocks stripped. Retries on connection errors, timeouts, 429 and 5xx.
- `AIError`: raised for connection, auth, 404 and unexpected-response errors.
- `get_client(config=None)`: builds a client from the config; `SMART_SHELL_BASE_URL` and `SMART_SHELL_API_KEY` take precedence.
- `resolve_model(client, model=None, config=None)`: explicit model, else configured default, else provider default, else first listed model.
- `is_configured(config=None)`: whether a provider or API key is set.

## shell_builder.py

- `generate_command_plan(prompt, client, model, os_info=None)`: returns a list of shell commands for the prompt.
- `display_banner()`, `display_welcome_message(shell_type)`.

## safety.py

- `check_command_safety(command)`: returns `{"status", "reason", "notes"}` where status is `blocked`, `high`, `medium`, `info_leak` or `safe`. See [Safety](safety.md).

## config.py

- `load_config()`: reads the config and removes any legacy stored sudo password.
- `save_config(config)`: writes the config with `0600` permissions.
- `ENV_API_KEY`: `"SMART_SHELL_API_KEY"`.

## setup_logic.py

- `setup_config()`: full wizard.
- `setup_provider(config)`: choose provider, base URL and key; returns a working `AIClient` or `None`.
- `set_default_model(client, config)`: pick a default model from the live list.

## utils.py

- `execute_command(command)`: runs a command in the user's shell, returns `True` on success.
- `print_plan_preview(plan, safety_results)`: shows the plan with safety levels.
- `get_os_info()`, `detect_shell()`.
- `reset_sudo_password()`: runs `sudo -k`.
- `log_error(message)`: appends to `~/.local/share/smart-shell/error.log`.

## history.py

- `save_to_history(prompt, command, executed=False)`, `update_history_result(history_id, success)`.
- `show_command_history()`, `show_last_command()`, `redo_last_command()`.
