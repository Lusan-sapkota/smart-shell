# Usage

## Interactive Mode

Start Smart-Shell in interactive mode:

```bash
smart-shell
```

Type natural language commands and Smart-Shell will convert them to Bash/Zsh. Exit with `exit`, `quit`, or `Ctrl+C`.

## One-off Commands

```bash
smart-shell run "list all pdf files in the current directory"
smart-shell run "delete all log files" --dry-run
smart-shell run "find large files" --model gemini-2.5-flash
smart-shell run "restart apache" --yes
```

## Available Commands

- `smart-shell` or `smart-shell run`: Convert natural language to Bash/Zsh commands
- `smart-shell setup`: Configure your API key
- `smart-shell version`: Display version information
- `smart-shell history`: Show command history

## Special Commands (Interactive Mode)

- `!history` - Show command history
- `!clear` - Clear the screen
- `!help` - Show help
- `!model <model-name>` - Change the AI model

## Options

- `--dry-run`, `-d`: Show command without executing
- `--model`, `-m`: Specify model to use
- `--interactive`, `-i`: Run in interactive mode
- `--yes`, `-y`: Automatically confirm all prompts

See [Features](features.md) for more details.
