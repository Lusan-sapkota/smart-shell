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

Type these at the `Smart-Shell (model):` prompt:

| Command          | Description                               |
|------------------|-------------------------------------------|
| `!help`          | Show help                                 |
| `!history`       | Show command history                      |
| `!clear`         | Clear the screen                          |
| `!models`        | List models from the provider             |
| `!model <name>`  | Switch model for this session             |
| `!explain <cmd>` | Explain what a command does, with its safety level |
| `!last`          | Show the last generated command           |
| `!redo`          | Re-run the last plan (all steps, after a safety check) |
| `!errors`        | Show the error log                        |
| `!forget-sudo`   | Run `sudo -k` to drop cached sudo credentials |
| `!update`        | Check for a new version and upgrade with uv, pipx or pip |
| `!docs`          | Show the documentation link               |

Exit with `exit`, `quit`, `bye`, `q`, Ctrl+C or Ctrl+D.

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
