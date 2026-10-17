# Development

Notes for contributors working on Smart-Shell itself.

## Setup

Requires Python 3.9 or newer and git.

```bash
git clone https://github.com/Lusan-sapkota/smart-shell.git
cd smart-shell
python3 -m venv venv
source venv/bin/activate
pip install -e . pytest
```

Configure a provider with `smart-shell setup`, or point it at one with environment variables:

```bash
export SMART_SHELL_BASE_URL=http://localhost:11434/v1   # e.g. a local Ollama
export SMART_SHELL_API_KEY=your-api-key                 # if the provider needs one
```

Check that it works without executing anything:

```bash
smart-shell run "list files in current directory" --dry-run
```

## Tests

```bash
pytest -q
```

Tests live in `tests/`. CI (`.github/workflows/test.yml`) runs them on Python 3.9 and 3.13 for pushes to `development` and `main` and for pull requests. Add a test for any new safety rule in `tests/test_safety.py`.

## Project structure

```text
smart_shell/
  main.py           CLI (click) and the interactive REPL
  ai_wrapper.py     requests-based client for OpenAI-compatible APIs, provider presets
  setup_logic.py    `smart-shell setup` wizard
  shell_builder.py  system prompt, plan parsing, banner
  safety.py         command risk classification
  history.py        command history
  updater.py        `!update` (git pull or pip upgrade)
  utils.py          command execution, OS/shell detection, error log
  config.py         load/save ~/.config/smart-shell/config.json
tests/              pytest suite
docs/               this documentation (MkDocs)
install.sh          installer
```

Dependencies are `rich`, `click` and `requests`. Keep `requirements.txt` and `pyproject.toml` in sync if that changes.

## Adding a provider

Any service with an OpenAI-compatible `/models` and `/chat/completions` endpoint already works through the `custom` provider. To add a preset, add an entry to `PROVIDERS` in `smart_shell/ai_wrapper.py`: `name: (base_url, default_model_or_None, needs_api_key)`.

## Safety changes

Patterns live in `smart_shell/safety.py`, grouped by level (blocked, high, medium, info_leak). Don't loosen a rule without a test showing the false positive it fixes. Update [Safety](safety.md) when levels or behavior change.

## Release

1. Bump the version in `pyproject.toml` and `smart_shell/__init__.py`.
2. Add an entry to `docs/CHANGELOG.md`.
3. Run `pytest -q`.
4. Tag the release.

See [Contributing](contributing.md) for the PR workflow and [API Reference](api.md) for the module overview.
