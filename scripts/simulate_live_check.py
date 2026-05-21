#!/usr/bin/env python3
"""Simulate a live check for a test TikTok account.

Creates a test account in the DB and fakes the monitor check to return a live.
Run with the project's virtualenv active.
"""
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import sys
import os

load_dotenv()

# Ensure project root is on sys.path so imports from project work when running from scripts/
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database import TikTokDatabase
from bot import TikTokLiveBot

async def main():
    db_url = None
    try:
        db = TikTokDatabase(None)
    except TypeError:
        # fallback if constructor requires url
        from os import getenv
        db = TikTokDatabase(getenv('DATABASE_URL'))

    username = 'test_account_sim'

    # Try connecting to DB; if it fails, fall back to in-memory simulation
    connected = False
    try:
        await db.connect()
        connected = True
    except Exception as e:
        print('DB connect failed, continuing with in-memory simulation:', e)

    bot = TikTokLiveBot(db if connected else None)

    # Fake the monitor check to always return a live for our test account
    async def fake_check(u):
        if u == username:
            return {
                'username': username,
                'is_live': True,
                'timestamp': datetime.utcnow().isoformat(),
                'stream_info': {'viewers': 42, 'title': 'Simulation Live'}
            }
        return {'username': u, 'is_live': False}

    bot.monitor.check_live_status = fake_check

    # If DB connected, insert test account and run bot.check_all_accounts()
    if connected:
        await db.add_account(username)
        lives = await bot.check_all_accounts()
        print('Detected live accounts (DB):', lives)

        # Close DB pool
        try:
            await db.pool.close()
        except Exception:
            pass
    else:
        # In-memory simulation: run fake_check directly
        res = await fake_check(username)
        print('Detected live accounts (in-memory):', [res] if res.get('is_live') else [])

if __name__ == '__main__':
    asyncio.run(main())
