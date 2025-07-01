# Features

## Smart-Shell offers a rich set of features to make your terminal experience smarter and safer:

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

- 📦 **Reliable Installation with pipx**  
  Install and manage Smart-Shell using `pipx` for an isolated and reliable setup, adhering to modern Linux standards (PEP 668).

- 🔄 **Smart Update System**  
  Real-time version checking against GitHub releases with automatic updates using `!update` command.

- 🔒 **Protected Interactive Prompt**  
  Smart prompt protection prevents accidental deletion of the "Smart-Shell (model):" prefix when backspacing.

- 🚨 **Smart Command Detection**  
  Detects when users try to run Smart-Shell CLI commands within the interactive mode and provides helpful guidance.

- ⚡ **Enhanced AI Performance**  
  Optimized generation parameters and more resilient error handling for faster, more reliable command generation.

- 🎯 **Flexible Confirmation System**  
  All confirmations accept both `y`/`yes` and `n`/`no` responses in any case for better user experience.


For a full list of commands and usage, see the [Installation](installation.md) and [Usage](usage.md) docs.
