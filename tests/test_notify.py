import io

from smart_shell import utils


class FakeTTY(io.StringIO):
    def isatty(self):
        return True


def test_notify_rings_and_sends_desktop_notification(monkeypatch):
    out = FakeTTY()
    monkeypatch.setattr(utils.sys, "stdout", out)
    monkeypatch.setattr(utils, "load_config", lambda: {})
    utils.notify("run ls?\a")
    text = out.getvalue()
    assert text.startswith("\a") and "]777;notify;Smart-Shell;run ls?" in text and text.count("\a") == 3


def test_notify_respects_off_and_non_tty(monkeypatch):
    out = FakeTTY()
    monkeypatch.setattr(utils.sys, "stdout", out)
    monkeypatch.setattr(utils, "load_config", lambda: {"notify": False})
    utils.notify("x")
    monkeypatch.setattr(utils, "load_config", lambda: {})
    monkeypatch.setattr(utils.sys, "stdout", io.StringIO())
    utils.notify("x")
    assert out.getvalue() == ""
