"""
Safety Module for Smart-Shell - Classifies commands into risk levels.
"""

import re
import shlex
from typing import Dict, Any

# Start of a command: line start, after ; & | ( ` { ! or a newline, after do/then/else, or behind a
# wrapper (sudo, nohup, time, command, exec, env) or a leading backslash.
CMD = r"(?:^|\n|[;&|(`{!]\s*|\b(?:do|then|else)\s+)(?:(?:sudo|nohup|time|command|exec|env)\s+)*\\?"

# rm with both a recursive and a force flag, in any order or spelling.
RM_RF = r"\brm\b(?=[^;&|\n]*(?:\s-\w*[rR]|\s--recursive))(?=[^;&|\n]*(?:\s-\w*f|\s--force))"

# BLOCKED: never executed, only editable.
BLOCKED_PATTERNS = {
    RM_RF + r"[^;&|\n]*\s(?:/|/\*|~/?|\$HOME/?)(?:\s|$|;|&|\|)": "Deletes the root filesystem or your entire home directory.",
    r"--no-preserve-root": "Disables rm's protection against deleting /.",
    r":\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;\s*:": "Fork bomb. Spawns processes until the system hangs.",
    r"\bmkfs(\.\w+)?\s+[^;&|]*/dev/": "Formats a disk, erasing everything on it.",
    r"\bdd\b[^;&|]*\bof=/dev/(sd|nvme|vd|hd|mmcblk)": "Writes raw data over a disk.",
    r">\s*/dev/(sd|nvme|vd|hd|mmcblk)": "Overwrites a raw disk device.",
}

# HIGH RISK: Commands that can cause irreversible data loss or system failure.
HIGH_RISK_PATTERNS = {
    # Unrecoverable deletions and disk operations
    RM_RF: "Recursively and forcefully removes files, can wipe critical data.",
    r"\|\s*(sudo\s+)?(?:(?:ba|z|da)?sh|python3?|perl|ruby|node)\b": "Pipes text straight into an interpreter. Whatever produced it gets executed.",
    r"<\(\s*(?:curl|wget)\b": "Runs a downloaded script.",
    r"\b(?:ba|z|da)?sh\s+-c\b": "Runs a string as a shell script, which hides what actually executes.",
    r"\b(?:wipefs|blkdiscard)\b": "Erases disk signatures or discards all data on a device.",
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
    CMD + r"eval\b": "Runs a string as code, which hides what actually executes.",
    r"\b(tee|cat)\s+.*\|\s*sponge\s+/etc/.*": "Overwrites system files silently.",
    r"tar\s+.*--overwrite\b": "Unpacks while overwriting files unsafely.",

    # Network & identity
    r"\b(iptables|ufw|firewall-cmd)\b": "Modifies firewall behavior, could block access.",
    r"\bifconfig\s+\S+\s+down\b": "Brings down network interface. May cut connectivity.",
    r"\bhostnamectl\s+set-hostname\b|" + CMD + r"(hostname|domainname)\s+[^-\s]": "Changes network identification of host.",

    # User and filesystem
    r"\b(fdisk|parted|gdisk|cfdisk)\b": "Modifies disk partitions.",
    r"\b(useradd|userdel|usermod|groupadd|groupdel|groupmod|deluser|adduser|chage)\b": "Changes users and access control.",
    r"\b(mount|umount)\b": "Alters filesystem mount state.",
    r"\b(chown|chmod|setfacl|chattr)\b": "Modifies file permissions or attributes.",
    CMD + r"passwd\b": "Resets user passwords.",
    r"\bcrontab\b": "Schedules jobs that run periodically, may persist undesired actions.",
    r"\.(bashrc|profile|zshrc|bash_profile)": "Modifying shell config can break login or shell startup.",

    # Dangerous file operations
    r"(?:" + CMD + r"|\bxargs\s+(?:-\S+\s+)*|-exec(?:dir)?\s+)(?:rm|rmdir|unlink|shred|truncate)\b": "Deletes or empties files.",
    CMD + r":?\s*>\s*[^>&\s]": "Empties a file by redirecting nothing into it.",
    r"(?<![\d&>])>(?!>|&|\s*/dev/null)\s*[^\s|;&]": "Overwrites a file with the command's output.",
    r"\bsed\s+(?:-\w*\s+)*-i": "Edits files in place.",
    r"\bln\s+-\w*f": "Replaces existing files with links.",
    r"\bgit\s+(?:clean\s+-\w*f|reset\s+--hard|checkout\s+(?:--\s|\.(?:\s|$))|restore\b|stash\s+(?:drop|clear)|push\s+.*(?:--force|-f\b)|branch\s+-D)": "Discards git work or rewrites history.",
    r"\b(?:docker|podman)\s+(?:rm|rmi|volume\s+rm|system\s+prune|image\s+prune|container\s+prune)\b": "Deletes containers, images or volumes.",
    r"rm\s+-[^f]*r": "Recursive deletion without force. Risky if paths are wrong.",
    r"\bfind\b.*\s-delete\b": "Find+delete combo is irreversible with wrong flags.",
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
    CMD + r"(env|printenv)\s*($|[;&|>])": "Lists all environment variables, which may contain secrets.",
    r"ps\s+auxww": "Shows full command line, may include keys/passwords.",
    r"grep\s+['\"]?(token|key|secret)['\"]?\s+.*": "Actively searching logs or configs for secrets.",
    CMD + r"set\s*($|[;&|>])": "Shows shell environment, often including variables.",
}


# SUDO: Commands that use sudo will be treated as MEDIUM risk by default,
# but we have a separate check for them to handle password logic.
SUDO_PATTERN = r"\bsudo\b"

def check_command_safety(command: str) -> Dict[str, Any]:
    """Check the safety level of a command based on predefined patterns."""
    for pattern, reason in BLOCKED_PATTERNS.items():
        if re.search(pattern, command, re.IGNORECASE):
            return {
                "status": "blocked",
                "reason": f"Blocked pattern matched: '{pattern}'.",
                "notes": reason
            }

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


# Auto mode runs a plan without asking only if every step is a plain pipeline of these read-only
# commands. An allowlist, because pattern rules for danger will always miss some spelling. Only
# commands with no flag that writes files or runs other programs belong here; commands that need
# their arguments checked are handled in _args_ok.
READ_ONLY = {
    "ls", "pwd", "cat", "head", "tail", "wc", "cut", "tr", "nl", "column", "grep", "egrep", "fgrep", "jq",
    "diff", "cmp", "comm", "file", "stat", "du", "df", "free", "uptime", "uname", "whoami", "id", "groups",
    "cal", "echo", "printf", "which", "type", "whereis", "ps", "pgrep", "lsblk", "lscpu", "lsusb", "lspci",
    "lsof", "netstat", "dig", "nslookup", "host", "realpath", "basename", "dirname", "readlink", "md5sum",
    "sha1sum", "sha256sum", "true", "false", "test", "seq", "nproc", "vmstat", "iostat", "zcat", "zgrep",
    "tac", "rev", "strings", "hexdump", "od", "base64",
    # Argument-checked below.
    "sort", "uniq", "git", "find", "xargs", "env", "printenv", "systemctl", "journalctl", "ip", "date", "hostname", "ss", "ping",
}
GIT_READ_ONLY = {"status", "log", "diff", "show", "blame", "shortlog", "describe", "rev-parse", "ls-files", "grep",
                 "branch", "tag", "remote", "config", "stash"}
# For these git subcommands every argument must come from this set (no names, so nothing is created or deleted).
GIT_LISTING = {
    "branch": {"-a", "--all", "-r", "--remotes", "-l", "--list", "-v", "-vv", "--show-current"},
    "tag": {"-l", "--list"},
    "remote": {"-v", "--verbose", "show", "get-url"},
    "config": {"--get", "--get-all", "-l", "--list", "--show-origin", "--global", "--local", "--system"},
    "stash": {"list", "show"},
}
GIT_EXEC_FLAGS = ("--output", "--ext-diff", "--textconv", "-O", "--open-files-in-pager", "--exec")
JOURNALCTL_FLAGS = ("-n", "--lines", "-u", "--unit", "-b", "--boot", "-p", "--priority", "--since", "--until",
                    "-r", "--reverse", "-k", "--dmesg", "--no-pager", "-e", "--pager-end", "-o", "--output", "--utc")
IP_WRITE_WORDS = {"add", "del", "delete", "set", "flush", "change", "replace", "append", "up", "down", "save",
                  "restore", "exec", "monitor"}
SHELL_SYNTAX = re.compile(r"[\n`]|\$\(|<\(|>\(|[{}]|\b(?:do|then|else|done|fi|function)\b")
SAFE_REDIRECT = re.compile(r"\s*(?:\d?>\s*/dev/null(?=\s|$|[|;&])|2>&1|>&2)")


def _args_ok(name, args):
    if name == "git":
        if not args or args[0] not in GIT_READ_ONLY or any(a.startswith(GIT_EXEC_FLAGS) for a in args):
            return False
        allowed = GIT_LISTING.get(args[0])
        if allowed is not None:
            rest = args[1:]
            # Bare `git stash` stashes changes; bare `git config` errors; the others just list.
            if args[0] in ("stash", "config") and not rest:
                return False
            return all(a in allowed or (args[0] == "config" and not a.startswith("-") and "--get" in " ".join(rest))
                       or (args[0] == "remote" and rest[:1] in (["show"], ["get-url"]) and not a.startswith("-"))
                       for a in rest)
        return True
    if name == "sort":
        # Plain sort flags only: -o/--output write a file, --compress-program runs one.
        return all(re.fullmatch(r"-[bdfghiMnrsuVz]+|-[kt]\S*", a) or not a.startswith("-") for a in args)
    if name == "uniq":
        # A second file argument is uniq's output file.
        return (all(re.fullmatch(r"-[cdiu]+", a) for a in args if a.startswith("-"))
                and len([a for a in args if not a.startswith("-")]) <= 1)
    if name == "find":
        return not any(a in ("-delete", "-exec", "-execdir", "-ok", "-okdir", "-fls") or a.startswith("-fprint")
                       for a in args)
    if name == "xargs":
        return [a for a in args if not a.startswith("-")][:1] == ["echo"]
    if name in ("env", "printenv", "hostname"):
        return not args
    if name == "systemctl":
        return bool(args) and args[0] in ("status", "list-units", "list-unit-files", "list-timers", "is-active",
                                           "is-enabled", "is-failed", "show", "cat")
    if name == "journalctl":
        return all(not a.startswith("-") or a.split("=")[0] in JOURNALCTL_FLAGS for a in args)
    if name == "ip":
        return not IP_WRITE_WORDS.intersection(args) and "-batch" not in args and "-b" not in args
    if name == "date":
        return all(a.startswith("+") or a in ("-u", "--utc", "-R", "-I", "--iso-8601") for a in args)
    if name == "ss":
        return not any(a in ("-K", "--kill") or (a.startswith("-") and not a.startswith("--") and "K" in a)
                       for a in args)
    if name == "ping":
        # Without a count ping never ends; -f floods.
        return "-c" in args and not any(a.startswith("-f") for a in args)
    return True


def is_auto_safe(command: str) -> bool:
    """True if auto mode may run this step without asking: read-only commands only, no shell tricks."""
    if check_command_safety(command)["status"] != "safe" or SHELL_SYNTAX.search(command):
        return False
    rest = SAFE_REDIRECT.sub(" ", command)
    # Any other redirect writes or reads a file; a lone & starts a second command we would not check.
    if re.search(r"[<>]", rest) or re.search(r"(?<!&)&(?!&)", rest):
        return False
    for part in re.split(r"\|\|?|&&|;", rest):
        try:
            words = shlex.split(part)
        except ValueError:
            return False
        if not words:
            continue
        if words[0] not in READ_ONLY or not _args_ok(words[0], words[1:]):
            return False
    return True
