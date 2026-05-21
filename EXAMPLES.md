# 📝 Cas d'usage et Exemples

## Scénarios d'utilisation

### 1. Monitoring simple d'un compte

**Objectif:** Monitorer un seul compte TikTok

```bash
# Démarrer le bot
python bot.py

# Sur Telegram:
/add_account cristiano  # ou /add_account @cristiano

# Le bot va vérifier toutes les 5 minutes
# Quand cristiano broadcast en live, vous recevrez une notif
```

**Fichier de config généré:**
```json
{
  "accounts": [
    {
      "username": "cristiano",
      "user_id": null,
      "added_date": "2024-01-15T10:30:00",
      "last_checked": "2024-01-15T10:35:00",
      "is_live": false
    }
  ]
}
```

---

### 2. Monitoring de plusieurs comptes

```bash
# Ajouter plusieurs comptes
/add_account account1
/add_account account2
/add_account account3
/add_account account4

# Voir tous les comptes
/list_accounts

# Output:
# 📋 Comptes en Monitoring:
#
# 1. @account1 - ⚪ Offline (Vérif: 10:35)
# 2. @account2 - 🔴 LIVE (Vérif: 10:34)
# 3. @account3 - ⚪ Offline (Vérif: 10:32)
# 4. @account4 - ⚪ Offline (Vérif: 10:30)
```

**Configuration JSON automatique:**
```json
{
  "accounts": [
    {"username": "account1", ...},
    {"username": "account2", ...},
    {"username": "account3", ...},
    {"username": "account4", ...}
  ]
}
```

---

### 3. Notification en temps réel

**Quand un live commence:**

Message reçu sur Telegram:
```
🎬 @creator_name EST EN LIVE!

⏰ 2024-01-15T10:45:30
👥 Spectateurs: 15234
📝 Titre: Hanging out with fans!

[Ouvrir sur TikTok](https://www.tiktok.com/@creator_name/live)
```

Bot log:
```
2024-01-15 10:45:30 - tiktok_monitor - INFO - ✓ creator_name is LIVE
2024-01-15 10:45:31 - bot - INFO - 🎬 NEW LIVE: creator_name
2024-01-15 10:45:31,300 - telegram.ext.Application - INFO - Message sent
```

---

### 4. Opérations de gestion

#### Ajouter un compte (3 façons)

**Option 1: Via commande directe**
```
/add username
```

**Option 2: Via commande complète**
```
/add_account username
```

**Option 3: Via menu interactif**
```
/start
[Clic sur ➕ Ajouter Compte]
[Envoyer nom d'utilisateur]
```

---

#### Retirer un compte (2 façons)

**Option 1: Via commande directe**
```
/remove username
```

**Option 2: Via menu interactif**
```
/start
[Clic sur ➖ Retirer Compte]
[Clic sur le compte à retirer]
```

---

### 5. Vérification de statut

```
/status

Output:
📊 Statut du Bot:

✅ Bot en ligne
📡 Vérification: Toutes les 300s
📺 Comptes monitores: 4
🔴 Comptes en live: 1
```

---

## Flux d'utilisation complète

### Scénario: Streamer qui veut capturer les lives de ses amis

1. **Initialisation (une fois)**
   ```bash
   python bot.py
   ```

2. **Ajouter les comptes**
   ```
   /start
   [➕ Ajouter Compte]
   streaming_friend_1
   streaming_friend_2
   streaming_friend_3
   ```

3. **Vérifier que tout marche**
   ```
   /list_accounts
   /status
   ```

4. **Attendre les notifications**
   - Quand friend_1 fait un live: notif auto
   - Quand friend_2 fait un live: notif auto
   - etc.

5. **Gérer la liste**
   ```
   /remove streaming_friend_2  # La personne a arrêté pour nous
   /add new_friend             # Nouveau compte à tracker
   ```

---

## Cas d'usage avancés

### A. Monitoring professionnel

**Cas:** Agence de marketing qui track les competitors

```json
{
  "accounts": [
    {"username": "competitor_1", "business": "Agency", ...},
    {"username": "competitor_2", "business": "Agency", ...},
    {"username": "competitor_3", "business": "Brand", ...},
    {"username": "competitor_4", "business": "Influencer", ...}
  ],
  "settings": {
    "check_interval": 60,      // Plus souvent
    "max_retries": 5,
    "timeout": 30
  }
}
```

### B. Monitoring de créateurs spécifiques

**Cas:** Fans qui ne veulent pas rater les lives

```bash
/add cristiano
/add messi  
/add neymar
/add ronaldo

# Bot notifie chaque live
```

### C. Monitoring d'événements

**Cas:** Événement streaming multi-créateurs

```bash
/add event_creator_1
/add event_creator_2
/add event_creator_3

# Les 3 créateurs vont streamer en même temps
# Vous recevez 3 notifs dans les 5 min
```

---

## Intégration avec d'autres services

### Slack notification

Modifier `bot.py`:

```python
import slack_sdk

slack_client = slack_sdk.WebClient(token=os.getenv('SLACK_TOKEN'))

# Dans monitoring_loop()
slack_client.chat_postMessage(
    channel="#tiktok-lives",
    text=f"🎬 @{username} EST EN LIVE!"
)
```

### Discord webhook

```python
import aiohttp

async def send_discord_notification(username, stream_info):
    webhook_url = os.getenv('DISCORD_WEBHOOK_URL')
    embed = {
        "title": f"@{username} est en live!",
        "color": 16711680,  # Red
        "fields": [
            {"name": "Spectateurs", "value": stream_info.get('viewers', 'N/A')}
        ]
    }
    async with aiohttp.ClientSession() as session:
        await session.post(webhook_url, json={"embeds": [embed]})
```

### Email notifications

```python
import smtplib
from email.mime.text import MIMEText

def send_email_notification(username):
    msg = MIMEText(f"@{username} est maintenant en live!")
    msg['Subject'] = "TikTok Live Alert"
    msg['From'] = "bot@example.com"
    msg['To'] = "your_email@example.com"
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login("your_email@gmail.com", "your_password")
        server.send_message(msg)
```

---

## Logs et debugging

### Vérifier les logs détaillés

```bash
# Mode continu
tail -f logs/bot.log

# Voir une partie spécifique
grep "cristiano" logs/bot.log

# Comptage des lives
grep "NEW LIVE" logs/bot.log | wc -l
```

### Recherche dans les logs

```bash
# Tous les lives de la journée
grep "$(date +%Y-%m-%d)" logs/bot.log | grep "NEW LIVE"

# Tous les erreurs
grep "ERROR" logs/bot.log

# Dernière vérification d'un compte
grep "account_name" logs/bot.log | tail -5
```

---

## Performance et optimisation

### Exemple: Monitoring 50 comptes

**Config recommandée:**

```ini
# .env
TELEGRAM_BOT_TOKEN=xxx
TELEGRAM_CHAT_ID=xxx
LOG_LEVEL=WARNING
```

```python
# bot.py
MONITOR_INTERVAL = 300  # 5 minutes (équilibré)
```

**Ressources estimées:**
- CPU: ~5-10% (lors de la vérification)
- RAM: ~50-100 MB
- Bande passante: ~1 MB par cycle de vérification

---

## Troubleshooting par scénario

### Scénario 1: Personne ne reçoit de notification

**Vérifications:**
1. ✓ Le bot est lancé?
   ```bash
   # En terminal, devrait afficher:
   ✅ Bot démarré et prêt à monitorer!
   ```

2. ✓ Le chat_id est correct?
   ```bash
   # Tester manuellement:
   /start
   # Devrait répondre
   ```

3. ✓ Les comptes existent?
   ```bash
   /list_accounts
   # Devrait montrer la liste
   ```

4. ✓ Quelqu'un est vraiment en live?
   - Vérifier manuellement sur TikTok

---

### Scénario 2: Faux positifs (notif de live alors qu'il n'y a pas)

**Cause:** Détection incorrect

**Solution:** Augmenter la confiance de détection (dans `tiktok_monitor.py`):

```python
def _check_if_live(self, data: dict) -> bool:
    """Check if the response indicates a live stream"""
    try:
        # Vérifications plus strictes
        if 'user' in data and 'status' in data:
            user_info = data['user']
            status = data['status']
            
            # Vérifier PLUSIEURS indicateurs
            if (user_info.get('is_live', False) and 
                status.get('is_live', False) and
                user_info.get('live_viewer_count', 0) > 0):
                return True
        return False
    except Exception as e:
        return False
```

---

### Scénario 3: Bot très lent

**Solutions:**

1. Augmenter l'intervalle de vérification:
   ```python
   MONITOR_INTERVAL = 600  # 10 min au lieu de 5
   ```

2. Réduire le nombre de comptes:
   ```bash
   /list_accounts
   /remove old_account
   /remove inactive_account
   ```

3. Réduire les logs:
   ```ini
   # .env
   LOG_LEVEL=ERROR
   ```

---

**Besoin plus d'aide? Consultez [README.md](README.md) ou [ADVANCED.md](ADVANCED.md)**
