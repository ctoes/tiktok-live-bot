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
import glob

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
# Setup logging with UTF-8 file handler and stdout stream handler
file_handler = logging.FileHandler('logs/bot.log', encoding='utf-8')
stream_handler = logging.StreamHandler(sys.stdout)
logging.basicConfig(
    level=os.getenv('LOG_LEVEL', 'INFO'),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[file_handler, stream_handler]
)
logger = logging.getLogger(__name__)

# Configuration
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = int(os.getenv('TELEGRAM_CHAT_ID', '0'))
DATABASE_URL = os.getenv('DATABASE_URL')
MONITOR_INTERVAL = 300  # 5 minutes

# Conversation states
WAITING_FOR_USERNAME = 1

# Recording tracking - maps chat_id to active recording info
# {chat_id: {'username': str, 'process': Popen, 'output_prefix': str, 'stop_flag': bool, 'task': Task}}
active_recordings = {}

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
              self.logger.info(f"Added account: {username}")
        return success
    
    async def remove_account(self, username: str) -> bool:
        """Remove a TikTok account from monitoring"""
        success = await self.db.remove_account(username)
        if success:
              self.logger.info(f"Removed account: {username}")
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
                    self.logger.info(f"NEW LIVE: {username}")
            else:
                # Mark as not live if it was before
                await self.db.update_account_status(username, False)
                
                if username in self.active_lives:
                    self.active_lives.discard(username)
                    self.logger.info(f"LIVE ENDED: {username}")
        
        return live_accounts
    
    def start_recording_process(self, username: str, chat_id: int) -> subprocess.Popen | None:
        """Start a yt-dlp recording process so it can be stopped."""
        os.makedirs('downloads', exist_ok=True)
        os.makedirs(os.path.join('logs', 'recordings'), exist_ok=True)

        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        output_prefix = os.path.join('downloads', f'{username}_{timestamp}')
        output_template = f'{output_prefix}.%(ext)s'
        log_path = os.path.join('logs', 'recordings', f'{username}_{chat_id}_{timestamp}.log')

        # Prepare log file early so direct-recording path can reference it
        log_file = open(log_path, 'w', encoding='utf-8')

        try:
            url = f"https://www.tiktok.com/@{username}/live"
            try:
                direct_stream_url = self.monitor.resolve_live_stream_url_sync(username)
                if direct_stream_url:
                    url = direct_stream_url
                    self.logger.info(f"Using direct TikTok stream URL for @{username}")
            except Exception as e:
                self.logger.debug(f"Could not resolve direct stream URL for @{username}: {e}")

            # If we have a direct CDN URL, prefer a lightweight direct recorder
            if url and (url.startswith('http') and ('pull' in url or url.endswith('.flv') or '.m3u8' in url)):
                try:
                    out_file_path = f"{output_prefix}.flv"
                    thread = threading.Thread(
                        target=self._direct_recording_worker,
                        args=(username, url, out_file_path, chat_id),
                        daemon=True,
                    )
                    thread.start()

                    active_recordings[chat_id] = {
                        'username': username,
                        'process': None,
                        'thread': thread,
                        'stop_flag': False,
                        'filepath': output_prefix,
                        'output_path': out_file_path,
                        'log_path': log_path,
                        'log_file': log_file,
                        'task': None,
                    }
                    self.logger.info(f"Direct recording thread started for @{username}")
                    return None
                except Exception as e:
                    self.logger.warning(f"Direct recording failed for @{username}: {e}. Falling back to yt-dlp.")

            cmd = [
                sys.executable,
                '-m', 'yt_dlp',
                url,
                '-f', 'best',
                '-o', output_template,
                '--no-part',
                '--newline',
                '--retries', '20',
                '--fragment-retries', '20',
                '--extractor-retries', '30',
                '--retry-sleep', 'extractor:5',
                '--socket-timeout', '30',
                '--http-chunk-size', '10485760',
                '--concurrent-fragments', '4',
                '--merge-output-format', 'mp4',
            ]

            # Adapt options for HLS vs FLV streams
            if url and '.m3u8' in url.lower():
                # HLS streams: don't try to start from beginning
                cmd.extend(['--no-live-from-start'])
            elif url and ('.flv' in url.lower() or 'pull-flv' in url):
                # FLV streams can handle --live-from-start (if available)
                pass

            cookies_file = os.getenv('TIKTOK_COOKIES_FILE')
            if cookies_file and os.path.exists(cookies_file):
                cmd.extend(['--cookies', cookies_file])
                self.logger.info(f"Using TikTok cookies file: {cookies_file}")
            else:
                self.logger.warning(
                    'No TIKTOK_COOKIES_FILE configured; TikTok may return false offline results for some lives.'
                )

            creationflags = getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0)
            self.logger.info(f"Starting recording for @{username} with command: {' '.join(cmd)}")

            proc = subprocess.Popen(
                cmd,
                stdout=log_file,
                stderr=subprocess.STDOUT,
                creationflags=creationflags,
            )

            active_recordings[chat_id] = {
                'username': username,
                'process': proc,
                'stop_flag': False,
                'filepath': output_prefix,
                'output_path': output_prefix,
                'log_path': log_path,
                'log_file': log_file,
                'task': None,
            }
            self.logger.info(f"Recording process started for @{username} (PID: {proc.pid})")
            return proc
        except Exception as e:
            self.logger.error(f"Failed to start recording for @{username}: {e}")
            active_recordings.pop(chat_id, None)
            return None

    def stop_recording_process(self, chat_id: int) -> bool:
        """Stop an active recording process."""
        session = active_recordings.get(chat_id)
        if not session:
            return False

        session['stop_flag'] = True
        proc = session.get('process')
        thread = session.get('thread')

        # If we started a direct recording thread, join it after signalling stop
        if thread is not None:
            try:
                # Wait a short time for the thread to stop
                thread.join(timeout=5)
            except Exception as e:
                self.logger.debug(f"Error joining direct recording thread: {e}")

        if proc is None:
            # No subprocess to terminate when using direct thread
            return True

        try:
            if proc.poll() is None:
                proc.terminate()
        except Exception as e:
            self.logger.warning(f"Failed to terminate recording process: {e}")

        log_file = session.get('log_file')
        if log_file:
            try:
                log_file.flush()
            except Exception:
                pass

        return True

    def _direct_recording_worker(self, username: str, live_url: str, out_path: str, chat_id: int):
        """Background thread worker that writes stream chunks to disk using monitor.download_live_stream."""
        try:
            os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
        except Exception:
            pass

        try:
            with open(out_path, 'wb') as out_file:
                for chunk in self.monitor.download_live_stream(live_url):
                    # Stop if requested
                    session = active_recordings.get(chat_id)
                    if not session or session.get('stop_flag'):
                        break
                    try:
                        out_file.write(chunk)
                    except Exception:
                        break
        except Exception as e:
            self.logger.error(f"Direct recording error for @{username}: {e}")
        finally:
            self.logger.info(f"Direct recording finished for @{username}: {out_path}")
            # Attempt to convert to mp4 using ffmpeg if available
            try:
                mp4_path = out_path.rsplit('.', 1)[0] + '.mp4'
                self.convert_flv_to_mp4(out_path, mp4_path)
                # Update recorded path in active_recordings
                session = active_recordings.get(chat_id)
                if session:
                    session['output_path'] = mp4_path
            except Exception as e:
                self.logger.debug(f"FFmpeg conversion skipped/failed: {e}")

    def convert_flv_to_mp4(self, src: str, dst: str) -> bool:
        """Convert an FLV file to MP4 using system ffmpeg. Returns True on success."""
        try:
            # Prefer ffmpeg on PATH
            cmd = [
                'ffmpeg',
                '-y',
                '-i', src,
                '-c', 'copy',
                dst,
            ]
            import subprocess
            result = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return result.returncode == 0
        except Exception as e:
            self.logger.debug(f"convert_flv_to_mp4 failed: {e}")
            return False

    def find_recorded_file(self, output_prefix: str) -> str | None:
        """Find the recorded file or partial file for a session output prefix."""
        pattern = f'{output_prefix}*'
        matches = glob.glob(pattern)
        if not matches:
            return None
        return max(matches, key=os.path.getmtime)

# Initialize bot
bot = None
app = None

# Command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command"""
    keyboard = [
        [InlineKeyboardButton("🔴 REC", callback_data='rec')],
        [InlineKeyboardButton("👁 WATCH", callback_data='watch')],
        [InlineKeyboardButton("⏹ STOP", callback_data='stop')],
        [InlineKeyboardButton("📊 STATUS", callback_data='status')],
        [InlineKeyboardButton("📋 LIST", callback_data='list')],
        [InlineKeyboardButton("❓ HELP", callback_data='help')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🎬 **TikTok Live Recorder Bot**\n\n"
        "Style TikRec: enregistrer, surveiller, stopper et recevoir les lives sur Telegram.\n\n"
        "Choisissez une action:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Help command"""
    help_text = """
🎬 **Commandes Disponibles:**

/start - Menu principal
/rec - Enregistrer un live TikTok maintenant
/watch - Ajouter un compte à surveiller et auto-enregistrer ses prochains lives
/stop - Arrêter l'enregistrement en cours
/status - Voir le statut du monitoring
/list_accounts - Voir tous les comptes monitores
/help - Cette aide

**Commandes rapides:**
/add username - Ajouter directement un compte
/remove username - Retirer directement un compte
/rec @username - Enregistrer immédiatement le live
/watch @username - Ajouter à la watchlist
/stop - Arrêter l'enregistrement
    """
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def watch_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Add account to watchlist and auto-record if live now"""
    if not context.args:
        await update.message.reply_text(
            "👀 Utilisation: `/watch @username`",
            parse_mode='Markdown'
        )
        return

    username = context.args[0].lstrip('@').strip()
    if not username:
        await update.message.reply_text("⚠️ Nom d'utilisateur invalide.")
        return

    success = await bot.add_account(username)
    if not success:
        await update.message.reply_text(f"❌ Le compte @{username} existe déjà ou est invalide.")
        return

    await update.message.reply_text(f"👀 @{username} ajouté à la watchlist.")

    # If the user is already live, auto-record immediately with a short retry window
    try:
        result = await wait_for_live_status(username, retries=2, interval_seconds=3)
        if result and result.get('is_live') and CHAT_ID and CHAT_ID not in active_recordings:
            msg = await update.message.reply_text(
                f"🔴 @{username} est déjà en live. Enregistrement automatique démarré.",
                parse_mode='Markdown'
            )
            proc = await asyncio.to_thread(bot.start_recording_process, username, CHAT_ID)
            if proc:
                active_recordings[CHAT_ID]['task'] = context.application.create_task(
                    monitor_recording_session(context.application, CHAT_ID, username, msg)
                )
            else:
                await msg.edit_text(
                    f"❌ Impossible de démarrer l'enregistrement automatique pour @{username}.",
                    parse_mode='Markdown'
                )
    except Exception as e:
        logger.warning(f"Watch command live check failed for @{username}: {e}")

async def rec_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """TikRec-style alias for immediate recording"""
    try:
        logger.info(f"/rec command received from {update.effective_user.id}: {context.args}")
        await download_live_command(update, context)
    except Exception as e:
        logger.error(f"Error in rec_command: {e}", exc_info=True)
        try:
            await update.message.reply_text(f"❌ Erreur: {str(e)}")
        except Exception as send_error:
            logger.error(f"Could not send error message: {send_error}")

async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """TikRec-style alias for stop"""
    await stop_download_command(update, context)

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

async def wait_for_live_status(username: str, retries: int = 6, interval_seconds: int = 5):
    """Retry live detection for a short period to avoid TikTok false negatives."""
    logger.info(f"Checking live status for @{username} (retries: {retries}, interval: {interval_seconds}s)")
    last_result = None
    for attempt in range(retries):
        logger.debug(f"  Attempt {attempt + 1}/{retries} for @{username}")
        last_result = await bot.monitor.check_live_status(username)
        if last_result and last_result.get('is_live'):
            logger.info(f"@{username} is LIVE after {attempt + 1} attempts")
            return last_result
        if attempt < retries - 1:
            logger.debug(f"  @{username} not live, waiting {interval_seconds}s before retry...")
            await asyncio.sleep(interval_seconds)
    
    logger.info(f"@{username} not detected as live after {retries} attempts")
    return last_result

async def monitor_recording_session(application: Application, chat_id: int, username: str, msg):
    """Wait for a recording process to finish, then send the file."""
    try:
        session = active_recordings.get(chat_id)
        if not session:
            return

        proc = session.get('process')
        log_path = session.get('log_path')
        
        # Monitor process in background for errors
        last_error_check = 0
        while proc and proc.poll() is None:
            # Check logs every 5 seconds for critical errors
            current_time = datetime.utcnow().timestamp()
            if current_time - last_error_check > 5 and log_path and os.path.exists(log_path):
                last_error_check = current_time
                try:
                    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                        log_content = f.read()
                    
                    # Check for fatal errors that should stop the recording
                    fatal_errors = [
                        'The channel is not currently live',
                        'The channel is offline',
                        'No video formats found',
                        'ERROR: [tiktok:live]',
                        'ERROR: Unable to download video',
                    ]
                    
                    for error in fatal_errors:
                        if error in log_content:
                            logger.warning(f"Fatal error detected in logs: {error}")
                            proc.terminate()
                            try:
                                proc.wait(timeout=5)
                            except subprocess.TimeoutExpired:
                                proc.kill()
                            break
                except Exception as e:
                    logger.debug(f"Error checking logs: {e}")
            
            await asyncio.sleep(1)
        
        if proc:
            await asyncio.to_thread(proc.wait)
        return_code = proc.returncode if proc else None

        session = active_recordings.get(chat_id)
        if not session:
            return

        output_prefix = session.get('output_path') or session.get('filepath')
        filepath = bot.find_recorded_file(output_prefix) if output_prefix else None
        stopped = session.get('stop_flag', False)

        if not filepath or not os.path.exists(filepath):
            error_details = ""
            likely_blocked = False
            if log_path and os.path.exists(log_path):
                try:
                    with open(log_path, 'r', encoding='utf-8', errors='ignore') as log_file:
                        tail = log_file.read()[-2000:]
                    likely_blocked = any(marker in tail for marker in (
                        'The channel is not currently live',
                        'status_code":4003110',
                        'statusCode":4003110',
                        'live detail API is deprecated',
                        'TikTok is requiring login',
                    ))
                    if tail.strip():
                        error_details = f"\n\nLog:\n```\n{tail[-1000:]}\n```"
                except Exception:
                    pass

            failure_hint = (
                "TikTok a probablement bloqué l'accès à ce live ou renvoyé un faux négatif.\n"
                "Si cela continue, fournissez un fichier de cookies TikTok via `TIKTOK_COOKIES_FILE`.\n"
            ) if likely_blocked else (
                "Le live n'était peut-être pas disponible au moment du démarrage, ou la résolution du flux a échoué.\n"
            )

            await msg.edit_text(
                f"❌ Impossible de trouver le fichier pour @{username}.\n\n"
                f"{failure_hint}"
                f"Vérifiez que @{username} était vraiment en live.\n\n"
                f"Code de sortie: `{return_code}`"
                f"{error_details}",
                parse_mode='Markdown'
            )
            return

        file_size = os.path.getsize(filepath)
        status_text = "⏸️ Arrêté" if stopped else "✅"

        try:
            await msg.edit_text(f"📥 Envoi du fichier {status_text}...", parse_mode='Markdown')
            with open(filepath, 'rb') as f:
                await application.bot.send_document(chat_id=chat_id, document=f)

            if not stopped:
                try:
                    os.remove(filepath)
                except Exception as e:
                    logger.warning(f"Could not delete file {filepath}: {e}")

            await msg.edit_text(
                f"{status_text} Live de @{username} terminé!\n\n"
                f"📁 Fichier: `{os.path.basename(filepath)}`\n"
                f"📊 Taille: `{file_size / (1024*1024):.1f}MB`",
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Could not send file: {e}")
            await msg.edit_text(
                f"{status_text} Live de @{username} terminé mais l'envoi a échoué.\n\n"
                f"📁 Fichier: `{filepath}`\n"
                f"📊 Taille: `{file_size / (1024*1024):.1f}MB`",
                parse_mode='Markdown'
            )
    finally:
        log_file = session.get('log_file') if session else None
        if log_file:
            try:
                log_file.close()
            except Exception:
                pass
        active_recordings.pop(chat_id, None)

async def download_live_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start recording a live stream immediately."""
    try:
        chat_id = update.effective_chat.id
        logger.info(f"download_live_command called for chat {chat_id} with args: {context.args}")

        if not context.args:
            await update.message.reply_text(
                "📥 **TikTok Live Recorder**\n\n"
                "Utilisation: `/download_live @username` ou `/rec @username`\n\n"
                "Pour arrêter: `/stop_download` ou `/stop`\n"
                "Pour auto-enregistrer les futurs lives: `/watch @username`",
                parse_mode='Markdown'
            )
            return

        username = context.args[0].lstrip('@').strip()
        logger.info(f"Processing download_live for username: {username}")
        
        if not username:
            await update.message.reply_text("⚠️ Nom d'utilisateur invalide.")
            return

        if chat_id in active_recordings:
            await update.message.reply_text("⚠️ Un enregistrement est déjà en cours. Utilisez `/stop` pour l'arrêter.")
            return

        msg = await update.message.reply_text(
            f"🔎 Vérification de `@{username}`...\n\n"
            f"Je retente quelques fois si TikTok répond trop tôt hors live.",
            parse_mode='Markdown'
        )

        live_result = await wait_for_live_status(username)
        logger.info(f"Live status result for {username}: {live_result.get('is_live') if live_result else 'None'}")

        if not live_result or not live_result.get('is_live'):
            await msg.edit_text(
                f"⚠️ @{username} n'a pas pu être confirmé comme live.\n\n"
                "Je tente quand même le téléchargement direct, car TikTok peut renvoyer un faux négatif.",
                parse_mode='Markdown'
            )

        await msg.edit_text(
            f"🔴 Recording `@{username}`...\n\n"
            f"Envoyez `/stop` pour couper et récupérer le fichier.",
            parse_mode='Markdown'
        )

        logger.info(f"Starting recording process for {username}")
        proc = await asyncio.to_thread(bot.start_recording_process, username, chat_id)
        if not proc:
            logger.warning(f"Failed to start recording process for {username}")
            await msg.edit_text(
                f"❌ Impossible de démarrer l'enregistrement pour @{username}.\n\n"
                "Le flux live n'a pas pu être résolu.",
                parse_mode='Markdown'
            )
            return

        logger.info(f"Recording started, creating monitoring task for {username}")
        active_recordings[chat_id]['task'] = context.application.create_task(
            monitor_recording_session(context.application, chat_id, username, msg)
        )
        logger.info(f"Recording task created for {username}")

    except Exception as e:
        logger.error(f"Error in download_live_command: {e}", exc_info=True)
        try:
            await update.message.reply_text(f"❌ Erreur durant le téléchargement: {str(e)[:100]}")
        except Exception as send_error:
            logger.error(f"Could not send error message: {send_error}")

async def stop_download_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop current recording."""
    chat_id = update.effective_chat.id
    session = active_recordings.get(chat_id)
    target = update.message
    if not target and hasattr(update, 'callback_query') and update.callback_query:
        target = update.callback_query.message

    if not session:
        if target:
            await target.reply_text("❌ Aucun enregistrement en cours pour ce chat.")
        return

    username = session.get('username', 'inconnu')
    bot.stop_recording_process(chat_id)
    if target:
        await target.reply_text(
            f"⏹️ Arrêt demandé pour @{username}.\n\n"
            "Je récupère le fichier partiel si disponible...",
            parse_mode='Markdown'
        )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == 'add':
        await query.edit_message_text("Envoyez le nom d'utilisateur TikTok à ajouter:")
        return WAITING_FOR_USERNAME
    elif query.data == 'rec':
        await query.edit_message_text(
            "🔴 **REC**\n\n"
            "Utilisez la commande:\n"
            "`/rec @username`\n\n"
            "Exemple: `/rec frank.the.fonk`",
            parse_mode='Markdown'
        )
    elif query.data == 'watch':
        await query.edit_message_text(
            "👁 **WATCH**\n\n"
            "Utilisez la commande:\n"
            "`/watch @username`\n\n"
            "Le bot enregistrera automatiquement les prochains lives.",
            parse_mode='Markdown'
        )
    elif query.data == 'stop':
        await stop_download_command(update, context)
    elif query.data == 'status':
        accounts = await bot.get_live_accounts()
        live_count = len([a for a in accounts if a.get('is_live')])
        total_count = len(accounts)
        await query.edit_message_text(
            f"📊 **Statut du Bot:**\n\n"
            f"✅ Bot en ligne\n"
            f"📡 Vérification: Toutes les {MONITOR_INTERVAL}s\n"
            f"📺 Comptes monitores: {total_count}\n"
            f"🔴 Comptes en live: {live_count}",
            parse_mode='Markdown'
        )
    elif query.data == 'help':
        await query.edit_message_text(
            "🎬 **Commandes Disponibles:**\n\n"
            "/start - Menu principal\n"
            "/rec - Enregistrer un live TikTok maintenant\n"
            "/watch - Ajouter un compte à surveiller et auto-enregistrer ses prochains lives\n"
            "/stop - Arrêter l'enregistrement en cours\n"
            "/status - Voir le statut du monitoring\n"
            "/list_accounts - Voir tous les comptes monitores\n"
            "/help - Cette aide\n\n"
            "**Commandes rapides:**\n"
            "/add username - Ajouter directement un compte\n"
            "/remove username - Retirer directement un compte\n"
            "/rec @username - Enregistrer immédiatement le live\n"
            "/watch @username - Ajouter à la watchlist\n"
            "/stop - Arrêter l'enregistrement",
            parse_mode='Markdown'
        )
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
            logger.info("Verifying accounts...")
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
                            notification_msg = await application.bot.send_message(
                                chat_id=CHAT_ID,
                                text=message,
                                parse_mode='Markdown',
                                disable_web_page_preview=False
                            )

                            # Auto-record the live if nothing is already recording for this chat
                            if CHAT_ID not in active_recordings:
                                proc = await asyncio.to_thread(bot.start_recording_process, username, CHAT_ID)
                                if proc:
                                    active_recordings[CHAT_ID]['task'] = application.create_task(
                                        monitor_recording_session(application, CHAT_ID, username, notification_msg)
                                    )
                                else:
                                    await notification_msg.edit_text(
                                            f"Impossible de démarrer l'enregistrement automatique pour @{username}.",
                                        parse_mode='Markdown'
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
        logger.info("Bot started and ready to monitor")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation: {e}")
        raise

def main():
    """Start the bot"""
    global app, bot
    
    logger.info("Initializing TikTok Live Monitor Bot...")
    
    if not TOKEN or TOKEN == 'your_telegram_bot_token_here':
        logger.error("TELEGRAM_BOT_TOKEN non configuré dans .env")
        return
    
    if not DATABASE_URL or DATABASE_URL == 'your_database_url_here':
        logger.error("DATABASE_URL non configuré dans .env")
        return
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        db = TikTokDatabase(DATABASE_URL)
        logger.info("Database initialized")
        
        # Initialize bot with database
        logger.info("Creating TikTokLiveBot instance...")
        bot = TikTokLiveBot(db)
        logger.info("Bot instance created")
        
        # Create application
        logger.info("Creating Telegram application...")
        app = Application.builder().token(TOKEN).post_init(post_init).build()
        logger.info("Application created")
        
        # Store db reference in app for shutdown
        app.bot_db = db
        
    except Exception as e:
        logger.error(f"Error initializing bot: {e}", exc_info=True)
        return
    
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
    logger.info("Adding command handlers...")
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('list_accounts', list_accounts))
    app.add_handler(CommandHandler('status', status_command))
    app.add_handler(CommandHandler('add', add_account_command))
    app.add_handler(CommandHandler('remove', remove_account_command))
    app.add_handler(CommandHandler('watch', watch_command))
    app.add_handler(CommandHandler('rec', rec_command))
    app.add_handler(CommandHandler('stop', stop_command))
    app.add_handler(CommandHandler('download_live', download_live_command))
    app.add_handler(CommandHandler('download', download_live_command))
    app.add_handler(CommandHandler('stop_download', stop_download_command))
    app.add_handler(CommandHandler('watch_account', watch_command))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(button_callback))
    logger.info("All handlers registered")
    
    # Run bot
    logger.info("Starting polling loop...")
    try:
        app.run_polling(allowed_updates=Update.ALL_TYPES, stop_signals=None)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error running bot: {e}", exc_info=True)

if __name__ == '__main__':
    try:
        logger.info("=" * 60)
        logger.info("TikTok Live Monitor Bot starting...")
        logger.info("=" * 60)
        main()
    except Exception as e:
        logger.error(f"FATAL ERROR: {e}", exc_info=True)
        import sys
        sys.exit(1)
