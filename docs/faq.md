# FAQ

## General

### What is Smart-Shell?
A terminal assistant that turns plain English into Bash or Zsh commands, checks them for risk, and runs them after you confirm.

### Which AI providers does it support?
Any OpenAI-compatible chat API. Presets exist for Gemini, OpenAI, DeepSeek, OpenRouter, Groq, Ollama and LM Studio; `custom` accepts any base URL. See [Installation](installation.md#providers).

### Can I use it without an API key or offline?
Yes. Use Ollama or LM Studio; see [Using local models (Ollama)](installation.md#using-local-models-ollama).

### Which shells and systems are supported?
Bash and Zsh on Linux, macOS and WSL.

### Is it safe?
Every command is classified as blocked, high, medium, info_leak or safe. Blocked commands never run; high and medium ask for confirmation. The rules are pattern-based, so always read the preview. See [Safety](safety.md).

## Setup

### How do I configure a provider or API key?
Run `smart-shell setup`. You can also set `SMART_SHELL_API_KEY` and `SMART_SHELL_BASE_URL`, which override the saved config.

### Where is the configuration stored?
`~/.config/smart-shell/config.json` (mode `0600`), with the keys `provider`, `base_url`, `api_key` and `default_model`. History and the error log are in `~/.local/share/smart-shell/`.

### Does Smart-Shell store my sudo password?
No. `sudo` prompts in the terminal. Passwords stored by older versions are removed from the config automatically.

### `smart-shell: command not found` after installing
Restart the terminal or run `source ~/.bashrc` (or `~/.zshrc`). Make sure `~/.local/bin` is on your `PATH` (`uv tool update-shell` or `pipx ensurepath`).

### pipx or PEP 668 errors during install {#pipx-or-pep668}
Newer distros block `pip install` into the system Python, which is why the installer uses uv or pipx. Install either one ([uv](https://docs.astral.sh/uv/), or `sudo apt install pipx`), open a new terminal and rerun the installer.

### Setup says it cannot connect
Check the API key and base URL. For Ollama, make sure `ollama serve` is running and you have pulled at least one model.

## Usage

### How do I switch models?
`smart-shell models` or `/models` lists what the provider offers. Use `--model <name>` for one run, `/model <name>` in interactive mode, or `smart-shell setup` to change the default.

### Can I use it in scripts?
Yes, with `smart-shell run "<prompt>"`. Add `-y` to skip confirmations (blocked commands still never run). Review generated commands carefully before automating them.

### How do I update?
Use `/update` in interactive mode, or `uv tool upgrade smart-shell-cli` / `pipx upgrade smart-shell-cli`.

### What is sent to the AI provider?
Your prompt plus basic OS and shell information so the command fits your system. In interactive mode, your last five requests from the same session (prompt, generated commands, and whether they succeeded) are included so follow-ups work. Command output and file contents are not sent. With a local model, nothing leaves your machine.

### What does it cost?
Smart-Shell is free and open source (Apache 2.0). Cloud providers bill according to their own pricing; local models cost nothing.

## Contributing

See [Contributing](contributing.md) and the [Development Guide](development.md). Bugs and feature requests go to [GitHub Issues](https://github.com/Lusan-sapkota/smart-shell/issues).
