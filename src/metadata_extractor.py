"""
Metadata Extractor module for YouTube Audio Downloader.

This module handles extraction and storage of metadata from YouTube videos,
including video information, technical audio details, and custom formatting.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import yt_dlp
try:
    from .config import Config
    from .audio_downloader import URLValidator
except ImportError:
    from config import Config
    from audio_downloader import URLValidator


class MetadataError(Exception):
    """Custom exception for metadata extraction errors."""
    pass


class MetadataTemplate:
    """Template system for metadata formatting."""
    
    DEFAULT_TEMPLATE = {
        "video_info": {
            "id": "%(id)s",
            "title": "%(title)s",
            "uploader": "%(uploader)s",
            "upload_date": "%(upload_date)s",
            "duration": "%(duration)s",
            "view_count": "%(view_count)s",
            "like_count": "%(like_count)s",
            "description": "%(description)s",
            "tags": "%(tags)s",
            "webpage_url": "%(webpage_url)s",
            "thumbnail": "%(thumbnail)s"
        },
        "technical_info": {
            "original_format": "%(format)s",
            "original_ext": "%(ext)s",
            "filesize": "%(filesize)s",
            "fps": "%(fps)s",
            "vcodec": "%(vcodec)s",
            "acodec": "%(acodec)s",
            "format_note": "%(format_note)s"
        },
        "download_info": {
            "extracted_at": None,  # Will be filled automatically
            "download_date": None,  # Will be filled automatically
            "output_format": "mp3",
            "quality": "320kbps",
            "downloader_version": "yt-dlp"
        }
    }
    
    @classmethod
    def apply_template(cls, template: Dict[str, Any], info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply template to video information.
        
        Args:
            template: Template dictionary
            info: Video information from yt-dlp
            
        Returns:
            Formatted metadata dictionary
        """
        result = {}
        
        for section, fields in template.items():
            result[section] = {}
            
            for key, template_value in fields.items():
                if template_value is None:
                    # Handle special automatic fields
                    if key == "extracted_at":
                        result[section][key] = datetime.now().isoformat()
                    elif key == "download_date":
                        result[section][key] = datetime.now().strftime("%Y-%m-%d")
                    else:
                        result[section][key] = None
                elif isinstance(template_value, str) and template_value.startswith("%(") and template_value.endswith(")s"):
                    # Extract field name from template
                    field_name = template_value[2:-2]
                    result[section][key] = info.get(field_name)
                else:
                    result[section][key] = template_value
        
        return result


class MetadataExtractor:
    """Main metadata extraction class."""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize MetadataExtractor.
        
        Args:
            config: Configuration instance
        """
        self.config = config or Config()
        self.logger = logging.getLogger(__name__)
        
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
    
    def extract_metadata(self, url: str, 
                        template: Optional[Dict[str, Any]] = None,
                        include_technical: bool = True) -> Dict[str, Any]:
        """
        Extract metadata from YouTube video.
        
        Args:
            url: YouTube video URL
            template: Optional custom metadata template
            include_technical: Whether to include technical information
            
        Returns:
            Extracted metadata dictionary
            
        Raises:
            MetadataError: If extraction fails
        """
        # Validate URL
        if not URLValidator.is_valid_youtube_url(url):
            raise MetadataError(f"Invalid YouTube URL: {url}")
        
        # Normalize URL
        normalized_url = URLValidator.normalize_url(url)
        self.logger.info(f"Extracting metadata for: {normalized_url}")
        
        try:
            # Configure yt-dlp for metadata extraction
            ydl_opts = {
                'quiet': True,
                'no_warnings': False,
                'extract_flat': False,
                'writeinfojson': False,
                'writethumbnail': False,
            }
            
            # Extract information
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(normalized_url, download=False)
            
            # Use provided template or default
            template_to_use = template or MetadataTemplate.DEFAULT_TEMPLATE
            
            # Apply template
            metadata = MetadataTemplate.apply_template(template_to_use, info)
            
            # Add additional processing
            metadata = self._post_process_metadata(metadata, info, include_technical)
            
            self.logger.info(f"Successfully extracted metadata for: {metadata.get('video_info', {}).get('title', 'Unknown')}")
            return metadata
            
        except yt_dlp.DownloadError as e:
            error_msg = f"YT-DLP extraction error: {str(e)}"
            self.logger.error(error_msg)
            raise MetadataError(error_msg) from e
            
        except Exception as e:
            error_msg = f"Unexpected error during metadata extraction: {str(e)}"
            self.logger.error(error_msg)
            raise MetadataError(error_msg) from e
    
    def _post_process_metadata(self, metadata: Dict[str, Any], 
                              raw_info: Dict[str, Any],
                              include_technical: bool) -> Dict[str, Any]:
        """
        Post-process extracted metadata.
        
        Args:
            metadata: Template-processed metadata
            raw_info: Raw information from yt-dlp
            include_technical: Whether to include technical info
            
        Returns:
            Post-processed metadata
        """
        # Format duration
        if metadata.get("video_info", {}).get("duration"):
            duration_seconds = metadata["video_info"]["duration"]
            if isinstance(duration_seconds, (int, float)):
                metadata["video_info"]["duration_formatted"] = self._format_duration(duration_seconds)
        
        # Format file size
        if include_technical and metadata.get("technical_info", {}).get("filesize"):
            filesize = metadata["technical_info"]["filesize"]
            if isinstance(filesize, (int, float)):
                metadata["technical_info"]["filesize_formatted"] = self._format_filesize(filesize)
        
        # Process tags (convert to list if string)
        tags = metadata.get("video_info", {}).get("tags")
        if isinstance(tags, str):
            metadata["video_info"]["tags"] = tags.split(", ") if tags else []
        elif not isinstance(tags, list):
            metadata["video_info"]["tags"] = []
        
        # Add computed fields
        metadata["computed"] = {
            "video_id": URLValidator.extract_video_id(raw_info.get('webpage_url', '')),
            "has_description": bool(metadata.get("video_info", {}).get("description")),
            "has_tags": len(metadata.get("video_info", {}).get("tags", [])) > 0,
            "estimated_file_size": self._estimate_mp3_size(raw_info.get('duration', 0)),
            "duration_formatted": metadata.get("video_info", {}).get("duration_formatted"),
            "metadata_version": "1.0"
        }
        
        return metadata
    
    def save_metadata(self, metadata: Dict[str, Any], 
                     output_file: Optional[Path] = None,
                     video_id: Optional[str] = None) -> Path:
        """
        Save metadata to JSON file.
        
        Args:
            metadata: Metadata dictionary to save
            output_file: Optional custom output file path
            video_id: Optional video ID for filename
            
        Returns:
            Path to saved metadata file
        """
        # Determine output file
        if output_file:
            metadata_file = output_file
        else:
            # Generate filename from video info
            title = metadata.get("video_info", {}).get("title", "Unknown")
            video_id = video_id or metadata.get("computed", {}).get("video_id", "unknown")
            
            # Clean filename
            safe_title = self._sanitize_filename(title)
            filename = f"{safe_title}_{video_id}.json"
            metadata_file = self.config.paths.metadata_dir / filename
        
        # Ensure directory exists
        metadata_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Save metadata with pretty formatting
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False, default=str)
            
            self.logger.info(f"Metadata saved to: {metadata_file}")
            return metadata_file
            
        except Exception as e:
            error_msg = f"Error saving metadata: {str(e)}"
            self.logger.error(error_msg)
            raise MetadataError(error_msg) from e
    
    def load_metadata(self, metadata_file: Path) -> Dict[str, Any]:
        """
        Load metadata from JSON file.
        
        Args:
            metadata_file: Path to metadata file
            
        Returns:
            Loaded metadata dictionary
        """
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            self.logger.info(f"Metadata loaded from: {metadata_file}")
            return metadata
            
        except FileNotFoundError:
            raise MetadataError(f"Metadata file not found: {metadata_file}")
        except json.JSONDecodeError as e:
            raise MetadataError(f"Invalid JSON in metadata file: {e}")
        except Exception as e:
            raise MetadataError(f"Error loading metadata: {str(e)}")
    
    def extract_and_save(self, url: str, 
                        output_file: Optional[Path] = None,
                        template: Optional[Dict[str, Any]] = None) -> tuple[Dict[str, Any], Path]:
        """
        Extract metadata and save to file in one operation.
        
        Args:
            url: YouTube video URL
            output_file: Optional output file path
            template: Optional metadata template
            
        Returns:
            Tuple of (metadata, file_path)
        """
        metadata = self.extract_metadata(url, template)
        file_path = self.save_metadata(metadata, output_file)
        return metadata, file_path
    
    def batch_extract(self, urls: List[str], 
                     stop_on_error: bool = False) -> List[Dict[str, Any]]:
        """
        Extract metadata for multiple URLs.
        
        Args:
            urls: List of YouTube URLs
            stop_on_error: Whether to stop on first error
            
        Returns:
            List of results (metadata or error info)
        """
        results = []
        
        for i, url in enumerate(urls, 1):
            self.logger.info(f"Processing metadata {i}/{len(urls)}: {url}")
            
            try:
                metadata, file_path = self.extract_and_save(url)
                
                result = {
                    'success': True,
                    'url': url,
                    'metadata': metadata,
                    'file_path': str(file_path)
                }
                results.append(result)
                
            except MetadataError as e:
                error_result = {
                    'success': False,
                    'url': url,
                    'error': str(e)
                }
                results.append(error_result)
                
                if stop_on_error:
                    self.logger.error("Stopping batch extraction due to error")
                    break
                else:
                    self.logger.warning(f"Continuing batch extraction after error: {e}")
        
        successful = len([r for r in results if r.get('success')])
        failed = len([r for r in results if not r.get('success')])
        self.logger.info(f"Batch metadata extraction completed. {successful} successful, {failed} failed")
        
        return results
    
    @staticmethod
    def _format_duration(seconds: float) -> str:
        """Format duration in seconds to HH:MM:SS."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int(seconds % 60)
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    @staticmethod
    def _format_filesize(bytes_count: int) -> str:
        """Format file size in bytes to human readable format."""
        if not bytes_count:
            return "0 B"
            
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_count < 1024.0:
                return f"{bytes_count:.1f} {unit}"
            bytes_count /= 1024.0
        return f"{bytes_count:.1f} TB"
    
    @staticmethod
    def _estimate_mp3_size(duration_seconds: float) -> str:
        """Estimate MP3 file size for 320kbps."""
        if not duration_seconds:
            return "Unknown"
        
        # 320 kbps = 40 KB/s
        estimated_bytes = duration_seconds * 40 * 1024
        return MetadataExtractor._format_filesize(int(estimated_bytes))
    
    @staticmethod
    def _sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe file system usage."""
        import re
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Limit length
        return filename[:100] if len(filename) > 100 else filename


# Utility functions for standalone usage
def extract_video_metadata(url: str, 
                          config: Optional[Config] = None) -> Dict[str, Any]:
    """
    Extract metadata from a single video (convenience function).
    
    Args:
        url: YouTube video URL
        config: Optional configuration
        
    Returns:
        Metadata dictionary
    """
    extractor = MetadataExtractor(config)
    return extractor.extract_metadata(url)


def save_video_metadata(url: str, 
                       output_file: Optional[Path] = None,
                       config: Optional[Config] = None) -> tuple[Dict[str, Any], Path]:
    """
    Extract and save metadata for a single video (convenience function).
    
    Args:
        url: YouTube video URL
        output_file: Optional output file
        config: Optional configuration
        
    Returns:
        Tuple of (metadata, file_path)
    """
    extractor = MetadataExtractor(config)
    return extractor.extract_and_save(url, output_file)


if __name__ == "__main__":
    # Demo usage
    print("MetadataExtractor module loaded successfully!")
    
    # Test with sample URLs
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ"
    ]
    
    print("URL validation tests:")
    for url in test_urls:
        is_valid = URLValidator.is_valid_youtube_url(url)
        print(f"  {url}: {'✅' if is_valid else '❌'}")
    
    print(f"\nConfiguration: {Config()}")
    print("Ready for metadata extraction!")
