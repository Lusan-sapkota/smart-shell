"""
AI Wrapper Module - One client for any OpenAI-compatible chat API.

Gemini, OpenAI, DeepSeek, OpenRouter, Groq, Ollama and LM Studio all expose
/models and /chat/completions, so a single requests-based client covers them.
"""

import os
import re
import time
import requests

from .config import load_config, ENV_API_KEY

ENV_BASE_URL = "SMART_SHELL_BASE_URL"

# name -> (base_url, default model or None to pick from the model list, needs api key)
# Order is the setup wizard's order: local first, so a fresh setup defaults to Ollama.
PROVIDERS = {
    "ollama": ("http://localhost:11434/v1", None, False),
    "lmstudio": ("http://localhost:1234/v1", None, False),
    "gemini": ("https://generativelanguage.googleapis.com/v1beta/openai", "gemini-flash-latest", True),
    "openai": ("https://api.openai.com/v1", None, True),
    "deepseek": ("https://api.deepseek.com/v1", "deepseek-chat", True),
    "openrouter": ("https://openrouter.ai/api/v1", None, True),
    "groq": ("https://api.groq.com/openai/v1", None, True),
}

MAX_RETRIES = 3
RETRY_DELAY = 2


class AIError(Exception):
    pass


class AIClient:
    def __init__(self, base_url, api_key=None):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def _request(self, method, path, timeout, **kwargs):
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        url = f"{self.base_url}{path}"
        for attempt in range(MAX_RETRIES + 1):
            try:
                resp = requests.request(method, url, headers=headers, timeout=timeout, **kwargs)
            except requests.ConnectionError:
                if attempt == MAX_RETRIES:
                    raise AIError(f"Cannot reach {self.base_url}. Is the server running and the URL right?")
            except requests.Timeout:
                if attempt == MAX_RETRIES:
                    raise AIError(f"Request to {self.base_url} timed out.")
            else:
                # Gemini answers a bad key with 400 rather than 401.
                if resp.status_code in (401, 403) or "API_KEY_INVALID" in resp.text or "valid API key" in resp.text:
                    raise AIError("API key rejected. Run 'smart-shell setup' to update it.")
                if resp.status_code == 404:
                    raise AIError(f"Not found: {url}. Check the base URL and model name.")
                if resp.status_code == 429 or resp.status_code >= 500:
                    if attempt == MAX_RETRIES:
                        raise AIError(f"Server busy or rate limited (HTTP {resp.status_code}). Try again later.")
                elif not resp.ok:
                    raise AIError(f"HTTP {resp.status_code}: {resp.text[:300]}")
                else:
                    return resp.json()
            time.sleep(RETRY_DELAY)

    def list_models(self):
        data = self._request("GET", "/models", timeout=15)
        # Gemini returns "models/gemini-..."; chat wants the bare name.
        return sorted(m["id"].removeprefix("models/") for m in data.get("data", []))

    def chat(self, model, system, user, temperature=0.3, max_tokens=3000):
        data = self._request("POST", "/chat/completions", timeout=300, json={
            "model": model.removeprefix("models/"),
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "temperature": temperature,
            "max_tokens": max_tokens,
        })
        try:
            text = data["choices"][0]["message"]["content"] or ""
        except (KeyError, IndexError, TypeError):
            raise AIError(f"Unexpected response: {str(data)[:300]}")
        # Local reasoning models (qwen3, deepseek-r1) put their thinking inline.
        return re.sub(r"<think>.*?</think>", "", text, flags=re.S).strip()


def override_provider(config, provider=None, base_url=None):
    """Config for a one-off run against another provider or URL."""
    if not provider and not base_url:
        return config
    saved = config.get("provider", "gemini" if config.get("api_key") else None)
    saved_url = config.get("base_url") or PROVIDERS.get(saved, (None,))[0]
    provider = provider or saved
    if provider == "custom" and not base_url:
        raise AIError("--provider custom needs --base-url.")
    new = dict(config, provider=provider)
    new["base_url"] = base_url or (saved_url if provider == saved else PROVIDERS[provider][0])
    if provider != saved:
        new.pop("default_model", None)
    # Never send the saved key to a server it wasn't saved for; use SMART_SHELL_API_KEY instead.
    if new["base_url"] != saved_url:
        new.pop("api_key", None)
    return new


def is_configured(config=None):
    config = load_config() if config is None else config
    return bool(config.get("provider") or config.get("api_key") or os.environ.get(ENV_API_KEY))


def get_client(config=None):
    """Build a client from the saved config, with env vars taking precedence."""
    config = load_config() if config is None else config
    # Configs from before multi-provider support are Gemini.
    provider = config.get("provider", "gemini")
    base_url = os.environ.get(ENV_BASE_URL) or config.get("base_url") or PROVIDERS.get(provider, PROVIDERS["gemini"])[0]
    return AIClient(base_url, os.environ.get(ENV_API_KEY) or config.get("api_key"))


def resolve_model(client, model=None, config=None):
    """Explicit model, else configured default, else provider default, else first available."""
    config = load_config() if config is None else config
    model = model or config.get("default_model") or PROVIDERS.get(config.get("provider", "gemini"), (None, None))[1]
    if model:
        return model
    models = client.list_models()
    if not models:
        raise AIError("The server reports no models. For Ollama, pull one first: ollama pull qwen2.5-coder")
    return models[0]
