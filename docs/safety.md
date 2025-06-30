# Safety

Smart-Shell includes a comprehensive safety system to protect users from potentially harmful commands.

## Safety Levels

- **Safe** 🟢: Commands that are considered safe to run
- **Warning** 🟡: Commands that might have unintended consequences (requires confirmation)
- **Blocked** 🔴: Commands that are potentially harmful (require explicit user confirmation before execution)

## Safety Checks

- **Blocked Commands:** Explicitly identifies dangerous commands (e.g., `rm -rf /`, fork bombs, disk formatting) and prompts the user for confirmation before execution. If the user confirms, the command will be executed.
- **Pattern Matching:** Uses regex to identify risky command patterns (e.g., `sudo`, `rm -rf`)
- **Path Analysis:** Detects operations on sensitive system paths (e.g., `/etc/passwd`)

> **Note:** Even high-risk ("blocked") commands can be executed if the user explicitly confirms when prompted. This ensures user control while maintaining safety.

For more details, see the [Safety System Documentation](SAFETY.md).
