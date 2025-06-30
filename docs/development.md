# Development

For developers and contributors. See the full [Development Guide](DEVELOPMENT.md) for details.

## Manual Installation

- Clone the repo:
  ```bash
  git clone https://github.com/Lusan-sapkota/smart-shell.git
  cd smart-shell
  ```
- Set up a virtual environment:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  pip install -e .
  ```
- Set your API key:
  ```bash
  export SMART_SHELL_API_KEY=your-api-key-here
  ```

## Contributing

- Please read [CONTRIBUTING](contributing.md) for guidelines.
- Issues and PRs are welcome!

## Project Structure

- `smart_shell/`: Main source code
- `docs/`: Documentation
- `examples/`: Usage examples
- `install.sh`: Installer script
- `requirements.txt`, `pyproject.toml`: Dependencies

See [API Reference](api.md) for code-level documentation.
