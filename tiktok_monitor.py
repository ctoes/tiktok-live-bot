import logging
from datetime import datetime
from typing import Optional, Dict, List
import asyncio
import yt_dlp

logger = logging.getLogger(__name__)

class TikTokMonitor:
    """Monitor TikTok accounts for live streams"""
    
    def __init__(self):
        self.live_urls = {}
    
    async def check_live_status(self, username: str) -> Optional[Dict]:
        """
        Check if a TikTok account is currently live
        Returns: Dict with live info if live, None otherwise
        """
        try:
            data = await asyncio.to_thread(self._check_live_sync, username)

            if data and data.get('is_live'):
                logger.info(f"✓ {username} is LIVE")
                return data
            else:
                logger.debug(f"✗ {username} is not live")
                return {
                    'username': username,
                    'is_live': False,
                    'timestamp': datetime.now().isoformat()
                }
        
        except Exception as e:
            logger.error(f"Error checking {username}: {str(e)}")
            return None

    def _check_live_sync(self, username: str) -> Dict:
        """Synchronous live status probe using yt-dlp."""
        url = f"https://www.tiktok.com/@{username}/live"
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'noplaylist': True,
            'extract_flat': False,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        live_status = info.get('live_status')
        is_live = bool(info.get('is_live')) or live_status in ('is_live', 'live')

        stream_info = {
            'stream_id': info.get('id'),
            'title': info.get('title') or info.get('description') or 'TikTok Live',
            'viewers': info.get('concurrent_view_count') or info.get('view_count') or info.get('live_viewer_count'),
            'cover_image': info.get('thumbnail'),
            'stream_url': info.get('url') or info.get('webpage_url'),
            'live_status': live_status,
        }

        return {
            'username': username,
            'is_live': is_live,
            'timestamp': datetime.now().isoformat(),
            'stream_info': stream_info,
        }
    
    async def get_live_stream_url(self, username: str) -> Optional[str]:
        """Get the direct stream URL for downloading"""
        try:
            data = await asyncio.to_thread(self._check_live_sync, username)
            if data and data.get('is_live'):
                return data.get('stream_info', {}).get('stream_url')
            return None
        except Exception as e:
            logger.error(f"Error getting stream URL for {username}: {e}")
            return None
    
    def close(self):
        """Close the session"""
        return None
