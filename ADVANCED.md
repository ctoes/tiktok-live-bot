# ⚙️ Configuration Avancée

## Paramètres personnalisables

### 1. Intervalle de vérification

**Fichier:** `bot.py` ligne 30
```python
MONITOR_INTERVAL = 300  # Secondes (300 = 5 minutes)
```

Recommandé:
- `60` = 1 minute (usage intensif)
- `300` = 5 minutes (équilibré)
- `600` = 10 minutes (economique)

### 2. Limite de boutons

**Fichier:** `bot.py` ligne 189 et 281
```python
for acc in accounts[:10]  # Maxim 10 boutons par message
```

Augmentez ce nombre pour plus de comptes par page (attention: UI peut être encombrée).

### 3. Niveaux de log

**Dans `.env`:**
```
LOG_LEVEL=DEBUG    # Très détaillé
LOG_LEVEL=INFO     # Défaut (recommandé)
LOG_LEVEL=WARNING  # Moins de détails
LOG_LEVEL=ERROR    # Seulement les erreurs
```

### 4. Timeout des requêtes

**Fichier:** `tiktok_monitor.py` ligne 31
```python
response = self.session.get(url, params=params, timeout=10)
```

Valeur en secondes. Augmentez si vous avez une connexion lente.

---

## Extensions possibles

### Ajouter plusieurs chats Telegram

Modifier `bot.py` pour supporter une liste de chats:

```python
CHAT_IDS = [123456789, 987654321, 111111111]

# Dans monitoring_loop()
for chat_id in CHAT_IDS:
    await application.bot.send_message(chat_id=chat_id, ...)
```

### Envoyer aussi la vidéo téléchargée

Décommenter dans `bot.py` monitoring_loop():
```python
# Télécharger et envoyer la vidéo
# video_path = await bot.download_live(username)
# if video_path:
#     await application.bot.send_video(
#         chat_id=CHAT_ID,
#         video=open(video_path, 'rb'),
#         caption=f"Video de @{username}"
#     )
```

### Ajouter une base de données

Remplacer JSON par SQLite:

```python
import sqlite3

class AccountsDB:
    def __init__(self, db_file='accounts.db'):
        self.conn = sqlite3.connect(db_file)
        self.create_tables()
    
    def create_tables(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY,
                username TEXT UNIQUE,
                user_id TEXT,
                added_date TIMESTAMP,
                last_checked TIMESTAMP,
                is_live BOOLEAN
            )
        ''')
        self.conn.commit()
    
    def add_account(self, username):
        self.conn.execute(
            'INSERT INTO accounts (username, added_date) VALUES (?, datetime("now"))',
            (username,)
        )
        self.conn.commit()
```

### Ajouter une API REST

Créer un serveur Flask pour contrôler le bot via API:

```python
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api/accounts', methods=['GET'])
async def get_accounts():
    return jsonify(await bot.get_live_accounts())

@app.route('/api/accounts/add', methods=['POST'])
async def add_account():
    data = request.json
    success = await bot.add_account(data['username'])
    return jsonify({'success': success})

if __name__ == '__main__':
    app.run(port=5000)
```

### Intégration avec base de données (PostgreSQL)

```python
import asyncpg

class PostgresDB:
    async def connect(self):
        self.pool = await asyncpg.create_pool(
            'postgresql://user:password@localhost/tiktok_bot'
        )
```

---

## Performance et Optimisation

### 1. Réduire l'utilisation de la bande passante

```python
# Diminuer la fréquence
MONITOR_INTERVAL = 600  # 10 minutes au lieu de 5
```

### 2. Utiliser un cache

```python
from functools import lru_cache
from datetime import datetime, timedelta

class CachedMonitor:
    def __init__(self):
        self.last_check = {}
        self.cache_ttl = 60  # 1 minute
    
    async def check_live_status(self, username):
        now = datetime.now()
        if username in self.last_check:
            if (now - self.last_check[username]).seconds < self.cache_ttl:
                return self.cached_results.get(username)
        
        result = await super().check_live_status(username)
        self.last_check[username] = now
        return result
```

### 3. Paralléliser les vérifications

```python
import asyncio

async def check_all_accounts(self):
    tasks = [
        self.check_live_status(acc['username'])
        for acc in self.accounts['accounts']
    ]
    results = await asyncio.gather(*tasks)
    return results
```

---

## Sécurité avancée

### 1. Rate limiting

```python
from telegram.ext import ConversationHandler

# Dans application builder
app.add_handler(
    ConversationHandler(
        entry_points=[CommandHandler('add_account', add_account_command)],
        states={
            WAITING_FOR_USERNAME: [MessageHandler(filters.TEXT, text_handler)]
        },
        fallbacks=[CommandHandler('cancel', lambda u, c: None)],
        allow_reentry=False,  # Prevent spam
        per_user=True
    )
)
```

### 2. Chiffrement du fichier de configuration

```python
from cryptography.fernet import Fernet

def encrypt_config(config_data):
    key = Fernet.generate_key()
    cipher = Fernet(key)
    encrypted = cipher.encrypt(json.dumps(config_data).encode())
    return encrypted, key
```

### 3. Authentification des utilisateurs

```python
AUTHORIZED_USERS = [123456789, 987654321]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in AUTHORIZED_USERS:
        await update.message.reply_text("❌ Non autorisé")
        return
    # ... rest of handler
```

---

## Déploiement en production

**→ [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)** pour la solution la plus simple et moderne!

### 0. Railway (Recommandé - Plus facile!)

Railway est la plateforme cloud la plus simple pour déployer des bots Python:

**Avantages:**
- ✅ Gratuit pour commencer (~$5/mois après)
- ✅ Déploiement automatique depuis GitHub
- ✅ Gestion des variables en GUI
- ✅ Support 24/7
- ✅ Scaling automatique

**Procédure:**
1. Créer compte sur https://railway.app
2. Connecter le repo GitHub
3. Ajouter les variables d'environnement
4. C'est en live! 🚀

Lire [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) pour les détails.

---

### 1. Sur un serveur Linux (systemd)

Créer `/etc/systemd/system/tiktok-bot.service`:

```ini
[Unit]
Description=TikTok Live Monitor Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/bot/Live
ExecStart=/home/ubuntu/bot/Live/venv/bin/python bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Activer:
```bash
sudo systemctl daemon-reload
sudo systemctl enable tiktok-bot
sudo systemctl start tiktok-bot
```

### 2. Avec Docker

`Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
```

Lancer:
```bash
docker build -t tiktok-bot .
docker run -d --name tiktok-bot --env-file .env tiktok-bot
```

### 3. Sur un serveur Windows (Task Scheduler)

1. Créer une tâche planifiée
2. Action: `python.exe` avec les arguments `bot.py`
3. Répertoire de travail: `c:\bot\Live`
4. À la connexion de l'utilisateur: Cocher "Exécuter qu'une session ouverte"

---

## Monitoring et support

### Logs centralisés

Envoyer ses logs à un service:

```python
import logging
import logging_loki

handler = logging_loki.LokiHandler(
    url="http://localhost:3100/loki/api/v1/push",
    tags={"app": "tiktok-bot"},
    auth=("user", "pass"),
)
logger.addHandler(handler)
```

### Health check

Créer un endpoint pour vérifier l'état:

```python
@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'accounts_monitored': len(bot.accounts['accounts']),
        'uptime': (datetime.now() - bot.start_time).total_seconds()
    })
```

---

**Pour plus d'infos: [README.md](README.md)**
