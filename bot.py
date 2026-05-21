#!/usr/bin/env python3
"""
TikTok Live Monitor Bot - Telegram Integration
Monitors TikTok accounts for live streams and sends them to Telegram
"""

import os
import logging
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from pathlib import Path
import yt_dlp
import threading
import subprocess
import signal

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, ConversationHandler, CallbackQueryHandler
)

from tiktok_monitor import TikTokMonitor
from database import TikTokDatabase

# Load environment variables
load_dotenv()

# Ensure stdout/stderr use UTF-8 on Windows consoles to avoid logging errors
import sys
try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Setup logging
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuration
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = int(os.getenv('TELEGRAM_CHAT_ID', '0'))
DATABASE_URL = os.getenv('DATABASE_URL')
MONITOR_INTERVAL = 300  # 5 minutes

# Conversation states
WAITING_FOR_USERNAME = 1

# Download tracking - maps chat_id to active download info
# {chat_id: {'username': str, 'stop_flag': bool, 'filepath': str, 'thread': Thread, 'process': Popen}}

class TikTokLiveBot:
    def __init__(self, db: TikTokDatabase):
        self.monitor = TikTokMonitor()
        self.db = db
        self.active_lives = set()
        self.logger = logger
    
    async def add_account(self, username: str) -> bool:
        """Add a TikTok account to monitor"""
        # Validate username format
        if not username or len(username) < 2:
            return False
        
        success = await self.db.add_account(username)
        if success:
            self.logger.info(f"✅ Added account: {username}")
        return success
    
    async def remove_account(self, username: str) -> bool:
        """Remove a TikTok account from monitoring"""
        success = await self.db.remove_account(username)
        if success:
            self.logger.info(f"✅ Removed account: {username}")
        return success
    
    async def get_live_accounts(self) -> list:
        """Get list of currently monitored accounts"""
        return await self.db.get_all_accounts()
    
    async def check_all_accounts(self) -> list:
        """Check all accounts for live status"""
        live_accounts = []
        accounts = await self.db.get_all_accounts()
        
        for account in accounts:
            username = account['username']
            result = await self.monitor.check_live_status(username)
            
            if result and result.get('is_live'):
                live_accounts.append(result)
                
                # Update account status in database
                await self.db.update_account_status(username, True)
                
                # Record live session
                viewers = result.get('stream_info', {}).get('viewers')
                title = result.get('stream_info', {}).get('title')
                await self.db.add_live_session(username, viewers, title)
                
                # Check if this is a new live session
                if username not in self.active_lives:
                    self.active_lives.add(username)
                    self.logger.info(f"🎬 NEW LIVE: {username}")
            else:
                # Mark as not live if it was before
                await self.db.update_account_status(username, False)
                
                if username in self.active_lives:
                    self.active_lives.discard(username)
                    self.logger.info(f"🛑 LIVE ENDED: {username}")
        
        return live_accounts
    
    async def download_live(self, username: str, chat_id: int = None) -> str:
        """Download the live stream with cancellation support"""
        try:
            url = f"https://www.tiktok.com/@{username}/live"
            
            ydl_opts = {
                'format': 'best',
                'quiet': False,
                'no_warnings': False,
                'outtmpl': f'downloads/%(username)s_%(id)s.%(ext)s',
                'socket_timeout': 10,
                'fragment_timeout': 10,
            }
            
            os.makedirs('downloads', exist_ok=True)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.logger.info(f"Starting download for {username}...")
                info = ydl.extract_info(url, download=True)
                filepath = ydl.prepare_filename(info)
                self.logger.info(f"Downloaded: {filepath}")
                return filepath
        
        except Exception as e:
            self.logger.error(f"Error downloading live from {username}: {e}")
            return None
    
    def download_live_blocking(self, username: str, chat_id: int = None) -> str:
        """Blocking version for download_live (runs in thread)"""
        try:
            url = f"https://www.tiktok.com/@{username}/live"
            
            ydl_opts = {
                'format': 'best',
                'quiet': False,
                'no_warnings': False,
                'outtmpl': f'downloads/%(username)s_%(id)s.%(ext)s',
                'socket_timeout': 10,
                'fragment_timeout': 10,
            }
            
            os.makedirs('downloads', exist_ok=True)
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                self.logger.info(f"Starting download for {username}...")
                info = ydl.extract_info(url, download=True)
                filepath = ydl.prepare_filename(info)
                self.logger.info(f"Downloaded: {filepath}")
                return filepath
        
        except Exception as e:
            self.logger.error(f"Error downloading live from {username}: {e}")
            return None

# Initialize bot
bot = None
app = None

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    keyboard = [
        [InlineKeyboardButton("➕ Ajouter Compte", callback_data='add')],
        [InlineKeyboardButton("➖ Retirer Compte", callback_data='remove')],
        [InlineKeyboardButton("📋 Lister Comptes", callback_data='list')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎬 **TikTok Live Monitor Bot**\n\n"
        "Je monitore les comptes TikTok et vous envoie les lives sur Telegram.\n\n"
        "Choisissez une action:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    help_text = """
🎬 **Commandes Disponibles:**

/start - Menu principal
/add_account - Ajouter un compte TikTok
/remove_account - Retirer un compte TikTok
/list_accounts - Voir tous les comptes monitores
/status - Voir le statut du monitoring
/download_live - Télécharger un live TikTok
/stop_download - Arrêter le téléchargement en cours
/help - Cette aide

**Commandes rapides:**
/add username - Ajouter directement un compte
/remove username - Retirer directement un compte
/download_live @username - Télécharger un live
/download @username - Alias court pour /download_live
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def list_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all monitored accounts"""
    accounts = await bot.get_live_accounts()

    # Determine where to send the reply: message or callback_query.message
    target = None
    if hasattr(update, 'message') and update.message:
        target = update.message
    elif hasattr(update, 'callback_query') and update.callback_query and update.callback_query.message:
        target = update.callback_query.message

    if not accounts:
        if target:
            await target.reply_text("❌ Aucun compte en cours de monitoring.")
        return

    message = "📋 **Comptes en Monitoring:**\n\n"
    for i, acc in enumerate(accounts, 1):
        status = "🔴 LIVE" if acc.get('is_live') else "⚪ Offline"
        last_check = acc.get('last_checked', 'Jamais')
        if last_check != 'Jamais' and last_check:
            last_check = str(last_check).split('T')[1].split('.')[0] if 'T' in str(last_check) else str(last_check)

        message += f"{i}. @{acc['username']} - {status} (Vérif: {last_check})\n"

    # If called from a CallbackQuery, prefer editing the message or answering the query
    if hasattr(update, 'callback_query') and update.callback_query:
        query = update.callback_query
        if query.message:
            await query.edit_message_text(message, parse_mode='Markdown')
        else:
            await query.answer(message, show_alert=True)
        return

    if target:
        await target.reply_text(message, parse_mode='Markdown')

async def add_account_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add account command"""
    # Check if username provided
    if context.args:
        username = context.args[0].lstrip('@')
        success = await bot.add_account(username)
        if success:
            await update.message.reply_text(f"✅ Compte @{username} ajouté avec succès!")
        else:
            await update.message.reply_text(f"❌ Le compte @{username} existe déjà ou est invalide.")
    else:
        await update.message.reply_text(
            "📝 Envoyez le nom d'utilisateur TikTok à ajouter (sans @):"
        )
        return WAITING_FOR_USERNAME

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    username = update.message.text.lstrip('@').strip()
    
    if not username:
        await update.message.reply_text("⚠️ Nom d'utilisateur invalide.")
        return
    
    success = await bot.add_account(username)
    if success:
        await update.message.reply_text(f"✅ Compte @{username} ajouté!")
    else:
        await update.message.reply_text(f"❌ Le compte @{username} existe déjà.")

async def remove_account_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Remove account command"""
    if context.args:
        username = context.args[0].lstrip('@')
        success = await bot.remove_account(username)
        if success:
            await update.message.reply_text(f"✅ Compte @{username} retiré!")
        else:
            await update.message.reply_text(f"❌ Compte @{username} non trouvé.")
    else:
        accounts = await bot.get_live_accounts()
        if not accounts:
            await update.message.reply_text("❌ Aucun compte à retirer.")
            return
        
        keyboard = [
            [InlineKeyboardButton(f"@{acc['username']}", callback_data=f"del_{acc['username']}")]
            for acc in accounts[:10]  # Max 10 buttons
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Quel compte retirer?",
            reply_markup=reply_markup
        )

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show bot status"""
    accounts = await bot.get_live_accounts()
    live_count = len([a for a in accounts if a.get('is_live')])
    total_count = len(accounts)
    
    status_text = f"""
📊 **Statut du Bot:**

✅ Bot en ligne
📡 Vérification: Toutes les {MONITOR_INTERVAL}s
📺 Comptes monitores: {total_count}
🔴 Comptes en live: {live_count}
    """
    
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def download_live_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Download a live stream"""
    chat_id = update.effective_chat.id
    
    if not context.args:
        await update.message.reply_text(
            "📥 **Télécharger un Live TikTok**\n\n"
            "Utilisation: `/download_live @username`\n\n"
            "Exemple: `/download_live @tiktok`\n\n"
            "Pour arrêter le téléchargement: `/stop_download`",
            parse_mode='Markdown'
        )
        return
    
    username = context.args[0].lstrip('@').strip()
    
    if not username:
        await update.message.reply_text("⚠️ Nom d'utilisateur invalide.")
        return
    
    # Check if download already in progress
    if chat_id in active_downloads:
        await update.message.reply_text("⚠️ Un téléchargement est déjà en cours. Utilisez `/stop_download` pour l'arrêter.")
        return
    
    # Notify user that download is starting
    msg = await update.message.reply_text(
        f"⏳ Téléchargement du live de @{username}...\n\n"
        "Cela peut prendre quelques minutes...\n\n"
        "Tapez `/stop_download` pour arrêter"
    )
    
    # Function to run download in thread
    def run_download():
        try:
            filepath = bot.download_live_blocking(username, chat_id)
            active_downloads[chat_id]['filepath'] = filepath
            active_downloads[chat_id]['completed'] = True
        except Exception as e:
            logger.error(f"Download thread error: {e}")
            active_downloads[chat_id]['error'] = str(e)
    
    # Track this download
    download_thread = threading.Thread(target=run_download, daemon=False)
    download_thread.start()
    
    active_downloads[chat_id] = {
        'username': username,
        'stop_flag': False,
        'filepath': None,
        'message_id': msg.message_id,
        'thread': download_thread,
        'completed': False,
        'error': None
    }
    
    # Wait for download to complete or be stopped
    await asyncio.sleep(0.5)  # Give thread a moment to start
    
    max_wait = 3600  # 1 hour max
    elapsed = 0
    check_interval = 2
    
    while elapsed < max_wait:
        if chat_id not in active_downloads:
            break
            
        dl_info = active_downloads[chat_id]
        
        if dl_info.get('stop_flag') or dl_info.get('completed') or dl_info.get('error'):
            break
        
        await asyncio.sleep(check_interval)
        elapsed += check_interval
    
    # Process result
    if chat_id not in active_downloads:
        return
    
    dl_info = active_downloads[chat_id]
    filepath = dl_info.get('filepath')
    was_stopped = dl_info.get('stop_flag', False)
    error = dl_info.get('error')
    
    try:
        if error:
            await msg.edit_text(
                f"❌ Erreur: {error}\n\n"
                "Vérifiez que le compte est en live.",
                parse_mode='Markdown'
            )
        elif filepath and os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            status_text = "⏸️ Arrêté" if was_stopped else "✅"
            
            # Try to send the file
            try:
                with open(filepath, 'rb') as f:
                    await msg.edit_text(f"📥 Envoi du fichier {status_text}...", parse_mode='Markdown')
                    await update.message.reply_document(f)
                
                # Clean up - delete the file after sending
                try:
                    os.remove(filepath)
                except Exception as e:
                    logger.warning(f"Could not delete file {filepath}: {e}")
                
                await msg.edit_text(
                    f"{status_text} Live de @{username} téléchargé et envoyé!\n\n"
                    f"📁 Fichier: `{os.path.basename(filepath)}`\n"
                    f"📊 Taille: `{file_size / (1024*1024):.1f}MB`",
                    parse_mode='Markdown'
                )
            except Exception as e:
                # If file sending fails (too large, etc), just report the path
                logger.error(f"Could not send file: {e}")
                await msg.edit_text(
                    f"{status_text} Live de @{username} téléchargé!\n\n"
                    f"📁 Fichier: `{filepath}`\n"
                    f"📊 Taille: `{file_size / (1024*1024):.1f}MB`\n"
                    f"⚠️ Trop volumineux pour Telegram (limite: 50MB)",
                    parse_mode='Markdown'
                )
        else:
            await msg.edit_text(
                f"❌ Impossible de télécharger le live de @{username}.\n\n"
                "Possible causes:\n"
                "• Le compte n'est pas en live maintenant\n"
                "• Le compte n'existe pas\n"
                "• Erreur réseau",
                parse_mode='Markdown'
            )
    except Exception as e:
        logger.error(f"Error processing download result: {e}")
    finally:
        # Clean up tracking
        if chat_id in active_downloads:
            del active_downloads[chat_id]

async def stop_download_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop current download"""
    chat_id = update.effective_chat.id
    
    if chat_id not in active_downloads:
        await update.message.reply_text(
            "❌ Aucun téléchargement en cours pour ce chat.",
            parse_mode='Markdown'
        )
        return
    
    # Set the stop flag
    active_downloads[chat_id]['stop_flag'] = True
    username = active_downloads[chat_id].get('username', 'inconnu')
    
    await update.message.reply_text(
        f"⏹️ Arrêt du téléchargement de @{username}...\n\n"
        "Le fichier partiellement téléchargé sera envoyé.",
        parse_mode='Markdown'
    )
    
    # Wait a bit for the download to stop
    await asyncio.sleep(3)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'add':
        await query.edit_message_text("Envoyez le nom d'utilisateur TikTok à ajouter:")
        return WAITING_FOR_USERNAME
    elif query.data == 'remove':
        accounts = await bot.get_live_accounts()
        if not accounts:
            await query.edit_message_text("❌ Aucun compte à retirer.")
            return
        
        keyboard = [
            [InlineKeyboardButton(f"@{acc['username']}", callback_data=f"del_{acc['username']}")]
            for acc in accounts[:10]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Quel compte retirer?", reply_markup=reply_markup)
    elif query.data == 'list':
        await list_accounts(update, context)
    elif query.data.startswith('del_'):
        username = query.data.replace('del_', '')
        success = await bot.remove_account(username)
        if success:
            await query.edit_message_text(f"✅ Compte @{username} retiré!")
        else:
            await query.edit_message_text(f"❌ Impossible de retirer @{username}")

async def monitoring_loop(application: Application):
    """Main monitoring loop - checks accounts every 5 minutes"""
    while True:
        try:
            logger.info("🔍 Vérification des comptes...")
            live_accounts = await bot.check_all_accounts()
            
            if live_accounts:
                for live_info in live_accounts:
                    username = live_info['username']
                    
                    message = f"""
🎬 **@{username} EST EN LIVE!**

⏰ {live_info['timestamp']}
"""
                    
                    if live_info.get('stream_info'):
                        info = live_info['stream_info']
                        if info.get('viewers'):
                            message += f"👥 Spectateurs: {info['viewers']}\n"
                        if info.get('title'):
                            message += f"📝 Titre: {info['title']}\n"
                    
                    message += f"\n[Ouvrir sur TikTok](https://www.tiktok.com/@{username}/live)"
                    
                    # Send to main chat
                    try:
                        if CHAT_ID:
                            await application.bot.send_message(
                                chat_id=CHAT_ID,
                                text=message,
                                parse_mode='Markdown',
                                disable_web_page_preview=False
                            )
                    except Exception as e:
                        logger.error(f"Erreur d'envoi du message: {e}")
            
            await asyncio.sleep(MONITOR_INTERVAL)
        
        except Exception as e:
            logger.error(f"Erreur dans la boucle de monitoring: {e}")
            await asyncio.sleep(60)  # Retry after 1 minute on error

async def post_init(application: Application):
    """Initialize after bot starts"""
    try:
        # Connect to database
        await application.bot_db.connect()
        
        # Start monitoring loop
        asyncio.create_task(monitoring_loop(application))
        logger.info("✅ Bot démarré et prêt à monitorer!")
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation: {e}")
        raise

def main():
    """Start the bot"""
    global app, bot
    
    if not TOKEN or TOKEN == 'your_telegram_bot_token_here':
        logger.error("❌ TELEGRAM_BOT_TOKEN non configuré dans .env")
        return
    
    if not DATABASE_URL or DATABASE_URL == 'your_database_url_here':
        logger.error("❌ DATABASE_URL non configuré dans .env")
        return
    
    # Initialize database
    db = TikTokDatabase(DATABASE_URL)
    
    # Initialize bot with database
    bot = TikTokLiveBot(db)
    
    # Create application
    app = Application.builder().token(TOKEN).post_init(post_init).build()
    
    # Store db reference in app for shutdown
    app.bot_db = db
    
    # Add conversation handler for adding accounts
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('add_account', add_account_command),
            CallbackQueryHandler(button_callback, pattern='^add$')
        ],
        states={
            WAITING_FOR_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler)]
        },
        fallbacks=[CommandHandler('cancel', lambda u, c: None)]
    )
    
    # Add handlers
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('list_accounts', list_accounts))
    app.add_handler(CommandHandler('status', status_command))
    app.add_handler(CommandHandler('add', add_account_command))
    app.add_handler(CommandHandler('remove', remove_account_command))
    app.add_handler(CommandHandler('download_live', download_live_command))
    app.add_handler(CommandHandler('download', download_live_command))
    app.add_handler(CommandHandler('stop_download', stop_download_command))
    app.add_handler(CommandHandler('stop', stop_download_command))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(button_callback))
    
    # Run bot
    logger.info("🚀 Démarrage du TikTok Live Monitor Bot...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
