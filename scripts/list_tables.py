import asyncio
import asyncpg
import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://neondb_owner:npg_l7K2xPCoahAj@ep-lingering-lab-apg6yogu-pooler.c-7.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require",
)


async def main():
    print("Connecting to database...")
    conn = await asyncpg.connect(DATABASE_URL)
    try:
        rows = await conn.fetch(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema='public'
            ORDER BY table_name;
            """
        )
        if not rows:
            print("Aucune table trouvée dans le schéma public.")
            return

        for r in rows:
            t = r["table_name"]
            try:
                cnt = await conn.fetchval(f"SELECT COUNT(*) FROM \"{t}\";")
            except Exception:
                cnt = "?"
            print(f"{t}: {cnt} rows")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(main())
