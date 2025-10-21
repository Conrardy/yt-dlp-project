# YouTube Audio Downloader with Metadata Extraction

A command-line tool to download high-quality audio from YouTube videos and extract metadata using YT-DLP.

## Features
- Download high-quality audio (MP3, 320 kbps)
- Extract and store metadata in JSON format
- Command-line interface with progress tracking
- Error handling and retry mechanisms

## Setup
1. Create virtual environment: `python -m venv venv`
2. Activate virtual environment: `.\venv\Scripts\Activate.ps1` (Windows) or `source venv/bin/activate` (Linux/Mac)
3. Install dependencies: `pip install -r requirements.txt`
4. Install FFmpeg (required for audio conversion)

## Usage
```bash
python src/main.py <youtube_url> [options]
```

## Project Structure
```
├── src/                    # Source code
│   ├── main.py            # Main CLI script
│   ├── audio_downloader.py # Audio download functionality
│   ├── metadata_extractor.py # Metadata extraction
│   └── config.py          # Configuration management
├── downloads/             # Downloaded audio files
├── metadata/             # Extracted metadata (JSON)
├── logs/                 # Application logs
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Requirements
- Python 3.11+
- FFmpeg (for audio conversion)
- YT-DLP
