# Features

## Natural language to commands

Describe what you want in plain English and Smart-Shell generates a Bash or Zsh command (or a short plan of several commands) for your OS and shell. The shell is detected from `$SHELL`.

Multi-step plans run in a single shell, joined with `&&`, so `cd` and environment changes carry over and execution stops at the first failing step.

## Providers

Local models come first: with Ollama or LM Studio everything runs on your machine, offline, with no API key. The same client also talks to any OpenAI-compatible chat API. Presets:

| Provider     | Base URL                                                   | API key |
|--------------|------------------------------------------------------------|---------|
| `ollama`     | `http://localhost:11434/v1`                                | no      |
| `lmstudio`   | `http://localhost:1234/v1`                                 | no      |
| `gemini`     | `https://generativelanguage.googleapis.com/v1beta/openai`  | yes     |
| `openai`     | `https://api.openai.com/v1`                                | yes     |
| `deepseek`   | `https://api.deepseek.com/v1`                              | yes     |
| `openrouter` | `https://openrouter.ai/api/v1`                             | yes     |
| `groq`       | `https://api.groq.com/openai/v1`                           | yes     |
| `custom`     | any URL you enter                                          | optional |

Models are listed live from the provider (`!models`, `smart-shell models`) and can be switched per run (`--model`) or per session (`!model <name>`).

## Safety

Every generated command is classified before it runs:

- **blocked**: never runs, can only be edited (e.g. `rm -rf /`, fork bombs, `mkfs` on a disk)
- **high**: destructive operations, defaults to no
- **medium**: sudo, package installs, permission and service changes, defaults to no
- **info_leak**: may print secrets (`env`, `printenv`, `echo $API_KEY`), defaults to yes
- **safe**: defaults to yes

Every plan is shown first with **yes / no / edit**, so you can tweak a command before it runs.

See [Safety](safety.md) for details.

## Interactive mode

A REPL with readline history, a prompt that shows the current model, and `!` commands: `!help`, `!history`, `!clear`, `!models`, `!model <name>`, `!explain <cmd>`, `!last`, `!redo`, `!errors`, `!forget-sudo`, `!update`, `!docs`.

## Other

- **Dry run** (`--dry-run`): preview the plan and its safety analysis without executing.
- **History** of prompts and commands, stored in `~/.local/share/smart-shell/`.
- **Error log** of failures, viewable with `!errors`.
- **Readable errors**: common failures (command not found, permission denied, missing file) get a one-line explanation.
- **Sudo**: Smart-Shell never stores your sudo password. `sudo` prompts in the terminal; `!forget-sudo` runs `sudo -k`.
- **Fix on failure**: when a command fails, Smart-Shell offers to send the command and the last lines of its error output to the model and proposes a corrected plan, checked and confirmed like any other. Nothing is sent unless you say yes.
- **Follow-ups**: in interactive mode, recent requests are passed as context, so "now do the same for /var/log" works.
- **Live output**: commands print as they run, and interactive prompts work.
- **One-off providers**: `--provider` / `--base-url` switch provider for a single run.
- **Updates**: `!update` checks PyPI and upgrades with the tool you installed with (uv, pipx or pip).
- **Desktop entry and tab completion**, set up by the installer.
