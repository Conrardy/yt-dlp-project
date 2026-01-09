"""
Pydantic models for API request/response schemas.

This module defines the data models used for API request validation and
response serialization. All models use Pydantic v2 for automatic
validation, serialization, and OpenAPI documentation generation.

Models:
    DownloadRequest: Request body for initiating a download
    VideoInfo: Detailed video metadata response
    DownloadResponse: Response after starting a download task
    ProgressUpdate: Real-time download progress data
    HistoryEntry: Download history record
    ErrorResponse: Standardized error response format

Example:
    Using models in API endpoints:
    
    >>> @app.post("/download", response_model=DownloadResponse)
    >>> async def download(request: DownloadRequest):
    ...     # Pydantic automatically validates the request body
    ...     url = request.url
    ...     return DownloadResponse(task_id="abc123", message="Started", url=url)
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DownloadRequest(BaseModel):
    """
    Request model for initiating a YouTube audio download.
    
    Attributes:
        url: A valid YouTube video URL. Supports various formats including:
             - https://www.youtube.com/watch?v=VIDEO_ID
             - https://youtu.be/VIDEO_ID
             - https://m.youtube.com/watch?v=VIDEO_ID
    
    Example:
        >>> request = DownloadRequest(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    """
    url: str = Field(..., description="YouTube video URL to download audio from")


class VideoInfo(BaseModel):
    """
    Response model containing detailed video metadata.
    
    This model represents the metadata extracted from a YouTube video
    without downloading the actual content.
    
    Attributes:
        title: The video title as displayed on YouTube
        uploader: Channel name or uploader username
        duration: Raw duration in seconds (as string)
        duration_formatted: Human-readable duration (e.g., "03:45" or "01:23:45")
        thumbnail: URL to the video thumbnail image
        video_id: 11-character YouTube video identifier
        upload_date: Upload date in YYYYMMDD format
        view_count: Total number of views
        like_count: Number of likes on the video
        description: Full video description text
        tags: List of tags associated with the video
        webpage_url: Canonical YouTube URL for the video
        estimated_file_size: Estimated MP3 file size (e.g., "8.5 MB")
    """
    title: str = Field(..., description="Video title")
    uploader: str = Field(..., description="Channel or uploader name")
    duration: Optional[str] = Field(None, description="Duration in seconds")
    duration_formatted: Optional[str] = Field(None, description="Formatted duration (MM:SS or HH:MM:SS)")
    thumbnail: Optional[str] = Field(None, description="Thumbnail image URL")
    video_id: Optional[str] = Field(None, description="11-character YouTube video ID")
    upload_date: Optional[str] = Field(None, description="Upload date (YYYYMMDD)")
    view_count: Optional[int] = Field(None, description="Total view count")
    like_count: Optional[int] = Field(None, description="Total like count")
    description: Optional[str] = Field(None, description="Video description")
    tags: Optional[List[str]] = Field(None, description="Video tags")
    webpage_url: Optional[str] = Field(None, description="Canonical YouTube URL")
    estimated_file_size: Optional[str] = Field(None, description="Estimated MP3 file size")


class DownloadResponse(BaseModel):
    """
    Response model returned when a download task is initiated.
    
    The task_id can be used to track download progress via the
    /api/progress/{task_id} SSE endpoint.
    
    Attributes:
        task_id: UUID string identifying the download task
        message: Human-readable status message
        url: The URL that was requested for download
    
    Example:
        >>> response = DownloadResponse(
        ...     task_id="550e8400-e29b-41d4-a716-446655440000",
        ...     message="Download started",
        ...     url="https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        ... )
    """
    task_id: str = Field(..., description="Unique identifier for tracking the download task")
    message: str = Field(..., description="Status message")
    url: str = Field(..., description="The YouTube URL being downloaded")


class ProgressUpdate(BaseModel):
    """
    Model for real-time download progress updates via Server-Sent Events (SSE).
    
    This model is sent periodically to connected clients during an active
    download, providing real-time feedback on download progress.
    
    Attributes:
        task_id: UUID of the download task
        status: Current status - one of 'pending', 'downloading', 'finished', 'error'
        percentage: Download completion percentage (0-100)
        downloaded: Human-readable downloaded size (e.g., "5.2 MB")
        total: Human-readable total size (e.g., "10.5 MB")
        speed: Current download speed (e.g., "1.2 MB/s")
        filename: Name of the file being downloaded
        message: Status message or error description
    """
    task_id: str = Field(..., description="Task identifier")
    status: str = Field(..., description="Download status: pending, downloading, finished, error")
    percentage: Optional[float] = Field(None, ge=0, le=100, description="Download progress (0-100)")
    downloaded: Optional[str] = Field(None, description="Downloaded size (human-readable)")
    total: Optional[str] = Field(None, description="Total size (human-readable)")
    speed: Optional[str] = Field(None, description="Download speed (human-readable)")
    filename: Optional[str] = Field(None, description="Output filename")
    message: Optional[str] = Field(None, description="Status message or error details")


class HistoryEntry(BaseModel):
    """
    Model representing a download history record from the database.
    
    Each successful download is recorded in the SQLite database and
    can be retrieved via the /api/history endpoint.
    
    Attributes:
        id: Auto-incrementing database primary key
        url: Original YouTube URL that was downloaded
        title: Video title at the time of download
        filename: Name of the saved MP3 file
        download_date: Timestamp when the download completed
        duration: Video duration in formatted form
        uploader: Channel name or uploader
        file_size: Size of the downloaded file in bytes
    """
    id: int = Field(..., description="Database record ID")
    url: str = Field(..., description="YouTube video URL")
    title: str = Field(..., description="Video title")
    filename: str = Field(..., description="Downloaded MP3 filename")
    download_date: datetime = Field(..., description="Download completion timestamp")
    duration: Optional[str] = Field(None, description="Video duration (formatted)")
    uploader: Optional[str] = Field(None, description="Channel or uploader name")
    file_size: Optional[int] = Field(None, description="File size in bytes")


class ErrorResponse(BaseModel):
    """
    Standardized error response model for API error handling.
    
    This model provides a consistent error format across all API endpoints,
    making it easier for clients to handle errors programmatically.
    
    Attributes:
        error: Brief error type or message
        detail: Detailed error description with additional context
    
    Example:
        >>> error = ErrorResponse(
        ...     error="Invalid URL",
        ...     detail="The provided URL is not a valid YouTube video URL"
        ... )
    """
    error: str = Field(..., description="Error type or brief message")
    detail: Optional[str] = Field(None, description="Detailed error description")
