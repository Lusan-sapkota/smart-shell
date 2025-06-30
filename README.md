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
  Ask questions, search documentation, or look up errors directly from the CLI.

- ⚡ **Modern CLI Experience**  
  A clean and user-friendly terminal UI with colorful output and rich formatting.

- 🛠️ **Open Source & Extensible**  
  Easily extend functionality or contribute — fully open and developer-friendly.

## 🚀 Quick Installation (One Command)

Simply run this single command to install Smart-Shell system-wide:

```bash
curl -sSL https://raw.githubusercontent.com/Lusan-sapkota/smart-shell/main/install.sh | bash
```

> Please note: Run smart-shell setup command after this to setup api key and sudo password.

That's it! After installation, you can immediately use Smart-Shell from any terminal by typing:

```bash
smart-shell
```

The installer will:
- Check dependencies and install them if needed
- Install Smart-Shell globally on your system
- Set up command completion for bash/zsh
- Create desktop entry for launching from application menu
- Prompt you to set up your API key (one-time setup)

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