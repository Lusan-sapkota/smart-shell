import pytest
import requests

from smart_shell import ai_wrapper
from smart_shell.ai_wrapper import AIClient, AIError, get_client, resolve_model


class FakeResponse:
    def __init__(self, status_code, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload
        self.text = text
        self.ok = status_code < 400

    def json(self):
        return self._payload


@pytest.fixture
def calls(monkeypatch):
    """Queue responses for requests.request and record what was sent."""
    queue, sent = [], []

    def fake_request(method, url, headers, timeout, **kwargs):
        sent.append((method, url, headers, kwargs))
        item = queue.pop(0)
        if isinstance(item, Exception):
            raise item
        return item

    monkeypatch.setattr(requests, "request", fake_request)
    monkeypatch.setattr(ai_wrapper, "RETRY_DELAY", 0)
    return queue, sent


def test_list_models_strips_gemini_prefix(calls):
    queue, sent = calls
    queue.append(FakeResponse(200, {"data": [{"id": "models/gemini-x"}, {"id": "a-model"}]}))
    assert AIClient("http://h/v1/", "k").list_models() == ["a-model", "gemini-x"]
    assert sent[0][1] == "http://h/v1/models"
    assert sent[0][2] == {"Authorization": "Bearer k"}


def test_chat_strips_think_block_and_sends_no_key_for_local(calls):
    queue, sent = calls
    queue.append(FakeResponse(200, {"choices": [{"message": {"content": "<think>hmm</think>\n{\"commands\": []}"}}]}))
    assert AIClient("http://localhost:11434/v1").chat("models/m", "sys", "hi") == '{"commands": []}'
    method, url, headers, kwargs = sent[0]
    assert (method, url, headers) == ("POST", "http://localhost:11434/v1/chat/completions", {})
    assert kwargs["json"]["model"] == "m"


def test_retries_then_succeeds(calls):
    queue, _ = calls
    queue += [requests.ConnectionError(), FakeResponse(503), FakeResponse(200, {"data": []})]
    assert AIClient("http://h").list_models() == []


def test_bad_key_is_reported(calls):
    queue, _ = calls
    queue.append(FakeResponse(400, text='{"error": {"message": "Please pass a valid API key"}}'))
    with pytest.raises(AIError, match="API key rejected"):
        AIClient("http://h", "bad").list_models()


def test_legacy_config_means_gemini(monkeypatch):
    monkeypatch.delenv("SMART_SHELL_API_KEY", raising=False)
    monkeypatch.delenv("SMART_SHELL_BASE_URL", raising=False)
    client = get_client({"api_key": "AIza-old"})
    assert client.base_url == ai_wrapper.PROVIDERS["gemini"][0]
    assert client.api_key == "AIza-old"


def test_resolve_model_falls_back_to_first_listed(calls):
    queue, _ = calls
    queue.append(FakeResponse(200, {"data": [{"id": "qwen2.5:0.5b"}]}))
    client = AIClient("http://localhost:11434/v1")
    assert resolve_model(client, "explicit", {}) == "explicit"
    assert resolve_model(client, None, {"provider": "deepseek"}) == "deepseek-chat"
    assert resolve_model(client, None, {"provider": "ollama"}) == "qwen2.5:0.5b"
