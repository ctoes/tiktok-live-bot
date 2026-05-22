import asyncpg
import logging
from datetime import datetime
from typing import List, Optional, Dict
import os

logger = logging.getLogger(__name__)

class TikTokDatabase:
    """PostgreSQL Database handler for TikTok accounts"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool = None
    
    async def connect(self):
        """Connect to Neon PostgreSQL database"""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            logger.info("Connected to Neon PostgreSQL")
            await self._create_tables()
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from database"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection closed")
    
    async def _create_tables(self):
        """Create necessary tables if they don't exist"""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS accounts (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    user_id TEXT,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_checked TIMESTAMP,
                    is_live BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS live_history (
                    id SERIAL PRIMARY KEY,
                    account_id INTEGER REFERENCES accounts(id),
                    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ended_at TIMESTAMP,
                    viewers_count INTEGER,
                    stream_title TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            ''')
            
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS bot_users (
                    id SERIAL PRIMARY KEY,
                    telegram_user_id INTEGER UNIQUE NOT NULL,
                    telegram_username TEXT,
                    telegram_chat_id INTEGER,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            ''')
            
            logger.info("Database tables initialized")
    
    # ACCOUNT OPERATIONS
    
    async def add_account(self, username: str) -> bool:
        """Add a TikTok account to monitor"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    '''INSERT INTO accounts (username) VALUES ($1)''',
                    username.lower()
                )
            logger.info(f"Added account: {username}")
            return True
        except asyncpg.UniqueViolationError:
            logger.warning(f"Account {username} already exists")
            return False
        except Exception as e:
            logger.error(f"Error adding account {username}: {e}")
            return False
    
    async def remove_account(self, username: str) -> bool:
        """Remove a TikTok account from monitoring"""
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute(
                    '''DELETE FROM accounts WHERE username = $1''',
                    username.lower()
                )
            
            # Check if any rows were deleted
            if result.endswith('1'):
                logger.info(f"Removed account: {username}")
                return True
            else:
                logger.warning(f"Account {username} not found")
                return False
        except Exception as e:
            logger.error(f"Error removing account {username}: {e}")
            return False
    
    async def get_all_accounts(self) -> List[Dict]:
        """Get all monitored accounts"""
        try:
            async with self.pool.acquire() as conn:
                accounts = await conn.fetch('SELECT * FROM accounts ORDER BY username')
            
            return [
                {
                    'id': acc['id'],
                    'username': acc['username'],
                    'user_id': acc['user_id'],
                    'added_date': acc['added_date'],
                    'last_checked': acc['last_checked'],
                    'is_live': acc['is_live']
                } for acc in accounts
            ]
        except Exception as e:
            logger.error(f"❌ Error fetching accounts: {e}")
            return []
    
    async def get_account(self, username: str) -> Optional[Dict]:
        """Get a specific account"""
        try:
            async with self.pool.acquire() as conn:
                account = await conn.fetchrow(
                    'SELECT * FROM accounts WHERE username = $1',
                    username.lower()
                )
            
            if account:
                return {
                    'id': account['id'],
                    'username': account['username'],
                    'user_id': account['user_id'],
                    'added_date': account['added_date'],
                    'last_checked': account['last_checked'],
                    'is_live': account['is_live']
                }
            return None
        except Exception as e:
            logger.error(f"❌ Error fetching account {username}: {e}")
            return None
    
    async def update_account_status(self, username: str, is_live: bool, 
                                   viewer_count: Optional[int] = None) -> bool:
        """Update account live status"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    '''UPDATE accounts 
                       SET is_live = $1, last_checked = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP
                       WHERE username = $2''',
                    is_live,
                    username.lower()
                )
            return True
        except Exception as e:
            logger.error(f"❌ Error updating account {username}: {e}")
            return False
    
    async def account_exists(self, username: str) -> bool:
        """Check if account exists"""
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchrow(
                    'SELECT id FROM accounts WHERE username = $1',
                    username.lower()
                )
            return result is not None
        except Exception as e:
            logger.error(f"❌ Error checking account existence: {e}")
            return False
    
    # LIVE HISTORY OPERATIONS
    
    async def add_live_session(self, username: str, viewers: Optional[int] = None,
                              title: Optional[str] = None) -> bool:
        """Record a live session"""
        try:
            async with self.pool.acquire() as conn:
                # Get account id
                account = await conn.fetchrow(
                    'SELECT id FROM accounts WHERE username = $1',
                    username.lower()
                )
                
                if not account:
                    return False
                
                await conn.execute(
                    '''INSERT INTO live_history (account_id, viewers_count, stream_title)
                       VALUES ($1, $2, $3)''',
                    account['id'],
                    viewers,
                    title
                )
            logger.info(f"📝 Recorded live session for {username}")
            return True
        except Exception as e:
            logger.error(f"❌ Error recording live session: {e}")
            return False
    
    async def get_live_history(self, username: str, limit: int = 10) -> List[Dict]:
        """Get live history for an account"""
        try:
            async with self.pool.acquire() as conn:
                sessions = await conn.fetch(
                    '''SELECT lh.* FROM live_history lh
                       JOIN accounts a ON lh.account_id = a.id
                       WHERE a.username = $1
                       ORDER BY lh.started_at DESC
                       LIMIT $2''',
                    username.lower(),
                    limit
                )
            
            return [
                {
                    'started_at': session['started_at'],
                    'ended_at': session['ended_at'],
                    'viewers_count': session['viewers_count'],
                    'stream_title': session['stream_title'],
                } for session in sessions
            ]
        except Exception as e:
            logger.error(f"❌ Error fetching live history: {e}")
            return []
    
    # BOT USER OPERATIONS
    
    async def add_bot_user(self, telegram_user_id: int, 
                          telegram_username: Optional[str] = None,
                          telegram_chat_id: Optional[int] = None) -> bool:
        """Add a Telegram user to the bot"""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    '''INSERT INTO bot_users (telegram_user_id, telegram_username, telegram_chat_id)
                       VALUES ($1, $2, $3)
                       ON CONFLICT (telegram_user_id) DO UPDATE SET
                       telegram_username = $2, telegram_chat_id = $3, updated_at = CURRENT_TIMESTAMP''',
                    telegram_user_id,
                    telegram_username,
                    telegram_chat_id
                )
            return True
        except Exception as e:
            logger.error(f"❌ Error adding bot user: {e}")
            return False
    
    async def get_bot_users(self) -> List[int]:
        """Get all active bot users"""
        try:
            async with self.pool.acquire() as conn:
                users = await conn.fetch(
                    'SELECT telegram_chat_id FROM bot_users WHERE is_active = TRUE'
                )
            return [user['telegram_chat_id'] for user in users if user['telegram_chat_id']]
        except Exception as e:
            logger.error(f"❌ Error fetching bot users: {e}")
            return []
    
    # STATISTICS
    
    async def get_stats(self) -> Dict:
        """Get database statistics"""
        try:
            async with self.pool.acquire() as conn:
                accounts_count = await conn.fetchval('SELECT COUNT(*) FROM accounts')
                live_accounts = await conn.fetchval('SELECT COUNT(*) FROM accounts WHERE is_live = TRUE')
                total_live_sessions = await conn.fetchval('SELECT COUNT(*) FROM live_history')
                bot_users_count = await conn.fetchval('SELECT COUNT(*) FROM bot_users WHERE is_active = TRUE')
            
            return {
                'total_accounts': accounts_count,
                'live_accounts': live_accounts,
                'total_live_sessions': total_live_sessions,
                'bot_users': bot_users_count
            }
        except Exception as e:
            logger.error(f"❌ Error fetching stats: {e}")
            return {
                'total_accounts': 0,
                'live_accounts': 0,
                'total_live_sessions': 0,
                'bot_users': 0
            }
