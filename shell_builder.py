#!/usr/bin/env python3
"""
Shell Builder Module - Generates shell commands from natural language prompts.
"""

import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.style import Style
from rich.align import Align

# Import our AI wrapper
from ai_wrapper import get_wrapper

console = Console()

# ASCII art banner
BANNER = r"""
    _____                      _      _____ _          _ _                                                      
   / ____|                    | |    / ____| |        | | |                                                     
  | (___  _ __ ___   __ _ _ __| |_  | (___ | |__   ___| | |                                                     
   \___ \| '_ ` _ \ / _` | '__| __|  \___ \| '_ \ / _ \ | |                                                     
   ____) | | | | | | (_| | |  | |_   ____) | | | |  __/ | |                                                     
  |_____/|_| |_| |_|\__,_|_|   \__| |_____/|_| |_|\___|_|_|                                                     

  Natural Language → Bash Commands
"""

# Supported models
SUPPORTED_MODELS = ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-pro"]

def generate_command(prompt, api_key, model=None):
    """
    Generate a shell command from a natural language prompt using Gemini.
    
    Args:
        prompt (str): Natural language prompt
        api_key (str): API key for Gemini
        model (str, optional): Model to use. Defaults to None.
        
    Returns:
        str: Generated shell command
    """
    # System prompt to instruct the model
    system_prompt = """
    You are a helpful Linux command generator. Your task is to convert natural language requests into appropriate Bash commands.
    
    Guidelines:
    1. Return ONLY the command with no explanations, comments, markdown formatting, or additional text.
    2. Ensure the command is secure and won't cause data loss.
    3. Use standard Bash syntax compatible with most Linux distributions.
    4. For complex tasks, use pipes, redirects, and multiple commands as needed.
    5. If the request is ambiguous, make reasonable assumptions.
    6. If the request is dangerous or could cause data loss, respond with "UNSAFE: [reason]"
    
    Examples:
    User: "List all PDF files in the current directory"
    Response: find . -maxdepth 1 -name "*.pdf"
    
    User: "Show system memory usage"
    Response: free -h
    
    User: "Delete all files on my computer"
    Response: UNSAFE: This command could cause catastrophic data loss
    """
    
    # Get the appropriate wrapper for the API
    wrapper = get_wrapper(api_key)
    
    # Set up the model
    model_name = validate_model(model)
    model = wrapper.get_model(model_name)
    
    # Generate response
    try:
        response = wrapper.generate_content(
            model,
            [system_prompt, prompt],
            temperature=0.2,
            top_p=0.8,
            top_k=40,
            max_output_tokens=200,
        )
        
        if hasattr(response, 'text'):
            # Standard API response
            command = response.text.strip()
        else:
            # Handle different response formats
            command = str(response).strip()
        
        # Check for UNSAFE prefix
        if command.startswith("UNSAFE:"):
            raise ValueError(command)
            
        return command
    except Exception as e:
        raise Exception(f"Error generating command: {str(e)}")

def display_banner():
    """Display the Smart-Shell banner."""
    text = Text(BANNER)
    panel = Panel(
        Align(
            text,
            align="center",
            vertical="middle"
        ),
        border_style="blue",
        padding=(1, 2),
        subtitle="Powered by Google Gemini"
    )
    console.print(panel)

def validate_model(model_name=None):
    """
    Validate the model name and return a supported model.
    
    Args:
        model_name (str, optional): Model name specified by user
        
    Returns:
        str: Valid model name to use
    """
    # If no model specified, use default
    if not model_name:
        return SUPPORTED_MODELS[0]
    
    # Check if model is supported
    if model_name not in SUPPORTED_MODELS:
        console.print(f"[yellow]⚠️ Model '{model_name}' not officially supported. Falling back to '{SUPPORTED_MODELS[0]}'.[/yellow]")
        return SUPPORTED_MODELS[0]
    
    return model_name

def list_supported_models():
    """
    Return a list of supported models.
    
    Returns:
        list: List of supported model names
    """
    return SUPPORTED_MODELS

if __name__ == "__main__":
    # This allows the module to be run directly for testing
    display_banner()
    console.print("[yellow]Shell Builder module - For testing only[/yellow]")
    console.print("Use 'smart-shell' command or main.py to run the application.") 