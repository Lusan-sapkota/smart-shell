# Features

## Smart-Shell offers a rich set of features to make your terminal experience smarter and safer:

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

- 📦 **Reliable Installation with pipx**  
  Install and manage Smart-Shell using `pipx` for an isolated and reliable setup, adhering to modern Linux standards (PEP 668).


For a full list of commands and usage, see the [Installation](installation.md) and [Usage](usage.md) docs.
