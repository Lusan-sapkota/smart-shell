# Safety

Smart-Shell includes a comprehensive safety system to protect users from potentially harmful commands.

## Safety Levels

- **Safe** 🟢: Commands that are considered safe to run
- **Warning** 🟡: Commands that might have unintended consequences (requires confirmation)
- **Blocked** 🔴: Commands that are potentially harmful (will not be executed)

## Safety Checks

- **Blocked Commands:** Explicitly blocks dangerous commands (e.g., `rm -rf /`, fork bombs, disk formatting)
- **Pattern Matching:** Uses regex to identify risky command patterns (e.g., `sudo`, `rm -rf`)
- **Path Analysis:** Detects operations on sensitive system paths (e.g., `/etc/passwd`)

For more details, see the [Safety System Documentation](SAFETY.md).
