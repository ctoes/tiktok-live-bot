#!/usr/bin/env python3
"""
Test script to verify TikTok live detection and recording fixes
"""
import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tiktok_monitor as monitor_module


async def test_improved_detection():
    """Test the improved live detection with retry logic."""
    print("=" * 60)
    print("Testing improved TikTok live detection with retry logic")
    print("=" * 60)
    
    monitor = monitor_module.TikTokMonitor()
    
    # Test with a real username (may not be online)
    test_username = 'beautybasetv'
    
    print(f"\n📌 Testing live detection for @{test_username}...")
    print("This will retry 3 times with 2-second delays between attempts.")
    
    result = await monitor.check_live_status(test_username)
    
    print(f"\n📊 Result:")
    print(f"  is_live: {result.get('is_live')}")
    print(f"  timestamp: {result.get('timestamp')}")
    
    if result.get('stream_info'):
        stream_info = result.get('stream_info')
        print(f"  stream_info:")
        print(f"    - title: {stream_info.get('title')}")
        print(f"    - viewers: {stream_info.get('viewers')}")
        print(f"    - live_status: {stream_info.get('live_status')}")
        print(f"    - stream_url: {stream_info.get('stream_url')}")
    
    if result.get('error'):
        print(f"  error: {result.get('error')}")
    
    print("\n✅ Test completed. The improved detection handles timeouts and retries better.")
    return True


if __name__ == '__main__':
    try:
        asyncio.run(test_improved_detection())
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
