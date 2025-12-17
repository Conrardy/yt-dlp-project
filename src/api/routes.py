"""
API routes for YouTube Audio Downloader.
"""

import uuid
import asyncio
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from sse_starlette.sse import EventSourceResponse
import json

try:
    from ..config import Config
    from ..audio_downloader import AudioDownloader, URLValidator
    from ..metadata_extractor import MetadataExtractor
except ImportError:
    from config import Config
    from audio_downloader import AudioDownloader, URLValidator
    from metadata_extractor import MetadataExtractor

from .models import (
    DownloadRequest, VideoInfo, DownloadResponse, 
    ProgressUpdate, HistoryEntry, ErrorResponse
)
from .database import get_database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["api"])

# In-memory task storage for progress tracking
tasks: Dict[str, Dict[str, Any]] = {}
config = Config()
downloader = AudioDownloader(config)
metadata_extractor = MetadataExtractor(config)
db = get_database()


def progress_callback_wrapper(task_id: str):
    """Create a progress callback for a specific task."""
    def callback(info: Dict[str, Any]):
        tasks[task_id].update({
            'status': info.get('status', 'downloading'),
            'percentage': info.get('percentage', 0),
            'downloaded': info.get('downloaded', ''),
            'total': info.get('total', ''),
            'speed': info.get('speed', ''),
            'filename': info.get('filename', ''),
            'message': info.get('message', '')
        })
    return callback


async def download_task(task_id: str, url: str):
    """
    Background task for downloading audio.
    
    Args:
        task_id: Unique task identifier
        url: YouTube URL to download
    """
    try:
        tasks[task_id]['status'] = 'downloading'
        tasks[task_id]['message'] = 'Starting download...'
        
        # Create downloader with progress callback
        progress_callback = progress_callback_wrapper(task_id)
        task_downloader = AudioDownloader(config, progress_callback)
        
        # Download audio
        result = task_downloader.download_audio(url)
        
        if result['success']:
            # Extract metadata for history and save to file
            metadata = None
            try:
                metadata = metadata_extractor.extract_metadata(url)
                video_info = metadata.get('video_info', {})
                computed = metadata.get('computed', {})
                
                # Save metadata to JSON file
                try:
                    metadata_file = metadata_extractor.save_metadata(metadata)
                    logger.info(f"Metadata saved to: {metadata_file}")
                except Exception as e:
                    logger.warning(f"Could not save metadata file: {e}")
                    # Continue even if metadata file save fails
                    
            except Exception as e:
                logger.warning(f"Could not extract metadata: {e}")
                video_info = {}
                computed = {}
            
            # Get file size - find the actual downloaded file
            # yt-dlp might modify the filename (e.g., add numbers if file exists)
            expected_filename = result.get('filename', '')
            file_path = config.paths.downloads_dir / expected_filename
            
            # If expected file doesn't exist, find the most recent MP3 file
            if not file_path.exists():
                mp3_files = list(config.paths.downloads_dir.glob("*.mp3"))
                if mp3_files:
                    # Sort by modification time, get most recent
                    file_path = max(mp3_files, key=lambda p: p.stat().st_mtime)
                    expected_filename = file_path.name
                    logger.info(f"Found downloaded file: {expected_filename}")
            
            file_size = file_path.stat().st_size if file_path.exists() else None
            
            # Add to history
            await db.add_download(
                url=url,
                title=result.get('title', 'Unknown'),
                filename=expected_filename,
                duration=computed.get('duration_formatted'),
                uploader=result.get('uploader'),
                file_size=file_size,
                video_id=computed.get('video_id')
            )
            
            tasks[task_id].update({
                'status': 'finished',
                'message': 'Download completed successfully',
                'filename': expected_filename,
                'result': result
            })
        else:
            tasks[task_id].update({
                'status': 'error',
                'message': result.get('error', 'Download failed'),
                'error': result.get('error')
            })
            
    except Exception as e:
        logger.error(f"Download task error: {e}")
        tasks[task_id].update({
            'status': 'error',
            'message': f'Error: {str(e)}',
            'error': str(e)
        })


@router.get("/info", response_model=VideoInfo)
async def get_video_info(url: str = Query(..., description="YouTube video URL")):
    """
    Get video information without downloading.
    
    Args:
        url: YouTube video URL
        
    Returns:
        Video information
    """
    if not URLValidator.is_valid_youtube_url(url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    
    try:
        metadata = metadata_extractor.extract_metadata(url)
        video_info = metadata.get('video_info', {})
        computed = metadata.get('computed', {})
        
        return VideoInfo(
            title=video_info.get('title', 'Unknown'),
            uploader=video_info.get('uploader', 'Unknown'),
            duration=str(video_info.get('duration', '')),
            duration_formatted=computed.get('duration_formatted'),
            thumbnail=video_info.get('thumbnail'),
            video_id=computed.get('video_id'),
            upload_date=video_info.get('upload_date'),
            view_count=video_info.get('view_count'),
            like_count=video_info.get('like_count'),
            description=video_info.get('description'),
            tags=video_info.get('tags', []),
            webpage_url=video_info.get('webpage_url'),
            estimated_file_size=computed.get('estimated_file_size')
        )
    except Exception as e:
        logger.error(f"Error extracting video info: {e}")
        raise HTTPException(status_code=500, detail=f"Error extracting video info: {str(e)}")


@router.post("/download", response_model=DownloadResponse)
async def start_download(
    request: DownloadRequest,
    background_tasks: BackgroundTasks
):
    """
    Start downloading audio from YouTube URL.
    
    Args:
        request: Download request with URL
        background_tasks: FastAPI background tasks
        
    Returns:
        Download response with task_id
    """
    if not URLValidator.is_valid_youtube_url(request.url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")
    
    # Generate task ID
    task_id = str(uuid.uuid4())
    
    # Initialize task
    tasks[task_id] = {
        'task_id': task_id,
        'url': request.url,
        'status': 'pending',
        'percentage': 0,
        'message': 'Task created'
    }
    
    # Start background download
    background_tasks.add_task(download_task, task_id, request.url)
    
    return DownloadResponse(
        task_id=task_id,
        message="Download started",
        url=request.url
    )


@router.get("/progress/{task_id}")
async def get_progress(task_id: str):
    """
    Stream progress updates via Server-Sent Events.
    
    Args:
        task_id: Task identifier
        
    Returns:
        SSE stream of progress updates
    """
    async def event_generator():
        """Generate SSE events for progress updates."""
        last_status = None
        
        while True:
            if task_id not in tasks:
                yield {
                    "event": "error",
                    "data": json.dumps({"error": "Task not found"})
                }
                break
            
            task = tasks[task_id]
            current_status = task.get('status')
            
            # Send update if status changed or periodically
            if current_status != last_status or current_status == 'downloading':
                progress = ProgressUpdate(
                    task_id=task_id,
                    status=task.get('status', 'pending'),
                    percentage=task.get('percentage', 0),
                    downloaded=task.get('downloaded'),
                    total=task.get('total'),
                    speed=task.get('speed'),
                    filename=task.get('filename'),
                    message=task.get('message')
                )
                
                yield {
                    "event": "progress",
                    "data": progress.model_dump_json()
                }
                
                last_status = current_status
                
                # Stop if finished or error
                if current_status in ['finished', 'error']:
                    # Clean up after a delay
                    await asyncio.sleep(2)
                    break
            
            await asyncio.sleep(0.5)  # Update every 500ms
    
    return EventSourceResponse(event_generator())


@router.get("/history")
async def get_history(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    Get download history.
    
    Args:
        limit: Maximum number of records
        offset: Number of records to skip
        
    Returns:
        List of download history entries
    """
    try:
        history = await db.get_history(limit=limit, offset=offset)
        return history
    except Exception as e:
        logger.error(f"Error getting history: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting history: {str(e)}")


@router.get("/downloads/{filename}")
async def download_file(filename: str):
    """
    Download a file from the downloads directory.
    
    Args:
        filename: Name of the file to download
        
    Returns:
        File response
    """
    file_path = config.paths.downloads_dir / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )


@router.get("/stats")
async def get_stats():
    """
    Get download statistics.
    
    Returns:
        Statistics dictionary
    """
    try:
        stats = await db.get_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=f"Error getting stats: {str(e)}")
