"""
Safety Module for Smart-Shell - Classifies commands into risk levels.
"""

import re
from typing import Dict, Any

# ==============================================================================
# Risk Level Definitions
# ==============================================================================

# HIGH RISK: Commands that can cause irreversible data loss or system failure.
HIGH_RISK_PATTERNS = {
    # Unrecoverable deletions and disk operations
    r"\brm\s+-rf\b": "Recursively and forcefully removes files, can wipe critical data.",
    r"rm\s+-rf\s+--no-preserve-root\s+/": "Deletes the entire filesystem. Extremely dangerous.",
    r"\bdd\b": "Direct disk writing utility. Misuse can destroy data or filesystems.",
    r"\bmkfs\b": "Formats storage partitions, erasing all existing data.",
    r">\s*/dev/sd[a-z]": "Overwrites entire disk blocks, catastrophic if misused.",
    r"\bshred\b\s+/dev/sd[a-z]": "Securely wipes entire disks irreversibly.",
    r"\bhdparm\b": "Low-level disk tuning tool. Can corrupt hardware settings.",

    # System-breaking operations
    r"\b(chown|chmod)\s+-R\s+(root|/|/bin|/etc|/boot|/usr)": "Recursively altering core permissions may break the OS.",
    r"mv\s+/\S+\s+/dev/null": "Discards critical system directories permanently.",
    r":\(\)\{\s*:\|\:&\s*\};:": "Classic fork bomb. Spawns infinite processes and crashes the system.",
    r"ln\s+-sf\s+.*\s+/etc/.*": "Overwrites critical symlinks. May mislead system paths.",
    r"echo\s+.*>\s*/etc/(passwd|shadow|group|gshadow)": "Overwrites core authentication files.",
    r">\s*/etc/(passwd|shadow|group|gshadow)": "Blanking critical auth files leads to lockouts.",
    r"\b(grub-install|lilo)\b": "Modifying bootloader improperly renders the system unbootable.",
    r"\bmount\s+.*-o\s+loop\b.*\b/dev/sd[a-z]\b": "Mounting to raw devices is unsafe.",
    r"yes\s+\|\s*rm": "Forces destructive confirmation without prompt.",
}

# MEDIUM RISK: Commands that alter system behavior or software state.
MEDIUM_RISK_PATTERNS = {
    # System and service control
    r"\b(shutdown|reboot|halt|poweroff|init\s+[06])\b": "May shut down or reboot the system.",
    r"\b(kill|pkill|killall)\b": "Terminates running processes, possibly critical ones.",
    r"\b(systemctl|service)\s+(stop|disable|mask)\b": "Disables services, affecting system behavior.",
    r"\bsystemctl\s+restart\s+(ssh|sshd|network|firewalld|iptables|systemd-logind)\b": "Restarts essential services.",
    r"sysctl\s+-w": "Modifies kernel parameters dynamically.",
    r"\b(modprobe|insmod|rmmod)\b": "Modifies kernel modules and system drivers.",
    r"\b(dpkg-reconfigure|update-alternatives)\b": "Alters package configuration globally.",
    r"journalctl\s+--vacuum-.*": "Deletes important log history.",

    # Package and script management
    r"\b(apt|apt-get|dpkg|yum|dnf|pacman|apk|emerge|nix-env|brew|pip|npm)\s+(install|remove|purge|update|upgrade)\b": "Package manager operations affect system state.",
    r"\b(wget|curl)\s+.*\|\s*(sh|bash|zsh)": "Pipes external content directly into shell. Dangerous.",
    r"\b(tee|cat)\s+.*\|\s*sponge\s+/etc/.*": "Overwrites system files silently.",
    r"tar\s+.*--overwrite\b": "Unpacks while overwriting files unsafely.",

    # Network & identity
    r"\b(iptables|ufw|firewall-cmd)\b": "Modifies firewall behavior, could block access.",
    r"\bifconfig\s+\S+\s+down\b": "Brings down network interface. May cut connectivity.",
    r"\b(hostname|domainname)\b": "Changes network identification of host.",

    # User and filesystem
    r"\b(fdisk|parted|gdisk|cfdisk)\b": "Modifies disk partitions.",
    r"\b(useradd|userdel|usermod|groupadd|groupdel|groupmod|deluser|adduser|chage)\b": "Changes users and access control.",
    r"\b(mount|umount)\b": "Alters filesystem mount state.",
    r"\b(chown|chmod|setfacl|chattr)\b": "Modifies file permissions or attributes.",
    r"passwd": "Resets user passwords.",
    r"\bcrontab\b": "Schedules jobs that run periodically — may persist undesired actions.",
    r"\.(bashrc|profile|zshrc|bash_profile)": "Modifying shell config can break login or shell startup.",

    # Dangerous file operations
    r"rm\s+-[^f]*r": "Recursive deletion without force. Risky if paths are wrong.",
    r"find\s+.*\s+-delete": "Find+delete combo is irreversible with wrong flags.",
    r"rsync\s+.*--delete": "Deletes destination files not in source.",
    r"cp\s+-rf\s+/\s+/tmp": "Copies entire root to another location. Risk of clogging disk.",
    r"chmod\s+777\s+/(.*)": "Exposes full access to critical paths.",
    r"\b(cat|less|more|tail|head)\s+.*\/(.ssh|passwd|shadow|sudoers)\b": "Prints sensitive security config.",
}

# INFO LEAK: Commands that could expose environment secrets or sensitive internals.
INFO_LEAK_PATTERNS = {
    r"echo\s+\$.*(TOKEN|KEY|PASS|SECRET)": "May leak sensitive tokens or secrets to screen.",
    r"cat\s+.*history": "May expose recent terminal usage, including secrets.",
    r"cat\s+\.env": "May reveal environment config secrets.",
    r"env\b": "Lists all environment variables — may contain sensitive values.",
    r"printenv": "Similar to `env`, could print private variables.",
    r"ps\s+auxww": "Shows full command line — may include keys/passwords.",
    r"grep\s+['\"]?(token|key|secret)['\"]?\s+.*": "Actively searching logs or configs for secrets.",
    r"set\b": "Shows shell environment, often including variables.",
}


# SUDO: Commands that use sudo will be treated as MEDIUM risk by default,
# but we have a separate check for them to handle password logic.
SUDO_PATTERN = r"\bsudo\b"

def check_command_safety(command: str) -> Dict[str, Any]:
    """
    Check the safety level of a command based on predefined patterns.
    
    Args:
        command (str): The command to check.
        
    Returns:
        A dictionary containing the safety status ('high', 'medium', 'safe')
        and a reason for the classification.
    """
    # 1. Check for HIGH risk commands
    for pattern, reason in HIGH_RISK_PATTERNS.items():
        if re.search(pattern, command, re.IGNORECASE):
            return {
                "status": "high",
                "reason": f"High-risk pattern matched: '{pattern}'.",
                "notes": reason
            }

    # 2. Check for SUDO usage, which automatically elevates risk to MEDIUM
    if re.search(SUDO_PATTERN, command, re.IGNORECASE):
        return {
            "status": "medium",
            "reason": "Command uses 'sudo'.",
            "notes": "Executing commands with root privileges can have significant system-wide effects."
        }

    # 3. Check for MEDIUM risk commands
    for pattern, reason in MEDIUM_RISK_PATTERNS.items():
        if re.search(pattern, command, re.IGNORECASE):
            return {
                "status": "medium",
                "reason": f"Medium-risk pattern matched: '{pattern}'.",
                "notes": reason
            }
    # 3. Check for INFO LEAK commands
    for pattern, reason in INFO_LEAK_PATTERNS.items():
        if re.search(pattern, command, re.IGNORECASE):
            return {
                "status": "info_leak",
                "reason": f"Info-leak pattern matched: '{pattern}'.",
                "notes": reason
            }
            
    # 4. If no specific risk pattern is matched, consider it safe
    return {
        "status": "safe",
        "reason": "No high or medium risk patterns were detected.",
        "notes": "Command appears to be safe for execution."
    }

# Main block for testing the safety checker
if __name__ == "__main__":
    test_commands = [
        "ls -la",
        "sudo reboot",
        "rm -rf /",
        "apt-get install htop",
        "kill -9 12345",
        "chmod 777 sensitive_file.txt",
        "dd if=/dev/random of=/dev/sda",
        "echo 'hello world'",
        "sudo userdel mallory"
    ]

    print("Running safety checks on test commands:")
    for cmd in test_commands:
        result = check_command_safety(cmd)
        status_color = {
            "safe": "\033[92m",   # Green
            "medium": "\033[93m", # Yellow
            "high": "\033[91m"    # Red
        }
        end_color = "\033[0m"
        print(
            f"Command: '{cmd}'\n"
            f"Status: {status_color[result['status']]}{result['status'].upper()}{end_color}\n"
            f"Reason: {result['reason']}\n"
            f"Notes: {result['notes']}\n"
            f"{'-'*30}"
        ) 