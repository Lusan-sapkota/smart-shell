# FAQ

**Q: What is Smart-Shell?**
A: Smart-Shell is an advanced AI-powered terminal assistant that converts natural language to Bash/Zsh commands using Google Gemini models. It's not just a wrapper - it's a comprehensive tool with safety systems, interactive features, and intelligent command generation.

**Q: Is it safe to use?**
A: Yes, Smart-Shell includes a robust 4-level safety system (Safe, Info Leak, Medium, High) that analyzes commands and requires confirmation for potentially risky operations. You maintain full control over what gets executed.

**Q: How do I install it?**
A: Use the quick install command: `curl -sSL https://raw.githubusercontent.com/Lusan-sapkota/smart-shell/main/install.sh | bash` or see [Installation](installation.md) for other options.

**Q: How do I set my API key?**
A: Run `smart-shell setup` for interactive configuration, or set the `SMART_SHELL_API_KEY` environment variable directly.

**Q: Can I update Smart-Shell automatically?**
A: Yes! Use the `!update` command in interactive mode to check for and install updates from GitHub automatically.

**Q: What special commands are available?**
A: Interactive mode supports many commands like `!help`, `!history`, `!models`, `!update`, `!clear`, `!web`, and more. See [Usage](usage.md) for the complete list.

**Q: How does the prompt protection work?**
A: The interactive prompt prevents accidental deletion of the "Smart-Shell (model):" prefix when backspacing, so you can only edit your actual input.

**Q: Can I contribute?**
A: Absolutely! See [Contributing](contributing.md) for guidelines on how to contribute to the project.

**Q: Where can I get help?**
A: Use `!help` in interactive mode, check the documentation, or open an issue on GitHub for support.

**Q: Does Smart-Shell work with both Bash and Zsh?**
A: Yes! Smart-Shell automatically detects your shell and generates compatible commands for both Bash and Zsh environments.
