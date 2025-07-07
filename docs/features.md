# Features

Smart-Shell is packed with powerful features designed to make your terminal experience smarter, safer, and more efficient. Here's what makes Smart-Shell special:

## 🧠 Core AI Features

### Natural Language Processing
- **Plain English to Commands**: Convert natural language descriptions into executable shell commands
- **Context Understanding**: Smart-Shell understands the context of your requests
- **Command Refinement**: AI continuously improves command suggestions based on your environment

### Multi-Model AI Support
- **Google Gemini Integration**: Powered by Google's latest Gemini AI models
- **Model Selection**: Choose between Gemini Pro, Flash, and Legacy models
- **Smart Cost Awareness**: Real-time pricing information with confirmation prompts for premium models
- **Performance Optimization**: Automatic model selection based on query complexity

## 🛡️ Advanced Safety System

### Four-Tier Risk Classification
Smart-Shell analyzes every command and provides detailed safety assessment:

- ✅ **Safe** – Commands that are completely safe to execute automatically
  - Examples: `ls`, `pwd`, `echo`, `cat` (for non-sensitive files)
  
- 🔵 **Info Leak** – Commands that may expose sensitive system information
  - Examples: `env`, `ps aux`, `cat ~/.bashrc`, `history`
  - Requires user confirmation before execution
  
- 🟡 **Medium Risk** – Commands requiring elevated privileges or system modifications
  - Examples: `sudo apt install`, `systemctl start`, `chmod`, `chown`
  - Requires explicit y/n confirmation
  
- � **High Risk** – Potentially destructive or dangerous operations
  - Examples: `rm -rf`, `dd`, `mkfs`, `format`
  - Shows detailed warning and requires explicit confirmation

### Safety Features
- **Real-time Analysis**: Every command is analyzed before execution
- **Detailed Reasoning**: Understand why a command is classified at a certain risk level
- **User Control**: Full control over what gets executed and when
- **Audit Trail**: Track command execution and safety decisions

## 🐚 Shell Integration

### Multi-Shell Support
- **Bash Compatibility**: Full support for Bash environments
- **Zsh Integration**: Native Zsh support with advanced features
- **Auto-Detection**: Automatically detects your current shell environment
- **Cross-Platform**: Works on Linux, macOS, and WSL

### Desktop Integration
- **Application Menu**: Launch Smart-Shell from your desktop environment
- **Desktop Files**: Proper .desktop integration for Linux systems
- **Command Completion**: Intelligent tab completion for both Bash and Zsh
- **Shell History**: Integrates with your existing shell history

## 💬 Interactive Experience

### Rich REPL Interface
- **Command History**: Access and replay previous commands
- **Special Commands**: Built-in commands for enhanced functionality
- **Protected Prompt**: Safe prompt handling that prevents command injection
- **Session Management**: Persistent sessions with state management

### Special Commands
Access powerful built-in commands with the `!` prefix:

- `!help` - Show available commands and usage information
- `!docs` - Open documentation links
- `!models` - List and switch between AI models
- `!history` - View command execution history
- `!clear` - Clear the terminal screen
- `!redo` - Re-execute the last command
- `!last` - Show the last executed command
- `!creator` - Information about Smart-Shell's creator
- `!forget-sudo` - Clear stored sudo password
- `!update` - Check for Smart-Shell updates
- `!errors` - View recent error logs
- `!web` - Toggle web search integration
- `!exit` - Exit Smart-Shell safely

## 🌐 Web Search Integration

### Real-Time Enhancement
- **Live Web Search**: Performs relevant web searches to enhance command accuracy
- **Context-Aware Results**: AI combines local knowledge with live web results
- **Smart Filtering**: Only relevant technical information is used
- **Privacy Control**: Toggle web search on/off as needed

### Enhanced Accuracy
- **Up-to-Date Information**: Access latest command syntax and options
- **Platform-Specific**: Results tailored to your operating system
- **Error Resolution**: Web search helps resolve command errors

## 🔧 Advanced Features

### Dry-Run Mode
- **Preview Commands**: See exactly what will be executed before running
- **Safety Testing**: Test commands without actually executing them
- **Command Validation**: Verify command syntax and parameters

### Configuration Management
- **API Key Management**: Secure storage and management of API keys
- **Sudo Password**: Optional encrypted storage of sudo password
- **Model Preferences**: Save preferred AI models and settings
- **Web Search Settings**: Control web search behavior

### Error Handling
- **Intelligent Error Analysis**: AI analyzes command failures and suggests fixes
- **Error History**: Track and learn from previous errors
- **Recovery Suggestions**: Get suggestions for fixing failed commands

## 🚀 Performance Features

### Optimized Operation
- **Fast Response**: Optimized for quick command generation
- **Efficient API Usage**: Smart API call management to minimize costs
- **Local Caching**: Cache frequently used commands and patterns
- **Background Processing**: Non-blocking operations where possible

### Resource Management
- **Memory Efficient**: Minimal memory footprint
- **CPU Optimization**: Efficient processing of natural language queries
- **Network Optimization**: Optimized API calls and web searches

## � Coming Soon (v1.1.0)

### Offline Mode
- **Complete Privacy**: Local LLM support for offline operation
- **Zero Cloud Dependency**: No data sent to external servers
- **Local Model Integration**: Support for Ollama, LM Studio, and custom models

### Safe Continuous REPL
- **Multi-Step Execution**: Handle complex multi-command workflows
- **Command Chaining**: Safe execution of dependent commands
- **Context Preservation**: Maintain context across command sequences
- **Enhanced Privacy**: Summarized outputs instead of raw terminal data

## 📊 Usage Statistics

Smart-Shell provides insights into your usage patterns:
- **Command Statistics**: Track most-used command types
- **Safety Metrics**: Monitor safety system effectiveness
- **Performance Metrics**: Response times and success rates
- **Cost Tracking**: Monitor AI API usage and costs

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
