import json
import logging
import os
import re
from datetime import datetime
from http.cookiejar import MozillaCookieJar
from typing import Optional, Dict, List
import asyncio
import requests
import yt_dlp
import time

logger = logging.getLogger(__name__)

class TikTokMonitor:
    """Monitor TikTok accounts for live streams"""
    
    def __init__(self):
        self.live_urls = {}

    def _create_session(self) -> requests.Session:
        try:
            from curl_cffi import Session as CurlSession

            session = CurlSession(impersonate='chrome136', http_version='v1')
            session.headers.update(
                {
                    'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126"',
                    'Sec-Ch-Ua-Mobile': '?0',
                    'Sec-Ch-Ua-Platform': '"Windows"',
                    'Accept-Language': 'en-US',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': (
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.127 Safari/537.36'
                    ),
                    'Accept': (
                        'text/html,application/xhtml+xml,application/xml;q=0.9,'
                        'image/avif,image/webp,image/apng,application/json,text/plain,*/*;q=0.8,'
                        'application/signed-exchange;v=b3;q=0.7'
                    ),
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-User': '?1',
                    'Sec-Fetch-Dest': 'document',
                    'Priority': 'u=0, i',
                    'Referer': 'https://www.tiktok.com/',
                    'Origin': 'https://www.tiktok.com',
                }
            )
        except Exception:
            session = requests.Session()
            session.headers.update(
                {
                    'User-Agent': (
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
                    ),
                    'Accept': 'application/json, text/plain, */*',
                    'Referer': 'https://www.tiktok.com/',
                    'Origin': 'https://www.tiktok.com',
                }
            )

        # Load cookies: support Netscape cookies.txt (MozillaCookieJar) or browser-exported cookies.json
        cookies_file = os.getenv('TIKTOK_COOKIES_FILE')
        if cookies_file and os.path.exists(cookies_file):
            try:
                if cookies_file.lower().endswith('.json'):
                    with open(cookies_file, 'r', encoding='utf-8') as fh:
                        data = json.load(fh)
                    jar = requests.cookies.RequestsCookieJar()
                    if isinstance(data, dict) and data.get('cookies'):
                        data = data.get('cookies')
                    for c in data:
                        name = c.get('name') or c.get('key')
                        value = c.get('value')
                        domain = c.get('domain')
                        path = c.get('path', '/')
                        if name and value is not None:
                            jar.set(name, value, domain=domain, path=path)
                    session.cookies.update(jar)
                else:
                    jar = MozillaCookieJar(cookies_file)
                    jar.load(ignore_discard=True, ignore_expires=True)
                    session.cookies.update(jar)
            except Exception as e:
                logger.warning(f"Could not load TikTok cookies from {cookies_file}: {e}")

        # Support proxy via TIKTOK_PROXY env var (http(s)://host:port)
        proxy = os.getenv('TIKTOK_PROXY')
        if proxy:
            try:
                proxies = {'http': proxy, 'https': proxy}
                # requests.Session supports .proxies
                session.proxies.update(proxies)
            except Exception as e:
                logger.debug(f"Failed to set proxy on session: {e}")

        return session

    def _extract_room_id(self, html: str) -> Optional[str]:
        patterns = (
            r'"roomId":"?(\d+)"?',
            r'"room_id":"?(\d+)"?',
            r'"roomID":"?(\d+)"?',
            r'"liveRoomId":"?(\d+)"?',
            r'"room_id_str":"?(\d+)"?',
        )

        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                return match.group(1)

        return None

    def _extract_stream_url_from_html(self, html: str) -> Optional[str]:
        patterns = (
            r'https://pull-[^"\']+',
            r'https://v16-[^"\']+',
            r'https://pull-flv-[^"\']+',
        )

        for pattern in patterns:
            match = re.search(pattern, html)
            if match:
                return match.group(0)

        return None

    def _extract_stream_url(self, room_data: Dict) -> Optional[str]:
        stream_url = room_data.get('stream_url')
        if not isinstance(stream_url, dict):
            return None

        flv_pull_url = stream_url.get('flv_pull_url')
        default_resolution = stream_url.get('default_resolution')
        if isinstance(flv_pull_url, dict) and flv_pull_url:
            if default_resolution and default_resolution in flv_pull_url:
                return flv_pull_url[default_resolution]

            for key in ('HD1', 'HD', 'SD1', 'LD1'):
                if key in flv_pull_url and flv_pull_url[key]:
                    return flv_pull_url[key]

            for value in flv_pull_url.values():
                if value:
                    return value

        for key in ('rtmp_pull_url', 'hls_pull_url'):
            value = stream_url.get(key)
            if isinstance(value, str) and value:
                return value

        live_core_sdk_data = stream_url.get('live_core_sdk_data')
        if isinstance(live_core_sdk_data, dict):
            pull_data = live_core_sdk_data.get('pull_data')
            if isinstance(pull_data, dict):
                stream_data = pull_data.get('stream_data')
                if isinstance(stream_data, str) and stream_data:
                    try:
                        parsed_stream_data = json.loads(stream_data)
                    except Exception:
                        parsed_stream_data = {}

                    data_section = parsed_stream_data.get('data') if isinstance(parsed_stream_data, dict) else None
                    if isinstance(data_section, dict):
                        for quality_data in data_section.values():
                            if not isinstance(quality_data, dict):
                                continue
                            main_stream = quality_data.get('main')
                            if not isinstance(main_stream, dict):
                                continue
                            for key in ('flv', 'hls', 'cmaf'):
                                value = main_stream.get(key)
                                if isinstance(value, str) and value:
                                    return value

        return None

    def resolve_live_info_sync(self, username: str, retry_count: int = 2) -> Dict:
        """Resolve room and stream info using TikTok webcast endpoints."""
        last_error = None

        for attempt in range(retry_count):
            try:
                session = self._create_session()
                live_page_url = f"https://www.tiktok.com/@{username}/live"
                html = session.get(live_page_url, timeout=20).text
                room_id = self._extract_room_id(html)
                stream_url = self._extract_stream_url_from_html(html)

                if not room_id:
                    raise RuntimeError("Could not extract room_id from TikTok live page")

                room_info_url = f'https://webcast.tiktok.com/webcast/room/info/?aid=1988&room_id={room_id}'
                room_info_response = session.get(room_info_url, timeout=20)
                room_info_data = room_info_response.json().get('data') or {}

                if not stream_url:
                    stream_url = self._extract_stream_url(room_info_data)
                stream_data_json = None
                viewers = None
                title = None

                stream_url_data = room_info_data.get('stream_url')
                if isinstance(stream_url_data, dict):
                    title = (
                        room_info_data.get('title')
                        or room_info_data.get('live_room_title')
                        or room_info_data.get('room_title')
                    )

                    live_core_sdk_data = stream_url_data.get('live_core_sdk_data')
                    if isinstance(live_core_sdk_data, dict):
                        pull_data = live_core_sdk_data.get('pull_data')
                        if isinstance(pull_data, dict):
                            stream_data_json = pull_data.get('stream_data')

                if isinstance(stream_data_json, str) and stream_data_json:
                    try:
                        parsed_stream_data = json.loads(stream_data_json)
                        common_data = parsed_stream_data.get('common', {}) if isinstance(parsed_stream_data, dict) else {}
                        if isinstance(common_data, dict):
                            viewers = common_data.get('user_count')
                        if not title and isinstance(parsed_stream_data, dict):
                            title = parsed_stream_data.get('title')
                    except Exception:
                        pass

                if viewers is None and isinstance(room_info_data.get('user_count'), (int, float)):
                    viewers = room_info_data.get('user_count')

                check_alive_url = (
                    'https://webcast.tiktok.com/webcast/room/check_alive/'
                    f'?aid=1988&region=CH&room_ids={room_id}&user_is_login=true'
                )
                check_alive_response = session.get(check_alive_url, timeout=20)
                check_alive_data = check_alive_response.json()
                live_entries = check_alive_data.get('data') or []
                room_alive = any(
                    isinstance(entry, dict) and entry.get('alive')
                    for entry in live_entries
                )

                stream_info = {
                    'stream_id': room_info_data.get('id') or room_id,
                    'title': title or room_info_data.get('title') or room_info_data.get('description') or 'TikTok Live',
                    'viewers': viewers,
                    'cover_image': room_info_data.get('cover') or room_info_data.get('cover_url'),
                    'stream_url': stream_url,
                    'live_status': 'is_live' if room_alive else 'offline',
                    'room_id': room_id,
                }

                return {
                    'username': username,
                    'is_live': bool(room_alive or stream_url),
                    'timestamp': datetime.now().isoformat(),
                    'room_id': room_id,
                    'stream_info': stream_info,
                    'error': None,
                    'source': 'webcast',
                }
            except Exception as e:
                last_error = str(e)
                logger.debug(f"Attempt {attempt + 1}/{retry_count} for @{username} failed: {last_error}")
                if attempt < retry_count - 1:
                    time.sleep(2)

        return {
            'username': username,
            'is_live': False,
            'timestamp': datetime.now().isoformat(),
            'stream_info': None,
            'error': last_error,
            'source': 'webcast',
        }

    def resolve_live_stream_url_sync(self, username: str, retry_count: int = 10) -> Optional[str]:
        """Resolve the live stream URL directly from TikTok webcast endpoints."""
        last_error = None
        session = None

        try:
            from curl_cffi import Session as CurlSession

            session = CurlSession(impersonate='chrome136', http_version='v1')
            session.headers.update(
                {
                    'Sec-Ch-Ua': '"Not/A)Brand";v="8", "Chromium";v="126"',
                    'Sec-Ch-Ua-Mobile': '?0',
                    'Sec-Ch-Ua-Platform': '"Windows"',
                    'Accept-Language': 'en-US',
                    'Upgrade-Insecure-Requests': '1',
                    'User-Agent': (
                        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.127 Safari/537.36'
                    ),
                    'Accept': (
                        'text/html,application/xhtml+xml,application/xml;q=0.9,'
                        'image/avif,image/webp,image/apng,application/json,text/plain,*/*;q=0.8,'
                        'application/signed-exchange;v=b3;q=0.7'
                    ),
                    'Sec-Fetch-Site': 'none',
                    'Sec-Fetch-Mode': 'navigate',
                    'Sec-Fetch-User': '?1',
                    'Sec-Fetch-Dest': 'document',
                    'Priority': 'u=0, i',
                    'Referer': 'https://www.tiktok.com/',
                    'Origin': 'https://www.tiktok.com',
                }
            )

            cookies_file = os.getenv('TIKTOK_COOKIES_FILE')
            if cookies_file and os.path.exists(cookies_file):
                jar = MozillaCookieJar(cookies_file)
                jar.load(ignore_discard=True, ignore_expires=True)
                session.cookies.update(jar)
        except Exception:
            session = self._create_session()

        for attempt in range(retry_count):
            try:
                live_page_url = f"https://www.tiktok.com/@{username}/live"
                html = session.get(live_page_url, timeout=20).text
                stream_url = self._extract_stream_url_from_html(html)

                if stream_url:
                    return stream_url

                room_id = self._extract_room_id(html)
                if not room_id:
                    raise RuntimeError("Could not extract room_id from TikTok live page")

                room_info_url = f'https://webcast.tiktok.com/webcast/room/info/?aid=1988&room_id={room_id}'
                room_info_response = session.get(room_info_url, timeout=20)
                room_info_data = room_info_response.json().get('data') or {}

                stream_url = self._extract_stream_url(room_info_data)
                if stream_url:
                    return stream_url

                last_error = f"No stream URL in room info (status={room_info_response.status_code})"
                logger.debug(
                    f"Attempt {attempt + 1}/{retry_count} for @{username} stream URL failed: {last_error}"
                )
                if attempt < retry_count - 1:
                    time.sleep(2)
            except Exception as e:
                last_error = str(e)
                logger.debug(f"Attempt {attempt + 1}/{retry_count} for @{username} stream URL failed: {last_error}")
                if attempt < retry_count - 1:
                    time.sleep(2)

        if session is not None:
            try:
                session.close()
            except Exception:
                pass

        logger.warning(f"Could not resolve stream URL for @{username}: {last_error}")
        return None
    
    def download_live_stream(self, live_url: str):
        """Generator that yields bytes chunks from a live stream URL."""
        session = None
        try:
            session = self._create_session()
            resp = session.get(live_url, stream=True, timeout=30)
            resp.raise_for_status()

            # requests-compatible iterator
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    yield chunk
        except Exception as e:
            logger.debug(f"Error streaming {live_url}: {e}")
            return
        finally:
            try:
                if session is not None:
                    session.close()
            except Exception:
                pass
    
    async def check_live_status(self, username: str) -> Optional[Dict]:
        """
        Check if a TikTok account is currently live
        Returns: Dict with live info if live, None otherwise
        """
        try:
            data = await asyncio.to_thread(self.resolve_live_info_sync, username)

            if not data or not data.get('is_live'):
                fallback = await asyncio.to_thread(self._check_live_sync, username)
                if fallback and fallback.get('is_live'):
                    data = fallback

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

    def get_room_id_from_user(self, user: str) -> Optional[str]:
        """Return the room_id for a given username, or None if not found."""
        try:
            data = self.resolve_live_info_sync(user, retry_count=3)
            if data and data.get('room_id'):
                return data.get('room_id')
        except Exception as e:
            logger.debug(f"get_room_id_from_user({user}) failed: {e}")
        return None

    def is_room_alive(self, room_id: str) -> bool:
        """Return True if the room_id corresponds to a live stream."""
        try:
            session = self._create_session()
            check_alive_url = (
                'https://webcast.tiktok.com/webcast/room/check_alive/'
                f'?aid=1988&region=CH&room_ids={room_id}&user_is_login=true'
            )
            resp = session.get(check_alive_url, timeout=15)
            data = resp.json()
            live_entries = data.get('data') or []
            return any(isinstance(entry, dict) and entry.get('alive') for entry in live_entries)
        except Exception as e:
            logger.debug(f"is_room_alive({room_id}) failed: {e}")
            return False

    def get_live_url(self, room_id: str) -> Optional[str]:
        """Return the CDN live URL (flv/m3u8/rtmp) for a room_id if available."""
        try:
            session = self._create_session()
            room_info_url = f'https://webcast.tiktok.com/webcast/room/info/?aid=1988&room_id={room_id}'
            resp = session.get(room_info_url, timeout=15)
            room_info_data = resp.json().get('data') or {}
            stream_url = self._extract_stream_url(room_info_data)
            if stream_url:
                return stream_url

            # Fallback: try to extract from page HTML if we can get username from owner
            owner = room_info_data.get('owner') or {}
            display_id = owner.get('display_id')
            if display_id:
                html = session.get(f'https://www.tiktok.com/@{display_id}/live', timeout=15).text
                return self._extract_stream_url_from_html(html)

        except Exception as e:
            logger.debug(f"get_live_url({room_id}) failed: {e}")
        return None

    def _check_live_sync(self, username: str, retry_count: int = 3) -> Dict:
        """Synchronous live status probe using yt-dlp with retry logic."""
        url = f"https://www.tiktok.com/@{username}/live"
        last_error = None
        
        for attempt in range(retry_count):
            try:
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                    'skip_download': True,
                    'noplaylist': True,
                    'socket_timeout': 10,
                    'socket_keepalive': True,
                    'concurrent_fragments': 1,
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    }
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)

                live_status = info.get('live_status')
                is_live = bool(info.get('is_live')) or live_status in ('is_live', 'is_upcoming', 'post_live')

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
            except yt_dlp.utils.UserNotLive as e:
                last_error = f"User not live: {str(e)}"
                logger.debug(f"Attempt {attempt + 1}/{retry_count}: {last_error}")
                if attempt < retry_count - 1:
                    time.sleep(2)  # Wait before retry
                continue
            except yt_dlp.utils.ExtractorError as e:
                last_error = f"Extractor error: {str(e)}"
                logger.debug(f"Attempt {attempt + 1}/{retry_count}: {last_error}")
                if attempt < retry_count - 1:
                    time.sleep(2)
                continue
            except Exception as e:
                last_error = str(e)
                logger.debug(f"Attempt {attempt + 1}/{retry_count}: {last_error}")
                if attempt < retry_count - 1:
                    time.sleep(2)
                continue
        
        # If all retries failed, return not live
        logger.warning(f"Could not determine live status for {username} after {retry_count} attempts. Last error: {last_error}")
        return {
            'username': username,
            'is_live': False,
            'timestamp': datetime.now().isoformat(),
            'stream_info': None,
            'error': last_error,
        }
    
    async def get_live_stream_url(self, username: str) -> Optional[str]:
        """Get the direct stream URL for downloading"""
        try:
            data = await asyncio.to_thread(self.resolve_live_info_sync, username)
            stream_url = data.get('stream_info', {}).get('stream_url') if data else None
            if stream_url:
                return stream_url

            fallback = await asyncio.to_thread(self._check_live_sync, username, retry_count=5)
            if fallback and fallback.get('is_live'):
                return fallback.get('stream_info', {}).get('stream_url')

            logger.warning(
                f"Could not get stream URL for {username}: not live or error - {data.get('error', 'unknown') if data else 'unknown'}"
            )
            return None
        except Exception as e:
            logger.error(f"Error getting stream URL for {username}: {e}")
            return None
    
    def close(self):
        """Close the session"""
        return None
