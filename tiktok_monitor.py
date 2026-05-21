import requests
import logging
from datetime import datetime
from typing import Optional, Dict, List
import json

logger = logging.getLogger(__name__)

class TikTokMonitor:
    """Monitor TikTok accounts for live streams"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.live_urls = {}
    
    async def check_live_status(self, username: str) -> Optional[Dict]:
        """
        Check if a TikTok account is currently live
        Returns: Dict with live info if live, None otherwise
        """
        try:
            # Method 1: Direct API call via unofficial endpoint
            url = f"https://www.tiktok.com/api/user/@{username}/video"
            
            params = {
                'aid': '1988',
                'app_name': 'tiktok_web',
                'device_id': '1234567890',
                'region': 'US',
                'priority_region': 'US'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Check if user is currently live
            if self._check_if_live(data):
                logger.info(f"✓ {username} is LIVE")
                return {
                    'username': username,
                    'is_live': True,
                    'timestamp': datetime.now().isoformat(),
                    'stream_info': self._extract_stream_info(data)
                }
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
    
    def _check_if_live(self, data: dict) -> bool:
        """Check if the response indicates a live stream"""
        try:
            # Look for live indicators in the response
            if 'user' in data:
                user_info = data['user']
                # Check for live status indicators
                if user_info.get('is_live', False):
                    return True
                if user_info.get('status', {}).get('is_live', False):
                    return True
            return False
        except Exception as e:
            logger.error(f"Error parsing live status: {e}")
            return False
    
    def _extract_stream_info(self, data: dict) -> Dict:
        """Extract stream information from response"""
        try:
            stream_info = {
                'stream_id': None,
                'title': None,
                'viewers': None,
                'cover_image': None,
                'stream_url': None
            }
            
            if 'user' in data:
                user = data['user']
                stream_info['stream_id'] = user.get('id')
                stream_info['title'] = user.get('live_title', 'TikTok Live')
                stream_info['viewers'] = user.get('live_viewer_count', 0)
                stream_info['cover_image'] = user.get('avatar_medium', {}).get('url_list', [None])[0]
            
            return stream_info
        except Exception as e:
            logger.error(f"Error extracting stream info: {e}")
            return {}
    
    async def get_live_stream_url(self, username: str) -> Optional[str]:
        """Get the direct stream URL for downloading"""
        try:
            # This would use yt-dlp or similar to extract the actual stream URL
            # For now, we return a placeholder
            url = f"https://www.tiktok.com/@{username}/live"
            return url
        except Exception as e:
            logger.error(f"Error getting stream URL for {username}: {e}")
            return None
    
    def close(self):
        """Close the session"""
        if self.session:
            self.session.close()
