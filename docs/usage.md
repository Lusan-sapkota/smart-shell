# Usage

## Quick start

```bash
smart-shell                                   # interactive mode
smart-shell "list all PDF files here"         # one-off prompt
smart-shell "free up disk space" --dry-run
```

## CLI commands

| Command                           | Description                                   |
|-----------------------------------|-----------------------------------------------|
| `smart-shell`                     | Start interactive mode                        |
| `smart-shell "<prompt>"`          | Run a single prompt (same as `smart-shell run "<prompt>"`) |
| `smart-shell setup`               | Configure provider, API key and default model |
| `smart-shell models`              | List models from the configured provider      |
| `smart-shell --list-models`       | Same as `models`                              |
| `smart-shell history`             | Show command history                          |
| `smart-shell version`             | Show version information                      |
| `smart-shell --help`              | Show CLI help                                 |

Options for `run`:

| Option                | Description                                                        |
|-----------------------|--------------------------------------------------------------------|
| `--dry-run`, `-d`     | Show the plan without executing it                                 |
| `--model`, `-m NAME`  | Use a specific model for this run                                  |
| `--interactive`, `-i` | Start interactive mode                                             |
| `-y`                  | Skip confirmations (blocked commands still never run)              |
| `--provider NAME`     | Use another provider for this run (`ollama`, `deepseek`, ...)      |
| `--base-url URL`      | Use another OpenAI-compatible URL for this run                     |

`--provider` and `--base-url` also work without a subcommand (`smart-shell --provider ollama`) to start interactive mode against that provider. Your saved API key is only sent to the server it was saved for; for a different cloud provider, pass the key in `SMART_SHELL_API_KEY`.

## Interactive commands

Type `/` at the `>` prompt to open the command menu: it shows each command with a short description, and after `/model ` it completes model names from your provider. The older `!help` style still works.

| Command          | Description                               |
|------------------|-------------------------------------------|
| `/help`          | Show help                                 |
| `/history`       | Show command history                      |
| `/clear`         | Clear the screen                          |
| `/models`        | List models from the provider             |
| `/model <name>`  | Switch model for this session             |
| `/explain <cmd>` | Explain what a command does, with its safety level |
| `/last`          | Show the last generated command           |
| `/redo`          | Re-run the last plan (all steps, after a safety check) |
| `/errors`        | Show the error log                        |
| `/forget-sudo`   | Run `sudo -k` to drop cached sudo credentials |
| `/update`        | Check for a new version and upgrade with uv, pipx or pip |
| `/docs`          | Show the documentation link               |
| `/mode <name>`   | Switch mode: `ask`, `auto` or `plan` (also Shift+Tab) |
| `/notify`        | Turn waiting-for-you notifications on or off |
| `/exit`          | Quit                                      |

### Keys

| Key                 | Action                                  |
|---------------------|-----------------------------------------|
| `Shift+Tab`         | Cycle mode: ask, auto, plan             |
| `Tab`, arrow keys   | Pick from the `/` menu                  |
| `Esc`, then `Enter` | New line inside a request               |
| `Up`, `Ctrl+R`      | Previous requests, search them          |
| `Ctrl+C`            | Clear the line (or stop a running command) |
| `Ctrl+D`            | Quit (as do `/exit`, `exit`, `quit`, `q`) |

The status bar at the bottom shows the mode, provider, model, shell and current folder.

### Modes

| Mode   | What happens |
|--------|--------------|
| `ask`  | Default. Every plan asks yes / no / edit. |
| `auto` | Plans where every step is **safe** run without asking. Anything else still asks: `sudo`, `rm` and other deletions, package installs, git resets, info leaks. Blocked plans never run. |
| `plan` | Shows plans only and runs nothing, like `--dry-run`. |

`smart-shell --dry-run` starts in plan mode.

### Notifications

When Smart-Shell waits for your answer (yes / no / edit, or "fix it?"), it rings the terminal bell. If you have been away from the keyboard for 5 seconds or more, it also sends a desktop notification:

- **Konsole, kitty, Alacritty, xterm, foot** and other terminals on Linux: through `notify-send` (KDE, GNOME and other desktops show it like any notification).
- **GNOME Terminal, Ptyxis, Ghostty, WezTerm**: through the terminal's own notification support.
- **iTerm2, Windows Terminal**: through the terminal's own notification support.
- **macOS Terminal.app**: through Notification Center.
- **Over SSH**: bell only.

Turn it off with `/notify`, or `"notify": false` in the config file.

## How a prompt runs

1. The model returns one or more commands.
2. Each command is classified (see [Safety](safety.md)) and shown in a preview.
3. You answer **yes / no / edit**. The default is no for high or medium risk, yes otherwise. Blocked plans can only be edited or cancelled. `-y` answers yes, except for blocked plans.
4. The plan runs in one shell joined with `&&`, stopping at the first failure. Output appears live, and interactive prompts (like `apt`'s y/n) work.
5. If it fails, Smart-Shell offers to ask the AI for a fix. It sends the command and the last lines of its error output, then shows the corrected plan for review.

In interactive mode, your last few requests and their commands are sent along with each new one, so follow-ups work: "list the biggest files in ~/Downloads", then "now delete the ones older than a year".

`sudo` asks for your password in the terminal as usual. Smart-Shell never stores it.

## Configuration

Run `smart-shell setup` (outside the REPL) to change provider or default model. See [Installation](installation.md#providers) for the config file and environment variables.
