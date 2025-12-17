"""
Pydantic models for API request/response schemas.
"""

from pydantic import BaseModel, HttpUrl
from typing import Optional, Dict, Any
from datetime import datetime


class DownloadRequest(BaseModel):
    """Request model for download endpoint."""
    url: str


class VideoInfo(BaseModel):
    """Response model for video information."""
    title: str
    uploader: str
    duration: Optional[str] = None
    duration_formatted: Optional[str] = None
    thumbnail: Optional[str] = None
    video_id: Optional[str] = None
    upload_date: Optional[str] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    description: Optional[str] = None
    tags: Optional[list] = None
    webpage_url: Optional[str] = None
    estimated_file_size: Optional[str] = None


class DownloadResponse(BaseModel):
    """Response model for download initiation."""
    task_id: str
    message: str
    url: str


class ProgressUpdate(BaseModel):
    """Model for progress updates via SSE."""
    task_id: str
    status: str  # 'downloading', 'finished', 'error'
    percentage: Optional[float] = None
    downloaded: Optional[str] = None
    total: Optional[str] = None
    speed: Optional[str] = None
    filename: Optional[str] = None
    message: Optional[str] = None


class HistoryEntry(BaseModel):
    """Model for download history entry."""
    id: int
    url: str
    title: str
    filename: str
    download_date: datetime
    duration: Optional[str] = None
    uploader: Optional[str] = None
    file_size: Optional[int] = None


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None
