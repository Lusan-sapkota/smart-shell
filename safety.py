#!/usr/bin/env python3
"""
Safety module for Smart-Shell - Checks commands for potential dangers.
"""

import re
import os
from typing import Dict, Any, List, Tuple, Optional

# Commands that are always blocked
BLOCKED_COMMANDS = [
    "rm -rf /",
    "rm -rf /*",
    "mkfs",
    "> /dev/sda",
    "dd if=/dev/zero of=/dev/sda",
    ":(){ :|:& };:",  # Fork bomb
    "chmod -R 777 /",
    "mv /* /dev/null",
    "> /dev/null/*",
    "rm -rf ~/",
    "rm -rf $HOME",
    "rm -rf --no-preserve-root /",
]

# Patterns that should trigger warnings
WARNING_PATTERNS = [
    # File operations
    r"rm\s+-rf\s+.*",          # Any rm -rf command
    r"rm\s+-r\s+.*",           # Any rm -r command
    r"rm\s+-f\s+.*",           # Any rm -f command
    r"rm\s+.*\*.*",            # rm with wildcard
    r"rmdir\s+.*",             # Any rmdir command
    
    # System commands
    r"dd\s+.*",                # Any dd command
    r"chmod\s+-R\s+.*",        # Any chmod -R command
    r"chown\s+-R\s+.*",        # Any chown -R command
    r"shutdown\s+.*",          # Any shutdown command
    r"reboot\s+.*",            # Any reboot command
    r"halt\s+.*",              # Any halt command
    r"poweroff\s+.*",          # Any poweroff command
    r"init\s+[06]",            # init 0 or init 6
    
    # Privilege commands
    r"sudo\s+.*",              # Any sudo command
    r"su\s+.*",                # Any su command
    
    # Network commands
    r"iptables\s+.*",          # Any iptables command
    r"ufw\s+.*",               # Any ufw command
    r"firewall-cmd\s+.*",      # Any firewall-cmd command
    
    # File system commands
    r"mount\s+.*",             # Any mount command
    r"umount\s+.*",            # Any umount command
    r"mkfs\s+.*",              # Any mkfs command
    r"fdisk\s+.*",             # Any fdisk command
    r"parted\s+.*",            # Any parted command
    
    # Moving/copying from root
    r"mv\s+\/\S+\s+.*",        # Moving from root directories
    r"cp\s+-r\s+\/\S+\s+.*",   # Copying recursively from root
    
    # Redirections to system files
    r">\s+\/\S+",              # Redirecting to system files
    r">>\s+\/\S+",             # Appending to system files
]

# Patterns that indicate a malformed command
MALFORMED_PATTERNS = [
    r"^\s*$",                  # Empty command
    r"^[^a-zA-Z0-9\.\/_-]+$",  # No valid characters
]

# Sensitive system paths that require warnings
SENSITIVE_PATHS = [
    "/boot",
    "/etc/passwd",
    "/etc/shadow",
    "/etc/sudoers",
    "/etc/ssh",
    "/usr/bin",
    "/bin",
    "/sbin",
    "/lib",
    "/lib64",
    "/usr/lib",
    "/usr/lib64",
    "/var/log",
    "/proc",
    "/sys",
    "/dev/sd",
    "/etc/fstab",
    "/etc/hosts",
    "/etc/hostname",
    "/etc/resolv.conf",
]

def check_command_safety(command: str) -> Dict[str, Any]:
    """
    Check if a command is safe to execute.
    
    Args:
        command (str): The command to check
        
    Returns:
        dict: Safety check result with keys:
            - status: 'safe', 'warning', 'blocked'
            - reason: Explanation of the warning/block (if applicable)
            - notes: Additional information (if applicable)
            - details: Detailed analysis of the command (if applicable)
    """
    # Check for empty command
    if not command or command.strip() == "":
        return {
            "status": "blocked",
            "reason": "Empty command",
            "notes": "The generated command is empty."
        }
    
    # Check for blocked commands
    for blocked in BLOCKED_COMMANDS:
        if blocked in command:
            return {
                "status": "blocked",
                "reason": "This command is explicitly blocked for safety reasons",
                "notes": "This command could cause serious damage to your system.",
                "details": f"Matched blocked pattern: '{blocked}'"
            }
    
    # Check for dangerous paths
    dangerous_paths = check_dangerous_paths(command)
    if dangerous_paths:
        return {
            "status": "warning",
            "reason": f"Command operates on sensitive system paths",
            "notes": "Operations on these paths could affect system stability.",
            "details": f"Sensitive paths detected: {', '.join(dangerous_paths)}"
        }
    
    # Check for dangerous redirections
    dangerous_redirections = check_dangerous_redirections(command)
    if dangerous_redirections:
        return {
            "status": "warning",
            "reason": "Command contains potentially dangerous redirections",
            "notes": "Be careful when redirecting to system files.",
            "details": f"Dangerous redirections: {', '.join(dangerous_redirections)}"
        }
    
    # Check for warning patterns
    for pattern in WARNING_PATTERNS:
        match = re.search(pattern, command)
        if match:
            matched_part = match.group(0)
            risk_assessment = assess_risk(command, matched_part)
            
            if risk_assessment["risk_level"] == "high":
                return {
                    "status": "warning",
                    "reason": "This command may have significant consequences",
                    "notes": risk_assessment["explanation"],
                    "details": f"Matched pattern: '{pattern}' with '{matched_part}'"
                }
            elif risk_assessment["risk_level"] == "medium":
                return {
                    "status": "warning",
                    "reason": "This command requires caution",
                    "notes": risk_assessment["explanation"],
                    "details": f"Matched pattern: '{pattern}' with '{matched_part}'"
                }
    
    # Check for malformed commands
    for pattern in MALFORMED_PATTERNS:
        if re.search(pattern, command):
            return {
                "status": "blocked",
                "reason": "Malformed command",
                "notes": "The generated command appears to be invalid."
            }
    
    # If we get here, the command is considered safe
    return {
        "status": "safe",
        "notes": "Command appears to be safe."
    }

def check_dangerous_paths(command: str) -> List[str]:
    """
    Check if a command operates on dangerous system paths.
    
    Args:
        command (str): The command to check
        
    Returns:
        list: List of dangerous paths found in the command
    """
    dangerous_paths = []
    
    # Extract paths from the command
    potential_paths = extract_paths(command)
    
    # Check if any extracted path is a sensitive path
    for path in potential_paths:
        for sensitive in SENSITIVE_PATHS:
            if path.startswith(sensitive):
                dangerous_paths.append(path)
                break
    
    return dangerous_paths

def check_dangerous_redirections(command: str) -> List[str]:
    """
    Check if a command contains dangerous redirections.
    
    Args:
        command (str): The command to check
        
    Returns:
        list: List of dangerous redirections found in the command
    """
    dangerous_redirections = []
    
    # Patterns for redirections
    redirection_patterns = [
        r">\s*(/[^\s;|><&]+)",    # > /path
        r">>\s*(/[^\s;|><&]+)",   # >> /path
        r"2>\s*(/[^\s;|><&]+)",   # 2> /path
        r"&>\s*(/[^\s;|><&]+)",   # &> /path
    ]
    
    for pattern in redirection_patterns:
        matches = re.finditer(pattern, command)
        for match in matches:
            path = match.group(1)
            for sensitive in SENSITIVE_PATHS:
                if path.startswith(sensitive):
                    dangerous_redirections.append(f"{match.group(0)} (to {path})")
                    break
    
    return dangerous_redirections

def extract_paths(command: str) -> List[str]:
    """
    Extract potential file paths from a command.
    
    Args:
        command (str): The command to extract paths from
        
    Returns:
        list: List of potential file paths
    """
    # Simple regex to find paths starting with /
    path_pattern = r'(?:^|\s+)(/[^\s;|><&]+)'
    paths = re.findall(path_pattern, command)
    
    # Remove quotes if present
    cleaned_paths = []
    for path in paths:
        if path.startswith("'") and path.endswith("'"):
            path = path[1:-1]
        elif path.startswith('"') and path.endswith('"'):
            path = path[1:-1]
        cleaned_paths.append(path)
    
    return cleaned_paths

def assess_risk(command: str, matched_part: str) -> Dict[str, Any]:
    """
    Assess the risk level of a command based on the matched pattern.
    
    Args:
        command (str): The full command
        matched_part (str): The part that matched a warning pattern
        
    Returns:
        dict: Risk assessment with keys:
            - risk_level: 'low', 'medium', 'high'
            - explanation: Explanation of the risk
    """
    # High risk commands
    if re.search(r"rm\s+-rf\s+[^/]+/\*", command):
        return {
            "risk_level": "high",
            "explanation": "This command will recursively delete all files in a directory. Make sure this is what you want."
        }
    
    if re.search(r"dd\s+.*\s+of=/dev/", command):
        return {
            "risk_level": "high",
            "explanation": "This command writes directly to a device file, which can overwrite disk data."
        }
    
    if re.search(r"chmod\s+-R\s+777", command):
        return {
            "risk_level": "high",
            "explanation": "This command sets permissions to 777 recursively, which is a security risk."
        }
    
    # Medium risk commands
    if re.search(r"sudo\s+", command):
        return {
            "risk_level": "medium",
            "explanation": "This command runs with elevated privileges. Review it carefully."
        }
    
    if re.search(r"rm\s+-rf", command):
        return {
            "risk_level": "medium",
            "explanation": "This command deletes files recursively and forcefully. Make sure the target is correct."
        }
    
    if re.search(r"shutdown|reboot|halt|poweroff", command):
        return {
            "risk_level": "medium",
            "explanation": "This command will shut down or restart your system."
        }
    
    # Default to low risk
    return {
        "risk_level": "low",
        "explanation": "This command requires caution but appears to be low risk."
    } 