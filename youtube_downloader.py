#!/usr/bin/env python3
"""
YouTube Audio Downloader - Main Entry Point

Entry point script for the YouTube Audio Downloader CLI application.
This script can be run directly or used as a module.
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from src.main import main

if __name__ == "__main__":
    sys.exit(main())
