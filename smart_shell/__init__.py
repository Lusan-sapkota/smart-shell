"""
Smart-Shell - An intelligent terminal assistant that converts natural language into executable Bash/Zsh commands.
"""

__version__ = "1.0.0"
__author__ = "Lusan Sapkota"

# Make key modules available at package level
from .main import main
from .setup_logic import setup_config
from .config import load_config, save_config
