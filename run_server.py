#!/usr/bin/env python3
"""
FastAPI server entry point for YouTube Audio Downloader.

This script starts the uvicorn ASGI server hosting the YouTube Audio Downloader
web application. It provides a convenient way to run the development server
with auto-reload enabled.

Features:
    - Auto-reload on code changes (development mode)
    - Binds to all network interfaces (0.0.0.0)
    - Runs on port 8000 by default
    - INFO level logging for request tracking

Usage:
    Run directly from the command line:
    
    $ python run_server.py
    
    Then open http://localhost:8000 in your browser.

Alternative:
    For more control over server options, use uvicorn directly:
    
    $ uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
    
Production:
    For production deployments, consider:
    - Disabling reload (remove reload=True)
    - Using a process manager like gunicorn
    - Adding SSL/TLS termination via a reverse proxy
    - Setting appropriate worker counts

Note:
    This script modifies sys.path to include the src directory,
    allowing imports to work correctly regardless of the working directory.
"""

import uvicorn
import sys
from pathlib import Path

# Add src directory to path for proper module imports
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def main():
    """
    Start the uvicorn development server.
    
    Configures and runs the FastAPI application with development-friendly
    settings including auto-reload and verbose logging.
    """
    uvicorn.run(
        "api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable auto-reload for development
        log_level="info"
    )


if __name__ == "__main__":
    main()
