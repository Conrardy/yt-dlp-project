"""
API module for YouTube Audio Downloader.

This module provides a FastAPI-based web interface for the YouTube Audio Downloader,
including REST API endpoints for downloading audio, extracting metadata, and
managing download history.

Modules:
    app: FastAPI application entry point and configuration
    routes: API endpoint definitions and handlers
    models: Pydantic schemas for request/response validation
    database: SQLite database operations for download history

Example:
    To start the API server:
    
    >>> from src.api.app import app
    >>> import uvicorn
    >>> uvicorn.run(app, host="0.0.0.0", port=8000)

API Endpoints:
    GET  /           - Main web interface
    GET  /api/info   - Get video metadata without downloading
    POST /api/download - Start audio download (returns task_id)
    GET  /api/progress/{task_id} - SSE stream for download progress
    GET  /api/history - Get download history
    GET  /api/downloads/{filename} - Download a file
    GET  /api/stats   - Get download statistics
"""

from .app import app
from .database import Database, get_database
from .models import (
    DownloadRequest,
    DownloadResponse,
    VideoInfo,
    ProgressUpdate,
    HistoryEntry,
    ErrorResponse,
)

__all__ = [
    "app",
    "Database",
    "get_database",
    "DownloadRequest",
    "DownloadResponse",
    "VideoInfo",
    "ProgressUpdate",
    "HistoryEntry",
    "ErrorResponse",
]
