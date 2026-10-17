import json

import importlib

main = importlib.import_module("smart_shell.main")


class FakeClient:
    def __init__(self, replies):
        self.replies, self.sent = list(replies), []

    def chat(self, model, system, user, **kwargs):
        self.sent.append(user)
        return self.replies.pop(0)


def run_with(monkeypatch, answers, results, plan, client=None, auto_yes=False):
    answers, results, ran = list(answers), list(results), []
    monkeypatch.setattr(main.Prompt, "ask", staticmethod(lambda *a, **k: answers.pop(0)))
    monkeypatch.setattr(main.Confirm, "ask", staticmethod(lambda *a, **k: answers.pop(0)))
    monkeypatch.setattr(main, "execute_command", lambda cmd: (ran.append(cmd), results.pop(0))[1])
    monkeypatch.setattr(main, "save_to_history", lambda *a, **k: "id")
    monkeypatch.setattr(main, "update_history_result", lambda *a: None)
    ok = main.review_and_run("req", plan, False, auto_yes, client, "m", {})
    return ok, ran


def test_failure_offers_ai_fix_with_error_output(monkeypatch):
    client = FakeClient([json.dumps({"commands": ["ls ./real_dir"]})])
    ok, ran = run_with(monkeypatch, ["y", True, "y"], [(False, "ls: nope: No such file"), (True, "")], ["ls nope"], client)
    assert ok and ran == ["ls nope", "ls ./real_dir"]
    assert "ls nope" in client.sent[0] and "No such file" in client.sent[0]


def test_edit_replaces_plan_and_is_rechecked(monkeypatch):
    ok, ran = run_with(monkeypatch, ["e", "echo hi", "y"], [(True, "")], ["date"])
    assert ok and ran == ["echo hi"]


def test_blocked_never_runs_even_with_yes(monkeypatch):
    ok, ran = run_with(monkeypatch, [], [], ["rm -rf /"], auto_yes=True)
    assert not ok and ran == []


def test_default_run_subcommand(monkeypatch):
    seen = []
    monkeypatch.setattr(main.click.Group, "parse_args", lambda self, ctx, args: seen.append(args))
    for args in (["list", "files"], ["--provider", "ollama", "list"], ["-d", "x"], ["models"], ["--provider", "ollama"], []):
        main.cli.parse_args(None, args)
    assert seen == [["run", "list", "files"], ["run", "--provider", "ollama", "list"], ["run", "-d", "x"],
                    ["models"], ["--provider", "ollama"], []]
