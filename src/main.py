#!/usr/bin/env python3
"""
YouTube Audio Downloader - Main CLI Application

A command-line tool to download high-quality audio from YouTube videos
and extract metadata using YT-DLP and FFmpeg.
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import List, Optional

try:
    from .config import Config
    from .audio_downloader import AudioDownloader, URLValidator
    from .metadata_extractor import MetadataExtractor
except ImportError:
    from config import Config
    from audio_downloader import AudioDownloader, URLValidator
    from metadata_extractor import MetadataExtractor


class YouTubeAudioDownloaderCLI:
    """Main CLI application class."""
    
    def __init__(self):
        """Initialize CLI application."""
        self.config = None
        self.downloader = None
        self.metadata_extractor = None
        self.logger = None
        
    def setup_logging(self, verbose: bool = False, quiet: bool = False):
        """Setup logging configuration based on CLI args."""
        if quiet:
            level = logging.WARNING
        elif verbose:
            level = logging.DEBUG
        else:
            level = logging.INFO
            
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        self.logger = logging.getLogger(__name__)
    
    def progress_callback(self, info: dict):
        """Progress callback for downloads."""
        if info['status'] == 'downloading':
            percentage = info.get('percentage', 0)
            speed = info.get('speed', 'Unknown')
            print(f"\r🔄 Downloading: {percentage:.1f}% - {speed}", end='', flush=True)
        elif info['status'] == 'finished':
            print(f"\n✅ Download completed: {info['filename']}")
    
    def download_command(self, args):
        """Handle download command."""
        print(f"🎵 YouTube Audio Downloader")
        print(f"📂 Output directory: {self.config.paths.downloads_dir}")
        
        urls = []
        
        # Handle URL input
        if args.url:
            urls.append(args.url)
        elif args.file:
            try:
                with open(args.file, 'r', encoding='utf-8') as f:
                    urls = [line.strip() for line in f if line.strip()]
            except FileNotFoundError:
                print(f"❌ File not found: {args.file}")
                return 1
        else:
            print("❌ No URL provided. Use --url or --file option.")
            return 1
        
        # Validate URLs
        valid_urls = []
        for url in urls:
            if URLValidator.is_valid_youtube_url(url):
                valid_urls.append(url)
            else:
                print(f"⚠️  Invalid YouTube URL (skipping): {url}")
        
        if not valid_urls:
            print("❌ No valid YouTube URLs found.")
            return 1
        
        print(f"📋 Processing {len(valid_urls)} video(s)...")
        
        # Download videos
        if len(valid_urls) == 1:
            return self._download_single(valid_urls[0], args)
        else:
            return self._download_batch(valid_urls, args)
    
    def _download_single(self, url: str, args) -> int:
        """Download a single video."""
        try:
            print(f"\n🔗 URL: {url}")
            
            # Extract metadata if requested
            if args.metadata or args.info_only:
                print("📄 Extracting metadata...")
                metadata = self.metadata_extractor.extract_metadata(url)
                
                # Display basic info
                video_info = metadata.get('video_info', {})
                print(f"📺 Title: {video_info.get('title', 'Unknown')}")
                print(f"👤 Uploader: {video_info.get('uploader', 'Unknown')}")
                
                duration = metadata.get('computed', {}).get('duration_formatted') or video_info.get('duration_formatted')
                if duration:
                    print(f"⏱️  Duration: {duration}")
                
                # Save metadata
                if args.metadata:
                    metadata_file = self.metadata_extractor.save_metadata(metadata)
                    print(f"💾 Metadata saved: {metadata_file.name}")
            
            # Download audio (unless info-only)
            if not args.info_only:
                print("🎵 Downloading audio...")
                result = self.downloader.download_audio(url, args.output)
                
                if result['success']:
                    print(f"✅ Successfully downloaded: {result['filename']}")
                    return 0
                else:
                    print(f"❌ Download failed: {result.get('error', 'Unknown error')}")
                    return 1
            
            return 0
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            self.logger.error(f"Download error: {e}")
            return 1
    
    def _download_batch(self, urls: List[str], args) -> int:
        """Download multiple videos."""
        successful = 0
        failed = 0
        
        for i, url in enumerate(urls, 1):
            print(f"\n📹 Processing video {i}/{len(urls)}")
            print(f"🔗 URL: {url}")
            
            try:
                # Extract metadata if requested
                if args.metadata:
                    metadata = self.metadata_extractor.extract_metadata(url)
                    metadata_file = self.metadata_extractor.save_metadata(metadata)
                    video_title = metadata.get('video_info', {}).get('title', 'Unknown')
                    print(f"📄 Metadata: {video_title}")
                
                # Download audio
                if not args.info_only:
                    result = self.downloader.download_audio(url)
                    if result['success']:
                        print(f"✅ Downloaded: {result['filename']}")
                        successful += 1
                    else:
                        print(f"❌ Failed: {result.get('error', 'Unknown error')}")
                        failed += 1
                else:
                    successful += 1
                        
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                failed += 1
                
                if not args.continue_on_error:
                    print("💥 Stopping batch download due to error.")
                    break
        
        # Summary
        print(f"\n📊 Batch completed:")
        print(f"✅ Successful: {successful}")
        print(f"❌ Failed: {failed}")
        
        return 0 if failed == 0 else 1
    
    def info_command(self, args):
        """Handle info command."""
        if not URLValidator.is_valid_youtube_url(args.url):
            print(f"❌ Invalid YouTube URL: {args.url}")
            return 1
        
        try:
            print(f"📄 Extracting video information...")
            metadata = self.metadata_extractor.extract_metadata(args.url)
            
            # Display detailed information
            video_info = metadata.get('video_info', {})
            technical_info = metadata.get('technical_info', {})
            computed = metadata.get('computed', {})
            
            print(f"\n📺 Video Information:")
            print(f"  Title: {video_info.get('title', 'N/A')}")
            print(f"  Uploader: {video_info.get('uploader', 'N/A')}")
            print(f"  Duration: {computed.get('duration_formatted') or 'N/A'}")
            print(f"  Upload Date: {video_info.get('upload_date', 'N/A')}")
            print(f"  View Count: {video_info.get('view_count', 'N/A'):,}" if video_info.get('view_count') else "  View Count: N/A")
            print(f"  Like Count: {video_info.get('like_count', 'N/A'):,}" if video_info.get('like_count') else "  Like Count: N/A")
            
            print(f"\n🔧 Technical Information:")
            print(f"  Video ID: {computed.get('video_id', 'N/A')}")
            print(f"  Original Format: {technical_info.get('original_format', 'N/A')}")
            print(f"  Estimated MP3 Size: {computed.get('estimated_file_size', 'N/A')}")
            
            if video_info.get('tags'):
                print(f"\n🏷️  Tags: {', '.join(video_info['tags'][:5])}{'...' if len(video_info['tags']) > 5 else ''}")
            
            if args.save_info:
                metadata_file = self.metadata_extractor.save_metadata(metadata)
                print(f"\n💾 Information saved to: {metadata_file}")
            
            return 0
            
        except Exception as e:
            print(f"❌ Error extracting information: {str(e)}")
            return 1
    
    def config_command(self, args):
        """Handle config command."""
        if args.show:
            print("⚙️ Current Configuration:")
            print(f"  Audio Quality: {self.config.audio.quality} kbps")
            print(f"  Audio Format: {self.config.audio.format}")
            print(f"  Downloads Directory: {self.config.paths.downloads_dir}")
            print(f"  Metadata Directory: {self.config.paths.metadata_dir}")
            print(f"  Logs Directory: {self.config.paths.logs_dir}")
            print(f"  Console Log Level: {self.config.logging.console_level}")
            print(f"  File Log Level: {self.config.logging.file_level}")
        
        if args.create_sample:
            config_file = Path("yt_downloader_config.json")
            self.config.save_to_file(config_file)
            print(f"📝 Sample configuration created: {config_file}")
        
        return 0
    
    def create_parser(self) -> argparse.ArgumentParser:
        """Create and configure argument parser."""
        parser = argparse.ArgumentParser(
            description="YouTube Audio Downloader - Download high-quality audio from YouTube videos",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  %(prog)s download "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  %(prog)s download --file urls.txt --metadata
  %(prog)s info "https://youtu.be/dQw4w9WgXcQ"
  %(prog)s config --show
  
For more information, visit: https://github.com/your-repo/yt-dlp-project
            """)
        
        # Global options
        parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
        parser.add_argument('-q', '--quiet', action='store_true', help='Enable quiet mode (errors only)')
        parser.add_argument('-c', '--config', type=Path, help='Path to configuration file')
        
        # Subcommands
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Download command
        download_parser = subparsers.add_parser('download', help='Download audio from YouTube')
        download_group = download_parser.add_mutually_exclusive_group(required=True)
        download_group.add_argument('url', nargs='?', help='YouTube video URL')
        download_group.add_argument('-f', '--file', type=Path, help='File containing list of URLs')
        
        download_parser.add_argument('-o', '--output', help='Output filename (without extension)')
        download_parser.add_argument('-m', '--metadata', action='store_true', help='Extract and save metadata')
        download_parser.add_argument('--info-only', action='store_true', help='Extract info only (no download)')
        download_parser.add_argument('--continue-on-error', action='store_true', help='Continue batch download on errors')
        
        # Info command
        info_parser = subparsers.add_parser('info', help='Extract video information')
        info_parser.add_argument('url', help='YouTube video URL')
        info_parser.add_argument('-s', '--save-info', action='store_true', help='Save information to file')
        
        # Config command  
        config_parser = subparsers.add_parser('config', help='Configuration management')
        config_parser.add_argument('--show', action='store_true', help='Show current configuration')
        config_parser.add_argument('--create-sample', action='store_true', help='Create sample configuration file')
        
        return parser
    
    def run(self, argv: Optional[List[str]] = None) -> int:
        """Run the CLI application."""
        parser = self.create_parser()
        
        if not argv:
            argv = sys.argv[1:]
        
        # Handle case with no arguments
        if not argv:
            parser.print_help()
            return 0
        
        args = parser.parse_args(argv)
        
        # Setup logging
        self.setup_logging(args.verbose, args.quiet)
        
        # Load configuration
        try:
            self.config = Config(args.config) if args.config else Config()
            if not self.config.validate():
                print("❌ Configuration validation failed")
                return 1
        except Exception as e:
            print(f"❌ Configuration error: {str(e)}")
            return 1
        
        # Initialize components
        try:
            self.downloader = AudioDownloader(self.config, self.progress_callback)
            self.metadata_extractor = MetadataExtractor(self.config)
        except Exception as e:
            print(f"❌ Initialization error: {str(e)}")
            return 1
        
        # Route to appropriate command handler
        try:
            if args.command == 'download':
                return self.download_command(args)
            elif args.command == 'info':
                return self.info_command(args)
            elif args.command == 'config':
                return self.config_command(args)
            else:
                parser.print_help()
                return 0
        except KeyboardInterrupt:
            print("\n🛑 Operation cancelled by user")
            return 130
        except Exception as e:
            print(f"❌ Unexpected error: {str(e)}")
            self.logger.error(f"Unexpected error: {e}")
            return 1


def main():
    """Main entry point."""
    app = YouTubeAudioDownloaderCLI()
    return app.run()


if __name__ == "__main__":
    sys.exit(main())