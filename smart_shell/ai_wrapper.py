"""
AI Wrapper Module - Provides a unified interface for AI model interactions.
"""

import os
import sys
import time
import requests
from rich.console import Console
from typing import Optional

console = Console()

# Maximum number of retries for API calls
MAX_RETRIES = 3
# Delay between retries (in seconds)
RETRY_DELAY = 2

def validate_api_key(api_key):
    """
    Validate the Gemini API key by making a lightweight API call.

    Args:
        api_key (str): The API key to validate.

    Returns:
        tuple: (is_valid, message)
    """
    if not api_key or len(api_key) < 10:
        return False, "API key is too short or empty."

    try:
        from google import genai
        from google.api_core import exceptions as google_exceptions

        client = genai.Client(api_key=api_key)
        
        # This is a lightweight call to check if the key is valid
        models = client.models.list()
        
        # Check if we got any models back
        if not models:
            return False, "API key is not valid or has no permissions."
            
        return True, "API key is valid."

    except ImportError:
        return False, "Google GenAI library not found. Please install with: pip install google-genai"
    except (google_exceptions.PermissionDenied, google_exceptions.InvalidArgument) as e:
        return False, f"Invalid API key: {str(e)}"
    except requests.exceptions.ConnectionError:
        return False, "No internet connection. Please check your network."
    except Exception as e:
        return False, f"An unexpected error occurred during validation: {str(e)}"

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
        console.print("pip install google-genai requests")
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
            # Import the google-genai library
            try:
                from google import genai
                self.genai = genai
                self.client = genai.Client(api_key=api_key)
            except ImportError:
                raise ImportError("Could not import google-genai. Please install it with: pip install google-genai")
            
            # Test API key validity and internet connection
            try:
                # First check internet connectivity
                self._check_internet_connection()
                
                # Then check API key validity by listing models
                models = self.client.models.list()
                if not models:
                    raise Exception("No models available - API key may be invalid")
            except requests.exceptions.ConnectionError:
                raise Exception("No internet connection. Please check your network and try again.")
            except requests.exceptions.Timeout:
                raise Exception("Connection timed out. Please check your network and try again.")
            except Exception as api_e:
                error_msg = str(api_e).lower()
                if "invalid api key" in error_msg or "unauthorized" in error_msg or "forbidden" in error_msg:
                    raise Exception("Invalid API key")
                elif "quota" in error_msg or "limit" in error_msg:
                    raise Exception("API quota exceeded")
                else:
                    raise Exception(f"API connection error: {str(api_e)}")
            
        except Exception as e:
            raise Exception(f"Failed to initialize Gemini API: {str(e)}")
    
    def _check_internet_connection(self):
        """
        Check if there is an active internet connection.
        
        Raises:
            Exception: If no internet connection is available
        """
        try:
            # Try to connect to Google's DNS server
            requests.get("https://8.8.8.8", timeout=3)
        except (requests.ConnectionError, requests.Timeout):
            raise Exception("No internet connection detected")
    
    def get_model(self, model_name="gemini-2.5-pro"):
        """
        Get a Gemini model.
        
        Args:
            model_name (str, optional): Name of the model to use. Defaults to "gemini-2.5-pro".
            
        Returns:
            str: Gemini model name to use for generation
        """
        try:
            # First check internet connectivity
            self._check_internet_connection()
            
            # With the new API, we just return the model name as a reference
            return model_name
            
        except requests.exceptions.ConnectionError:
            raise Exception("No internet connection. Please check your network and try again.")
        except requests.exceptions.Timeout:
            raise Exception("Connection timed out. Please check your network and try again.")
        except Exception as e:
            error_msg = str(e).lower()
            
            # Handle specific error cases
            if "not found" in error_msg or "does not exist" in error_msg:
                console.print(f"[red]Error: Model '{model_name}' not found or no longer available.[/red]")
                console.print("[yellow]The API or model version may be outdated.[/yellow]")
                console.print("[yellow]Falling back to default model gemini-2.5-pro...[/yellow]")
                return "gemini-2.5-pro"
            elif "unauthorized" in error_msg or "permission" in error_msg:
                console.print(f"[red]Error: No permission to access model '{model_name}'.[/red]")
                console.print("[yellow]Your API key may not have access to this model.[/yellow]")
                console.print("[yellow]Falling back to default model gemini-2.5-pro...[/yellow]")
                return "gemini-2.5-pro"
            else:
                console.print(f"[red]Error getting model {model_name}: {str(e)}[/red]")
                console.print("[yellow]Falling back to default model gemini-2.5-pro...[/yellow]")
                return "gemini-2.5-pro"
    
    def generate_content(self, model, prompts, retry=True, **kwargs):
        """
        Generate content using the specified model.
        
        Args:
            model (str): Gemini model name
            prompts (list): List of prompts (system prompt and user prompt)
            retry (bool): Whether to retry on failure
            **kwargs: Additional arguments for the model
            
        Returns:
            object: Generated content
        """
        # Extract system prompt and user prompt
        system_prompt = prompts[0]
        user_prompt = prompts[1]
        
        retries = 0
        while retries <= MAX_RETRIES:
            try:
                # Check internet connection before making the API call
                self._check_internet_connection()
                
                # Generate content using the new API
                from google.genai import types
                
                response = self.client.models.generate_content(
                    model=model,
                    contents=user_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=system_prompt,
                        temperature=kwargs.get("temperature", 0.2),
                        top_p=kwargs.get("top_p", 0.8),
                        top_k=kwargs.get("top_k", 40),
                        max_output_tokens=kwargs.get("max_output_tokens", 200),
                    )
                )
                
                return response
                    
            except requests.exceptions.ConnectionError:
                if not retry or retries >= MAX_RETRIES:
                    raise Exception("No internet connection. Please check your network and try again.")
                console.print(f"[yellow]Network connection error. Retrying ({retries+1}/{MAX_RETRIES})...[/yellow]")
                time.sleep(RETRY_DELAY)
                retries += 1
                
            except requests.exceptions.Timeout:
                if not retry or retries >= MAX_RETRIES:
                    raise Exception("Connection timed out. Please check your network and try again.")
                console.print(f"[yellow]Connection timed out. Retrying ({retries+1}/{MAX_RETRIES})...[/yellow]")
                time.sleep(RETRY_DELAY)
                retries += 1
                
            except Exception as e:
                error_msg = str(e).lower()
                
                # For some errors, we can retry
                if ("quota" in error_msg or "rate limit" in error_msg or "exceeded" in error_msg or 
                    "network" in error_msg or "connection" in error_msg or "timeout" in error_msg):
                    
                    if not retry or retries >= MAX_RETRIES:
                        if "quota" in error_msg or "rate limit" in error_msg or "exceeded" in error_msg:
                            raise Exception("API quota or rate limit exceeded. Please try again later.")
                        elif "network" in error_msg or "connection" in error_msg or "timeout" in error_msg:
                            raise Exception("Network connection error. Please check your internet connection.")
                    
                    console.print(f"[yellow]Temporary error: {str(e)}. Retrying ({retries+1}/{MAX_RETRIES})...[/yellow]")
                    time.sleep(RETRY_DELAY)
                    retries += 1
                else:
                    # For other errors, fail immediately
                    if "invalid" in error_msg and "key" in error_msg:
                        raise Exception("Invalid API key. Please check your key and try again.")
                    elif "blocked" in error_msg or "content" in error_msg and "policy" in error_msg:
                        raise Exception("Content blocked by API safety filters. Please modify your prompt.")
                    elif "too long" in error_msg or "token" in error_msg and "limit" in error_msg:
                        raise Exception("Prompt too long. Please shorten your request.")
                    else:
                        raise Exception(f"Failed to generate content: {str(e)}")
        
        # If we've exhausted all retries
        raise Exception("Failed to generate content after multiple attempts. Please try again later.")

    def explain_command(self, command: str, model: str) -> Optional[str]:
        """
        Uses the AI to generate a one-sentence explanation for a shell command.

        Args:
            command (str): The shell command to explain.
            model (str): The model to use for the explanation.

        Returns:
            A string containing the explanation, or None on failure.
        """
        system_prompt = (
            "You are a concise shell command explainer. "
            "Describe the following command in a single, simple sentence. "
            "Do not add any introductory text, formatting, or comments. "
            "For example, for 'ls -la', respond with 'Lists all files and directories in the current location, including hidden ones.'"
        )
        
        try:
            # Use the main generation function with a short timeout and fewer retries
            response = self.generate_content(
                model=model,
                prompts=[system_prompt, command],
                retry=False, # Don't retry on this, it's non-critical
                temperature=0.0, # Be factual
                max_output_tokens=100
            )

            if response and hasattr(response, 'text') and response.text:
                return response.text.strip()
            return None
        except Exception:
            # If any error occurs, just fail gracefully
            return None

    def list_available_models(self):
        """
        List all available models from the Gemini API that support content generation.
        
        Returns:
            list: A list of available model names.
        """
        try:
            # Check internet connection
            self._check_internet_connection()
            
            # Try to get models from API
            console.print("[blue]Fetching available models from API...[/blue]")
            models = self.client.models.list()
            model_names = []
            
            for model in models:
                # The official documentation example shows using `supported_actions`
                # to find models that can generate content. This is the correct way.
                if (hasattr(model, 'supported_actions') and 
                    model.supported_actions is not None and 
                    'generateContent' in model.supported_actions):
                    model_names.append(model.name)
            
            if not model_names:
                console.print("[yellow]Could not find any supported models from the API. Using defaults.[/yellow]")
                return ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-pro"]
                
            return model_names
        except requests.exceptions.ConnectionError:
            console.print("[yellow]Warning: Could not fetch models (no internet). Using defaults.[/yellow]")
            return ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-pro"]
        except requests.exceptions.Timeout:
            console.print("[yellow]Warning: Could not fetch models (connection timed out). Using defaults.[/yellow]")
            return ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-pro"]
        except Exception as e:
            # If API call fails, return default supported models
            console.print(f"[yellow]Note: Could not fetch models from API: {str(e)}[/yellow]")
            return ["gemini-2.5-pro", "gemini-2.5-flash", "gemini-2.0-pro"] 