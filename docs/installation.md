# Installation

Requires Python 3.9 or newer on Linux, macOS or WSL.

## Quick install

```bash
curl -sSL https://raw.githubusercontent.com/Lusan-sapkota/smart-shell/main/install.sh | bash
```

The script:

1. Installs the `smart-shell-cli` package with uv if it is installed, otherwise with pipx.
2. Removes any older install, including the pre-1.1.0 `smart-shell` package name.
3. Adds Bash/Zsh tab completion and a desktop entry.
4. Runs `smart-shell setup`.

## Install with uv

If you already use [uv](https://docs.astral.sh/uv/), you can skip the script:

```bash
uv tool install smart-shell-cli   # or: pipx install smart-shell-cli
smart-shell setup
```

Upgrade with `uv tool upgrade smart-shell-cli`, remove with `uv tool uninstall smart-shell-cli`. With pipx: `pipx install smart-shell-cli`, `pipx upgrade smart-shell-cli`. For the unreleased `development` branch: `uv tool install git+https://github.com/Lusan-sapkota/smart-shell@development`.

Dependencies are `rich`, `click` and `requests`. To install them yourself (for example behind a restrictive firewall):

```bash
pip install --user rich click requests
```

For a development install, see [Development](development.md).

## Using local models (Ollama)

Smart-Shell works fully offline with [Ollama](https://ollama.com/). No API key is needed.

```bash
ollama pull qwen2.5-coder   # any chat model works; coder models do well
ollama serve                # skip if Ollama already runs as a service
smart-shell setup           # choose "ollama", keep http://localhost:11434/v1
```

Pick the pulled model as your default and you're done. LM Studio works the same way: start its local server and choose `lmstudio` (`http://localhost:1234/v1`).

## Providers

Run the setup wizard at any time:

```bash
smart-shell setup
```

It asks you to:

1. Choose a provider: `ollama` or `lmstudio` (local, the default), `gemini`, `openai`, `deepseek`, `openrouter`, `groq`, or `custom` (any OpenAI-compatible base URL).
2. Confirm the base URL.
3. Enter an API key if the provider needs one. The connection is checked by listing models.
4. Pick a default model from the live model list.

### Configuration

Settings are saved to `~/.config/smart-shell/config.json` with `0600` permissions:

```json
{
  "provider": "ollama",
  "base_url": "http://localhost:11434/v1",
  "default_model": "qwen2.5-coder:latest"
}
```

Cloud providers also store `api_key`. Environment variables override the saved values:

- `SMART_SHELL_API_KEY`
- `SMART_SHELL_BASE_URL`

Configs from older versions that only contain `api_key` are treated as Gemini.

## Troubleshooting

- **`smart-shell: command not found`**: make sure `~/.local/bin` is on your `PATH` (`uv tool update-shell` or `pipx ensurepath`), then open a new terminal.
- **pipx / PEP 668 errors**: install pipx (`sudo apt install pipx`), run `pipx ensurepath`, and rerun the installer. See the [FAQ](faq.md).
- **Connection check fails during setup**: verify the API key, or for Ollama that `ollama serve` is running.
