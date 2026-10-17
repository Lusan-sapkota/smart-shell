# Smart-Shell

[![Release](https://img.shields.io/github/v/release/Lusan-sapkota/smart-shell)](https://github.com/Lusan-sapkota/smart-shell/releases/latest)
[![Tests](https://github.com/Lusan-sapkota/smart-shell/actions/workflows/test.yml/badge.svg)](https://github.com/Lusan-sapkota/smart-shell/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](https://github.com/Lusan-sapkota/smart-shell/blob/main/LICENSE)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://www.python.org/)
[![AI](https://img.shields.io/badge/AI-Local%20%2F%20OpenAI--compatible-orange)](https://smart-shell.lusansapkota.com.np/installation/#providers)

<p align="center">
  <img src="https://raw.githubusercontent.com/Lusan-sapkota/smart-shell/main/docs/images/image.png" alt="Smart-Shell Demo" width="500"/>
</p>

Smart-Shell turns plain English into Bash or Zsh commands, checks them for risk, and runs them after you confirm. It runs on a local AI model through Ollama or LM Studio, fully offline with no API key, or on any OpenAI-compatible API: Gemini, OpenAI, DeepSeek, OpenRouter, Groq.

## Features

- **Natural language to commands** for Bash and Zsh, with the shell detected automatically.
- **Local AI first.** Ollama or LM Studio: no API key, nothing leaves your machine.
- **Or any OpenAI-compatible API.** Presets for gemini, openai, deepseek, openrouter and groq, plus `custom` for any base URL.
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

The script installs Smart-Shell with uv (or pipx if you don't have uv), adds tab completion and a desktop entry, and runs the setup wizard.

Already use [uv](https://docs.astral.sh/uv/)? Skip the script:

```bash
uv tool install smart-shell-cli   # or: pipx install smart-shell-cli
```

Then:

```bash
smart-shell setup   # pick a provider, enter a key if needed, choose a default model
smart-shell         # start the interactive shell
smart-shell run "find files over 100MB in my home folder" --dry-run
```

To run fully offline with a local model, see [Using local models (Ollama)](https://smart-shell.lusansapkota.com.np/installation/#using-local-models-ollama). For a manual or development install, see [Development](https://smart-shell.lusansapkota.com.np/development/).

## Uninstall

```bash
curl -sSL https://raw.githubusercontent.com/Lusan-sapkota/smart-shell/main/install.sh | bash -s -- --uninstall
rm -rf ~/.config/smart-shell ~/.local/share/smart-shell   # also delete config and history
```

Details in [Uninstall](https://smart-shell.lusansapkota.com.np/uninstall/).

## Documentation

- [Features](https://smart-shell.lusansapkota.com.np/features/)
- [Installation](https://smart-shell.lusansapkota.com.np/installation/)
- [Usage](https://smart-shell.lusansapkota.com.np/usage/)
- [Safety](https://smart-shell.lusansapkota.com.np/safety/)
- [Uninstall](https://smart-shell.lusansapkota.com.np/uninstall/)
- [Development](https://smart-shell.lusansapkota.com.np/development/)
- [API Reference](https://smart-shell.lusansapkota.com.np/api/)
- [FAQ](https://smart-shell.lusansapkota.com.np/faq/)
- [Changelog](https://smart-shell.lusansapkota.com.np/CHANGELOG/)
- [Future Changes](https://smart-shell.lusansapkota.com.np/futurechanges/)
- [Contributing](https://smart-shell.lusansapkota.com.np/contributing/)
- [Author](https://smart-shell.lusansapkota.com.np/author/)

Full documentation: [smart-shell.lusansapkota.com.np](https://smart-shell.lusansapkota.com.np/).

## License

Apache 2.0. See [LICENSE](https://github.com/Lusan-sapkota/smart-shell/blob/main/LICENSE).

## Author

Created by [Lusan Sapkota](https://lusansapkota.com.np).

## Disclaimer

Smart-Shell is an AI assistant and can generate wrong or unsafe commands. Always read a command before you confirm it, especially anything that modifies the system or touches sensitive data.
