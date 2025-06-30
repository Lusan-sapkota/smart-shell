# Safety System Documentation

Smart-Shell includes a comprehensive safety system to protect users from potentially harmful commands. This document explains how the safety system works and its components.

## Safety Levels

Commands are classified into three safety levels:

1. **Safe** 🟢 - Commands that are considered safe to run
2. **Warning** 🟡 - Commands that might have unintended consequences (requires confirmation)
3. **Blocked** 🔴 - Commands that are potentially harmful (will not be executed)

## Safety Checks

The safety system performs several types of checks:

### 1. Blocked Commands

Certain commands are explicitly blocked due to their high potential for damage:

```python
BLOCKED_COMMANDS = [
    "rm -rf /",
    "rm -rf /*",
    "mkfs",
    "> /dev/sda",
    "dd if=/dev/zero of=/dev/sda",
    ":(){ :|:& };:",  # Fork bomb
    "chmod -R 777 /",
    "mv /* /dev/null",
    # ...and others
]
```

### 2. Pattern Matching

Regular expressions identify potentially risky command patterns:

```python
WARNING_PATTERNS = [
    r"rm\s+-rf\s+.*",          # Any rm -rf command
    r"rm\s+-r\s+.*",           # Any rm -r command
    r"sudo\s+.*",              # Any sudo command
    # ...and many others
]
```

### 3. Path Analysis

The system checks if commands operate on sensitive system paths:

```python
SENSITIVE_PATHS = [
    "/boot",
    "/etc/passwd",
    "/etc/shadow",
    "/etc/sudoers",
    # ...and many others
]
```

### 4. Redirection Analysis

Commands that redirect output to sensitive system files are flagged:

```python
# Patterns for redirections
redirection_patterns = [
    r">\s*(/[^\s;|><&]+)",    # > /path
    r">>\s*(/[^\s;|><&]+)",   # >> /path
    # ...and others
]
```

### 5. Risk Assessment

Each command undergoes risk assessment to determine its potential impact:

```python
def assess_risk(command, matched_part):
    # High risk commands
    if re.search(r"rm\s+-rf\s+[^/]+/\*", command):
        return {
            "risk_level": "high",
            "explanation": "This command will recursively delete all files in a directory."
        }
    
    # Medium risk commands
    if re.search(r"sudo\s+", command):
        return {
            "risk_level": "medium",
            "explanation": "This command runs with elevated privileges."
        }
    
    # ...and other risk assessments
```

## User Confirmation

Commands that trigger warnings require explicit user confirmation before execution:

```python
if safety_result["status"] == "warning" and not auto_yes:
    confirm = Confirm.ask("Do you want to proceed?", default=False)
    if not confirm:
        return False
```

## Command Editing

If a command is blocked, users can edit it to make it safer:

```python
if Prompt.ask("Would you like to edit the command?", choices=["y", "n"], default="y") == "y":
    edited_command = Prompt.ask("Enter modified command", default=command)
    # Re-check safety of edited command
    safety_result = check_command_safety(edited_command)
```

## Secure Execution

Commands are executed using a secure approach:

1. Commands are written to temporary script files
2. Proper permissions are set
3. Scripts are executed with `shell=False` to prevent shell injection
4. Temporary files are cleaned up after execution

## Error Recovery

The system attempts to recover from common errors:

1. Missing commands trigger package installation suggestions
2. Permission errors prompt for sudo execution
3. Path issues offer directory creation options

## Extending the Safety System

When adding new safety checks:

1. Consider the risk level and appropriate response
2. Add specific patterns to the appropriate list
3. Update risk assessment logic if needed
4. Document the new check in this file

## Safety Limitations

While the safety system is comprehensive, it has limitations:

1. It cannot catch all possible harmful commands
2. Complex or obfuscated commands may bypass checks
3. New or unusual command patterns may not be recognized

Always review commands before execution, especially when they affect system files or require elevated privileges. 