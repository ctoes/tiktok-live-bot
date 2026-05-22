#!/usr/bin/env python3
"""
Test different yt-dlp configurations for TikTok live recording
"""
import yt_dlp
import sys

def test_config(config_name, opts):
    """Test a specific yt-dlp configuration."""
    print(f"\n{'='*60}")
    print(f"Testing: {config_name}")
    print('='*60)
    
    url = "https://www.tiktok.com/@beautybasetv/live"
    
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
        
        print(f"✅ SUCCESS")
        print(f"  - is_live: {info.get('is_live')}")
        print(f"  - live_status: {info.get('live_status')}")
        print(f"  - title: {info.get('title')}")
        print(f"  - formats available: {len(info.get('formats', []))}")
        return True
    
    except yt_dlp.utils.UserNotLive as e:
        print(f"❌ User not live: {e}")
        return False
    except yt_dlp.utils.DownloadError as e:
        print(f"❌ Download error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {e}")
        return False


def main():
    """Test different configurations."""
    print("Testing different yt-dlp configurations for TikTok live")
    
    configs = [
        ("Basic config (skip_download)", {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'noplaylist': True,
        }),
        
        ("With socket timeout", {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'noplaylist': True,
            'socket_timeout': 30,
        }),
        
        ("With full user-agent", {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'noplaylist': True,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
        }),
        
        ("Force all formats", {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'noplaylist': True,
            'noforcejson': False,
        }),
        
        ("Download with all options", {
            'quiet': False,
            'no_warnings': False,
            'skip_download': True,
            'noplaylist': True,
            'socket_timeout': 30,
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        }),
    ]
    
    results = []
    for config_name, opts in configs:
        success = test_config(config_name, opts)
        results.append((config_name, success))
    
    print(f"\n{'='*60}")
    print("Summary:")
    print('='*60)
    for config_name, success in results:
        status = "✅ Works" if success else "❌ Failed"
        print(f"{status}: {config_name}")


if __name__ == '__main__':
    main()
