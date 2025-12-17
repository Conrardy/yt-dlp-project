# YouTube Audio Downloader with Metadata Extraction

A comprehensive command-line tool to download high-quality audio from YouTube videos and extract metadata using YT-DLP and FFmpeg.

## ✨ Features

- 🎵 **High-Quality Audio**: Download MP3 audio at 320 kbps
- 📄 **Metadata Extraction**: Extract and save video information in JSON format
- 🖥️ **Command-Line Interface**: Easy-to-use CLI with multiple commands
- 📊 **Progress Tracking**: Real-time download progress with speed indicators
- 🔄 **Batch Processing**: Download multiple videos from a file list
- ⚙️ **Configurable**: Flexible configuration system with validation
- 🛡️ **Error Handling**: Robust error handling and retry mechanisms
- 📝 **Comprehensive Logging**: Detailed logging to files and console

## 🚀 Quick Start

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd yt-dlp-project
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   
   # Windows
   .\.venv\Scripts\Activate.ps1
   
   # Linux/Mac  
   source .venv/bin/activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install FFmpeg** (required for audio conversion)
   - **Windows**: See `FFMPEG_INSTALL.md` for detailed instructions
   - **Linux**: `sudo apt install ffmpeg`
   - **Mac**: `brew install ffmpeg`

### Basic Usage

#### Command-Line Interface (CLI)

```bash
# Download a single video
python youtube_downloader.py download "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Download with metadata extraction
python youtube_downloader.py download "https://youtu.be/dQw4w9WgXcQ" --metadata

# Get video information only (no download)
python youtube_downloader.py info "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# Show current configuration
python youtube_downloader.py config --show
```

#### Web Interface (FastAPI)

1. **Start the web server**
   ```bash
   python run_server.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Open your browser**
   Navigate to `http://localhost:8000` to access the web interface.

3. **Features available in the web interface:**
   - 📺 Analyze YouTube video URLs and view metadata
   - ⬇️ Download audio with real-time progress tracking
   - 📊 View download history with statistics
   - 📥 Download previously downloaded files
   - 🎨 Modern, responsive UI

The web interface provides all the functionality of the CLI in an easy-to-use graphical interface with Server-Sent Events (SSE) for real-time progress updates.

## 📖 Detailed Usage

### Download Commands

```bash
# Single video download
python youtube_downloader.py download "URL"

# Custom output filename
python youtube_downloader.py download "URL" --output "my_audio_file"

# Download multiple videos from file
python youtube_downloader.py download --file urls.txt

# Download with metadata extraction
python youtube_downloader.py download "URL" --metadata

# Info extraction only (no download)
python youtube_downloader.py download "URL" --info-only

# Continue on errors during batch processing
python youtube_downloader.py download --file urls.txt --continue-on-error
```

### Information Commands

```bash
# Get detailed video information
python youtube_downloader.py info "URL"

# Save information to file
python youtube_downloader.py info "URL" --save-info
```

### Configuration Commands

```bash
# Show current configuration
python youtube_downloader.py config --show

# Create sample configuration file
python youtube_downloader.py config --create-sample
```

### Global Options

```bash
# Verbose output (debug mode)
python youtube_downloader.py --verbose download "URL"

# Quiet mode (errors only)
python youtube_downloader.py --quiet download "URL"

# Use custom configuration file
python youtube_downloader.py --config my_config.json download "URL"
```

## 📁 Project Structure

```
yt-dlp-project/
├── src/                           # Source code
│   ├── __init__.py               # Package initialization
│   ├── main.py                   # Main CLI application
│   ├── config.py                 # Configuration management
│   ├── audio_downloader.py       # Audio download functionality
│   ├── metadata_extractor.py     # Metadata extraction
│   ├── api/                      # FastAPI web interface
│   │   ├── __init__.py
│   │   ├── app.py                # FastAPI application
│   │   ├── routes.py             # API endpoints
│   │   ├── models.py             # Pydantic schemas
│   │   └── database.py           # SQLite database for history
│   ├── static/                   # Static web assets
│   │   ├── css/
│   │   │   └── style.css         # Styles
│   │   └── js/
│   │       └── app.js            # Frontend JavaScript
│   └── templates/                # HTML templates
│       └── index.html            # Main web page
├── downloads/                     # Downloaded audio files
├── metadata/                      # Extracted metadata (JSON)
├── logs/                         # Application logs
├── .venv/                        # Python virtual environment
├── youtube_downloader.py         # Main entry point script (CLI)
├── run_server.py                 # Web server entry point
├── test_functionality.py         # Test script
├── requirements.txt              # Python dependencies
├── README.md                     # This documentation
├── FFMPEG_INSTALL.md            # FFmpeg installation guide
└── .gitignore                   # Git ignore rules
```

## ⚙️ Configuration

The application uses a flexible configuration system. Default settings:

- **Audio Quality**: 320 kbps MP3
- **Downloads Directory**: `./downloads/`
- **Metadata Directory**: `./metadata/`
- **Logs Directory**: `./logs/`
- **Log Level**: INFO (console), DEBUG (file)

Create a custom configuration:

```bash
python youtube_downloader.py config --create-sample
```

This creates `yt_downloader_config.json` which you can modify and use with:

```bash
python youtube_downloader.py --config yt_downloader_config.json download "URL"
```

## 📋 Requirements

- **Python**: 3.11+ (tested with 3.13)
- **FFmpeg**: For audio conversion (must be in PATH)
- **Internet Connection**: For downloading from YouTube

### Python Dependencies

- `yt-dlp`: YouTube video/audio downloader
- `argparse`: Command-line argument parsing (built-in)
- `pathlib`: Path manipulation (built-in)
- `logging`: Logging functionality (built-in)

## 🧪 Testing

Run the test suite to verify functionality:

```bash
python test_functionality.py
```

This tests:
- URL validation
- Configuration system
- Component initialization  
- Metadata extraction (requires internet)

## 📊 Example Output

```
🎵 YouTube Audio Downloader
📂 Output directory: C:\dev-perso\yt-dlp-project\downloads

🔗 URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ
📄 Extracting metadata...
📺 Title: Rick Astley - Never Gonna Give You Up (Official Video)
👤 Uploader: Rick Astley
⏱️ Duration: 03:32
💾 Metadata saved: Rick_Astley_Never_Gonna_Give_You_Up_dQw4w9WgXcQ.json

🎵 Downloading audio...
🔄 Downloading: 45.2% - 1.2MB/s
✅ Successfully downloaded: Rick Astley - Never Gonna Give You Up (Official Video).mp3
```

## 🛠️ Development

### Adding New Features

1. **Configuration**: Add new settings to `src/config.py`
2. **Download Logic**: Extend `src/audio_downloader.py`
3. **Metadata**: Enhance `src/metadata_extractor.py`
4. **CLI**: Update commands in `src/main.py`

### Code Structure

- **Modular Design**: Each component is self-contained
- **Configuration-Driven**: All settings managed centrally
- **Error Handling**: Comprehensive exception management
- **Logging**: Detailed logging throughout the application

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if needed
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## ⚠️ Disclaimer

This tool is for personal use only. Please respect YouTube's terms of service and copyright laws. Only download content you have the right to download.
