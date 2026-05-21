# Railway Deployment Guide

This guide walks you through deploying the TikTok Live Monitor Bot to Railway.

## Prerequisites

- Railway account (https://railway.app)
- GitHub repository connected to Railway (already done: https://github.com/ctoes/tiktok-live-bot)
- Telegram Bot Token (from @BotFather)
- Telegram Chat ID (from getUpdates)
- Neon PostgreSQL Database URL

## Deployment Steps

### 1. Ensure Your Repository is Up to Date

Push all local changes to GitHub:

```bash
cd C:\bot\Live
git add .
git commit -m "Ready for Railway deployment"
git push origin main
```

### 2. Connect Railway to Your GitHub Repo

1. Go to https://railway.app
2. Create a new project or open existing one
3. Click "New" → "Project from Repo"
4. Select your GitHub repository: `ctoes/tiktok-live-bot`
5. Railway will auto-detect the Python project using `Procfile` and `railway.json`

### 3. Set Environment Variables in Railway

In the Railway dashboard for your project, set these variables:

| Variable | Value | Example |
|----------|-------|---------|
| `TELEGRAM_BOT_TOKEN` | Your bot token from @BotFather | `8804397046:AAHRxBElN...` |
| `TELEGRAM_CHAT_ID` | Your chat ID (numeric) | `1448843666` |
| `DATABASE_URL` | Neon PostgreSQL connection URL | `postgresql://neondb_owner:...@ep-...` |
| `LOG_LEVEL` | Logging level | `INFO` |

**To find your Telegram Chat ID:**
```powershell
$token = "YOUR_BOT_TOKEN"
Invoke-WebRequest -Uri "https://api.telegram.org/bot$token/getUpdates" -UseBasicParsing | ConvertFrom-Json
```
Look for `message.chat.id` in the JSON response.

### 4. Deploy

Railway will automatically:
1. Pull your code from GitHub
2. Install dependencies from `requirements.txt`
3. Run the bot using the start command: `python bot.py`

Watch the deployment logs in the Railway dashboard to confirm success.

### 5. Verify Deployment

Send the `/start` command to your Telegram bot. You should receive the main menu. Test:
- `/add_account username` - Add a TikTok account to monitor
- `/list_accounts` - List all monitored accounts
- `/status` - Check bot status

## Monitoring and Logs

- View live logs in the Railway dashboard
- The bot writes logs to stdout and to `logs/bot.log` locally

## Database

The bot uses **Neon PostgreSQL** (serverless, production-ready):
- Tables auto-create on first run: `accounts`, `live_history`, `bot_users`
- Connection is pooled via asyncpg with SSL
- Data persists across bot restarts

## Updating the Bot

To update the bot after future changes:
```bash
git add .
git commit -m "Update: description of changes"
git push origin main
```
Railway will automatically re-deploy within seconds to minutes.

## Troubleshooting

### Bot doesn't respond to commands
- Check `TELEGRAM_BOT_TOKEN` is correct and hasn't expired
- Verify `TELEGRAM_CHAT_ID` matches where you're sending messages
- Check Railway deployment logs for errors

### Database connection fails
- Verify `DATABASE_URL` is correct and network connectivity works
- Test with: `python scripts/test_db_connect.py` (set `DATABASE_URL` before running)

### No live streams detected
- Add a TikTok account with `/add testuser`
- Wait 5 minutes (default monitoring interval in `bot.py`)
- Check logs for monitoring messages: "Vérification des comptes..."

## Local Development

To run locally:

```powershell
# Activate virtualenv
. .venv\Scripts\Activate.ps1

# Set environment variables
$env:TELEGRAM_BOT_TOKEN = 'your_token'
$env:TELEGRAM_CHAT_ID = 'your_chat_id'
$env:DATABASE_URL = 'your_neon_url'
$env:LOG_LEVEL = 'INFO'

# Run bot
python bot.py
```

## Files

- `bot.py` - Main bot application and handlers
- `database.py` - Neon PostgreSQL integration
- `tiktok_monitor.py` - TikTok live status monitoring
- `Procfile` - Railway start command
- `railway.json` - Railway configuration
- `requirements.txt` - Python dependencies
- `scripts/` - Helper and test scripts
