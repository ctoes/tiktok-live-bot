#!/usr/bin/env python3
import os
import sys
import asyncio
import traceback

try:
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

import asyncpg

async def main(dsn):
    try:
        print('Attempting asyncpg.connect() to:', dsn)
        conn = await asyncio.wait_for(asyncpg.connect(dsn), timeout=15)
        try:
            val = await conn.fetchval('SELECT 1')
            print('Connected successfully, test query returned:', val)
        finally:
            await conn.close()
    except Exception as e:
        print('Connection failed:')
        traceback.print_exc()

if __name__ == '__main__':
    dsn = os.getenv('DATABASE_URL')
    if len(sys.argv) > 1:
        dsn = sys.argv[1]
    if not dsn:
        print('DATABASE_URL not provided via env or arg')
        sys.exit(2)
    asyncio.run(main(dsn))
