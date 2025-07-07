# Safety

Smart-Shell includes a comprehensive safety system to protect users from potentially harmful commands.

## Safety Levels

- **Safe** 🟢: Commands that are considered safe to run (executed automatically)
- **Medium** 🟡: Commands that might have consequences like sudo operations (requires y/n confirmation)
- **High** 🔴: Commands that are potentially dangerous like file deletion (requires y/n confirmation)
- **Info Leak** 🔵: Commands that might expose sensitive information (requires confirmation)

## Safety Checks

- **Risk Assessment:** All commands are analyzed for potential risks before execution
- **Pattern Matching:** Uses regex to identify risky command patterns (e.g., `sudo`, `rm -rf`, `dd`, `chmod 777`)
- **Path Analysis:** Detects operations on sensitive system paths (e.g., `/etc/passwd`, system directories)
- **User Confirmation:** Medium and high-risk commands require explicit y/n confirmation
- **Command Editing:** Users can edit blocked commands before execution

## Confirmation System

- All confirmations accept `y`/`yes` or `n`/`no` (case insensitive)
- Users maintain full control - even high-risk commands can be executed with confirmation
- Clear explanations are provided for why commands are flagged

> **Note:** The safety system is designed to inform and protect, not restrict. Users have final control over command execution after being informed of potential risks.

For more details, see the full documentation.
