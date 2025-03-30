#!/usr/bin/env python3
# File: aidev_github.py
# Path: AIDEV-GitHub/aidev_github.py
# Standard: AIDEV-PascalCase-1.6
# Created: 2025-03-30
# Last Modified: 2025-03-30  1:00AM
# Description: Main entry point for AIDEV-GitHub

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Import CLI module
from CLI.CommandLineInterface import Main

if __name__ == "__main__":
    sys.exit(Main())