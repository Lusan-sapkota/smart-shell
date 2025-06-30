# Smart-Shell

[![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen)](https://github.com/Lusan-sapkota/smart-shell)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Gemini](https://img.shields.io/badge/AI-Google%20Gemini-orange)](https://ai.google.dev/)

> **Smart-Shell is in active development.**

<p align="center">
  <img src="docs/images/image.png" alt="Smart-Shell Demo" width="500"/>
</p>

Smart-Shell is an intelligent terminal assistant that converts natural language into executable Bash or Zsh commands using Google's Gemini AI models via the new google-genai SDK.

## ✨ Features

- 🧠 **Natural Language to Command**  
  Convert plain English into valid Bash/Zsh commands instantly.

- 🐚 **Shell Auto-Detection**  
  Automatically detects and supports both **Bash** and **Zsh** environments.

- 💬 **Interactive Mode with Command History**  
  Rich REPL interface with support for special commands like:  
  `!help`, `!docs`, `!models`, `!history`, `!clear`, `!redo`, `!last`, `!creator`, `!forget-sudo`, `!update`, `!errors`, `!web`, and more.

- 🛡️ **Built-in Safety System**  
  Analyzes each command and classifies it into **three risk levels** - Reason also provided:
  - ✅ **Safe** – Executed automatically.
  - ⚠️ **Medium** – Requires manual confirmation (yes/no).
  - ❌ **High** – Requires manual confirmation (yes/no).  
  This ensures dangerous or potentially destructive commands are never run blindly.

- 🤖 **AI-Powered Command Planning**  
  Generates and refines shell commands using **Google Gemini** models.

- 🔀 **Multi-Model Support**  
  Easily switch between Gemini **Pro**, **Flash**, and **Legacy** models as needed.

- 🧪 **Dry-Run Mode**  
  Preview the exact command before execution for extra safety and transparency.

- 📟 **Standard CLI Commands**  
  Includes `--help`, `--version`, and other CLI flags for quick access.

- 🖥️ **Desktop Integration**  
  Comes with a `.desktop` entry — launch directly from your system's **Application Menu**.

- ⌨️ **Tab Completion**  
  Supports intelligent tab completion for both **Bash** and **Zsh** shells.

- 🔐 **Simple Setup**  
  Easy configuration of your API key and sudo password during first run.

- 🌐 **Web Search Integration**  
  When enabled, Smart-Shell performs relevant **web searches** in real-time to enhance command accuracy.  
  AI combines local knowledge with live web results to refine its suggestions — giving you smarter, context-aware commands.  
  You can toggle web search anytime using the `!web` command.

- ⚡ **Modern CLI Experience**  
  A clean and user-friendly terminal UI with colorful output and rich formatting.

- 🛠️ **Open Source & Extensible**  
  Easily extend functionality or contribute — fully open and developer-friendly.

## Quick Install (Recommended)

Smart-Shell requires [pipx](https://pypa.github.io/pipx/) for user installations on most modern Linux systems (PEP 668).

```bash
curl -sSL https://raw.githubusercontent.com/Lusan-sapkota/smart-shell/main/install.sh | bash
```

> Please note: After running the install script, you may be prompted to install [pipx](https://pypa.github.io/pipx/) if you want a user-level isolated install. The script will guide you if this is needed.
> After installation, run `smart-shell setup` to configure your API key and sudo password.
> If you want to install from source for development, clone the repo and run the install script from the project directory.

After installation, use Smart-Shell from any terminal:

```bash
smart-shell
```

### Setting up your API key

After installation, you'll need to set up your Google Gemini API key (one-time setup):

```bash
smart-shell setup
```

For manual installation and development instructions, see [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

## 📖 Documentation

- [Features](docs/features.md)
- [Installation](docs/installation.md)
- [Usage](docs/usage.md)
- [Safety](docs/safety.md)
- [Development](docs/development.md)
- [API Reference](docs/api.md)
- [Changelog](CHANGELOG.md)
- [License](LICENSE)
- [Author](docs/author.md)
- [Contributing](docs/contributing.md)
- [FAQ](docs/faq.md)

> 📚 **Full documentation is available at the [Smart-Shell MkDocs site](https://lusan-sapkota.github.io/smart-shell/).**

## 📜 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

Created by [Lusan Sapkota](https://lusansapkota.com.np)

## ⚠️ Disclaimer

Smart-Shell is an AI assistant and may occasionally generate incorrect or unsafe commands. Always review commands before execution, especially those involving system modifications or sensitive data.