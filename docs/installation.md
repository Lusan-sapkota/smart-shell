# Installation

## Quick Installation (Recommended)

Smart-Shell is distributed as a standalone project and is not available on PyPI. The recommended way to install is using the official install script, which handles all dependencies and environment setup for you.

**Quick install (recommended for most users):**

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

## CLI Commands

- `smart-shell run <prompt>` — Convert natural language to Bash/Zsh commands
- `smart-shell --interactive` — Start interactive mode
- `smart-shell setup` — Configure API key and settings
- `smart-shell models` — List available AI models
- `smart-shell history` — Show command history
- `smart-shell --help` or `smart-shell help` — Show CLI help
- `smart-shell --version` or `smart-shell version` — Show version information

## Manual Installation (Advanced)

- **System-wide:** Use the install script and select system-wide (requires sudo).
- **Virtualenv:** Use the install script and select virtual environment (for development).

For development setup, see [Development](development.md).

For troubleshooting and more, see the [FAQ](faq.md).
