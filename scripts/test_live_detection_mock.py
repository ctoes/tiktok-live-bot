#!/usr/bin/env python3
import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import tiktok_monitor as monitor_module


class FakeYDL:
    def __init__(self, opts):
        self.opts = opts

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def extract_info(self, url, download=False):
        return {
            'id': 'live123',
            'title': 'Mock Live',
            'is_live': True,
            'live_status': 'is_live',
            'concurrent_view_count': 42,
            'thumbnail': 'https://example.com/thumb.jpg',
            'url': 'https://example.com/stream.m3u8',
        }


def fake_resolve_live_info_sync(self, username, retry_count=2):
    return {
        'username': username,
        'is_live': True,
        'timestamp': '2026-01-01T00:00:00',
        'room_id': '1234567890',
        'stream_info': {
            'stream_id': 'live123',
            'title': 'Mock Live',
            'viewers': 42,
            'cover_image': 'https://example.com/thumb.jpg',
            'stream_url': 'https://example.com/stream.m3u8',
            'live_status': 'is_live',
            'room_id': '1234567890',
        },
        'error': None,
        'source': 'webcast',
    }


async def main():
    original = monitor_module.TikTokMonitor.resolve_live_info_sync
    monitor_module.yt_dlp.YoutubeDL = FakeYDL
    monitor_module.TikTokMonitor.resolve_live_info_sync = fake_resolve_live_info_sync
    try:
        monitor = monitor_module.TikTokMonitor()
        result = await monitor.check_live_status('beautybasetv')
        assert result is not None, 'result is None'
        assert result['is_live'] is True, 'is_live false'
        assert result['stream_info']['title'] == 'Mock Live', 'bad title'
        assert result['stream_info']['viewers'] == 42, 'bad viewers'
        print('PASS: live detection mock returns live')
    finally:
        monitor_module.yt_dlp.YoutubeDL = FakeYDL if False else original
        monitor_module.TikTokMonitor.resolve_live_info_sync = original


if __name__ == '__main__':
    asyncio.run(main())
