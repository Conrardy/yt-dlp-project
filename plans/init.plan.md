# Instruction: YouTube Audio Downloader with Metadata Extraction
> Please follow this plan using proper rules.

## Goal
Develop a command-line tool to download high-quality audio from YouTube videos and extract metadata using YT-DLP.

## Existing files
knowledge.md

## New file to create
- Command-line tool script
- Audio processing script
- Metadata extraction script

## Grouped tasks
### Configuration and Setup
> Set up the development environment and install necessary tools.
- Define audio quality and format requirements: **MP3, high quality (320 kbps).**
- Set up the development environment: **Python 3.11, virtual environment recommended.**
- Install YT-DLP and FFmpeg: **Use `pip install yt-dlp` and ensure FFmpeg is in the system PATH.**

### Command-Line Tool Development
> Create the command-line interface and implement user interaction features.
- Create command-line interface structure: **Use `argparse` for argument parsing.**
- Implement progress tracking and error handling: **Log progress and errors to console and a log file.**

### Audio Download and Conversion
> Implement audio download and conversion functionality.
- Develop script to download audio using YT-DLP: **Use `yt_dlp.YoutubeDL` with options for best audio quality.**
- Implement audio conversion to MP3 using FFmpeg: **Convert to 320 kbps MP3.**

### Metadata Extraction
> Extract and store metadata from the downloaded audio.
- Extract and store metadata in JSON format: **Use `yt_dlp` to extract metadata and save as JSON.**

### Integration and Testing
> Integrate all components and test the workflow.
- Integrate components into the command-line tool: **Combine scripts into a single CLI tool.**
- Test the entire workflow: **Test with various YouTube URLs and edge cases.**

## Validation checkpoints
- Verify audio download and conversion quality: **Check bitrate and audio clarity.**
- Confirm metadata extraction accuracy: **Validate JSON metadata against YouTube video details.**
- Ensure command-line tool functionality and user interaction features: **Test all CLI commands and options.**
