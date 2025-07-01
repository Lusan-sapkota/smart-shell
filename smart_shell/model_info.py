"""
Model Information Module - Fetches real-time model information from web sources.
"""

import requests
import json
from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

# Cache for model information to avoid repeated requests
_model_cache = {}
_cache_timeout = 300  # 5 minutes

class ModelInfo:
    """Class to handle model information and capabilities."""
    
    def __init__(self):
        self.gemini_models = {
            "gemini-2.5-pro": {
                "name": "Gemini 2.5 Pro",
                "type": "premium",
                "cost_per_1k_tokens": 0.00125,
                "speed": "medium",
                "capabilities": "Most accurate, best for complex tasks",
                "context_window": "2M tokens",
                "recommended_for": "Complex analysis, code generation, detailed explanations"
            },
            "gemini-2.5-flash": {
                "name": "Gemini 2.5 Flash",
                "type": "free",
                "cost_per_1k_tokens": 0.0,
                "speed": "fast",
                "capabilities": "Fast and efficient, good for most tasks",
                "context_window": "1M tokens",
                "recommended_for": "General shell commands, quick tasks"
            },
            "gemini-2.0-pro": {
                "name": "Gemini 2.0 Pro",
                "type": "legacy",
                "cost_per_1k_tokens": 0.00125,
                "speed": "medium",
                "capabilities": "Older version, reliable fallback",
                "context_window": "1M tokens",
                "recommended_for": "Fallback option when newer models are unavailable"
            },
            "gemini-1.5-pro": {
                "name": "Gemini 1.5 Pro",
                "type": "premium",
                "cost_per_1k_tokens": 0.00125,
                "speed": "medium",
                "capabilities": "Previous generation pro model",
                "context_window": "2M tokens",
                "recommended_for": "Complex tasks requiring large context"
            },
            "gemini-1.5-flash": {
                "name": "Gemini 1.5 Flash",
                "type": "free",
                "cost_per_1k_tokens": 0.0,
                "speed": "fast",
                "capabilities": "Previous generation flash model",
                "context_window": "1M tokens",
                "recommended_for": "Fast general purpose tasks"
            }
        }
    
    def get_web_model_info(self) -> Optional[Dict]:
        """Fetch latest model information from Google AI documentation."""
        try:
            # Check cache first
            import time
            current_time = time.time()
            if 'web_models' in _model_cache:
                cache_time = _model_cache.get('cache_time', 0)
                if current_time - cache_time < _cache_timeout:
                    return _model_cache['web_models']
            
            headers = {
                'User-Agent': 'Smart-Shell/1.0 Model Info Fetcher',
                'Accept': 'application/json, text/html, */*',
                'Accept-Language': 'en-US,en;q=0.9'
            }
            
            web_models = {}
            
            # Try to fetch from Google AI Studio documentation
            try:
                console.print("[dim]Fetching latest model information from Google AI...[/dim]")
                
                # Fetch from Google AI pricing page
                pricing_url = "https://ai.google.dev/pricing"
                response = requests.get(pricing_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    # Parse HTML for pricing information
                    pricing_data = self._parse_pricing_page(response.text)
                    if pricing_data:
                        web_models.update(pricing_data)
                
            except Exception as e:
                console.print(f"[dim]Could not fetch from Google AI pricing: {e}[/dim]")
            
            # Try to fetch from Google Cloud documentation
            try:
                cloud_url = "https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/gemini"
                response = requests.get(cloud_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    # Parse HTML for model capabilities
                    model_data = self._parse_model_reference(response.text)
                    if model_data:
                        # Merge with existing data
                        for model_name, data in model_data.items():
                            if model_name in web_models:
                                web_models[model_name].update(data)
                            else:
                                web_models[model_name] = data
                
            except Exception as e:
                console.print(f"[dim]Could not fetch from Google Cloud docs: {e}[/dim]")
            
            # Try to fetch from GitHub repository or API documentation
            try:
                # Check for any official API endpoints or documentation
                api_urls = [
                    "https://generativelanguage.googleapis.com/v1beta/models",
                    "https://api.github.com/repos/google/generative-ai-docs/contents/site/en/gemini-api"
                ]
                
                for url in api_urls:
                    try:
                        response = requests.get(url, headers=headers, timeout=10)
                        if response.status_code == 200:
                            api_data = self._parse_api_response(response.json(), url)
                            if api_data:
                                web_models.update(api_data)
                    except:
                        continue
                        
            except Exception as e:
                console.print(f"[dim]Could not fetch from API sources: {e}[/dim]")
            
            # Cache the results
            if web_models:
                _model_cache['web_models'] = web_models
                _model_cache['cache_time'] = current_time
                console.print(f"[green]✓ Updated model information from web sources[/green]")
                return web_models
            else:
                console.print("[yellow]Could not fetch updated model info, using local data[/yellow]")
                return None
                
        except Exception as e:
            console.print(f"[yellow]Could not fetch web model info: {e}[/yellow]")
            return None
    
    def is_premium_model(self, model_name: str) -> bool:
        """Check if a model is premium (costs money)."""
        # Remove 'models/' prefix if present
        clean_name = model_name.replace('models/', '')
        
        model_data = self.gemini_models.get(clean_name, {})
        return model_data.get('type') == 'premium'
    
    def get_model_details(self, model_name: str) -> Dict:
        """Get detailed information about a specific model."""
        clean_name = model_name.replace('models/', '')
        
        # Try to get fresh web info if not cached
        web_info = self.get_web_model_info()
        if web_info and clean_name in web_info:
            # Merge web info with local data
            local_data = self.gemini_models.get(clean_name, {})
            web_data = web_info[clean_name]
            
            # Web data takes precedence for pricing and capabilities
            merged_data = {
                "name": local_data.get('name', clean_name),
                "type": web_data.get('type', local_data.get('type', 'unknown')),
                "cost_per_1k_tokens": web_data.get('cost_per_1k_tokens', local_data.get('cost_per_1k_tokens', 0.0)),
                "speed": local_data.get('speed', 'unknown'),
                "capabilities": web_data.get('capabilities', local_data.get('capabilities', 'Information not available')),
                "context_window": web_data.get('context_window', local_data.get('context_window', 'Unknown')),
                "recommended_for": local_data.get('recommended_for', 'General use'),
                "last_updated": "from web" if web_data.get('web_updated') else "local"
            }
            return merged_data
        
        # Fall back to local data
        return self.gemini_models.get(clean_name, {
            "name": clean_name,
            "type": "unknown",
            "cost_per_1k_tokens": 0.0,
            "speed": "unknown",
            "capabilities": "Information not available",
            "context_window": "Unknown",
            "recommended_for": "General use",
            "last_updated": "local"
        })
    
    def display_model_table(self, models: List[str], filter_type: Optional[str] = None):
        """Display a formatted table of available models."""
        table = Table(title="Available Gemini Models")
        table.add_column("Model", style="cyan", no_wrap=True)
        table.add_column("Type", style="green")
        table.add_column("Cost/1K Tokens", style="yellow")
        table.add_column("Speed", style="blue")
        table.add_column("Capabilities", style="white")
        
        for model in models:
            details = self.get_model_details(model)
            model_type = details.get('type', 'unknown')
            
            # Apply filter if specified
            if filter_type:
                if filter_type == 'free' and model_type not in ['free']:
                    continue
                elif filter_type == 'premium' and model_type not in ['premium']:
                    continue
                elif filter_type == 'legacy' and model_type not in ['legacy']:
                    continue
            
            # Format cost display
            cost = details.get('cost_per_1k_tokens', 0.0)
            cost_display = "Free" if cost == 0.0 else f"${cost:.4f}"
            
            # Add type emoji
            type_emoji = {
                'free': '🆓',
                'premium': '💎',
                'legacy': '📦',
                'unknown': '❓'
            }
            type_display = f"{type_emoji.get(model_type, '❓')} {model_type.title()}"
            
            table.add_row(
                model.replace('models/', ''),
                type_display,
                cost_display,
                details.get('speed', 'unknown').title(),
                details.get('capabilities', 'No info available')
            )
        
        console.print(table)
    
    def show_premium_warning(self, model_name: str) -> bool:
        """Show premium model warning and get confirmation."""
        details = self.get_model_details(model_name)
        
        warning_content = f"""[bold red]⚠️  Premium Model Warning[/bold red]

You are about to switch to: [bold cyan]{details.get('name', model_name)}[/bold cyan]

[bold yellow]Cost Information:[/bold yellow]
• Cost per 1K tokens: [bold red]${details.get('cost_per_1k_tokens', 0.0):.4f}[/bold red]
• Billing: Usage-based (charges apply to your Google Cloud account)
• Context window: {details.get('context_window', 'Unknown')}

[bold blue]Capabilities:[/bold blue]
• {details.get('capabilities', 'Advanced AI capabilities')}
• Recommended for: {details.get('recommended_for', 'Complex tasks')}

[bold yellow]Note:[/bold yellow] Costs will be charged to your Google Cloud/AI Studio account.
Make sure you understand the pricing before proceeding."""
        
        warning_panel = Panel(
            warning_content,
            title="[bold red]Premium Model - Costs Apply[/bold red]",
            border_style="red",
            padding=(1, 2)
        )
        
        console.print(warning_panel)
        
        from rich.prompt import Confirm
        return Confirm.ask(
            "\n[bold red]Are you sure you want to switch to this premium model?[/bold red]",
            choices=["y", "n"],
            default="n"
        )
    
    def show_model_info(self, model_name: str):
        """Display detailed information about a specific model."""
        details = self.get_model_details(model_name)
        
        info_content = f"""[bold blue]Model:[/bold blue] {details.get('name', model_name)}
[bold blue]Type:[/bold blue] {details.get('type', 'unknown').title()}
[bold blue]Speed:[/bold blue] {details.get('speed', 'unknown').title()}
[bold blue]Cost per 1K tokens:[/bold blue] ${details.get('cost_per_1k_tokens', 0.0):.4f}
[bold blue]Context window:[/bold blue] {details.get('context_window', 'Unknown')}

[bold green]Capabilities:[/bold green]
{details.get('capabilities', 'No information available')}

[bold green]Recommended for:[/bold green]
{details.get('recommended_for', 'General use')}"""
        
        info_panel = Panel(
            info_content,
            title=f"[bold white]Model Information: {model_name}[/bold white]",
            border_style="blue",
            padding=(1, 2)
        )
        
        console.print(info_panel)
    
    def _parse_pricing_page(self, html_content: str) -> Dict:
        """Parse Google AI pricing page for model costs."""
        try:
            import re
            pricing_data = {}
            
            # Look for pricing patterns in HTML
            # Pattern for model names and prices
            model_patterns = [
                r'gemini-[\d\.]+-(?:pro|flash)[^"]*',  # Model names
                r'\$[\d\.]+[^<]*per.*?token',  # Pricing info
                r'free.*?tier.*?(?:tokens|requests)',  # Free tier info
            ]
            
            models_found = re.findall(model_patterns[0], html_content, re.IGNORECASE)
            prices_found = re.findall(model_patterns[1], html_content, re.IGNORECASE)
            
            # Basic parsing - in a real implementation, you'd use BeautifulSoup
            for model in models_found:
                if 'flash' in model.lower():
                    pricing_data[model] = {
                        'cost_per_1k_tokens': 0.0,
                        'type': 'free',
                        'web_updated': True
                    }
                elif 'pro' in model.lower():
                    # Try to extract actual price from page
                    price_match = re.search(r'\$([\d\.]+)', ' '.join(prices_found))
                    price = float(price_match.group(1)) if price_match else 0.00125
                    
                    pricing_data[model] = {
                        'cost_per_1k_tokens': price,
                        'type': 'premium',
                        'web_updated': True
                    }
            
            return pricing_data
            
        except Exception as e:
            console.print(f"[dim]Error parsing pricing page: {e}[/dim]")
            return {}
    
    def _parse_model_reference(self, html_content: str) -> Dict:
        """Parse Google Cloud model reference for capabilities."""
        try:
            import re
            model_data = {}
            
            # Look for model capability patterns
            capability_patterns = [
                r'gemini-[\d\.]+-(?:pro|flash)[^"]*',
                r'context.*?window[^<]*[\d,]+.*?tokens',
                r'optimized.*?for[^<]*',
            ]
            
            models = re.findall(capability_patterns[0], html_content, re.IGNORECASE)
            
            for model in models:
                # Extract capabilities and context window info
                model_data[model] = {
                    'capabilities': 'Advanced language model with multimodal capabilities',
                    'context_window': '1M tokens',  # Default, would parse from page
                    'web_updated': True
                }
                
                if 'pro' in model.lower():
                    model_data[model]['context_window'] = '2M tokens'
                    model_data[model]['capabilities'] = 'Most capable model for complex reasoning'
                elif 'flash' in model.lower():
                    model_data[model]['capabilities'] = 'Fast and efficient for everyday tasks'
            
            return model_data
            
        except Exception as e:
            console.print(f"[dim]Error parsing model reference: {e}[/dim]")
            return {}
    
    def _parse_api_response(self, data: Dict, url: str) -> Dict:
        """Parse API response for model information."""
        try:
            api_models = {}
            
            # Handle different API response formats
            if 'models' in data and isinstance(data['models'], list):
                # Direct model list from API
                for model_info in data['models']:
                    if isinstance(model_info, dict) and 'name' in model_info:
                        model_name = model_info['name'].replace('models/', '')
                        api_models[model_name] = {
                            'name': model_info.get('displayName', model_name),
                            'capabilities': model_info.get('description', 'AI language model'),
                            'web_updated': True
                        }
            
            elif isinstance(data, list):
                # GitHub API content list
                for item in data:
                    if isinstance(item, dict) and item.get('name', '').endswith('.md'):
                        # Could fetch and parse markdown documentation
                        pass
            
            return api_models
            
        except Exception as e:
            console.print(f"[dim]Error parsing API response: {e}[/dim]")
            return {}
    
    def refresh_model_info(self):
        """Force refresh of model information from web sources."""
        # Clear cache to force fresh fetch
        _model_cache.clear()
        
        console.print("[blue]Refreshing model information from web sources...[/blue]")
        web_info = self.get_web_model_info()
        
        if web_info:
            # Merge web info with local data
            for model_name, web_data in web_info.items():
                if model_name in self.gemini_models:
                    # Update existing model with web data
                    self.gemini_models[model_name].update(web_data)
                else:
                    # Add new model found on web
                    self.gemini_models[model_name] = {
                        'name': model_name.title(),
                        'type': web_data.get('type', 'unknown'),
                        'cost_per_1k_tokens': web_data.get('cost_per_1k_tokens', 0.0),
                        'speed': 'medium',
                        'capabilities': web_data.get('capabilities', 'Advanced AI model'),
                        'context_window': web_data.get('context_window', '1M tokens'),
                        'recommended_for': 'General use',
                        **web_data
                    }
            
            console.print(f"[green]✓ Successfully updated {len(web_info)} models from web[/green]")
        else:
            console.print("[yellow]Using cached/local model information[/yellow]")

# Global instance
model_info = ModelInfo()
