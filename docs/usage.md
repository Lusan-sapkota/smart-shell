# Usage

## Quick start

```bash
smart-shell                                   # interactive mode
smart-shell run "list all PDF files here"     # one-off prompt
smart-shell run "free up disk space" --dry-run
```

## CLI commands

| Command                           | Description                                   |
|-----------------------------------|-----------------------------------------------|
| `smart-shell`                     | Start interactive mode                        |
| `smart-shell run "<prompt>"`      | Run a single prompt                           |
| `smart-shell setup`               | Configure provider, API key and default model |
| `smart-shell models`              | List models from the configured provider      |
| `smart-shell --list-models`       | Same as `models`                              |
| `smart-shell history`             | Show command history                          |
| `smart-shell version`             | Show version information                      |
| `smart-shell --help`, `help`      | Show CLI help                                 |

Options for `run`:

| Option                | Description                                                        |
|-----------------------|--------------------------------------------------------------------|
| `--dry-run`, `-d`     | Show the plan without executing it                                 |
| `--model`, `-m NAME`  | Use a specific model for this run                                  |
| `--interactive`, `-i` | Start interactive mode                                             |
| `-y`                  | Skip confirmations (blocked commands still never run)              |

## Interactive commands

Type these at the `Smart-Shell (model):` prompt:

| Command          | Description                               |
|------------------|-------------------------------------------|
| `!help`          | Show help                                 |
| `!history`       | Show command history                      |
| `!clear`         | Clear the screen                          |
| `!models`        | List models from the provider             |
| `!model <name>`  | Switch model for this session             |
| `!last`          | Show the last generated command           |
| `!redo`          | Re-run the last plan (all steps, after a safety check) |
| `!errors`        | Show the error log                        |
| `!forget-sudo`   | Run `sudo -k` to drop cached sudo credentials |
| `!update`        | Check GitHub for updates and install them |
| `!creator`       | Show creator information                  |
| `!docs`          | Show the documentation link               |

Exit with `exit`, `quit`, `bye`, `q`, Ctrl+C or Ctrl+D.

## How a prompt runs

1. The model returns one or more commands.
2. Each command is classified (see [Safety](safety.md)) and shown in a preview.
3. Blocked commands stop the run; you can edit the command instead.
4. High or medium risk commands ask for y/n confirmation (unless `-y`).
5. The plan runs in one shell joined with `&&`, stopping at the first failure.

`sudo` asks for your password in the terminal as usual. Smart-Shell never stores it.

## Configuration

Run `smart-shell setup` (outside the REPL) to change provider or default model. See [Installation](installation.md#providers) for the config file and environment variables.
