#!/usr/bin/env python3
"""Test the download flow by monkeypatching yt_dlp to avoid network.

This simulates `yt_dlp.YoutubeDL` behavior so we can verify `download_live()` logic.
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from bot import TikTokLiveBot


class DummyYDL:
    def __init__(self, opts):
        self.opts = opts

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def extract_info(self, url, download=True):
        # Simulate metadata returned by yt-dlp
        return {'id': 'sim123', 'ext': 'mp4', 'title': 'simulated', 'requested_formats': []}

    def prepare_filename(self, info):
        return os.path.join('downloads', f"{info.get('id')}.{info.get('ext')}")


async def main():
    # Create a bot instance without a DB (we only test download_live)
    bot = TikTokLiveBot(None)

    # Monkeypatch yt_dlp.YoutubeDL
    import yt_dlp
    orig = yt_dlp.YoutubeDL
    yt_dlp.YoutubeDL = DummyYDL

    try:
        path = await bot.download_live('test_account_sim')
        print('Simulated download path:', path)
    finally:
        yt_dlp.YoutubeDL = orig


if __name__ == '__main__':
    asyncio.run(main())
