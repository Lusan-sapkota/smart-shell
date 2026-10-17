# Safety

Every generated command is checked by pattern rules in `smart_shell/safety.py` before anything runs. The preview shows each command with its level and the reason.

## Levels

| Level       | Behavior                                  | Examples |
|-------------|-------------------------------------------|----------|
| `blocked`   | Never runs. You can edit the command; the edited version is checked again. | `rm -rf /`, `rm -rf ~` or `$HOME`, `--no-preserve-root`, fork bomb, `mkfs` on `/dev/...`, `dd of=/dev/sda`, `> /dev/sda` |
| `high`      | Asks y/n (default no)                     | `rm` with recursive and force flags in any spelling (`-rf`, `-fr`, `-r -f`, `--recursive --force`), piping anything into `sh`/`bash`/`zsh`, `dd`, `shred` on disks, overwriting `/etc/passwd` |
| `medium`    | Asks y/n (default no)                     | `sudo`, package installs and removals, `kill`, `chmod`/`chown`, `eval`, stopping or disabling services, user and group changes, firewall rules, mounts |
| `info_leak` | Flagged in the preview                    | `env`, `printenv`, `echo $API_KEY` (any `TOKEN`/`KEY`/`PASS`/`SECRET` variable), `cat ~/.bash_history`, `cat .env` |
| `safe`      | Runs directly                             | `ls`, `pwd`, `df -h` |

If a plan contains several commands, the highest level among them decides whether you are asked.

## Auto-confirm

`smart-shell run ... -y` skips the high and medium confirmations. Blocked commands still never run.

## Sudo

Smart-Shell does not store or ask for your sudo password. `sudo` prompts in the terminal itself. Passwords saved by older versions are deleted from the config automatically. `!forget-sudo` runs `sudo -k`.

## Limits

The checks are pattern-based. They catch common destructive commands but cannot prove a command is harmless, so read the preview before confirming. Use `--dry-run` when in doubt.
