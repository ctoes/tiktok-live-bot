# 🎬 TikTok Live Monitor Bot

Un bot Telegram qui monitore automatiquement les comptes TikTok et vous envoie les directs (lives) en temps réel, avec stockage dans une base de données PostgreSQL (Neon).

## ✨ Fonctionnalités

- ✅ Monitore plusieurs comptes TikTok
- ✅ Détecte automatiquement quand un compte est en live
- ✅ Envoie les notifications sur Telegram
- ✅ Gestion des comptes via commandes Telegram
- ✅ Vérification toutes les 5 minutes
- ✅ Interface interactive avec boutons
- ✅ **Stockage PostgreSQL (Neon)** - persistant et scalable
- ✅ Historique des lives enregistré
- ✅ Statistiques et analytics

## 📋 Prérequis

- Python 3.8+
- Un compte Telegram
- Un token Telegram Bot
- Un chat ID Telegram
- **Un compte Neon PostgreSQL** (gratuit)

## 🚀 Installation

### 1. Cloner/Configurer le projet

```bash
cd c:\bot\Live
```

### 2. Créer un environnement virtuel

```bash
python -m venv venv
.\venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer Neon PostgreSQL

**Lire:** [NEON_SETUP.md](NEON_SETUP.md)

Résumé:
1. Créer un compte sur https://neon.tech
2. Créer un projet
3. Copier la connection string

### 5. Configurer les variables d'environnement

**Créer un fichier `.env`:**

```bash
copy .env.example .env
```

**Éditer `.env` et remplir:**

```
TELEGRAM_BOT_TOKEN=votre_token_ici
TELEGRAM_CHAT_ID=votre_chat_id_ici
DATABASE_URL=postgresql://...@neon.tech/your_db?sslmode=require
LOG_LEVEL=INFO
```

### 6. Obtenir le token Telegram Bot

1. Ouvrir Telegram et chercher **@BotFather**
2. Taper `/newbot` et suivre les instructions
3. BotFather vous donnera un token → **collez-le dans .env**

### 7. Obtenir votre Chat ID Telegram

1. Envoyer un message à votre bot
2. Aller sur: `https://api.telegram.org/bot<VOTRE_TOKEN>/getUpdates`
3. Chercher `"chat":{"id":12345678}` → **collez le ID dans .env**

## 🎮 Utilisation

### Démarrer le bot

```bash
python bot.py
```

### Commandes Telegram

**Commandes principales:**

| Commande | Description |
|----------|-------------|
| `/start` | Menu principal avec boutons |
| `/help` | Affiche l'aide |
| `/add_account @username` | Ajouter un compte TikTok |
| `/remove_account @username` | Retirer un compte TikTok |
| `/list_accounts` | Voir tous les comptes |
| `/status` | Statut du bot |

**Exemples:**

```
/add_account tiktok_user
/add @tiktok_user
/remove_account tiktok_user
/list_accounts
```

### Interface Interactive

Tapez `/start` pour afficher un menu avec des boutons:
- ➕ Ajouter Compte
- ➖ Retirer Compte
- 📋 Lister Comptes

## 📁 Structure du projet

```
c:\bot\Live\
├── bot.py                    # Bot principal Telegram
├── tiktok_monitor.py         # Module de monitoring TikTok
├── database.py               # Gestion PostgreSQL
├── requirements.txt          # Dépendances Python
├── .env.example              # Template des variables
├── .env                      # Variables (à créer)
├── config/
│   └── accounts.json         # Configuration locale (optionnel)
├── logs/
│   └── bot.log              # Fichier de log
└── downloads/               # Lives téléchargées (créé automatiquement)
```

## 🗄️ Base de données

### Structure PostgreSQL

Les données sont stockées dans **Neon PostgreSQL**:

**Tables:**
1. **accounts** - Les comptes TikTok à monitorer
2. **live_history** - Historique des lives enregistrés
3. **bot_users** - Utilisateurs Telegram

### Voir les données

Dans Neon Dashboard → SQL Editor:

```sql
SELECT * FROM accounts;
SELECT * FROM live_history;
```

**[Guide complet Neon](NEON_SETUP.md)**

## 🔧 Configuration Avancée

### Modifier l'intervalle de vérification

Dans `bot.py`, ligne 30:
```python
MONITOR_INTERVAL = 300  # En secondes (300 = 5 minutes)
```

### Ajouter des comptes manuellement

Éditer `config/accounts.json`:
```json
{
  "accounts": [
    {
      "username": "mon_compte",
      "user_id": null,
      "added_date": "2024-01-01T12:00:00",
      "last_checked": null,
      "is_live": false
    }
  ]
}
```

## 📊 Logs

Les logs sont sauvegardés dans `logs/bot.log` et aussi affichés en console.

## ⚠️ Limitations & Notes

- La détection de live dépend des API TikTok (qui changent régulièrement)
- Certains comptes privés peuvent ne pas fonctionner
- Le téléchargement automatique des lives est basé sur `yt-dlp`
- Les comptes mobiles uniquement peuvent avoir des restrictions

## 🐛 Dépannage

### Bot ne démarre pas
- Vérifier que `TELEGRAM_BOT_TOKEN` est correct dans `.env`
- Vérifier que `DATABASE_URL` est correct
- Vérifier les logs: `cat logs/bot.log`

### Connection database error
- Vérifier internet connection
- Vérifier la connection string Neon dans `.env`
- Vérifier le format SSL: `?sslmode=require`

### Pas de notifications
- Vérifier `TELEGRAM_CHAT_ID` dans `.env`
- Vérifier que le bot a le droit d'envoyer les messages
- Tester: `/start` sur Telegram

### Monitoring ne fonctionne pas
- Les APIs TikTok changent souvent
- Vérifier les logs pour plus de détails
- Vérifier les noms d'utilisateur (sans @)

## 📝 Exemple d'utilisation complète

```
1. python bot.py                    # Démarrer le bot
2. /start                           # Menu principal
3. /add_account tiktok_user        # Ajouter un compte
4. /list_accounts                  # Voir les comptes
5. Attendre la notification pour un live!
```

## 🔐 Sécurité

- Ne **JAMAIS** partager votre `TELEGRAM_BOT_TOKEN`
- Ne **JAMAIS** partager votre `DATABASE_URL` (contient le password)
- Ne **JAMAIS** commiter le fichier `.env` avec les vrais tokens
- Garder `.env` en local uniquement

## 📞 Support

Si vous rencontrez des problèmes:

1. Vérifier les logs
2. Consulter [FAQ.md](FAQ.md)
3. Consulter [NEON_SETUP.md](NEON_SETUP.md) pour les problèmes DB
4. Consulter [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) pour déployer
5. Relire [README.md](README.md) pour les détails

## 📄 Licence

Libre de modification et distribution.

---

**Bon monitoring! 🎬**
