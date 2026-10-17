# Installation

Requires Python 3.9 or newer on Linux, macOS or WSL.

## Quick install

```bash
curl -sSL https://raw.githubusercontent.com/Lusan-sapkota/smart-shell/main/install.sh | bash
```

The script:

1. Checks for Python, pip and pipx.
2. Installs Smart-Shell using one of three methods: system-wide (sudo), user install with pipx (recommended), or a virtual environment (for development).
3. Creates a desktop entry and Bash/Zsh tab completion.
4. Runs `smart-shell setup`.

Dependencies are `rich`, `click` and `requests`. To install them yourself (for example behind a restrictive firewall):

```bash
pip install --user rich click requests
```

For a development install, see [Development](development.md).

## Providers

Run the setup wizard at any time:

```bash
smart-shell setup
```

It asks you to:

1. Choose a provider: `gemini`, `openai`, `deepseek`, `openrouter`, `groq`, `ollama`, `lmstudio`, or `custom` (any OpenAI-compatible base URL).
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

## Using local models (Ollama)

Smart-Shell works fully offline with [Ollama](https://ollama.com/). No API key is needed.

```bash
ollama pull qwen2.5-coder   # any chat model works; coder models do well
ollama serve                # skip if Ollama already runs as a service
smart-shell setup           # choose "ollama", keep http://localhost:11434/v1
```

Pick the pulled model as your default and you're done. LM Studio works the same way: start its local server and choose `lmstudio` (`http://localhost:1234/v1`).

## Troubleshooting

- **`smart-shell: command not found`**: make sure `~/.local/bin` is on your `PATH` (`pipx ensurepath`), then open a new terminal.
- **pipx / PEP 668 errors**: install pipx (`sudo apt install pipx`), run `pipx ensurepath`, and rerun the installer. See the [FAQ](faq.md).
- **Connection check fails during setup**: verify the API key, or for Ollama that `ollama serve` is running.
