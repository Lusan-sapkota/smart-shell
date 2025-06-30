# Smart-Shell Documentation

This documentation is built with [MkDocs](https://www.mkdocs.org/) and the Material theme. It covers all features, installation methods, usage, safety, development, API reference, changelog, and more.

---

## 📦 Features

- Interactive Mode: Natural language to Bash/Zsh command conversion
- Safety Checks: Protection against dangerous commands
- Multiple AI Models: Gemini model support
- Command History: Track and recall commands
- Secure API Key Management
- Tab Completion
- Desktop Integration
- Network Error Handling
- Automatic Retries
- Dry Run Mode
- Model Selection
- History Search
- Custom Configuration
- Extensible

---

## 🚀 Quick Installation

```bash
curl -sSL https://raw.githubusercontent.com/Lusan-sapkota/smart-shell/main/install.sh | bash
```

---

## 🛠️ Manual Installation & Development

### Prerequisites
- Python 3.8 or higher
- pip
- git

### Clone the Repository

```bash
git clone https://github.com/Lusan-sapkota/smart-shell.git
cd smart-shell
```

### Set Up Development Environment

#### Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

#### User Installation

```bash
pip install --user -e .
```

#### System-wide Installation

```bash
sudo pip install -e .
```

### Set Up Your API Key

1. Get your API key from [Google AI Studio](https://ai.google.dev/)
2. Set it as an environment variable:
   ```bash
   export SMART_SHELL_API_KEY=your-api-key-here
   ```

---

## 🧑‍💻 Project Structure

- `smart_shell/`: Main source code
- `docs/`: Documentation
- `examples/`: Usage examples
- `install.sh`: Installer script
- `requirements.txt`, `pyproject.toml`: Dependencies

---

## 🛡️ Safety System

Smart-Shell includes a comprehensive safety system to protect users from potentially harmful commands.

### Safety Levels
- **Safe** 🟢: Commands that are considered safe
- **Warning** 🟡: Might have unintended consequences (requires confirmation)
- **Blocked** 🔴: Potentially harmful (will not be executed)

### Safety Checks
- **Blocked Commands:** Explicitly blocks dangerous commands (e.g., `rm -rf /`, fork bombs, disk formatting)
- **Pattern Matching:** Uses regex to identify risky command patterns (e.g., `sudo`, `rm -rf`)
- **Path Analysis:** Detects operations on sensitive system paths (e.g., `/etc/passwd`)

---

## 🧩 API Reference

### Main Modules
- `smart_shell.main`: Entry point and CLI logic
- `smart_shell.ai_wrapper`: Handles AI model communication
- `smart_shell.safety`: Safety checks and command validation
- `smart_shell.config`: Configuration and API key management
- `smart_shell.shell_builder`: Bash/Zsh command construction
- `smart_shell.utils`: Utility functions
- `smart_shell.setup_logic`: Setup and installation logic

### Key Classes & Functions
- `AIWrapper`: Main class for interacting with Gemini models
- `AIWrapper.generate_command(prompt, model)`: Generate Bash/Zsh command from prompt
- `SafetyChecker`: Class for command safety analysis
- `SafetyChecker.check(command)`: Returns safety level and reason
- `ConfigManager`: Handles config file and environment variables
- `ConfigManager.get_api_key()`: Returns API key
- `ShellBuilder`: Converts structured command to Bash/Zsh

---

## 📝 Changelog

See [CHANGELOG.md](../CHANGELOG.md) for the full project changelog.

---

## 👤 Author

Created by [Lusan Sapkota](https://lusansapkota.com.np)

---

## 🤝 Contributing

- Fork the repository
- Create a new branch for your feature or bugfix
- Make your changes and add tests if applicable
- Submit a pull request with a clear description

See [Contributing](contributing.md) for more.

---

## ❓ FAQ

- **What is Smart-Shell?**
  - An AI-powered terminal assistant that converts natural language to Bash/Zsh commands using Gemini models.
- **Is it safe to use?**
  - Yes, Smart-Shell includes robust safety checks to prevent dangerous commands.
- **How do I install it?**
  - Use the quick install command or see Installation.
- **How do I set my API key?**
  - Run `smart-shell setup` or set the `SMART_SHELL_API_KEY` environment variable.
- **Can I contribute?**
  - Absolutely! See Contributing.
- **Where can I get help?**
  - Open an issue on GitHub or check the Development Guide.

---

## 📚 Building Docs with MkDocs

1. Install MkDocs and dependencies:
   ```bash
   pip install mkdocs mkdocs-material mkdocstrings
   ```
2. Serve the docs locally:
   ```bash
   mkdocs serve
   ```
3. Build static site for GitHub Pages:
   ```bash
   mkdocs build
   ```
4. Deploy to GitHub Pages:
   ```bash
   mkdocs gh-deploy
   ```

---

For more, see the [MkDocs documentation](https://www.mkdocs.org/).
