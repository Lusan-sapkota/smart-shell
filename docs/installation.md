# Installation

## Quick Installation (Recommended)

Smart-Shell is designed for easy installation with a single command that handles all dependencies and environment setup automatically.

**Quick install (recommended for most users):**

```bash
curl -sSL https://raw.githubusercontent.com/Lusan-sapkota/smart-shell/main/install.sh | bash
```

The installation script will:

1. Check and install all required dependencies
2. Install Smart-Shell using pipx (for better isolation)
3. Create desktop entries for easy access
4. Set up command completion for Bash and Zsh
5. Apply fixes for common Python module path issues
6. Automatically run the setup wizard to configure your API key

> If you're behind a corporate firewall or have restricted internet access, you might need to manually install dependencies first:
> ```bash
> pip install --user google-genai rich click pyyaml requests google-api-core
> ```

After installation, use Smart-Shell from any terminal:

```bash
smart-shell
```

## CLI Commands

- `smart-shell` — Start Smart-Shell in interactive mode
- `smart-shell run <prompt>` — Convert natural language to Bash/Zsh commands
- `smart-shell --interactive` or `-i` — Start interactive mode explicitly
- `smart-shell setup` — Configure API key and settings
- `smart-shell models` — List available AI models
- `smart-shell history` — Show command history
- `smart-shell --help` or `smart-shell help` — Show CLI help
- `smart-shell --version` or `smart-shell version` — Show version information
- `smart-shell --dry-run` or `-d` — Show command without executing

## Manual Installation Options

The install script offers three installation methods:

1. **System-wide installation** (requires sudo)
   - Installs Smart-Shell for all users on the system
   - Requires administrator privileges

2. **User installation** (recommended)
   - Uses pipx for isolated installation in your user directory
   - No administrator privileges required
   - Automatically installed if pipx is not found

3. **Virtual environment** (for development)
   - Creates a dedicated virtual environment
   - Useful for development or testing

For development setup, see [Development](development.md).

For troubleshooting and more, see the [FAQ](faq.md).

## Dependencies

Smart-Shell requires the following Python packages:

- `google-genai` - Google's Gemini AI SDK
- `rich` - For beautiful terminal formatting
- `click` - For command-line interface
- `pyyaml` - For configuration management
- `requests` - For API communication
- `google-api-core` - Core Google API functionality

The installation script handles all these dependencies automatically.
