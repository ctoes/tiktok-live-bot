# 🛠️ Workflow Complet: Dev → Test → GitHub → Railway

Workflows complet passé par passé de développer votre bot localement à le déployer 24/7 sur Railway.

## 📋 Vue d'ensemble

```
┌─────────────────┐
│  Développement  │
│   Locale (PC)   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│   Test Localement       │
│  python bot.py          │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│   Push sur GitHub       │
│   git push              │
└────────┬────────────────┘
         │
         ▼
┌──────────────────────────────┐
│   Déployer sur Railway       │
│   → Automatique depuis GitHub│
└────────┬─────────────────────┘
         │
         ▼
┌──────────────────────────┐
│  🎉 En live 24/7!       │
│  Logs en temps réel     │
└──────────────────────────┘
```

## 1️⃣ Phase de Développement

### Configurer l'environnement

```bash
# Créer le dossier
mkdir c:\bot\Live
cd c:\bot\Live

# Créer environnement virtuel
python -m venv venv
.\venv\Scripts\activate

# Installer dépendances
pip install -r requirements.txt

# Configurer .env
copy .env.example .env
# Éditer .env avec vos identifiants
```

### Développer et tester

```bash
# Éditer le code (bot.py, database.py, etc)
# Tester localement:

python bot.py

# Sur Telegram:
# /start
# /add_account username
# Vérifier que ça marche!
```

### Voir les logs

```bash
# Ouvrir dans un éditeur:
cat logs/bot.log

# Ou suivre en temps réel:
tail -f logs/bot.log
```

## 2️⃣ Phase de Test

### Vérifications avant push

Checklist avant de pousser sur GitHub:

- [ ] Bot marche localement
- [ ] Pas de logs d'erreur
- [ ] `requirements.txt` à jour
- [ ] `.env` PAS commité
- [ ] Code nettoyé (pas de debug)
- [ ] `Procfile` présent
- [ ]`database.py` marche

### Tests d'intégration

```bash
# Tester avec plusieurs comptes
/add_account account1
/add_account account2
/add_account account3

# Tester les commandes principales
/list_accounts
/remove_account account1
/status

# Vérifier les logs
tail -f logs/bot.log
```

### Tests de la base de données

```python
# Dans Python:
import asyncio
from database import TikTokDatabase
import os
from dotenv import load_dotenv

async def test():
    load_dotenv()
    db = TikTokDatabase(os.getenv('DATABASE_URL'))
    await db.connect()
    
    # Tester l'ajout
    success = await db.add_account("test_user")
    print(f"Add: {success}")
    
    # Tester la récupération
    accounts = await db.get_all_accounts()
    print(f"Accounts: {len(accounts)}")
    
    # Tester les stats
    stats = await db.get_stats()
    print(f"Stats: {stats}")
    
    await db.disconnect()

asyncio.run(test())
```

## 3️⃣ Phase GitHub

### Initialiser Git

```bash
# Se mettre dans le dossier bot
cd c:\bot\Live

# Initialiser git
git init

# Vérifier que .gitignore existe et contient .env
cat .gitignore | grep ".env"

# Ajouter tous les fichiers
git add .

# Créer le commit initial
git commit -m "Initial commit: TikTok Live Monitor Bot with PostgreSQL"
```

### Créer le repo GitHub

1. Aller sur: https://github.com/new
2. Nommer le repo: `tiktok-bot-live`
3. Description: "TikTok Live Monitor Bot with PostgreSQL & Railway Deployment"
4. Public (sinon Railway ne peut pas accéder)
5. Create repository

### Pousser le code

```bash
# Ajouter l'origine GitHub
git remote add origin https://github.com/YOUR_USERNAME/tiktok-bot-live.git

# Pousser le code
git branch -M main
git push -u origin main
```

### Vérifier sur GitHub

1. Aller sur: https://github.com/YOUR_USERNAME/tiktok-bot-live
2. Voir tous les fichiers
3. Voir que `.env` n'est pas listé

## 4️⃣ Phase Déploiement Railway

### Créer le projet Railway

1. Aller sur: https://railway.app
2. Cliquer: **New Project**
3. Choisir: **Deploy from GitHub repo**
4. Sélectionner le repo: `tiktok-bot-live`
5. Cliquer: **Deploy**

⏳ Attendre 2-3 minutes que Railway build et démarre l'app...

### Configurer les variables

Dans Railway Dashboard:

```
App → Variables → Ajouter:

TELEGRAM_BOT_TOKEN=votre_token_ici
TELEGRAM_CHAT_ID=votre_id_ici
DATABASE_URL=postgresql://...@neon.tech/db?sslmode=require
LOG_LEVEL=INFO
```

Sauvegarder. Railway redémarre automatiquement.

### Vérifier le déploiement

1. Aller dans **Deployments**
2. Status doit être **Success** (vert)
3. Cliquer : **View Logs**
4. Chercher: `✅ Bot démarré et prêt à monitorer!`

Si erreur: lire les logs pour le problème.

### Tester sur Telegram

```
Envoyer: /start

Vous devez voir:
🎬 **TikTok Live Monitor Bot**
Je monitore les comptes TikTok...

Menu avec 3 boutons
```

✅ **C'est en live!**

## 5️⃣ Phase Maintenance

### Mettre à jour le code

```bash
# Faire des changements au code (localement)

# Commiter
git add .
git commit -m "Description du changement"

# Pousser sur GitHub
git push origin main
```

⏳ Railway détecte le changement et redéploie automatiquement (~30-60s)

### Monitorer les logs en live

Railway Dashboard → App → View Logs

```
// Logs en temps réel
2024-01-15 10:30:42 - 🔍 Vérification des comptes...
2024-01-15 10:30:50 - 🎬 NEW LIVE: cristiano
```

### Arrêter/Redémarrer

Railway Dashboard → App → Settings → Stop/Start

## 🎓 Commandes Git utiles

### Vérifier le statut

```bash
git status  # Voir les changements non commitées
git log --oneline  # Voir l'historique des commits
```

### Annuler des changements

```bash
git checkout -- .  # Annuler tous les changements
git revert HEAD  # Créer un commit qui annule le dernier
```

### Gérer les branches

```bash
git branch  # Voir les branches
git branch new-feature  # Créer une branche
git checkout new-feature  # Switcher vers la branche
git merge new-feature  # Merger la branche
```

## 🛡️ Bonnes pratiques

### 1. Commits clairs

```bash
❌ Mauvais
git commit -m "fix"

✅ Bon
git commit -m "Fix TikTok API timeout issue for large account lists"
```

### 2. Ne jamais commiter les secrets

```bash
✅ Bon: TELEGRAM_BOT_TOKEN fourni via Railway variables
❌ Mauvais: TELEGRAM_BOT_TOKEN="123abc..." dans le code
```

### 3. Tester avant de push

```bash
# Avant git push:
python bot.py  # Test local
python check_setup.py  # Vérifier setup
```

### 4. Laisser des commentaires

```python
# Mauvais:
accounts = await db.get_all_accounts()

# Bon:
# Récupérer tous les comptes TikTok à monitorer
accounts = await db.get_all_accounts()
```

## 📊 Exemple de workflow complet

```bash
# 1. DEV - Ajouter une nouvelle feature
# Éditer bot.py pour ajouter /stats

# 2. TEST - Vérifier que ça marche
python bot.py
# /stats → Shows statistics ✅

# 3. GIT - Commiter le changement
git add .
git commit -m "Add /stats command to show live statistics"

# 4. PUSH - Pousser sur GitHub
git push origin main

# 5. RAILWAY - Auto-redéploie
# 30 secondes plus tard, Railway a déployé la nouvelle version
# En prod, vous pouvez utiliser /stats directement!

# 6. VERIFY - Vérifier dans Railway logs
# Logs affichent la nouvelle version en live
```

## 🚀 Workflow avancé: Branches Git

Pour un développement plus pro:

```bash
# Créer une branche pour la nouvelle feature
git checkout -b feature/stats-command

# Développer sur cette branche
# ... éditer bot.py ...

# Tester
python bot.py

# Commiter les changements
git add .
git commit -m "Add /stats command"

# Pousser la branche
git push origin feature/stats-command

# Sur GitHub: Créer une Pull Request
# Revue du code
# Merge dans main

# Railway redéploie automatiquement
```

## 📞 Support

| Problème | Solution |
|----------|----------|
| Git error | Lire [GITHUB_SETUP.md](GITHUB_SETUP.md) |
| Railway error | Lire [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) |
| DB error | Lire [NEON_SETUP.md](NEON_SETUP.md) |
| Code error | Lire [FAQ.md](FAQ.md) |

---

**Prêt à déployer? Commencez par [GITHUB_SETUP.md](GITHUB_SETUP.md)!** 🚀
