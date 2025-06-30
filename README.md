# Smart-Shell

[![Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen)](https://github.com/Lusan-sapkota/smart-shell)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![Gemini](https://img.shields.io/badge/AI-Google%20Gemini-orange)](https://ai.google.dev/)

> **Smart-Shell is in active development.** Features and functionality may change rapidly.

Smart-Shell is an intelligent terminal assistant that converts natural language into executable Bash commands using Google's Gemini AI models.

```
    _____                      _      _____ _          _ _                                                      
   / ____|                    | |    / ____| |        | | |                                                     
  | (___  _ __ ___   __ _ _ __| |_  | (___ | |__   ___| | |                                                     
   \___ \| '_ ` _ \ / _` | '__| __|  \___ \| '_ \ / _ \ | |                                                     
   ____) | | | | | | (_| | |  | |_   ____) | | | |  __/ | |                                                     
  |_____/|_| |_| |_|\__,_|_|   \__| |_____/|_| |_|\___|_|_|                                                     
```

## ✨ Features

- 🔄 **Interactive Mode**: Continuous natural language to Bash command conversion
- 🛡️ **Safety Checks**: Built-in protection against dangerous commands
- 🤖 **Multiple AI Models**: Support for various Gemini models
- 📋 **Command History**: Track and recall past commands
- 🔑 **Secure API Key Management**: Environment variables or config file storage
- 🔌 **Tab Completion**: Bash completion for all commands and options
- 🖥️ **Desktop Integration**: Launch from application menu

## 🚀 Installation

### Quick Install

Run the installation script:

```bash
chmod +x install.sh
./install.sh
```

The script will guide you through the installation process with the following options:
1. System-wide installation (requires sudo)
2. User-only installation
3. Virtual environment installation

### Manual Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Lusan-sapkota/smart-shell.git
   cd smart-shell
   ```

2. Install the package:
   ```bash
   # System-wide
   sudo pip3 install -e .
   
   # User-only
   pip3 install --user -e .
   
   # Virtual environment
   python3 -m venv venv
   source venv/bin/activate
   pip3 install -e .
   ```

3. Set up your API key:
   ```bash
   smart-shell setup
   ```

## 📖 Usage

### Interactive Mode (Recommended)

Simply run:

```bash
smart-shell
```

This will start an interactive session where you can type natural language commands until you exit.
Type `exit`, `quit`, or press `Ctrl+C` to exit.

### One-off Commands

```bash
# Basic usage
smart-shell run "list all pdf files in the current directory"

# Dry run (shows command without executing)
smart-shell run "delete all log files" --dry-run

# Use a specific model
smart-shell run "find large files" --model gemini-2.5-flash

# Auto-confirm all prompts
smart-shell run "restart apache" --yes
```

### Available Commands

- `smart-shell` or `smart-shell run`: Convert natural language to Bash commands
- `smart-shell setup`: Configure your API key
- `smart-shell version`: Display version information
- `smart-shell history`: Show command history

### Special Commands (Interactive Mode)

In interactive mode, you can use these special commands:
- `!history` - Show command history
- `!clear` - Clear the screen
- `!help` - Show help
- `!model <model-name>` - Change the AI model

### Options

- `--dry-run`, `-d`: Show command without executing
- `--model`, `-m`: Specify model to use (gemini-2.5-pro, gemini-2.5-flash, etc.)
- `--interactive`, `-i`: Run in interactive mode
- `--yes`, `-y`: Automatically confirm all prompts

## ⚙️ Configuration

Smart-Shell stores your API key and preferences in `~/.config/smart-shell/config.json`. You can edit this file directly or use the setup command:

```bash
smart-shell setup
```

You can also set your API key via environment variable (recommended for security):
```bash
export SMART_SHELL_API_KEY=your-api-key-here
```

## 🔐 API Key Support

Smart-Shell is optimized for Google Gemini models, but any valid Gemini-compatible API key is supported.
This allows developers to use their own Google Cloud or AI Studio API credentials.

While Smart-Shell could be adapted to work with other AI providers, Gemini was chosen due to its:
- Generous developer limits (60 RPM, 1000 RPD)
- Excellent command generation capability
- Speed, accuracy, and low cost
- Reliability for AI-driven shell experiences

## 🧠 AI Models

Smart-Shell supports multiple Gemini AI models:

| Model Name | Speed | Capabilities |
|------------|-------|--------------|
| gemini-2.5-pro | Medium | Most accurate, default model |
| gemini-2.5-flash | Fast | Lower latency, good output |
| gemini-2.0-pro | Legacy | Older version, fallback |

If using an invalid model name, Smart-Shell will show an error and fall back to the default model.

## 🛡️ Safety

Smart-Shell includes safety checks to prevent execution of potentially dangerous commands. Commands are categorized as:

- 🟢 **Safe**: Commands that are considered safe to run
- 🟡 **Warning**: Commands that might have unintended consequences (requires confirmation)
- 🔴 **Blocked**: Commands that are potentially harmful (will not be executed)

The safety system can:
- Detect dangerous system paths
- Identify risky command patterns
- Analyze redirections to sensitive locations
- Assess overall risk level of commands

## 🛠️ Development

See [DEVELOPMENT.md](docs/DEVELOPMENT.md) for development guidelines.

## 📜 License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

Created by [Lusan Sapkota](https://lusansapkota.com.np)

## ⚠️ Disclaimer

Smart-Shell is an AI assistant and may occasionally generate incorrect or unsafe commands. Always review commands before execution, especially those involving system modifications or sensitive data. 