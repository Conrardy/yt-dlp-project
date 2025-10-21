"""
Audio Downloader module for YouTube Audio Downloader.

This module handles the downloading and conversion of audio from YouTube videos
using yt-dlp with progress tracking and error handling.
"""

import re
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Callable, List
from urllib.parse import urlparse, parse_qs
import yt_dlp
try:
    from .config import Config
except ImportError:
    from config import Config


class DownloadError(Exception):
    """Custom exception for download errors."""
    pass


class URLValidator:
    """Utility class for validating YouTube URLs."""
    
    # YouTube URL patterns
    YOUTUBE_PATTERNS = [
        r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtu\.be/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'(?:https?://)?(?:m\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
    ]
    
    @classmethod
    def is_valid_youtube_url(cls, url: str) -> bool:
        """
        Check if URL is a valid YouTube video URL.
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid YouTube URL, False otherwise
        """
        if not url or not isinstance(url, str):
            return False
            
        for pattern in cls.YOUTUBE_PATTERNS:
            if re.match(pattern, url.strip()):
                return True
        return False
    
    @classmethod
    def extract_video_id(cls, url: str) -> Optional[str]:
        """
        Extract video ID from YouTube URL.
        
        Args:
            url: YouTube URL
            
        Returns:
            Video ID if found, None otherwise
        """
        for pattern in cls.YOUTUBE_PATTERNS:
            match = re.match(pattern, url.strip())
            if match:
                return match.group(1)
        return None
    
    @classmethod
    def normalize_url(cls, url: str) -> str:
        """
        Normalize YouTube URL to standard format.
        
        Args:
            url: YouTube URL to normalize
            
        Returns:
            Normalized YouTube URL
        """
        video_id = cls.extract_video_id(url)
        if video_id:
            return f"https://www.youtube.com/watch?v={video_id}"
        return url


class ProgressTracker:
    """Progress tracking for downloads."""
    
    def __init__(self, callback: Optional[Callable] = None):
        """
        Initialize progress tracker.
        
        Args:
            callback: Optional callback function for progress updates
        """
        self.callback = callback
        self.logger = logging.getLogger(__name__)
        self._current_video = None
        
    def hook(self, d: Dict[str, Any]) -> None:
        """
        Progress hook for yt-dlp.
        
        Args:
            d: Progress dictionary from yt-dlp
        """
        try:
            if d['status'] == 'downloading':
                self._handle_downloading(d)
            elif d['status'] == 'finished':
                self._handle_finished(d)
            elif d['status'] == 'error':
                self._handle_error(d)
        except Exception as e:
            self.logger.error(f"Error in progress hook: {e}")
    
    def _handle_downloading(self, d: Dict[str, Any]) -> None:
        """Handle downloading status."""
        filename = d.get('filename', 'Unknown')
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
        downloaded_bytes = d.get('downloaded_bytes', 0)
        speed = d.get('speed', 0)
        
        if total_bytes > 0:
            percentage = (downloaded_bytes / total_bytes) * 100
            speed_str = self._format_bytes(speed) + '/s' if speed else 'Unknown'
            
            progress_info = {
                'status': 'downloading',
                'filename': Path(filename).name,
                'percentage': percentage,
                'downloaded': self._format_bytes(downloaded_bytes),
                'total': self._format_bytes(total_bytes),
                'speed': speed_str
            }
            
            self.logger.info(f"Downloading: {percentage:.1f}% - {speed_str}")
            
            if self.callback:
                self.callback(progress_info)
    
    def _handle_finished(self, d: Dict[str, Any]) -> None:
        """Handle finished status."""
        filename = d.get('filename', 'Unknown')
        
        progress_info = {
            'status': 'finished',
            'filename': Path(filename).name
        }
        
        self.logger.info(f"Download completed: {Path(filename).name}")
        
        if self.callback:
            self.callback(progress_info)
    
    def _handle_error(self, d: Dict[str, Any]) -> None:
        """Handle error status."""
        self.logger.error("Download error occurred")
        
        if self.callback:
            self.callback({'status': 'error', 'message': 'Download failed'})
    
    @staticmethod
    def _format_bytes(bytes_count: int) -> str:
        """Format bytes to human readable format."""
        if not bytes_count:
            return "0 B"
            
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.1f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.1f} TB"


class AudioDownloader:
    """Main audio downloader class."""
    
    def __init__(self, config: Optional[Config] = None, progress_callback: Optional[Callable] = None):
        """
        Initialize AudioDownloader.
        
        Args:
            config: Configuration instance
            progress_callback: Optional callback for progress updates
        """
        self.config = config or Config()
        self.logger = logging.getLogger(__name__)
        self.progress_tracker = ProgressTracker(progress_callback)
        
        # Setup logging
        self._setup_logging()
        
        # Validate configuration
        if not self.config.validate():
            raise ValueError("Invalid configuration provided")
    
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        log_file = self.config.paths.logs_dir / self.config.logging.log_filename
        
        # Configure logger
        self.logger.setLevel(logging.DEBUG)
        
        # File handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, self.config.logging.file_level))
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, self.config.logging.console_level))
        
        # Formatter
        formatter = logging.Formatter(
            self.config.logging.log_format,
            self.config.logging.date_format
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers if not already added (avoid duplicates)
        handler_names = [type(h).__name__ for h in self.logger.handlers]
        if 'FileHandler' not in handler_names:
            self.logger.addHandler(file_handler)
        if 'StreamHandler' not in handler_names:
            self.logger.addHandler(console_handler)
    
    def download_audio(self, url: str, output_filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Download audio from YouTube URL.
        
        Args:
            url: YouTube video URL
            output_filename: Optional custom output filename
            
        Returns:
            Dictionary with download results
            
        Raises:
            DownloadError: If download fails
        """
        # Validate URL
        if not URLValidator.is_valid_youtube_url(url):
            raise DownloadError(f"Invalid YouTube URL: {url}")
        
        # Normalize URL
        normalized_url = URLValidator.normalize_url(url)
        self.logger.info(f"Starting download for: {normalized_url}")
        
        try:
            # Get YT-DLP options
            ydl_opts = self._get_ydl_options(output_filename)
            
            # Add progress hook
            ydl_opts['progress_hooks'] = [self.progress_tracker.hook]
            
            # Download
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info first
                info = ydl.extract_info(normalized_url, download=False)
                
                # Log video info
                self.logger.info(f"Video title: {info.get('title', 'Unknown')}")
                self.logger.info(f"Duration: {info.get('duration', 'Unknown')} seconds")
                self.logger.info(f"Uploader: {info.get('uploader', 'Unknown')}")
                
                # Download the video
                ydl.download([normalized_url])
                
                # Prepare result
                result = {
                    'success': True,
                    'url': normalized_url,
                    'title': info.get('title'),
                    'duration': info.get('duration'),
                    'uploader': info.get('uploader'),
                    'output_dir': str(self.config.paths.downloads_dir),
                    'filename': self._get_output_filename(info, output_filename)
                }
                
                self.logger.info("Download completed successfully")
                return result
                
        except yt_dlp.DownloadError as e:
            error_msg = f"YT-DLP download error: {str(e)}"
            self.logger.error(error_msg)
            raise DownloadError(error_msg) from e
            
        except Exception as e:
            error_msg = f"Unexpected error during download: {str(e)}"
            self.logger.error(error_msg)
            raise DownloadError(error_msg) from e
    
    def download_batch(self, urls: List[str], stop_on_error: bool = False) -> List[Dict[str, Any]]:
        """
        Download multiple videos.
        
        Args:
            urls: List of YouTube URLs
            stop_on_error: Whether to stop on first error
            
        Returns:
            List of download results
        """
        results = []
        
        for i, url in enumerate(urls, 1):
            self.logger.info(f"Processing video {i}/{len(urls)}: {url}")
            
            try:
                result = self.download_audio(url)
                results.append(result)
                
            except DownloadError as e:
                error_result = {
                    'success': False,
                    'url': url,
                    'error': str(e)
                }
                results.append(error_result)
                
                if stop_on_error:
                    self.logger.error("Stopping batch download due to error")
                    break
                else:
                    self.logger.warning(f"Continuing batch download after error: {e}")
        
        self.logger.info(f"Batch download completed. {len([r for r in results if r.get('success')])} successful, {len([r for r in results if not r.get('success')])} failed")
        return results
    
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """
        Get video information without downloading.
        
        Args:
            url: YouTube video URL
            
        Returns:
            Video information dictionary
        """
        if not URLValidator.is_valid_youtube_url(url):
            raise DownloadError(f"Invalid YouTube URL: {url}")
        
        normalized_url = URLValidator.normalize_url(url)
        
        try:
            ydl_opts = {'quiet': True}
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(normalized_url, download=False)
                
                return {
                    'title': info.get('title'),
                    'duration': info.get('duration'),
                    'uploader': info.get('uploader'),
                    'upload_date': info.get('upload_date'),
                    'view_count': info.get('view_count'),
                    'like_count': info.get('like_count'),
                    'description': info.get('description'),
                    'tags': info.get('tags', []),
                    'thumbnail': info.get('thumbnail'),
                    'webpage_url': info.get('webpage_url')
                }
                
        except Exception as e:
            raise DownloadError(f"Error extracting video info: {str(e)}") from e
    
    def _get_ydl_options(self, output_filename: Optional[str] = None) -> Dict[str, Any]:
        """Get YT-DLP options with custom filename if provided."""
        ydl_opts = self.config.get_ydl_opts().copy()
        
        if output_filename:
            # Use custom filename
            output_path = self.config.paths.downloads_dir / f"{output_filename}.%(ext)s"
            ydl_opts['outtmpl'] = str(output_path)
        
        return ydl_opts
    
    def _get_output_filename(self, info: Dict[str, Any], custom_filename: Optional[str] = None) -> str:
        """Get the expected output filename."""
        if custom_filename:
            return f"{custom_filename}.mp3"
        
        # Clean title for filename
        title = info.get('title', 'Unknown')
        # Remove invalid filename characters
        cleaned_title = re.sub(r'[<>:"/\\|?*]', '_', title)
        return f"{cleaned_title}.mp3"


# Utility functions for standalone usage
def download_single_video(url: str, 
                         config: Optional[Config] = None,
                         progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
    """
    Download a single video (convenience function).
    
    Args:
        url: YouTube video URL
        config: Optional configuration
        progress_callback: Optional progress callback
        
    Returns:
        Download result dictionary
    """
    downloader = AudioDownloader(config, progress_callback)
    return downloader.download_audio(url)


def validate_youtube_url(url: str) -> bool:
    """
    Validate YouTube URL (convenience function).
    
    Args:
        url: URL to validate
        
    Returns:
        True if valid YouTube URL
    """
    return URLValidator.is_valid_youtube_url(url)


if __name__ == "__main__":
    # Demo usage
    def progress_callback(info):
        if info['status'] == 'downloading':
            print(f"Progress: {info['percentage']:.1f}% - {info['speed']}")
        elif info['status'] == 'finished':
            print(f"Finished: {info['filename']}")
    
    # Test URL validation
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ",
        "invalid_url"
    ]
    
    print("URL Validation Tests:")
    for url in test_urls:
        is_valid = validate_youtube_url(url)
        print(f"  {url}: {'✅' if is_valid else '❌'}")
    
    print(f"\nAudioDownloader module loaded successfully!")
    print(f"Configuration: {Config()}")
