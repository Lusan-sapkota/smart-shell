#!/usr/bin/env python3
"""
Example script demonstrating basic usage of Smart-Shell.
"""

import sys
import os
import subprocess

# Add parent directory to path to import Smart-Shell modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shell_builder import generate_command
from safety import check_command_safety
from utils import print_command_preview, execute_command
from config import load_config

def run_example():
    """Run a basic example of Smart-Shell."""
    print("Smart-Shell Basic Example")
    print("-----------------------")
    
    # Load configuration (make sure you've set up your API key)
    config = load_config()
    if not config.get("api_key"):
        print("No API key found. Please set up your API key first.")
        print("Run: python main.py --setup")
        return
    
    # Example prompts to try
    example_prompts = [
        "list all Python files in the current directory",
        "show disk usage in human-readable format",
        "find the 5 largest files in /tmp",
        "count lines of code in all Python files recursively"
    ]
    
    # Let user choose a prompt or enter their own
    print("\nChoose an example prompt or enter your own:")
    for i, prompt in enumerate(example_prompts, 1):
        print(f"{i}. {prompt}")
    print("0. Enter your own prompt")
    
    choice = input("\nYour choice (0-4): ")
    
    if choice == "0":
        prompt = input("Enter your prompt: ")
    elif choice in ["1", "2", "3", "4"]:
        prompt = example_prompts[int(choice) - 1]
    else:
        print("Invalid choice.")
        return
    
    print(f"\nPrompt: {prompt}")
    print("Generating command...")
    
    try:
        # Generate command
        command = generate_command(prompt, config["api_key"])
        
        # Check safety
        safety_result = check_command_safety(command)
        
        # Print preview
        print_command_preview(command, safety_result)
        
        # Ask for confirmation
        if safety_result["status"] == "blocked":
            print("Command is blocked for safety reasons.")
            return
        
        if safety_result["status"] == "warning":
            confirm = input("This command has warnings. Execute anyway? (y/n): ")
            if confirm.lower() != "y":
                return
        else:
            confirm = input("Execute this command? (y/n): ")
            if confirm.lower() != "y":
                return
        
        # Execute command
        execute_command(command)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    run_example() 