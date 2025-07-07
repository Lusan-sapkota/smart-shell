# Frequently Asked Questions (FAQ)

## 🤔 General Questions

### What is Smart-Shell?
Smart-Shell is an advanced AI-powered terminal assistant that converts natural language to Bash/Zsh commands using Google Gemini AI models. It's not just a simple wrapper - it's a comprehensive tool with safety systems, interactive features, and intelligent command generation.

### How does Smart-Shell work?
Smart-Shell uses Google's Gemini AI models to interpret your natural language requests and convert them into appropriate shell commands. It includes a sophisticated safety system that analyzes each command before execution.

### Is Smart-Shell safe to use?
Yes! Smart-Shell includes a robust 4-tier safety system (Safe, Info Leak, Medium, High) that analyzes every command and requires confirmation for potentially risky operations. You maintain full control over what gets executed.

### What shells does Smart-Shell support?
Smart-Shell works with both **Bash** and **Zsh**. It automatically detects your current shell environment and generates compatible commands.

### What operating systems are supported?
Smart-Shell works on:
- **Linux** (all major distributions)
- **macOS** 
- **Windows** (via WSL - Windows Subsystem for Linux)

## 🚀 Installation & Setup

### How do I install Smart-Shell?
**Quick Installation:**
```bash
curl -sSL https://raw.githubusercontent.com/Lusan-sapkota/smart-shell/main/install.sh | bash
```

For other installation methods, see our [Installation Guide](installation.md).

### How do I set up my API key?
1. **Interactive setup:** Run `smart-shell setup`
2. **Environment variable:** Set `SMART_SHELL_API_KEY` in your shell profile
3. **Direct configuration:** The setup wizard will guide you through the process

### Where do I get a Google Gemini API key?
1. Visit [Google AI Studio](https://ai.google.dev/)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key and use it in Smart-Shell setup

### Can I use Smart-Shell without an API key?
Currently, Smart-Shell requires a Google Gemini API key for AI functionality. However, **v1.1.0 will introduce offline mode** with local LLM support that won't require any API keys.

## 💬 Usage Questions

### What special commands are available?
Smart-Shell's interactive mode supports many built-in commands:

- `!help` - Show available commands and usage
- `!history` - View command execution history
- `!models` - List and switch between AI models
- `!update` - Check for and install updates
- `!clear` - Clear the terminal screen
- `!web` - Toggle web search integration
- `!redo` - Re-execute the last command
- `!last` - Show the last executed command
- `!errors` - View recent error logs
- `!docs` - Open documentation links
- `!creator` - Information about the creator
- `!forget-sudo` - Clear stored sudo password
- `!exit` - Exit Smart-Shell safely

### How does the safety system work?
Smart-Shell analyzes every command and classifies it into four risk levels:

- ✅ **Safe** - Executed automatically (e.g., `ls`, `pwd`)
- 🔵 **Info Leak** - May expose sensitive data, requires confirmation (e.g., `env`, `history`)
- 🟡 **Medium** - Requires elevated privileges, needs confirmation (e.g., `sudo apt install`)
- 🔴 **High** - Potentially destructive, requires explicit confirmation (e.g., `rm -rf`)

### How does prompt protection work?
The interactive prompt prevents accidental deletion of the "Smart-Shell (model):" prefix when backspacing, so you can only edit your actual input. This prevents command injection and maintains a clean interface.

### Can I use Smart-Shell in scripts?
Smart-Shell is primarily designed for interactive use. For scripting, you can use the command-line interface:
```bash
smart-shell "your natural language command here"
```

## 🔧 Technical Questions

### How do I update Smart-Shell?
- **Interactive mode:** Use the `!update` command
- **Command line:** Run `smart-shell --update`
- **Manual:** Use `pipx upgrade smart-shell` if installed with pipx

### How much does it cost to use Smart-Shell?
Smart-Shell itself is free and open source. However, it uses Google's Gemini API, which has usage-based pricing:
- **Gemini Flash:** Very affordable for most users
- **Gemini Pro:** Higher cost but more capable
- **Rate limits:** Free tier includes generous limits

Smart-Shell shows cost information when switching models.

### Can I use Smart-Shell offline?
**Current version:** Requires internet connection for AI functionality.
**Coming in v1.1.0:** Complete offline mode with local LLM support (Ollama, LM Studio, etc.).

### How do I configure Smart-Shell?
Configuration is stored in `~/.config/smart-shell/config.json`. You can:
- Use `smart-shell setup` for interactive configuration
- Edit the config file directly
- Set environment variables for overrides

### What data does Smart-Shell collect?
Smart-Shell is privacy-focused:
- **Sent to AI:** Only your natural language commands
- **Not sent:** Terminal output, file contents, system information
- **Local storage:** API keys (encrypted), preferences, command history
- **No telemetry:** Smart-Shell doesn't collect usage analytics

## 🛠️ Troubleshooting

### Smart-Shell command not found after installation
1. **Restart your terminal** or run `source ~/.bashrc` (or `~/.zshrc`)
2. **Check PATH:** Ensure `~/.local/bin` is in your PATH
3. **Reinstall:** Try the installation script again
4. **Manual installation:** See [Installation Guide](installation.md)

### API key errors
- **Invalid key:** Verify your API key at [Google AI Studio](https://ai.google.dev/)
- **Quota exceeded:** Check your API usage limits
- **Network issues:** Verify internet connection

### Permission errors
- **Sudo issues:** Smart-Shell can store your sudo password (encrypted) for convenience
- **File permissions:** Ensure you have proper permissions for configuration directory

### Command execution fails
- **Check syntax:** Verify the generated command makes sense
- **Dry run:** Use dry-run mode to preview commands before execution
- **Error logs:** Use `!errors` to view recent error information

### Installation issues with pipx
See our [Installation Guide](installation.md) for comprehensive troubleshooting, including:
- PEP 668 compliance issues
- Python environment problems
- Dependency conflicts

## 🤝 Contributing & Support

### Can I contribute to Smart-Shell?
Absolutely! We welcome contributions:
- **Bug reports:** Open issues on GitHub
- **Feature requests:** Suggest new features
- **Code contributions:** Submit pull requests
- **Documentation:** Help improve docs

See our [Contributing Guide](contributing.md) for details.

### Where can I get help?
1. **Built-in help:** Use `!help` in Smart-Shell
2. **Documentation:** Check our comprehensive docs
3. **GitHub Issues:** Report bugs or ask questions
4. **Community:** Join discussions on GitHub

### How do I report a bug?
1. **Check existing issues:** Search GitHub issues first
2. **Gather information:** Include Smart-Shell version, OS, error messages
3. **Create an issue:** Use our bug report template
4. **Provide details:** Steps to reproduce, expected vs actual behavior

### How can I request a feature?
1. **Check roadmap:** Review [Future Changes](futurechanges.md)
2. **Search existing:** Look for similar feature requests
3. **Create request:** Open a GitHub issue with the feature request template
4. **Describe use case:** Explain why the feature would be valuable

## 🔮 Future Plans

### What's coming in v1.1.0?
Major features planned for the next release:
- **Offline Mode:** Complete privacy with local LLM support
- **Safe Continuous REPL:** Multi-step command execution
- **Enhanced Safety:** Advanced risk classification
- **Local Models:** Support for Ollama, LM Studio, and custom models

### When will offline mode be available?
Offline mode is targeted for **Smart-Shell v1.1.0** in **Q2-Q3 2025**. Follow our [Development Timeline](futurechanges.md) for updates.

### Will Smart-Shell always be free?
Yes! Smart-Shell is open source under the Apache 2.0 license and will always remain free. The only costs are optional API usage fees from Google's Gemini service.
