import asyncio
import asyncpg
import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_l7K2xPCoahAj@ep-lingering-lab-apg6yogu-pooler.c-7.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require",
)


CREATE_TABLES_SQL = [
    """
    CREATE TABLE IF NOT EXISTS accounts (
        id SERIAL PRIMARY KEY,
        username VARCHAR(255) UNIQUE NOT NULL,
        user_id BIGINT,
        added_date TIMESTAMPTZ DEFAULT now(),
        last_checked TIMESTAMPTZ,
        is_live BOOLEAN DEFAULT FALSE,
        created_at TIMESTAMPTZ DEFAULT now(),
        updated_at TIMESTAMPTZ DEFAULT now()
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS live_history (
        id SERIAL PRIMARY KEY,
        account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE,
        started_at TIMESTAMPTZ,
        ended_at TIMESTAMPTZ,
        viewers_count INTEGER,
        stream_title TEXT
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS bot_users (
        id SERIAL PRIMARY KEY,
        telegram_user_id BIGINT UNIQUE NOT NULL,
        telegram_username VARCHAR(255),
        telegram_chat_id BIGINT,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMPTZ DEFAULT now()
    );
    """,
]


async def main():
    print("Connecting to database...")
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        for sql in CREATE_TABLES_SQL:
            await conn.execute(sql)
        print("Tables créées ou déjà existantes.")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
