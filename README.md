# Smart-Shell

[![Tests](https://github.com/Lusan-sapkota/smart-shell/actions/workflows/test.yml/badge.svg)](https://github.com/Lusan-sapkota/smart-shell/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![AI](https://img.shields.io/badge/AI-OpenAI--compatible-orange)](docs/installation.md#providers)

<p align="center">
  <img src="docs/images/image.png" alt="Smart-Shell Demo" width="500"/>
</p>

Smart-Shell turns plain English into Bash or Zsh commands, checks them for risk, and runs them after you confirm. It works with any OpenAI-compatible chat API: Gemini, OpenAI, DeepSeek, OpenRouter, Groq, or a local model through Ollama or LM Studio (fully offline).

## Features

- **Natural language to commands** for Bash and Zsh, with the shell detected automatically.
- **Any OpenAI-compatible provider.** Built-in presets for gemini, openai, deepseek, openrouter, groq, ollama and lmstudio, plus `custom` for any base URL.
- **Offline mode** with Ollama or LM Studio: no API key, nothing leaves your machine.
- **Safety checks** on every command: blocked, high, medium, info_leak and safe. Blocked commands never run; high and medium need a y/n confirmation.
- **Multi-step plans** run in one shell, joined with `&&`, stopping at the first failure.
- **Dry-run mode** (`--dry-run`) to preview without executing.
- **Interactive REPL** with history and `!` commands (`!models`, `!model <name>`, `!redo`, `!errors`, ...).
- **No stored sudo password.** `sudo` prompts in your terminal as usual.
- **Self-update** with `!update`, a desktop entry, and Bash/Zsh tab completion from the installer.

## Install

```bash
curl -sSL https://raw.githubusercontent.com/Lusan-sapkota/smart-shell/main/install.sh | bash
```

The script installs Smart-Shell (uv if you have it, otherwise pipx; system-wide and virtualenv are also offered), adds a desktop entry and tab completion, and runs the setup wizard.

Already use [uv](https://docs.astral.sh/uv/)? Skip the script:

```bash
uv tool install git+https://github.com/Lusan-sapkota/smart-shell
```

Then:

```bash
smart-shell setup   # pick a provider, enter a key if needed, choose a default model
smart-shell         # start the interactive shell
smart-shell run "find files over 100MB in my home folder" --dry-run
```

To run fully offline with a local model, see [Using local models (Ollama)](docs/installation.md#using-local-models-ollama). For a manual or development install, see [docs/development.md](docs/development.md).

## Uninstall

```bash
uv tool uninstall smart-shell             # or: pipx uninstall smart-shell / sudo pip3 uninstall smart-shell
rm -rf ~/.config/smart-shell ~/.local/share/smart-shell
rm -f ~/.local/share/applications/smart-shell.desktop
rm -f ~/.bash_completion.d/smart-shell-completion.bash
sed -i '/# Smart-Shell completion/,+1d' ~/.bashrc ~/.zshrc
```

Details in [docs/uninstall.md](docs/uninstall.md).

## Documentation

- [Features](docs/features.md)
- [Installation](docs/installation.md)
- [Usage](docs/usage.md)
- [Safety](docs/safety.md)
- [Uninstall](docs/uninstall.md)
- [Development](docs/development.md)
- [API Reference](docs/api.md)
- [FAQ](docs/faq.md)
- [Changelog](docs/CHANGELOG.md)
- [Future Changes](docs/futurechanges.md)
- [Contributing](docs/contributing.md)
- [Author](docs/author.md)

Full documentation: [smart-shell.lusansapkota.com.np](https://smart-shell.lusansapkota.com.np/).

## License

Apache 2.0. See [LICENSE](LICENSE).

## Author

Created by [Lusan Sapkota](https://lusansapkota.com.np).

## Disclaimer

Smart-Shell is an AI assistant and can generate wrong or unsafe commands. Always read a command before you confirm it, especially anything that modifies the system or touches sensitive data.
