#!/usr/bin/env python3
"""
YouTube Audio Downloader - Command Line Interface Entry Point.

This is the main entry point for the YouTube Audio Downloader CLI application.
It provides a command-line interface for downloading high-quality audio from
YouTube videos with support for metadata extraction and batch processing.

Commands:
    download    Download audio from YouTube videos
    info        Extract and display video information
    config      View or create configuration files

Usage Examples:
    Download a single video:
        $ python youtube_downloader.py download "https://www.youtube.com/watch?v=VIDEO_ID"
    
    Download with metadata extraction:
        $ python youtube_downloader.py download "URL" --metadata
    
    Get video information only:
        $ python youtube_downloader.py info "URL"
    
    Download from a file list:
        $ python youtube_downloader.py download --file urls.txt
    
    Show configuration:
        $ python youtube_downloader.py config --show

Options:
    -v, --verbose       Enable verbose output (debug level)
    -q, --quiet         Quiet mode (errors only)
    -c, --config FILE   Use custom configuration file
    -h, --help          Show help message

Exit Codes:
    0   - Success
    1   - Error (invalid URL, download failed, etc.)
    130 - Interrupted by user (Ctrl+C)

Requirements:
    - Python 3.11+
    - yt-dlp
    - FFmpeg (for audio conversion)

Note:
    This script modifies sys.path to include the src directory,
    allowing it to be run from any working directory.

See Also:
    run_server.py - For the web interface alternative
    README.md     - For full documentation
"""

import sys
from pathlib import Path

# Add src directory to Python path for module imports
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from src.main import main

if __name__ == "__main__":
    sys.exit(main())
