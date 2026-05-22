#!/usr/bin/env python3
"""
Advanced yt-dlp probe for TikTok live with multiple strategies
"""
import yt_dlp
import json

def test_with_browserargs():
    """Test with browserargs to mimic real browser."""
    print("\n" + "="*60)
    print("Testing with browserargs (browser impersonation)")
    print("="*60)
    
    try:
        ydl_opts = {
            'quiet': False,
            'no_warnings': False,
            'skip_download': True,
            'noplaylist': True,
            'browserargs': ['--disable-blink-features=AutomationControlled'],
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            }
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info("https://www.tiktok.com/@beautybasetv/live", download=False)
        
        print(f"✅ SUCCESS with browserargs")
        print(f"  - is_live: {info.get('is_live')}")
        print(f"  - live_status: {info.get('live_status')}")
        return True
    except Exception as e:
        print(f"❌ Failed: {type(e).__name__}: {str(e)[:100]}")
        return False


def test_with_impersonate():
    """Test with impersonate option."""
    print("\n" + "="*60)
    print("Testing with impersonate=chrome (Playwright)")
    print("="*60)
    
    try:
        ydl_opts = {
            'quiet': False,
            'no_warnings': False,
            'skip_download': True,
            'noplaylist': True,
            'impersonate': 'chrome',
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info("https://www.tiktok.com/@beautybasetv/live", download=False)
        
        print(f"✅ SUCCESS with impersonate=chrome")
        print(f"  - is_live: {info.get('is_live')}")
        print(f"  - live_status: {info.get('live_status')}")
        return True
    except Exception as e:
        print(f"❌ Failed: {type(e).__name__}: {str(e)[:100]}")
        return False


def test_with_cookies():
    """Test with extraction-flat to get channel page info first."""
    print("\n" + "="*60)
    print("Testing with extract_flat (get channel info)")
    print("="*60)
    
    try:
        ydl_opts = {
            'quiet': False,
            'no_warnings': False,
            'skip_download': True,
            'extract_flat': True,
        }
        
        # Try the channel page instead of live page
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info("https://www.tiktok.com/@beautybasetv", download=False)
        
        print(f"✅ SUCCESS with extract_flat on channel")
        print(f"  - Channel info retrieved")
        print(f"  - Keys: {list(info.keys())[:10]}")
        return True
    except Exception as e:
        print(f"❌ Failed: {type(e).__name__}: {str(e)[:100]}")
        return False


def test_direct_download_probe():
    """Test if we can at least get video info by attempting download (without saving)."""
    print("\n" + "="*60)
    print("Testing direct download request (check if content exists)")
    print("="*60)
    
    try:
        ydl_opts = {
            'quiet': False,
            'no_warnings': False,
            'skip_download': True,
            'write_info_json': False,
            'socket_timeout': 10,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info("https://www.tiktok.com/@beautybasetv/live", download=False)
        
        print(f"✅ SUCCESS")
        print(f"  - is_live: {info.get('is_live')}")
        return True
    except yt_dlp.utils.UserNotLive as e:
        print(f"⚠️  Channel appears offline: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {str(e)[:150]}")
        return False


if __name__ == '__main__':
    print("Advanced TikTok Live Detection Probe")
    print("Testing multiple strategies...")
    
    # Track results
    results = {
        'browserargs': test_with_browserargs(),
        'impersonate_chrome': test_with_impersonate(),
        'extract_flat': test_with_cookies(),
        'direct_download': test_direct_download_probe(),
    }
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for strategy, success in results.items():
        status = "✅ WORKS" if success else "❌ FAILS"
        print(f"{status}: {strategy}")
    
    if any(results.values()):
        print("\n✅ At least one strategy works!")
    else:
        print("\n❌ All strategies failed - @beautybasetv may not be online")
