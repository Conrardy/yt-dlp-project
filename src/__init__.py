"""
YouTube Audio Downloader Package

A comprehensive Python package for downloading high-quality audio from YouTube videos
with metadata extraction and command-line interface.
"""

__version__ = "1.0.0"
__author__ = "YouTube Audio Downloader Project"
__description__ = "Download high-quality audio from YouTube videos with metadata extraction"

# Import main classes for easy access
from .config import Config
from .audio_downloader import AudioDownloader, URLValidator
from .metadata_extractor import MetadataExtractor
from .main import YouTubeAudioDownloaderCLI

# Convenience functions
from .audio_downloader import download_single_video, validate_youtube_url
from .metadata_extractor import extract_video_metadata, save_video_metadata

__all__ = [
    'Config',
    'AudioDownloader',
    'URLValidator', 
    'MetadataExtractor',
    'YouTubeAudioDownloaderCLI',
    'download_single_video',
    'validate_youtube_url',
    'extract_video_metadata',
    'save_video_metadata'
]
