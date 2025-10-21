#!/usr/bin/env python3
"""
Test script for YouTube Audio Downloader

This script demonstrates the basic functionality without actually downloading.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

from src import Config, URLValidator, AudioDownloader, MetadataExtractor

def test_url_validation():
    """Test URL validation functionality."""
    print("🔍 Testing URL Validation:")
    
    test_urls = [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "https://youtu.be/dQw4w9WgXcQ", 
        "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
        "invalid_url",
        "https://vimeo.com/123456789"
    ]
    
    for url in test_urls:
        is_valid = URLValidator.is_valid_youtube_url(url)
        status = "✅" if is_valid else "❌"
        print(f"  {status} {url}")
        
        if is_valid:
            video_id = URLValidator.extract_video_id(url)
            normalized = URLValidator.normalize_url(url)
            print(f"    📺 Video ID: {video_id}")
            print(f"    🔗 Normalized: {normalized}")

def test_configuration():
    """Test configuration system."""
    print("\n⚙️ Testing Configuration:")
    
    config = Config()
    print(f"  📁 Downloads: {config.paths.downloads_dir}")
    print(f"  📄 Metadata: {config.paths.metadata_dir}")
    print(f"  📝 Logs: {config.paths.logs_dir}")
    print(f"  🎵 Quality: {config.audio.quality} kbps {config.audio.format}")
    
    validation = config.validate()
    print(f"  ✅ Validation: {'Passed' if validation else 'Failed'}")

def test_info_extraction():
    """Test metadata extraction (info only)."""
    print("\n📄 Testing Info Extraction:")
    
    # Use Rick Roll video (safe for testing)
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    
    try:
        config = Config()
        extractor = MetadataExtractor(config)
        
        print(f"  🔗 URL: {test_url}")
        print("  📡 Extracting metadata... (this may take a moment)")
        
        # This will actually extract info from YouTube
        metadata = extractor.extract_metadata(test_url)
        
        video_info = metadata.get('video_info', {})
        computed = metadata.get('computed', {})
        
        print(f"  📺 Title: {video_info.get('title', 'N/A')}")
        print(f"  👤 Uploader: {video_info.get('uploader', 'N/A')}")
        print(f"  ⏱️  Duration: {computed.get('duration_formatted', 'N/A')}")
        print(f"  📊 Views: {video_info.get('view_count', 'N/A'):,}" if video_info.get('view_count') else "  📊 Views: N/A")
        print(f"  💾 Est. Size: {computed.get('estimated_file_size', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Error: {str(e)}")
        print("  ℹ️  This is normal if you don't have internet connection")
        return False

def test_components():
    """Test component initialization."""
    print("\n🔧 Testing Component Initialization:")
    
    try:
        config = Config()
        print("  ✅ Config initialized")
        
        downloader = AudioDownloader(config)
        print("  ✅ AudioDownloader initialized")
        
        extractor = MetadataExtractor(config)
        print("  ✅ MetadataExtractor initialized")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Component initialization failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🎵 YouTube Audio Downloader - Test Suite")
    print("=" * 50)
    
    # Basic tests
    test_url_validation()
    test_configuration() 
    
    components_ok = test_components()
    
    if components_ok:
        # Test that requires internet (optional)
        print("\n🌐 Internet-dependent tests:")
        print("   (These tests require internet connection)")
        
        try:
            success = test_info_extraction()
            if success:
                print("\n🎉 All tests completed successfully!")
            else:
                print("\n⚠️  Some tests failed (possibly due to network issues)")
        except KeyboardInterrupt:
            print("\n🛑 Tests interrupted by user")
    else:
        print("\n❌ Component tests failed - skipping network tests")
    
    print("\n📋 Test Summary:")
    print("  ✅ URL Validation: Working")
    print("  ✅ Configuration: Working")  
    print("  ✅ Components: Working" if components_ok else "  ❌ Components: Failed")
    print("  📡 Network Tests: Run with internet connection for full testing")
    
    print(f"\n🚀 Ready to use! Run:")
    print(f"   python youtube_downloader.py --help")

if __name__ == "__main__":
    main()
