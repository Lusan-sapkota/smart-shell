# Smart-Shell

![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen)
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
  Rich REPL interface with protected prompt and support for special commands like:  
  `!help`, `!docs`, `!models`, `!history`, `!clear`, `!redo`, `!last`, `!creator`, `!forget-sudo`, `!update`, `!errors`, `!web`, and more.

- 🛡️ **Built-in Safety System**  
  Analyzes each command and classifies it into **four risk levels** with detailed reasoning:
  - ✅ **Safe** – Executed automatically.
  - 🔵 **Info Leak** – May expose sensitive data (requires confirmation).
  - 🟡 **Medium** – Sudo operations and system changes (requires y/n confirmation).
  - 🔴 **High** – Dangerous operations like file deletion (requires y/n confirmation).  
  This ensures potentially destructive commands are never run without user awareness.

- 🤖 **AI-Powered Command Planning**  
  Generates and refines shell commands using **Google Gemini** models.

- 🔀 **Multi-Model Support with Smart Warnings**  
  Easily switch between Gemini **Pro**, **Flash**, and **Legacy** models with detailed cost information and confirmation prompts for premium models.

- 💳 **Smart Cost Awareness**  
  Real-time model pricing information with detailed cost breakdowns and confirmation prompts when switching to premium models.

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

Install Smart-Shell with a single command:

```bash
curl -sSL https://raw.githubusercontent.com/Lusan-sapkota/smart-shell/main/install.sh | bash
```

Our intelligent installation script:
- ✅ Automatically checks and installs all dependencies (including pipx if needed)
- ✅ Handles package installation with proper isolation
- ✅ Creates desktop entries and command completion
- ✅ Fixes common Python module path issues
- ✅ Runs the setup wizard to configure your API key

After installation, use Smart-Shell from any terminal:

```bash
smart-shell
```

The first time you run Smart-Shell, it will guide you through setting up your Google Gemini API key. You can also run the setup wizard anytime:

```bash
smart-shell setup
```

For manual installation and development instructions, see [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

## �️ Uninstall

To completely remove Smart-Shell from your system, run this single command:

```bash
curl -sSL https://raw.githubusercontent.com/Lusan-sapkota/smart-shell/main/install.sh | bash -s -- --uninstall
```

### Manual Uninstall

If you prefer to uninstall manually, follow these steps:

**1. Remove the Smart-Shell package:**

```bash
# If installed with pipx (recommended)
pipx uninstall smart-shell

# If installed system-wide
sudo pip3 uninstall smart-shell

# If installed in a virtual environment
rm -rf ./venv  # (from the project directory)
```

**2. Remove configuration files:**

```bash
rm -rf ~/.config/smart-shell
```

**3. Remove desktop entry:**

```bash
rm -f ~/.local/share/applications/smart-shell.desktop
```

**4. Remove shell completion:**

```bash
rm -f ~/.local/share/bash-completion/completions/smart-shell-completion.bash
```

**5. Clean up shell configuration:**

```bash
# Remove from .bashrc
sed -i '/# Smart-Shell completion/,+1d' ~/.bashrc

# Remove from .zshrc (if exists)
sed -i '/# Smart-Shell completion/,+1d' ~/.zshrc
```

**6. Remove any remaining executables:**

```bash
rm -f ~/.local/bin/smart-shell
rm -f ~/.local/bin/smart-shell.bak
```

After completing these steps, restart your terminal or run `source ~/.bashrc` (or `source ~/.zshrc`) to reload your shell configuration.

## �📖 Documentation

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
- [Uninstall](docs/uninstall.md)
- [New-Version](docs/futurechanges.md)

> 📚 **Full documentation is available at the [Smart-Shell MkDocs site](https://lusan-sapkota.github.io/smart-shell/).**

## 📜 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

Created by [Lusan Sapkota](https://lusansapkota.com.np)

## ⚠️ Disclaimer

Smart-Shell is an AI assistant and may occasionally generate incorrect or unsafe commands. Always review commands before execution, especially those involving system modifications or sensitive data.
