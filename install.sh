#!/bin/bash
# Smart-Shell Installation Script

set -e  # Exit immediately if a command exits with a non-zero status

# Color codes for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}==============================================${NC}"
echo -e "${GREEN}     Smart-Shell Installation Script        ${NC}"
echo -e "${BLUE}==============================================${NC}"

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

# Main installation function
install_smart_shell() {
    local install_option=$1
    local install_path=""
    
    case $install_option in
        1)
            echo -e "\n${BLUE}Installing Smart-Shell system-wide...${NC}"
            sudo pip3 install -e . || {
                echo -e "${RED}Failed to install system-wide. Trying with --break-system-packages flag...${NC}"
                sudo pip3 install --break-system-packages -e .
            }
            install_path="/usr/local/bin/smart-shell"
            ;;
        2)
            echo -e "\n${BLUE}Installing Smart-Shell for current user...${NC}"
            pip3 install --user -e . || {
                echo -e "${RED}Failed to install for user. Trying with --break-system-packages flag...${NC}"
                pip3 install --user --break-system-packages -e .
            }
            install_path="$HOME/.local/bin/smart-shell"
            # Make sure ~/.local/bin is in PATH
            if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
                echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
                echo -e "${GREEN}✓ Added ~/.local/bin to PATH in .bashrc${NC}"
                # Also add to .zshrc if it exists
                if [ -f "$HOME/.zshrc" ]; then
                    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc"
                    echo -e "${GREEN}✓ Added ~/.local/bin to PATH in .zshrc${NC}"
                fi
            fi
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
            pip3 install -e .
            install_path="$PWD/venv/bin/smart-shell"
            
            # Create activation script
            cat > smart-shell-activate.sh << EOF
#!/bin/bash
source "$PWD/venv/bin/activate"
smart-shell \$@
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
    
    return 0
}

# Main script execution

# Check dependencies
check_dependencies

# Check for virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo -e "\n${YELLOW}No virtual environment detected.${NC}"
    echo -e "${BLUE}Would you like to install Smart-Shell:${NC}"
    echo -e "1) System-wide (requires sudo)"
    echo -e "2) For current user only"
    echo -e "3) In a new virtual environment"
    read -p "Choose an option (1-3): " INSTALL_OPTION
    
    # Install Smart-Shell
    install_smart_shell "$INSTALL_OPTION"
    
    # Create desktop entry for GUI launchers (except for virtual env)
    if [ "$INSTALL_OPTION" == "1" ] || [ "$INSTALL_OPTION" == "2" ]; then
        create_desktop_entry "$INSTALL_PATH"
    fi
else
    echo -e "\n${BLUE}Installing Smart-Shell in current virtual environment...${NC}"
    pip3 install -e .
    INSTALL_PATH="$VIRTUAL_ENV/bin/smart-shell"
fi

# Create bash completion
create_bash_completion

# Final instructions
echo -e "\n${GREEN}==============================================${NC}"
echo -e "${GREEN}Smart-Shell has been installed successfully!${NC}"
echo -e "${GREEN}==============================================${NC}"
echo -e "\n${YELLOW}You can now use it by typing:${NC} smart-shell"
echo -e "\n${YELLOW}To activate tab completion, either:${NC}"
echo -e "  1. Start a new terminal session, or"
echo -e "  2. Run: source ~/.bashrc"
echo -e "\n${YELLOW}To set up your API key, run:${NC}"
echo -e "  smart-shell setup"
echo -e "\n${YELLOW}To run in interactive mode (recommended):${NC}"
echo -e "  smart-shell run --interactive"
echo -e "  or simply: smart-shell"
echo -e "\n${GREEN}Enjoy using Smart-Shell!${NC}" 