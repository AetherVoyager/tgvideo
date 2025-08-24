#!/usr/bin/env python3
"""
Test script for TgMusicBot video features
This script helps verify that video functionality is working correctly
"""

import os
import sys
import asyncio
from pathlib import Path

# Add the TgMusic directory to Python path
sys.path.insert(0, str(Path(__file__).parent / "TgMusic"))

def test_video_handler_import():
    """Test if video handler module can be imported."""
    try:
        from TgMusic.modules.video_handler import VideoHandler, handle_video_reply
        print("✅ Video handler module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import video handler: {e}")
        return False

def test_video_formats():
    """Test supported video formats."""
    try:
        from TgMusic.modules.video_handler import VideoHandler
        
        expected_formats = ['mp4', 'avi', 'mkv', 'mov', 'wmv', 'flv', 'webm', 'm4v', '3gp']
        actual_formats = VideoHandler.SUPPORTED_VIDEO_FORMATS
        
        if set(expected_formats) == set(actual_formats):
            print("✅ All expected video formats are supported")
            return True
        else:
            print(f"❌ Video format mismatch. Expected: {expected_formats}, Got: {actual_formats}")
            return False
    except Exception as e:
        print(f"❌ Error testing video formats: {e}")
        return False

def test_play_module_import():
    """Test if enhanced play module can be imported."""
    try:
        from TgMusic.modules.play import handle_play_command, VideoHandler
        print("✅ Enhanced play module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import enhanced play module: {e}")
        return False

def test_start_module_import():
    """Test if enhanced start module can be imported."""
    try:
        from TgMusic.modules.start import start_cmd, callback_query_help
        print("✅ Enhanced start module imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import enhanced start module: {e}")
        return False

def test_core_modules():
    """Test if core modules are accessible."""
    try:
        from TgMusic.core import chat_cache, call, tg
        from TgMusic.core import CachedTrack, MusicTrack, PlatformTracks
        print("✅ Core modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import core modules: {e}")
        return False

def test_utils():
    """Test if utility functions are accessible."""
    try:
        from TgMusic.modules.utils import sec_to_min, get_audio_duration
        from TgMusic.modules.utils.play_helpers import edit_text
        print("✅ Utility modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import utility modules: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing TgMusicBot Video Features\n")
    print("=" * 50)
    
    tests = [
        ("Core Modules", test_core_modules),
        ("Utility Modules", test_utils),
        ("Video Handler", test_video_handler_import),
        ("Video Formats", test_video_formats),
        ("Enhanced Play Module", test_play_module_import),
        ("Enhanced Start Module", test_start_module_import),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Video features are ready to use.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
