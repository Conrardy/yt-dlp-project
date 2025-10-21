"""
Configuration module for YouTube Audio Downloader.

This module contains all configuration settings, default values,
and validation logic for the YouTube Audio Downloader project.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class AudioConfig:
    """Configuration for audio download and conversion settings."""
    
    # Audio quality settings
    quality: str = "320"  # kbps for MP3
    format: str = "mp3"
    codec: str = "mp3"
    
    # Audio extraction options
    extract_audio: bool = True
    audio_format: str = "mp3"
    audio_quality: str = "0"  # 0 = best quality for MP3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert AudioConfig to dictionary."""
        return {
            "quality": self.quality,
            "format": self.format,
            "codec": self.codec,
            "extract_audio": self.extract_audio,
            "audio_format": self.audio_format,
            "audio_quality": self.audio_quality
        }


@dataclass
class PathConfig:
    """Configuration for file paths and directories."""
    
    # Base project directory
    base_dir: Path = field(default_factory=lambda: Path.cwd())
    
    # Output directories
    downloads_dir: Path = field(init=False)
    metadata_dir: Path = field(init=False)
    logs_dir: Path = field(init=False)
    
    def __post_init__(self):
        """Initialize directory paths after dataclass creation."""
        self.downloads_dir = self.base_dir / "downloads"
        self.metadata_dir = self.base_dir / "metadata"
        self.logs_dir = self.base_dir / "logs"
        
        # Create directories if they don't exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all required directories exist."""
        for directory in [self.downloads_dir, self.metadata_dir, self.logs_dir]:
            directory.mkdir(exist_ok=True)
    
    def to_dict(self) -> Dict[str, str]:
        """Convert PathConfig to dictionary with string paths."""
        return {
            "base_dir": str(self.base_dir),
            "downloads_dir": str(self.downloads_dir),
            "metadata_dir": str(self.metadata_dir),
            "logs_dir": str(self.logs_dir)
        }


@dataclass
class YtDlpConfig:
    """Configuration for YT-DLP specific options."""
    
    # Output filename template
    outtmpl: str = "%(title)s.%(ext)s"
    
    # Format selection
    format_selector: str = "bestaudio/best"
    
    # Post-processing options
    postprocessors: list = field(default_factory=lambda: [
        {
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }
    ])
    
    # Download options
    extract_flat: bool = False
    writethumbnail: bool = True
    writeinfojson: bool = True
    writedescription: bool = False
    writesubtitles: bool = False
    writeautomaticsub: bool = False
    
    # Network options
    retries: int = 3
    fragment_retries: int = 3
    socket_timeout: int = 30
    
    # Other options
    ignoreerrors: bool = False
    no_warnings: bool = False
    
    def get_ydl_opts(self, output_dir: Path) -> Dict[str, Any]:
        """Get YT-DLP options dictionary."""
        return {
            'format': self.format_selector,
            'outtmpl': str(output_dir / self.outtmpl),
            'postprocessors': self.postprocessors,
            'extract_flat': self.extract_flat,
            'writethumbnail': self.writethumbnail,
            'writeinfojson': self.writeinfojson,
            'writedescription': self.writedescription,
            'writesubtitles': self.writesubtitles,
            'writeautomaticsub': self.writeautomaticsub,
            'retries': self.retries,
            'fragment_retries': self.fragment_retries,
            'socket_timeout': self.socket_timeout,
            'ignoreerrors': self.ignoreerrors,
            'no_warnings': self.no_warnings,
        }


@dataclass
class LoggingConfig:
    """Configuration for logging settings."""
    
    # Log levels
    console_level: str = "INFO"
    file_level: str = "DEBUG"
    
    # Log format
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format: str = "%Y-%m-%d %H:%M:%S"
    
    # File settings
    log_filename: str = "yt_downloader.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert LoggingConfig to dictionary."""
        return {
            "console_level": self.console_level,
            "file_level": self.file_level,
            "log_format": self.log_format,
            "date_format": self.date_format,
            "log_filename": self.log_filename,
            "max_file_size": self.max_file_size,
            "backup_count": self.backup_count
        }


class Config:
    """Main configuration class that combines all configuration sections."""
    
    def __init__(self, config_file: Optional[Path] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Optional path to configuration file
        """
        self.audio = AudioConfig()
        self.paths = PathConfig()
        self.ytdlp = YtDlpConfig()
        self.logging = LoggingConfig()
        
        # Load configuration from file if provided
        if config_file and config_file.exists():
            self.load_from_file(config_file)
    
    def get_ydl_opts(self) -> Dict[str, Any]:
        """Get complete YT-DLP options with paths configured."""
        return self.ytdlp.get_ydl_opts(self.paths.downloads_dir)
    
    def save_to_file(self, config_file: Path):
        """
        Save current configuration to file.
        
        Args:
            config_file: Path where to save the configuration
        """
        config_data = {
            "audio": self.audio.to_dict(),
            "paths": self.paths.to_dict(),
            "logging": self.logging.to_dict()
        }
        
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
    
    def load_from_file(self, config_file: Path):
        """
        Load configuration from file.
        
        Args:
            config_file: Path to configuration file
        """
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # Update audio config
            if 'audio' in config_data:
                for key, value in config_data['audio'].items():
                    if hasattr(self.audio, key):
                        setattr(self.audio, key, value)
            
            # Update logging config
            if 'logging' in config_data:
                for key, value in config_data['logging'].items():
                    if hasattr(self.logging, key):
                        setattr(self.logging, key, value)
                        
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load configuration file: {e}")
    
    def validate(self) -> bool:
        """
        Validate configuration settings.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        try:
            # Validate audio quality
            if not self.audio.quality.isdigit():
                print("Error: Audio quality must be a number")
                return False
            
            quality_int = int(self.audio.quality)
            if quality_int < 64 or quality_int > 320:
                print("Error: Audio quality must be between 64 and 320 kbps")
                return False
            
            # Validate audio format
            supported_formats = ['mp3', 'wav', 'aac', 'm4a', 'ogg']
            if self.audio.format not in supported_formats:
                print(f"Error: Unsupported audio format. Supported: {supported_formats}")
                return False
            
            # Validate paths exist and are writable
            for directory in [self.paths.downloads_dir, self.paths.metadata_dir, self.paths.logs_dir]:
                if not directory.exists():
                    print(f"Error: Directory does not exist: {directory}")
                    return False
                if not os.access(directory, os.W_OK):
                    print(f"Error: No write permission for directory: {directory}")
                    return False
            
            # Validate logging level
            valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
            if self.logging.console_level not in valid_levels:
                print(f"Error: Invalid console log level. Valid levels: {valid_levels}")
                return False
            if self.logging.file_level not in valid_levels:
                print(f"Error: Invalid file log level. Valid levels: {valid_levels}")
                return False
            
            return True
            
        except Exception as e:
            print(f"Error during validation: {e}")
            return False
    
    def __str__(self) -> str:
        """String representation of the configuration."""
        return f"""
Configuration:
  Audio: {self.audio.format} @ {self.audio.quality}kbps
  Paths: {self.paths.downloads_dir}
  Logging: {self.logging.console_level} (console), {self.logging.file_level} (file)
"""


# Default configuration instance
default_config = Config()


def get_config(config_file: Optional[Path] = None) -> Config:
    """
    Get configuration instance.
    
    Args:
        config_file: Optional path to configuration file
        
    Returns:
        Configuration instance
    """
    if config_file:
        return Config(config_file)
    return default_config


def create_sample_config(output_file: Path):
    """
    Create a sample configuration file.
    
    Args:
        output_file: Path where to create the sample configuration
    """
    sample_config = Config()
    sample_config.save_to_file(output_file)
    print(f"Sample configuration created at: {output_file}")


if __name__ == "__main__":
    # Demo usage
    config = get_config()
    print("Default configuration:")
    print(config)
    
    # Validate configuration
    if config.validate():
        print("✅ Configuration is valid")
    else:
        print("❌ Configuration validation failed")
    
    # Show YT-DLP options
    print("\nYT-DLP Options:")
    import pprint
    pprint.pprint(config.get_ydl_opts())
