#!/usr/bin/env python3
"""
AI Wrapper Module - Provides a unified interface for AI model interactions.
"""

import os
import sys
from rich.console import Console

console = Console()

def get_wrapper(api_key):
    """
    Get the appropriate AI wrapper based on the API key.
    
    Args:
        api_key (str): API key for the AI service
        
    Returns:
        object: AI wrapper instance
    """
    try:
        return GeminiWrapper(api_key)
    except ImportError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        console.print("[yellow]Please install the required dependencies:[/yellow]")
        console.print("pip install google-generativeai")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error initializing AI wrapper: {str(e)}[/red]")
        sys.exit(1)

class GeminiWrapper:
    """Wrapper for Google's Gemini API."""
    
    def __init__(self, api_key):
        """
        Initialize the Gemini wrapper.
        
        Args:
            api_key (str): API key for Gemini
        """
        try:
            # Import the library
            import google.generativeai as genai
            
            # Store the module
            self.genai = genai
            
            # Set the API key
            os.environ["GOOGLE_API_KEY"] = api_key
            
        except ImportError:
            raise ImportError("Could not import google.generativeai. Please install it with: pip install google-generativeai")
        except Exception as e:
            raise Exception(f"Failed to initialize Gemini API: {str(e)}")
    
    def get_model(self, model_name="gemini-2.5-pro"):
        """
        Get a Gemini model.
        
        Args:
            model_name (str, optional): Name of the model to use. Defaults to "gemini-2.5-pro".
            
        Returns:
            object: Gemini model
        """
        try:
            # Import the specific model class from the correct module
            from google.generativeai.generative_models import GenerativeModel
            
            # Create and return the model
            return GenerativeModel(model_name=model_name)
        except Exception as e:
            console.print(f"[red]Error getting model {model_name}: {str(e)}[/red]")
            console.print("[yellow]Falling back to default model gemini-2.5-pro...[/yellow]")
            try:
                from google.generativeai.generative_models import GenerativeModel
                return GenerativeModel(model_name="gemini-2.5-pro")
            except Exception as fallback_error:
                raise Exception(f"Failed to get fallback model: {str(fallback_error)}")
    
    def generate_content(self, model, prompts, **kwargs):
        """
        Generate content using the specified model.
        
        Args:
            model (object): Gemini model
            prompts (list): List of prompts (system prompt and user prompt)
            **kwargs: Additional arguments for the model
            
        Returns:
            object: Generated content
        """
        try:
            # Extract system prompt and user prompt
            system_prompt = prompts[0]
            user_prompt = prompts[1]
            
            # Generate content
            chat = model.start_chat(system_instruction=system_prompt)
            response = chat.send_message(user_prompt, **kwargs)
            
            return response
        except Exception as e:
            raise Exception(f"Failed to generate content: {str(e)}")

    def list_available_models(self):
        """
        List available models.
        
        Returns:
            list: List of available models
        """
        # Return default supported models
        # This is more reliable than trying to query the API
        return ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-pro"] 