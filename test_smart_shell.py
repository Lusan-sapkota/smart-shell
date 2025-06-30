#!/usr/bin/env python3
"""
Test script for Smart-Shell.
"""

import os
import sys
from rich.console import Console

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import Smart-Shell modules
from shell_builder import display_banner, generate_command
from safety import check_command_safety
from utils import print_command_preview

console = Console()

def test_banner():
    """Test displaying the banner."""
    console.print("\n[bold green]Testing Banner Display:[/bold green]")
    display_banner()

def test_safety_check():
    """Test the safety check system."""
    console.print("\n[bold green]Testing Safety Check System:[/bold green]")
    
    # Test safe command
    safe_cmd = "ls -la"
    console.print(f"[blue]Testing safe command:[/blue] {safe_cmd}")
    result = check_command_safety(safe_cmd)
    console.print(f"Result: {result['status']}")
    
    # Test warning command
    warn_cmd = "rm -rf *"
    console.print(f"[blue]Testing warning command:[/blue] {warn_cmd}")
    result = check_command_safety(warn_cmd)
    console.print(f"Result: {result['status']}")
    
    # Test blocked command
    block_cmd = "rm -rf /"
    console.print(f"[blue]Testing blocked command:[/blue] {block_cmd}")
    result = check_command_safety(block_cmd)
    console.print(f"Result: {result['status']}")

def test_command_preview():
    """Test command preview functionality."""
    console.print("\n[bold green]Testing Command Preview:[/bold green]")
    
    # Test safe command preview
    safe_cmd = "ls -la"
    console.print(f"[blue]Preview of safe command:[/blue] {safe_cmd}")
    result = check_command_safety(safe_cmd)
    print_command_preview(safe_cmd, result)
    
    # Test warning command preview
    warn_cmd = "rm -rf *"
    console.print(f"[blue]Preview of warning command:[/blue] {warn_cmd}")
    result = check_command_safety(warn_cmd)
    print_command_preview(warn_cmd, result)

def test_generate_command():
    """Test command generation if API key is available."""
    console.print("\n[bold green]Testing Command Generation:[/bold green]")
    
    # Check for API key
    api_key = os.environ.get("SMART_SHELL_API_KEY")
    if not api_key:
        console.print("[yellow]Skipping command generation test - no API key found.[/yellow]")
        console.print("Set the SMART_SHELL_API_KEY environment variable to test this feature.")
        return
    
    try:
        # Test command generation
        prompt = "list files in the current directory"
        console.print(f"[blue]Generating command for:[/blue] {prompt}")
        command = generate_command(prompt, api_key)
        console.print(f"[green]Generated command:[/green] {command}")
        
        # Check safety
        result = check_command_safety(command)
        print_command_preview(command, result)
    except Exception as e:
        console.print(f"[bold red]Error in command generation:[/bold red] {str(e)}")

def run_tests():
    """Run all tests."""
    console.print("[bold]Smart-Shell Test Suite[/bold]")
    console.print("=======================")
    
    test_banner()
    test_safety_check()
    test_command_preview()
    test_generate_command()
    
    console.print("\n[bold green]All tests completed![/bold green]")

if __name__ == "__main__":
    run_tests() 