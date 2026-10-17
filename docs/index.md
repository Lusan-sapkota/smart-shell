# Smart-Shell

![Smart-Shell Logo](images/image.png)

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](license.md)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![AI](https://img.shields.io/badge/AI-Local%20%2F%20OpenAI--compatible-orange)](installation.md#providers)

Smart-Shell turns plain English into Bash or Zsh commands, checks each one for risk, and runs it after you confirm. It runs on a local AI model through Ollama or LM Studio, fully offline, or on any OpenAI-compatible chat API (Gemini, OpenAI, DeepSeek, OpenRouter, Groq).

## Quick start

```bash
pipx install smart-shell-cli   # or: uv tool install smart-shell-cli
smart-shell setup              # choose a provider and default model
smart-shell         # start the interactive shell
```

Then try prompts like:

- "list all files in the current directory"
- "show system memory usage"
- "create a new directory called project"

## Documentation

**Getting started**

- [Features](features.md): what Smart-Shell does
- [Installation](installation.md): install options, providers, local models
- [Usage](usage.md): CLI and interactive commands
- [Uninstall](uninstall.md)

**Reference**

- [Safety](safety.md): risk levels and confirmations
- [API Reference](api.md): module overview
- [FAQ](faq.md)

**Development**

- [Development Guide](development.md)
- [Contributing](contributing.md)

**Project**

- [Changelog](CHANGELOG.md)
- [Future Changes](futurechanges.md)
- [License](license.md)
- [Author](author.md)

## Support

Report bugs or request features on [GitHub Issues](https://github.com/Lusan-sapkota/smart-shell/issues).
