import json

from smart_shell.shell_builder import format_session_context, generate_command_plan


class FakeClient:
    def __init__(self, replies):
        self.replies, self.sent = list(replies), []

    def chat(self, model, system, user, **kwargs):
        self.sent.append(user)
        return self.replies.pop(0)


def test_session_context_is_sent_with_follow_ups():
    session = [{"prompt": "count lines in ~/notes", "commands": ["wc -l ~/notes/*"], "result": "succeeded"}]
    client = FakeClient([json.dumps({"commands": ["wc -l /var/log/*"]})])
    assert generate_command_plan("same for /var/log", client, "m", session=session) == ["wc -l /var/log/*"]
    assert "wc -l ~/notes/*" in client.sent[0] and client.sent[0].endswith("New request: same for /var/log")


def test_no_context_sends_bare_prompt_and_retries_bad_json():
    client = FakeClient(["not json", '<think>x</think>{"commands": ["ls"]}'])
    assert generate_command_plan("list", client, "m") == ["ls"]
    assert client.sent == ["list", "list"]


def test_context_keeps_last_five():
    session = [{"prompt": f"p{i}", "commands": ["true"], "result": "not run"} for i in range(8)]
    text = format_session_context(session)
    assert "p2" not in text and "p3" in text and "p7" in text


def test_parse_plan_tolerates_small_model_replies():
    from smart_shell.shell_builder import parse_plan
    assert parse_plan(r'```json\n{"commands": ["find /etc -exec ls {} \;"]}\n```') == {"commands": [r"find /etc -exec ls {} \;"]}
    assert parse_plan("Use df:\n\n```bash\n# disk usage\ndf -h\n```\nDone.") == {"commands": ["df -h"]}
    assert parse_plan("I can't help with that.") is None
