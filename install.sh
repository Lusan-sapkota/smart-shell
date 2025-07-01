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
        echo -e "  Installing pipx..."
        
        # Try to install pipx
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y pipx
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y pipx
        elif command -v yum &> /dev/null; then
            python3 -m pip install --user pipx
        elif command -v pacman &> /dev/null; then
            sudo pacman -S --noconfirm python-pipx
        else
            echo -e "  Installing pipx with pip..."
            python3 -m pip install --user pipx
        fi
        
        # Ensure pipx is in PATH
        python3 -m pipx ensurepath
        
        # Check if pipx was installed successfully
        if command -v pipx &> /dev/null; then
            echo -e "${GREEN}✓ pipx installed successfully${NC}"
            
            # Try to add pipx to PATH for current session
            export PATH="$HOME/.local/bin:$PATH"
        else
            echo -e "${RED}Failed to install pipx. Please install it manually:${NC}"
            echo -e "  python3 -m pip install --user pipx"
            echo -e "  python3 -m pipx ensurepath"
            exit 1
        fi
    fi
}

# Function to handle GitHub cloning or use current directory
setup_source_directory() {
    # Check for broken or conflicting smart-shell executables before cloning
    if [[ -f "$HOME/.local/bin/smart-shell" && ! -L "$HOME/.local/bin/smart-shell" ]]; then
        echo -e "${RED}WARNING: A non-symlinked smart-shell executable already exists at $HOME/.local/bin/smart-shell.${NC}"
        echo -e "This can cause pipx to fail or Smart-Shell to not run correctly."
        echo -e "Removing it automatically..."
        rm "$HOME/.local/bin/smart-shell"
        echo -e "${GREEN}✓ Removed conflicting executable${NC}"
    fi

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
        
        # First ensure the dependencies are installed
        echo -e "${BLUE}Ensuring dependencies are installed...${NC}"
        python3 -m pip install --user --upgrade google-genai toml rich click pyyaml requests google-api-core || true
        
        pipx install . --force || {
            echo -e "${RED}pipx install failed. Please check your environment or see the FAQ.${NC}"
            echo -e "${RED}This may be due to a previous broken or conflicting install, or a pipx environment issue.${NC}"
            echo -e "${YELLOW}Attempting to fix automatically...${NC}"
            pipx uninstall smart-shell || true
            cd "$PWD"
            
            # Try to install with dependencies explicitly included
            pipx install . --force --include-deps && echo -e "${GREEN}Automatic fix succeeded. Continuing...${NC}" && return 0
            
            echo -e "${RED}Automatic fix failed. Please try the manual steps below:${NC}"
            echo -e "  1. Uninstall any broken install: ${YELLOW}pipx uninstall smart-shell${NC}"
            echo -e "  2. Install dependencies: ${YELLOW}pip install google-genai rich click pyyaml requests toml google-api-core${NC}"
            echo -e "  3. Clone the repo manually: ${YELLOW}git clone https://github.com/Lusan-sapkota/smart-shell.git && cd smart-shell${NC}"
            echo -e "  4. Install from the repo: ${YELLOW}pipx install . --include-deps${NC}"
            echo -e "  5. Then run: ${YELLOW}smart-shell setup${NC}"
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
                echo -e "${RED}Failed to create virtual environment. Is python3-venv installed?${NC}"
                exit 1
            }
            echo -e "\n${BLUE}Installing Smart-Shell in virtual environment...${NC}"
            ./venv/bin/pip install -e . || {
                echo -e "${RED}Failed to install in virtual environment.${NC}"
                exit 1
            }
            install_path="$(pwd)/venv/bin/smart-shell"
            echo -e "${GREEN}✓ Smart-Shell installed in virtual environment at ${install_path}${NC}"
            echo -e "\nTo activate this environment, run:"
            echo -e "  source venv/bin/activate"
            ;;
        *)
            echo -e "${RED}Invalid installation option.${NC}"
            exit 1
            ;;
    esac

    INSTALL_PATH="$install_path"
}

# Function to apply Python module path fix
apply_python_path_fix() {
    echo -e "\n${BLUE}Applying Python module path fix...${NC}"
    # Check if the smart-shell script already exists (it should if pipx installed it)
    if [[ -f "$HOME/.local/bin/smart-shell" ]]; then
        # Create a backup
        cp "$HOME/.local/bin/smart-shell" "$HOME/.local/bin/smart-shell.bak"
        
        # Write a custom wrapper script
        cat > "$HOME/.local/bin/smart-shell" << 'EOF'
#!/usr/bin/env python3
import sys
import os
import importlib.util
import subprocess

# Try to import smart_shell
try:
    import smart_shell
    from smart_shell.main import main
    
    # If import succeeds, run the main function
    if __name__ == '__main__':
        sys.exit(main())
        
except ModuleNotFoundError:
    # If smart_shell module is not found, try to find its location
    print("Smart-Shell module not found in Python path. Attempting to fix...")
    
    # Try to find smart_shell package in pipx environment
    pipx_path = os.path.expanduser("~/.local/share/pipx/venvs/smart-shell")
    if os.path.exists(pipx_path):
        # Get the Python version in the pipx environment
        py_versions = [d for d in os.listdir(os.path.join(pipx_path, 'lib')) if d.startswith('python')]
        if py_versions:
            py_version = py_versions[0]
            site_packages = os.path.join(pipx_path, 'lib', py_version, 'site-packages')
            
            if os.path.exists(os.path.join(site_packages, 'smart_shell')):
                # Add site-packages to Python path
                sys.path.insert(0, site_packages)
                
                try:
                    # Try importing again
                    import smart_shell
                    from smart_shell.main import main
                    
                    print("Fixed! Running Smart-Shell...")
                    if __name__ == '__main__':
                        sys.exit(main())
                except Exception as e:
                    print(f"Failed to import smart_shell after path fix: {e}")
            else:
                print(f"smart_shell package not found in {site_packages}")
        else:
            print(f"No Python version found in {pipx_path}/lib")
    
    # If all else fails, try running pip install with dependencies
    print("Attempting to reinstall Smart-Shell with dependencies...")
    try:
        # First install dependencies
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "google-genai", "rich", "click", "pyyaml", "requests", "google-api-core"], check=True)
        # Then install smart-shell
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "smart-shell"], check=True)
        print("Reinstallation complete. Please try running 'smart-shell' again.")
    except Exception as e:
        print(f"Failed to reinstall: {e}")
        print("Please run manually: pip install google-genai rich click pyyaml toml requests google-api-core smart-shell toml")
        
    sys.exit(1)
EOF
        
        # Make it executable
        chmod +x "$HOME/.local/bin/smart-shell"
        echo -e "${GREEN}✓ Applied Python module path fix${NC}"
    fi
}

# Function to check if installation is working
verify_installation() {
    echo -e "\n${BLUE}Verifying installation...${NC}"
    
    # Check if smart-shell is in PATH
    if command -v smart-shell &> /dev/null; then
        echo -e "${GREEN}✓ smart-shell command is available in PATH${NC}"
        
        # Try running smart-shell version
        if smart-shell version &> /dev/null; then
            echo -e "${GREEN}✓ Smart-Shell command runs successfully${NC}"
        else
            echo -e "${YELLOW}⚠ Smart-Shell command failed to run${NC}"
        fi
    else
        echo -e "${RED}✗ smart-shell command not found in PATH${NC}"
        echo -e "Try running: ${YELLOW}source ~/.bashrc${NC} or ${YELLOW}source ~/.zshrc${NC}"
    fi
    
    # Check if python module is importable
    if python3 -c "import smart_shell" &> /dev/null; then
        echo -e "${GREEN}✓ Python module 'smart_shell' is importable${NC}"
    else
        echo -e "${RED}✗ Python module 'smart_shell' is not importable${NC}"
        echo -e "This might be due to a problem with your Python path or the installation."
    fi
}

# Function to run setup automatically
run_smart_shell_setup() {
    echo -e "\n${BLUE}Running Smart-Shell setup...${NC}"
    
    # Skip if we're in non-interactive mode
    if [[ "$NON_INTERACTIVE" == "true" ]]; then
        echo -e "${YELLOW}Skipping setup in non-interactive mode.${NC}"
        echo -e "Run 'smart-shell setup' to configure your API key later."
        return
    fi
    
    # Check if smart-shell command is available
    if command -v smart-shell &> /dev/null; then
        echo -e "${GREEN}Starting setup wizard...${NC}"
        echo -e "${YELLOW}You'll be asked to enter your Google AI API key.${NC}"
        echo -e "${YELLOW}If you don't have one, get it from: https://ai.google.dev/tutorials/setup${NC}"
        echo -e "(It's free to sign up and includes generous free quota)"
        echo
        
        # Run the setup command
        smart-shell setup || {
            echo -e "${YELLOW}Setup wizard exited. You can run it later with 'smart-shell setup'${NC}"
        }
    else
        echo -e "${YELLOW}Cannot run setup wizard yet. Please run 'smart-shell setup' after installation completes.${NC}"
    fi
}

# Check dependencies
check_dependencies

# Set up source directory (clone repo or use current directory)
setup_source_directory

# Determine if we're running in non-interactive mode
if [[ -t 0 ]]; then
    NON_INTERACTIVE="false"
else
    NON_INTERACTIVE="true"
    echo -e "Running in non-interactive mode. Defaulting to user installation."
fi

# Prompt for installation method if in interactive mode
if [[ "$NON_INTERACTIVE" == "false" ]]; then
    echo -e "\nPlease select installation method:"
    echo -e "1) System-wide installation (requires sudo)"
    echo -e "2) User installation (recommended)"
    echo -e "3) Virtual environment (for development)"
    
    read -p "Enter your choice [2]: " INSTALL_OPTION
    
    # Default to user installation if no input
    INSTALL_OPTION=${INSTALL_OPTION:-2}
else
    # Default to user installation in non-interactive mode
    INSTALL_OPTION=2
    echo -e "Running in non-interactive mode. Defaulting to user installation."
fi

# Install Smart-Shell
install_smart_shell "$INSTALL_OPTION"

# Create desktop entry
create_desktop_entry "$INSTALL_PATH"

# Set up command completion
create_bash_completion

# Apply Python module path fix
apply_python_path_fix

# Verify installation
verify_installation

# Run setup automatically after successful installation
run_smart_shell_setup

# Final success message
echo -e "\n${GREEN}✓ Smart-Shell installation complete!${NC}"
echo -e "To get started, run: smart-shell"

echo -e "\n=============================================="
echo -e "${GREEN}Smart-Shell has been installed successfully!${NC}"
echo -e "=============================================="
echo -e "\nYou can now use it by typing: smart-shell"
echo -e "\nTo activate tab completion, either:"
echo -e "  1. Start a new terminal session, or"
echo -e "  2. Run: source ~/.bashrc"
echo -e "\nTo run in interactive mode:"
echo -e "  smart-shell"
echo -e "\n${YELLOW}Enjoy using Smart-Shell!${NC}"