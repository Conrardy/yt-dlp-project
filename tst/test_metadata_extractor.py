"""
Test file for metadata_extractor module.
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
    """
    # Arrange
    test_cases = [
        (0, "00:00"),
        (30, "00:30"),
        (65, "01:05"),
        (3661, "01:01:01"),  # 1 hour, 1 minute, 1 second
        (3600, "01:00:00"),  # Exactly 1 hour
    ]
    
    for seconds, expected in test_cases:
        # Act
        result = MetadataExtractor._format_duration(seconds)
        
        # Assert
        assert result == expected, f"Expected {expected} for {seconds} seconds, got {result}"
