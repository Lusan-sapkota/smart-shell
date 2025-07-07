# Uninstall Smart-Shell

This guide provides detailed instructions for completely removing Smart-Shell from your system.

## Quick Uninstall (Recommended)

The fastest way to uninstall Smart-Shell is using our automated uninstall script:

```bash
curl -sSL https://raw.githubusercontent.com/Lusan-sapkota/smart-shell/main/install.sh | bash -s -- --uninstall
```

This command will:

- ✅ Automatically detect your installation method
- ✅ Remove the Smart-Shell package from your system
- ✅ Clean up all configuration files
- ✅ Remove desktop entries and shell completions
- ✅ Clean up shell configuration files
- ✅ Remove any remaining executables

## Manual Uninstall

If you prefer to uninstall manually or need more control over the process, follow these step-by-step instructions:

### Step 1: Remove the Smart-Shell Package

Choose the method that matches how you originally installed Smart-Shell:

#### For pipx Installation (Recommended)

```bash
pipx uninstall smart-shell
```

#### For System-wide Installation

```bash
sudo pip3 uninstall smart-shell
```

#### For Virtual Environment Installation

```bash
# Navigate to your project directory and remove the virtual environment
rm -rf ./venv
```

### Step 2: Remove Configuration Files

Smart-Shell stores its configuration in your home directory. Remove the configuration directory:

```bash
rm -rf ~/.config/smart-shell
```

This will remove:

- API key configuration
- Model preferences
- Stored sudo password (encrypted)
- Web search settings
- Command history
- Other user preferences

### Step 3: Remove Desktop Integration

Remove the desktop entry that allows launching Smart-Shell from your application menu:

```bash
rm -f ~/.local/share/applications/smart-shell.desktop
```

### Step 4: Remove Shell Completion

Remove the bash completion script:

```bash
rm -f ~/.local/share/bash-completion/completions/smart-shell-completion.bash
```

### Step 5: Clean Up Shell Configuration

Remove Smart-Shell entries from your shell configuration files:

#### For Bash users

```bash
sed -i '/# Smart-Shell completion/,+1d' ~/.bashrc
```

#### For Zsh users

```bash
sed -i '/# Smart-Shell completion/,+1d' ~/.zshrc
```

#### Manual removal (alternative)

If the `sed` commands don't work, you can manually edit your shell configuration files and remove these lines:

```bash
# Smart-Shell completion
[ -f ~/.local/share/bash-completion/completions/smart-shell-completion.bash ] && source ~/.local/share/bash-completion/completions/smart-shell-completion.bash
```

### Step 6: Remove Executables and Backups

Remove any remaining Smart-Shell executables and backup files:

```bash
rm -f ~/.local/bin/smart-shell
rm -f ~/.local/bin/smart-shell.bak
```

### Step 7: Clean Up pipx Environment (pipx users only)

If you used pipx to install Smart-Shell, you may want to clean up the pipx virtual environment:

```bash
# Remove the pipx virtual environment directory
rm -rf ~/.local/share/pipx/venvs/smart-shell
```

## Verification

After completing the uninstall process, verify that Smart-Shell has been completely removed:

### Check if the command is still available

```bash
which smart-shell
```

This should return no output if Smart-Shell was successfully uninstalled.

### Check for remaining files

```bash
# Check for configuration files
ls -la ~/.config/smart-shell

# Check for desktop entries
ls -la ~/.local/share/applications/smart-shell*

# Check for completion scripts
ls -la ~/.local/share/bash-completion/completions/smart-shell*

# Check for executables
ls -la ~/.local/bin/smart-shell*
```

All of these commands should return "No such file or directory" if the uninstall was successful.

## Restart Your Terminal

After completing the uninstall process, restart your terminal or reload your shell configuration:

```bash
# For bash
source ~/.bashrc

# For zsh
source ~/.zshrc
```

## Troubleshooting

### Smart-Shell command still available after uninstall

If the `smart-shell` command is still available after uninstall, check:

1. **Multiple installation methods**: You might have installed Smart-Shell using multiple methods (pip, pipx, system-wide). Check and remove all installations.

2. **PATH issues**: The executable might still be in your PATH. Check:

   ```bash
   echo $PATH | tr ':' '\n' | xargs -I {} find {} -name "smart-shell*" 2>/dev/null
   ```

3. **System-wide installation**: If you installed system-wide, you might need to check:

   ```bash
   sudo find /usr -name "smart-shell*" 2>/dev/null
   sudo find /opt -name "smart-shell*" 2>/dev/null
   ```

### Permission errors

If you encounter permission errors during uninstall:

1. Use `sudo` for system-wide installations
2. Ensure you have write permissions to your home directory
3. Check if files are owned by a different user:

   ```bash
   ls -la ~/.config/smart-shell
   ls -la ~/.local/bin/smart-shell*
   ```

### Configuration files not removed

If configuration files persist:

```bash
# Force remove with verbose output
rm -rfv ~/.config/smart-shell
```

## Reinstallation

If you want to reinstall Smart-Shell after uninstalling, you can use the quick installation command:

```bash
curl -sSL https://raw.githubusercontent.com/Lusan-sapkota/smart-shell/main/install.sh | bash
```

For more installation options, see the [Installation Guide](installation.md).

## Support

If you encounter issues during uninstallation or have questions:

- Check the [FAQ](faq.md) for common issues
- Visit our [GitHub Issues](https://github.com/Lusan-sapkota/smart-shell/issues)
- See the [Contributing Guide](contributing.md) for community support

## Feedback

We're sorry to see you go! If you have feedback about Smart-Shell or suggestions for improvement, please:

- Open an issue on [GitHub](https://github.com/Lusan-sapkota/smart-shell/issues)
- Share your thoughts in our discussions
- Help us improve by contributing to the project

Thank you for trying Smart-Shell!