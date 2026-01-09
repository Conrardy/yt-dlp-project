"""
Unit tests for the metadata_extractor module.

This module contains unit tests for the MetadataExtractor class and its
helper methods. Tests are designed to run without network access where
possible, testing pure functions and static methods.

Test Categories:
    - Duration formatting: Tests for _format_duration()
    - File size formatting: Tests for _format_filesize()
    - MP3 size estimation: Tests for _estimate_mp3_size()
    - Filename sanitization: Tests for _sanitize_filename()

Usage:
    Run tests using pytest from the project root:
    
    $ pytest tst/test_metadata_extractor.py -v
    
    Or run directly:
    
    $ python tst/test_metadata_extractor.py

Note:
    Tests that require network access (actual metadata extraction)
    are not included here. See test_functionality.py for integration tests.
"""

import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from metadata_extractor import MetadataExtractor


def test_format_duration():
    """
    Test the _format_duration static method.
    
    Verifies that durations in seconds are correctly converted to
    human-readable format (MM:SS or HH:MM:SS for longer durations).
    
    Test cases cover:
        - Zero duration
        - Sub-minute durations
        - Multi-minute durations
        - Hour-plus durations
        - Exact hour boundaries
    """
    # Arrange: Define test cases as (input_seconds, expected_output)
    test_cases = [
        (0, "00:00"),         # Zero duration
        (30, "00:30"),        # 30 seconds
        (65, "01:05"),        # 1 minute 5 seconds
        (3661, "01:01:01"),   # 1 hour, 1 minute, 1 second
        (3600, "01:00:00"),   # Exactly 1 hour
    ]
    
    for seconds, expected in test_cases:
        # Act
        result = MetadataExtractor._format_duration(seconds)
        
        # Assert
        assert result == expected, f"Expected {expected} for {seconds} seconds, got {result}"


def test_format_filesize():
    """
    Test the _format_filesize static method.
    
    Verifies that byte counts are correctly converted to human-readable
    format with appropriate units (B, KB, MB, GB, TB).
    """
    test_cases = [
        (0, "0 B"),
        (512, "512.0 B"),
        (1024, "1.0 KB"),
        (1536, "1.5 KB"),
        (1048576, "1.0 MB"),
        (1073741824, "1.0 GB"),
    ]
    
    for bytes_count, expected in test_cases:
        result = MetadataExtractor._format_filesize(bytes_count)
        assert result == expected, f"Expected {expected} for {bytes_count} bytes, got {result}"


def test_estimate_mp3_size():
    """
    Test the _estimate_mp3_size static method.
    
    Verifies that MP3 file size estimation for 320kbps bitrate
    returns reasonable values.
    """
    # 320 kbps = 40 KB/s
    # 60 seconds = 60 * 40 KB = 2400 KB ≈ 2.3 MB
    result = MetadataExtractor._estimate_mp3_size(60)
    assert "MB" in result, f"Expected MB unit for 60 seconds, got {result}"
    
    # Zero duration should return "Unknown"
    result = MetadataExtractor._estimate_mp3_size(0)
    assert result == "Unknown", f"Expected 'Unknown' for 0 seconds, got {result}"


def test_sanitize_filename():
    """
    Test the _sanitize_filename static method.
    
    Verifies that invalid filename characters are replaced and
    filenames are truncated to safe lengths.
    """
    test_cases = [
        ("Normal Title", "Normal Title"),
        ("Title: With Colon", "Title_ With Colon"),
        ("Title/With/Slashes", "Title_With_Slashes"),
        ('Title "With" Quotes', "Title _With_ Quotes"),
        ("Title<With>Brackets", "Title_With_Brackets"),
        ("A" * 150, "A" * 100),  # Should be truncated to 100 chars
    ]
    
    for input_name, expected in test_cases:
        result = MetadataExtractor._sanitize_filename(input_name)
        assert result == expected, f"Expected '{expected}' for '{input_name}', got '{result}'"


if __name__ == "__main__":
    # Run tests when executed directly
    print("Running MetadataExtractor unit tests...")
    
    test_format_duration()
    print("✅ test_format_duration passed")
    
    test_format_filesize()
    print("✅ test_format_filesize passed")
    
    test_estimate_mp3_size()
    print("✅ test_estimate_mp3_size passed")
    
    test_sanitize_filename()
    print("✅ test_sanitize_filename passed")
    
    print("\n🎉 All tests passed!")
