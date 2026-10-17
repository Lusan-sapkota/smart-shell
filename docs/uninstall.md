# Uninstall

## 1. Remove the package

Use the method you installed with:

```bash
uv tool uninstall smart-shell     # uv
pipx uninstall smart-shell        # pipx
sudo pip3 uninstall smart-shell   # system-wide
rm -rf ./venv                     # virtual environment, from the project directory
```

## 2. Remove config, history and logs

```bash
rm -rf ~/.config/smart-shell ~/.local/share/smart-shell
```

This deletes your provider settings and API key, command history and the error log.

## 3. Remove desktop entry and completion

```bash
rm -f ~/.local/share/applications/smart-shell.desktop
rm -f ~/.bash_completion.d/smart-shell-completion.bash
```

## 4. Clean up shell config

The installer adds two lines to `~/.bashrc` (and `~/.zshrc` if present):

```bash
# Smart-Shell completion
[ -f ~/.bash_completion.d/smart-shell-completion.bash ] && source ~/.bash_completion.d/smart-shell-completion.bash
```

Remove them by hand or with:

```bash
sed -i '/# Smart-Shell completion/,+1d' ~/.bashrc
sed -i '/# Smart-Shell completion/,+1d' ~/.zshrc
```

Then open a new terminal.

## Verify

```bash
which smart-shell   # should print nothing
```

If it still prints a path, you may have installed more than once (for example both pipx and system-wide). Remove each install, and check `~/.local/bin/smart-shell`.

To reinstall later, see [Installation](installation.md).
