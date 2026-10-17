# Safety

Every generated command is checked by pattern rules in `smart_shell/safety.py` before anything runs. The preview shows each command with its level and the reason.

## Levels

| Level       | Behavior                                  | Examples |
|-------------|-------------------------------------------|----------|
| `blocked`   | Never runs. You can edit it or cancel; the edited version is checked again. | `rm -rf /`, `rm -rf ~` or `$HOME`, `--no-preserve-root`, fork bomb, `mkfs` on `/dev/...`, `dd of=/dev/sda`, `> /dev/sda` |
| `high`      | Asks yes/no/edit (default no)             | `rm` with recursive and force flags in any spelling (`-rf`, `-fr`, `-r -f`, `--recursive --force`), piping anything into `sh`/`bash`/`zsh`, `dd`, `shred` on disks, overwriting `/etc/passwd` |
| `medium`    | Asks yes/no/edit (default no)             | `sudo`, any `rm`, `rmdir`, `unlink`, `truncate`, emptying a file with `>`, `git reset --hard` / `clean -f` / `push --force`, `docker rm` / `prune`, package installs and removals, `kill`, `chmod`/`chown`, `eval`, stopping or disabling services, user and group changes, firewall rules, mounts |
| `info_leak` | Asks yes/no/edit (default yes)            | `env`, `printenv`, `echo $API_KEY` (any `TOKEN`/`KEY`/`PASS`/`SECRET` variable), `cat ~/.bash_history`, `cat .env` |
| `safe`      | Asks yes/no/edit (default yes)            | `ls`, `pwd`, `df -h` |

In **auto** mode (Shift+Tab), a plan runs without asking only if every step is a plain pipeline of known read-only commands (an allowlist in `smart_shell/safety.py`: `ls`, `cat`, `df`, `grep`, `git status`, `find` without `-delete`/`-exec`, and so on). Shell constructs that can hide a command (`;` loops, `bash -c`, `$(...)`, backticks, `<(...)`, newlines) and any redirect that writes a file also make it ask. One `rm` or `sudo` step is enough to make the whole plan ask.

The pattern rules below set the label and the default answer; the allowlist is what auto mode trusts, because pattern rules can always miss some spelling.

If a plan contains several commands, the highest level among them sets the default answer. Every plan is shown before it runs, and you can edit it first.

## Auto-confirm

`smart-shell "..." -y` skips the confirmation and the fix offer. Blocked commands still never run.

## Sudo

Smart-Shell does not store or ask for your sudo password. `sudo` prompts in the terminal itself. Passwords saved by older versions are deleted from the config automatically. `/forget-sudo` runs `sudo -k`.

## Limits

The checks are pattern-based. They catch common destructive commands but cannot prove a command is harmless, so read the preview before confirming. Use `--dry-run` when in doubt.
