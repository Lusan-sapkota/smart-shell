#!/bin/bash
# Smart-Shell Installation Script

set -e  # Exit immediately if a command exits with a non-zero status

# Color codes for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print banner
print_banner() {
    echo -e "${BLUE}"
    echo "    _____                      _      _____ _          _ _"
    echo "   / ____|                    | |    / ____| |        | | |"
    echo "  | (___  _ __ ___   __ _ _ __| |_  | (___ | |__   ___| | |"
    echo "   \\___ \\| '_ \` _ \\ / _\` | '__| __|  \\___ \\| '_ \\ / _ \\ | |"
    echo "   ____) | | | | | | (_| | |  | |_   ____) | | | |  __/ | |"
    echo "  |_____/|_| |_| |_|\\__,_|_|   \\__| |_____/|_| |_|\\___|_|_|"
    echo -e "${NC}"
    echo -e "${YELLOW}Smart Shell Installation${NC}"
    echo
}

print_banner

# Function to check dependencies
check_dependencies() {
    echo -e "\n${BLUE}Checking dependencies...${NC}"
    
    # Check Python version
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | awk '{print $2}')
        echo -e "${GREEN}✓ Python found:${NC} $PYTHON_VERSION"
    else
        echo -e "${RED}✗ Python 3 not found. Please install Python 3.8 or newer.${NC}"
        exit 1
    fi
    
    # Check pip
    if command -v pip3 &> /dev/null; then
        PIP_VERSION=$(pip3 --version | awk '{print $2}')
        echo -e "${GREEN}✓ pip found:${NC} $PIP_VERSION"
    else
        echo -e "${RED}✗ pip3 is not installed.${NC}"
        echo -e "  Installing pip..."
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y python3-pip
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y python3-pip
        elif command -v yum &> /dev/null; then
            sudo yum install -y python3-pip
        elif command -v pacman &> /dev/null; then
            sudo pacman -S --noconfirm python-pip
        else
            echo -e "${RED}Cannot install pip automatically. Please install pip3 manually.${NC}"
            exit 1
        fi
    fi
    
    # Check for pipx (recommended for PEP 668 systems)
    if command -v pipx &> /dev/null; then
        echo -e "${GREEN}✓ pipx found (recommended for installation)${NC}"
    else
        echo -e "${YELLOW}⚠ pipx not found (recommended for better isolation)${NC}"
        echo -e "\n${YELLOW}TL;DR for Ubuntu/Debian users:${NC}"
        echo -e "  sudo apt install pipx"
        echo -e "  pipx ensurepath"
        echo -e "  source ~/.bashrc   # or ~/.zshrc depending on your shell"
        echo -e "Then re-run the install script."
        echo -e "${RED}pipx is required for user installation on PEP 668 systems. Please install pipx and re-run this script.${NC}"
        exit 1
    fi
}

# Function to handle GitHub cloning or use current directory
setup_source_directory() {
    # Check if we're running from a piped curl command or direct execution
    if [[ ! -f "pyproject.toml" ]]; then
        echo -e "\n${BLUE}Downloading Smart-Shell...${NC}"
        # Create a temporary directory
        TEMP_DIR=$(mktemp -d)
        # Clone the repository
        git clone https://github.com/Lusan-sapkota/smart-shell.git "$TEMP_DIR" || {
            echo -e "${RED}Failed to clone repository. Please check your internet connection.${NC}"
            exit 1
        }
        # Move to the cloned directory
        cd "$TEMP_DIR"
        echo -e "${GREEN}✓ Downloaded Smart-Shell to temporary directory${NC}"
    else
        echo -e "${GREEN}✓ Using current directory as Smart-Shell source${NC}"
    fi
}

# Function to create desktop entry
create_desktop_entry() {
    local install_path=$1
    
    echo -e "\n${BLUE}Creating desktop entry...${NC}"
    DESKTOP_DIR="$HOME/.local/share/applications"
    mkdir -p "$DESKTOP_DIR"
    
    cat > "$DESKTOP_DIR/smart-shell.desktop" << EOF
[Desktop Entry]
Name=Smart-Shell
Comment=AI-powered Bash command assistant
Exec=x-terminal-emulator -e "$install_path"
Icon=terminal
Terminal=true
Type=Application
Categories=Utility;TerminalEmulator;
Keywords=Shell;Terminal;Command;AI;
EOF
    
    echo -e "${GREEN}✓ Desktop entry created at $DESKTOP_DIR/smart-shell.desktop${NC}"
    
    # Update desktop database
    if command -v update-desktop-database &> /dev/null; then
        update-desktop-database "$DESKTOP_DIR"
    fi
}

# Function to create bash completion
create_bash_completion() {
    echo -e "\n${BLUE}Setting up command completion...${NC}"
    COMPLETION_DIR="$HOME/.bash_completion.d"
    mkdir -p "$COMPLETION_DIR"

    cat > "$COMPLETION_DIR/smart-shell-completion.bash" << 'EOF'
_smart_shell_completion() {
    local cur prev opts
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"
    opts="run setup version history --help --dry-run --model --interactive --yes"

    if [[ ${cur} == -* ]] ; then
        COMPREPLY=( $(compgen -W "--help --dry-run --model --interactive --yes" -- ${cur}) )
        return 0
    fi

    case "${prev}" in
        smart-shell)
            COMPREPLY=( $(compgen -W "run setup version history" -- ${cur}) )
            return 0
            ;;
        --model|-m)
            COMPREPLY=( $(compgen -W "gemini-2.5-pro gemini-2.5-flash gemini-2.0-pro" -- ${cur}) )
            return 0
            ;;
        *)
            ;;
    esac

    COMPREPLY=( $(compgen -W "${opts}" -- ${cur}) )
    return 0
}

complete -F _smart_shell_completion smart-shell
EOF

    # Add to .bashrc if not already there
    if ! grep -q "source $COMPLETION_DIR/smart-shell-completion.bash" "$HOME/.bashrc"; then
        echo -e "\n# Smart-Shell completion" >> "$HOME/.bashrc"
        echo "[ -f $COMPLETION_DIR/smart-shell-completion.bash ] && source $COMPLETION_DIR/smart-shell-completion.bash" >> "$HOME/.bashrc"
        echo -e "${GREEN}✓ Added completion to .bashrc${NC}"
    else
        echo -e "${GREEN}✓ Completion already in .bashrc${NC}"
    fi
    
    # Also add to .zshrc if it exists
    if [ -f "$HOME/.zshrc" ]; then
        if ! grep -q "source $COMPLETION_DIR/smart-shell-completion.bash" "$HOME/.zshrc"; then
            echo -e "\n# Smart-Shell completion" >> "$HOME/.zshrc"
            echo "[ -f $COMPLETION_DIR/smart-shell-completion.bash ] && source $COMPLETION_DIR/smart-shell-completion.bash" >> "$HOME/.zshrc"
            echo -e "${GREEN}✓ Added completion to .zshrc${NC}"
        else
            echo -e "${GREEN}✓ Completion already in .zshrc${NC}"
        fi
    fi
}

# Function to install Smart-Shell
install_smart_shell() {
    local install_option=$1
    local install_path=""

    # For user install, require pipx
    if [[ "$install_option" == "2" ]]; then
        if ! command -v pipx &> /dev/null; then
            echo -e "${RED}ERROR: pipx is required for user installation on this system (PEP 668).${NC}"
            echo -e "${YELLOW}Please install pipx with:${NC}"
            echo -e "  sudo apt install pipx   # (Ubuntu/Debian recommended)"
            echo -e "  pipx ensurepath"
            echo -e "  source ~/.bashrc   # or ~/.zshrc depending on your shell"
            echo -e "Then run the following command to install Smart-Shell:${NC}"
            echo -e "  pipx install smart-shell"
            echo -e "Or use the quick install script (recommended):"
            echo -e "  curl -sSL https://raw.githubusercontent.com/Lusan-sapkota/smart-shell/main/install.sh | bash"
            echo -e "Then run: pipx install smart-shell again if prompted."
            echo -e "See the FAQ: https://lusan-sapkota.github.io/smart-shell/faq/#pipx-or-pep668"
            exit 1
        fi
        echo -e "\n${BLUE}Installing with pipx (recommended)...${NC}"
        pipx install . || {
            echo -e "${RED}pipx install failed. Please check your environment or see the FAQ.${NC}"
            exit 1
        }
        if command -v smart-shell &> /dev/null; then
            install_path=$(which smart-shell)
            INSTALL_PATH="$install_path"
            return 0
        fi
    fi

    case $install_option in
        1)
            echo -e "\n${BLUE}Installing Smart-Shell system-wide...${NC}"
            sudo python3 -m pip uninstall -y smart-shell 2>/dev/null || true
            sudo python3 -m pip install --break-system-packages . || {
                echo -e "${RED}Failed to install system-wide.${NC}"
                exit 1
            }
            install_path="/usr/local/bin/smart-shell"
            ;;
        3)
            echo -e "\n${BLUE}Creating a new virtual environment...${NC}"
            python3 -m venv venv || {
                echo -e "${RED}Failed to create virtual environment. Installing venv package...${NC}"
                if command -v apt-get &> /dev/null; then
                    sudo apt-get update && sudo apt-get install -y python3-venv
                elif command -v dnf &> /dev/null; then
                    sudo dnf install -y python3-venv
                elif command -v yum &> /dev/null; then
                    sudo yum install -y python3-venv
                elif command -v pacman &> /dev/null; then
                    sudo pacman -S --noconfirm python-virtualenv
                fi
                python3 -m venv venv
            }
            source venv/bin/activate
            python -m pip install .
            install_path="$PWD/venv/bin/smart-shell"
            # Create activation script
            cat > smart-shell-activate.sh << EOF
#!/bin/bash
source "$PWD/venv/bin/activate"
smart-shell "$@"
EOF
            chmod +x smart-shell-activate.sh
            echo -e "${GREEN}✓ Virtual environment created at $PWD/venv${NC}"
            echo -e "${YELLOW}To use Smart-Shell, either:${NC}"
            echo -e "  1. Activate the environment with: source $PWD/venv/bin/activate"
            echo -e "  2. Or use the wrapper script: ./smart-shell-activate.sh"
            ;;
        *)
            echo -e "${RED}Invalid option. Exiting.${NC}"
            exit 1
            ;;
    esac
    INSTALL_PATH="$install_path"
}

# Function to prompt for API key setup
setup_api_key() {
    echo -e "\n${BLUE}Setting up API key...${NC}"
    echo -e "${YELLOW}Do you want to set up your API key now?${NC} (Recommended)"
    read -p "Set up API key now? (Y/n): " SETUP_API_KEY
    SETUP_API_KEY=${SETUP_API_KEY:-Y}
    
    if [[ "$SETUP_API_KEY" == "Y" || "$SETUP_API_KEY" == "y" ]]; then
        if command -v smart-shell &> /dev/null; then
            smart-shell setup
        else
            echo -e "${YELLOW}Please run 'smart-shell setup' after installation to configure your API key.${NC}"
        fi
    else
        echo -e "${YELLOW}You can set up your API key later by running:${NC}"
        echo -e "  smart-shell setup"
    fi
}

# Function to verify installation
verify_installation() {
    echo -e "\n${BLUE}Verifying installation...${NC}"
    
    # Check if smart-shell is in PATH
    if command -v smart-shell &> /dev/null; then
        echo -e "${GREEN}✓ smart-shell command is available in PATH${NC}"
        
        # Test if we can run the command
        if smart-shell --help &> /dev/null; then
            echo -e "${GREEN}✓ Smart-Shell is working correctly${NC}"
        else
            echo -e "${YELLOW}⚠ Smart-Shell command failed to run${NC}"
        fi
    else
        echo -e "${YELLOW}⚠ smart-shell command not found in PATH. You may need to:${NC}"
        echo -e "  1. Restart your terminal"
        echo -e "  2. Add the installation directory to your PATH"
        echo -e "  3. Use the full path to run smart-shell: $INSTALL_PATH"
    fi
    
    # Check if we can import the module
    if python3 -c "import smart_shell" &> /dev/null; then
        echo -e "${GREEN}✓ Python module 'smart_shell' is importable${NC}"
    else
        echo -e "${YELLOW}⚠ Python cannot import 'smart_shell'${NC}"
    fi
}

# Main installation flow
main() {
    check_dependencies
    setup_source_directory

    if [[ ! -f "pyproject.toml" ]]; then
        echo -e "${RED}Error: pyproject.toml not found. Not in Smart-Shell source directory.${NC}"
        exit 1
    fi
    
    echo -e "\n${YELLOW}Please select installation method:${NC}"
    echo "1) System-wide installation (requires sudo)"
    echo "2) User installation (recommended)"
    echo "3) Virtual environment (for development)"
    
    if [ -t 0 ]; then
        # Interactive mode
        read -p "Enter your choice (1-3): " INSTALL_OPTION
    else
        # Non-interactive mode, default to user installation
        INSTALL_OPTION=2
        echo -e "${YELLOW}Running in non-interactive mode. Defaulting to user installation.${NC}"
    fi
    
    install_smart_shell "$INSTALL_OPTION"
    
    # Verify Python package is importable
    if [[ "$INSTALL_OPTION" == "3" ]]; then
        if ! venv/bin/python -c "import smart_shell" &> /dev/null; then
            echo -e "${RED}ERROR: Python cannot import 'smart_shell' in the virtual environment. Installation may have failed.${NC}"
            echo -e "${YELLOW}For guaranteed success, use pipx for user installs.${NC}"
            exit 1
        fi
    fi
    
    if ! python3 -c "import smart_shell" &> /dev/null; then
        echo -e "${YELLOW}⚠ Python cannot import 'smart_shell' directly. This may be expected in some environments.${NC}"
        echo -e "${YELLOW}For guaranteed success, use pipx for user installs. See: https://lusan-sapkota.github.io/smart-shell/faq/#pipx-or-pep668${NC}"
    fi
    
    # Only create desktop entry for system or user installations
    if [[ "$INSTALL_OPTION" == "1" || "$INSTALL_OPTION" == "2" ]]; then
        create_desktop_entry "$INSTALL_PATH"
        create_bash_completion
    fi
    
    # Setup API key if interactive
    if [ -t 0 ]; then
        setup_api_key
    else
        echo -e "\n${YELLOW}Skipping API key setup in non-interactive mode.${NC}"
        echo -e "Run 'smart-shell setup' to configure your API key later."
    fi
    
    verify_installation

    echo -e "\n${GREEN}✓ Smart-Shell installation complete!${NC}"
    echo -e "${YELLOW}To get started, run:${NC} smart-shell"
    echo -e "\n${RED}IMPORTANT:${NC} Please run 'smart-shell setup' to configure your API key."
}

# Run the main function
main

# Final instructions
echo -e "\n${GREEN}==============================================${NC}"
echo -e "${GREEN}Smart-Shell has been installed successfully!${NC}"
echo -e "${GREEN}==============================================${NC}"
echo -e "\n${YELLOW}You can now use it by typing:${NC} smart-shell"
echo -e "\n${YELLOW}To activate tab completion, either:${NC}"
echo "  1. Start a new terminal session, or"
echo "  2. Run: source ~/.bashrc"
echo -e "\n${YELLOW}To run in interactive mode:${NC}"
echo "  smart-shell"
echo -e "\n${RED}IMPORTANT:${NC} Please run 'smart-shell setup' to configure your API key."
echo -e "\n${YELLOW}Enjoy using Smart-Shell!${NC}"