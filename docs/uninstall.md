# Uninstall

## With the installer

```bash
curl -sSL https://raw.githubusercontent.com/Lusan-sapkota/smart-shell/main/install.sh | bash -s -- --uninstall
```

This removes the package (uv or pipx), tab completion, its lines in `~/.bashrc` / `~/.zshrc` and the desktop entry. Your config and history are kept; delete them as in step 2 below.

## By hand

### 1. Remove the package

```bash
uv tool uninstall smart-shell-cli     # uv
pipx uninstall smart-shell-cli        # pipx
```

Versions before 1.1.0 were installed under the name `smart-shell`; use that name for older installs.

### 2. Remove config, history and logs

```bash
rm -rf ~/.config/smart-shell ~/.local/share/smart-shell
```

This deletes your provider settings and API key, command history and the error log.

### 3. Remove desktop entry and completion

```bash
rm -f ~/.local/share/applications/smart-shell.desktop
rm -f ~/.local/share/smart-shell/completion.*
rm -f ~/.bash_completion.d/smart-shell-completion.bash   # from versions before 1.1.0
```

### 4. Clean up shell config

The installer adds two lines starting with `# Smart-Shell completion` to `~/.bashrc` (and `~/.zshrc` if present). Remove them by hand or with:

```bash
sed -i '/# Smart-Shell completion/,+1d' ~/.bashrc
sed -i '/# Smart-Shell completion/,+1d' ~/.zshrc
```

Then open a new terminal.

### Verify

```bash
which smart-shell   # should print nothing
```

If it still prints a path, you may have installed more than once (for example with both uv and pipx, or under the old `smart-shell` name). Remove each install, and check `~/.local/bin/smart-shell`.

To reinstall later, see [Installation](installation.md).
