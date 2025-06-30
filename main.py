"""
Main entry point for the Smart-Shell application.
"""
import sys
from pathlib import Path

# Add the package directory to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from smart_shell.main import main

if __name__ == "__main__":
    main() 