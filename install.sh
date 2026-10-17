#!/usr/bin/env bash
# Smart-Shell installer. Installs with uv (preferred) or pipx.
#   curl -sSL https://raw.githubusercontent.com/Lusan-sapkota/smart-shell/main/install.sh | bash
#   curl -sSL https://raw.githubusercontent.com/Lusan-sapkota/smart-shell/main/install.sh | bash -s -- --uninstall
set -euo pipefail

PACKAGE="smart-shell-cli"
SOURCE="${SMART_SHELL_SOURCE:-$PACKAGE}"
DATA_DIR="$HOME/.local/share/smart-shell"
DESKTOP_FILE="$HOME/.local/share/applications/smart-shell.desktop"
RC_MARKER="# Smart-Shell completion"

info() { echo -e "\033[0;34m$*\033[0m"; }
ok()   { echo -e "\033[0;32m$*\033[0m"; }
fail() { echo -e "\033[0;31m$*\033[0m" >&2; exit 1; }

remove_rc_lines() {
    for rc in "$HOME/.bashrc" "$HOME/.zshrc"; do
        [ -f "$rc" ] && sed -i "/$RC_MARKER/,+1d" "$rc"
    done
    return 0
}

remove_package() {
    # "smart-shell" is the package name used before v1.1.0.
    for name in "$PACKAGE" smart-shell; do
        if command -v uv &>/dev/null; then uv tool uninstall "$name" &>/dev/null || true; fi
        if command -v pipx &>/dev/null; then pipx uninstall "$name" &>/dev/null || true; fi
    done
}

uninstall() {
    info "Uninstalling Smart-Shell..."
    remove_package
    remove_rc_lines
    rm -f "$DESKTOP_FILE" "$DATA_DIR"/completion.* "$HOME/.bash_completion.d/smart-shell-completion.bash"
    ok "Smart-Shell removed."
    echo "Your config and history are kept. Delete them with:"
    echo "  rm -rf ~/.config/smart-shell $DATA_DIR"
}

install_package() {
    # Inside a checkout, install that checkout instead of the published source.
    local src="$SOURCE"
    if [ -f pyproject.toml ] && grep -q "name = \"$PACKAGE\"" pyproject.toml; then src="."; fi

    remove_package
    if command -v uv &>/dev/null; then
        info "Installing $PACKAGE with uv from $src..."
        uv tool install --force "$src"
        uv tool update-shell &>/dev/null || true
        BIN="$(uv tool dir --bin)/smart-shell"
    elif command -v pipx &>/dev/null; then
        info "Installing $PACKAGE with pipx from $src..."
        pipx install --force "$src"
        pipx ensurepath &>/dev/null || true
        BIN="${PIPX_BIN_DIR:-$HOME/.local/bin}/smart-shell"
    else
        fail "Smart-Shell needs uv or pipx. Install uv (https://docs.astral.sh/uv/) or pipx, then rerun this script."
    fi
    "$BIN" version &>/dev/null || fail "Installed, but '$BIN version' failed."
    ok "Installed $BIN"
}

install_completion() {
    mkdir -p "$DATA_DIR"
    remove_rc_lines
    for shell in bash zsh; do
        _SMART_SHELL_COMPLETE="${shell}_source" "$BIN" > "$DATA_DIR/completion.$shell"
        rc="$HOME/.${shell}rc"
        if [ "$shell" = bash ] || [ -f "$rc" ]; then
            printf '%s\n[ -f %s ] && source %s\n' "$RC_MARKER" "$DATA_DIR/completion.$shell" "$DATA_DIR/completion.$shell" >> "$rc"
        fi
    done
    ok "Tab completion added for bash$([ -f "$HOME/.zshrc" ] && echo " and zsh")."
}

install_desktop_entry() {
    mkdir -p "$(dirname "$DESKTOP_FILE")"
    cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Name=Smart-Shell
Comment=Natural language to shell commands
Exec=$BIN
Icon=utilities-terminal
Terminal=true
Type=Application
Categories=Utility;
EOF
    ok "Desktop entry added."
}

if [ "${1:-}" = "--uninstall" ]; then
    uninstall
    exit 0
fi

install_package
install_completion
install_desktop_entry

# Under `curl | bash` stdin is the script, so read the wizard's answers from the terminal.
if [ -r /dev/tty ] && [ -t 1 ]; then
    "$BIN" setup < /dev/tty || echo "Run 'smart-shell setup' later to pick a provider."
else
    echo "Run 'smart-shell setup' to pick a provider."
fi
ok "Done. Open a new terminal (or source your shell rc) and run: smart-shell"
