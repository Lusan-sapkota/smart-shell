"""
UI Module - The interactive prompt: input line, status bar, / command completion and history.
"""

import os
import sys

from prompt_toolkit import PromptSession
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style

COMMANDS = {
    "/help": "show commands and safety levels",
    "/model": "switch model, e.g. /model qwen2.5-coder:3b",
    "/models": "list models from the provider",
    "/explain": "explain a command, e.g. /explain tar -xzf a.tgz",
    "/mode": "ask, auto or plan (Shift+Tab cycles)",
    "/history": "show recent commands",
    "/last": "show the last generated command",
    "/redo": "run the last plan again",
    "/errors": "show the error log",
    "/clear": "clear the screen",
    "/forget-sudo": "drop cached sudo credentials",
    "/update": "check for a new version",
    "/docs": "show the documentation link",
    "/exit": "quit Smart-Shell",
}

MODES = {
    "ask": "every plan asks yes / no / edit",
    "auto": "safe plans run without asking; risky ones still ask",
    "plan": "show plans only, run nothing",
}

STYLE = Style.from_dict({
    "mode-ask": "fg:ansicyan bold",
    "mode-auto": "fg:ansiyellow bold",
    "mode-plan": "fg:ansimagenta bold",
    "prompt": "ansicyan bold",
    "bottom-toolbar": "noreverse bg:default fg:ansibrightblack",
    "bottom-toolbar.key": "fg:ansicyan",
})


class SlashCompleter(Completer):
    """Completes / commands, and model names after /model."""

    def __init__(self, list_models):
        self.list_models = list_models
        self.models = None

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor
        if not text.startswith("/"):
            return
        if text.startswith("/mode "):
            word = text[len("/mode "):]
            for mode, meta in MODES.items():
                if mode.startswith(word):
                    yield Completion(mode, start_position=-len(word), display_meta=meta)
            return
        if text.startswith("/model "):
            if self.models is None:
                try:
                    self.models = self.list_models()
                except Exception:
                    self.models = []
            word = text[len("/model "):]
            for name in self.models:
                if name.startswith(word):
                    yield Completion(name, start_position=-len(word))
            return
        for name, meta in COMMANDS.items():
            if name.startswith(text):
                yield Completion(name, start_position=-len(text), display_meta=meta)


def make_reader(history_file, list_models, status, cycle_mode):
    """Return read() -> str; raises EOFError on Ctrl+D. status() gives the status bar, Shift+Tab calls cycle_mode()."""
    if not sys.stdin.isatty():
        # Piped input (scripts, tests): plain input() without the UI.
        return lambda: input("> ")

    bindings = KeyBindings()

    @bindings.add("s-tab", eager=True)
    def _(event):
        cycle_mode()
        event.app.invalidate()

    @bindings.add("escape", "enter")
    def _(event):
        event.current_buffer.insert_text("\n")

    session = PromptSession(
        history=FileHistory(history_file),
        completer=SlashCompleter(list_models),
        complete_while_typing=True,
        key_bindings=bindings,
        style=STYLE,
        bottom_toolbar=lambda: HTML(status()),
        prompt_continuation="  ",
    )

    def read():
        width = os.get_terminal_size().columns if sys.stdout.isatty() else 80
        print("\033[90m" + "─" * width + "\033[0m")
        while True:
            try:
                return session.prompt([("class:prompt", "> ")])
            except KeyboardInterrupt:
                # Ctrl+C clears the line, like other CLIs; Ctrl+D or /exit quits.
                continue

    return read
