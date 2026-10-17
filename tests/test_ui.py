from prompt_toolkit.document import Document

from smart_shell.ui import COMMANDS, SlashCompleter


def complete(text, models=("qwen2.5:0.5b", "qwen2.5-coder:3b", "llama3")):
    calls = []
    completer = SlashCompleter(lambda: calls.append(1) or list(models))
    return [c.text for c in completer.get_completions(Document(text), None)], calls


def test_slash_menu_and_model_names():
    assert complete("/mo")[0] == ["/model", "/models"]
    assert complete("/")[0] == list(COMMANDS)
    assert complete("list files")[0] == []
    names, calls = complete("/model qwen")
    assert names == ["qwen2.5:0.5b", "qwen2.5-coder:3b"] and calls == [1]


def test_model_list_failure_is_quiet():
    completer = SlashCompleter(lambda: (_ for _ in ()).throw(RuntimeError("offline")))
    assert list(completer.get_completions(Document("/model q"), None)) == []
