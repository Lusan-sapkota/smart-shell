import io

import pytest

from smart_shell import utils


class FakeTTY(io.StringIO):
    def isatty(self):
        return True


@pytest.fixture
def term(monkeypatch):
    launched = []
    monkeypatch.setattr(utils.sys, "platform", "linux")
    monkeypatch.setattr(utils, "load_config", lambda: {})
    monkeypatch.setattr(utils.shutil, "which", lambda name: f"/usr/bin/{name}")
    monkeypatch.setattr(utils.subprocess, "Popen", lambda cmd, **kw: launched.append(cmd))
    monkeypatch.setattr(utils, "_last_input", utils.time.monotonic() - 60)
    for var in ("VTE_VERSION", "TERM_PROGRAM", "WT_SESSION", "SSH_CONNECTION", "WAYLAND_DISPLAY"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("DISPLAY", ":0")

    def env(**values):
        for k, v in values.items():
            monkeypatch.setenv(k, v)
    def tty():
        # pytest swaps sys.stdout after fixtures run, so this is called from the test body.
        out = FakeTTY()
        monkeypatch.setattr(utils.sys, "stdout", out)
        return out
    return tty, launched, env


def test_konsole_gets_a_desktop_notification(term):
    tty, launched, env = term
    out = tty()
    env(KONSOLE_VERSION="251203")
    utils.notify("run ls?")
    assert out.getvalue() == "\a"
    assert launched and launched[0][0] == "notify-send" and launched[0][-1] == "run ls?"


def test_vte_terminal_uses_escape_code_not_notify_send(term):
    tty, launched, env = term
    out = tty()
    env(VTE_VERSION="7800")
    utils.notify("run ls?\a")
    assert "]777;notify;Smart-Shell;run ls?" in out.getvalue() and not launched


def test_no_desktop_notification_right_after_typing_or_over_ssh(term, monkeypatch):
    tty, launched, env = term
    out = tty()
    utils.mark_input()
    utils.notify("x")
    monkeypatch.setattr(utils, "_last_input", 0)
    env(SSH_CONNECTION="1.2.3.4 1 5.6.7.8 22")
    utils.notify("x")
    assert out.getvalue() == "\a\a" and not launched


def test_off_or_not_a_terminal_does_nothing(term, monkeypatch):
    tty, launched, _ = term
    out = tty()
    monkeypatch.setattr(utils, "load_config", lambda: {"notify": False})
    utils.notify("x")
    monkeypatch.setattr(utils, "load_config", lambda: {})
    monkeypatch.setattr(utils.sys, "stdout", io.StringIO())
    utils.notify("x")
    assert out.getvalue() == "" and not launched
