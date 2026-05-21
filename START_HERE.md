# 🎬 COMMENCEZ ICI!

Bienvenue dans votre **TikTok Live Monitor Bot** ! 👋

## ⚡ 3 options pour commencer

### 🏃 Vous êtes pressé? (5 minutes)
Lisez **[QUICKSTART.md](QUICKSTART.md)** et lancez le bot

### 📖 Vous voulez les détails? (20 minutes)
Lisez **[INSTALLATION.md](INSTALLATION.md)** pour tout comprendre

### 📚 Vous voulez tout savoir? (1h)
Commencez par **[INDEX.md](INDEX.md)** pour la documentation complète

---

## 🚀 Installation express (copier-coller)

```bash
# 1. Créer l'environnement virtuel
python -m venv venv

# 2. L'activer (Windows)
.\venv\Scripts\activate
# ou (Linux/Mac)
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer le bot
copy .env.example .env
# Éditer .env et ajouter votre token

# 5. Lancer le bot!
python bot.py
```

---

## 🔧 Configuration Telegram (2 minutes)

1. **Obtenir un token:**
   - Ouvrir Telegram → Chercher **@BotFather**
   - Envoyer `/newbot`
   - Suivre les instructions
   - Copier le token → coller dans `.env`

2. **Obtenir votre Chat ID:**
   - Envoyer un message à votre bot
   - Ouvrir: `https://api.telegram.org/bot{VOTRE_TOKEN}/getUpdates`
   - Chercher `"chat":{"id":12345678}` → copier le nombre dans `.env`

3. **Créer une base de données Neon:**
   - Aller sur: https://neon.tech
   - Créer un compte et un projet
   - Copier la connection string dans DATABASE_URL

**[Lire les guides détaillés](SETUP_TOKEN.md) et [Neon](NEON_SETUP.md)**

---

## 🎮 Tester le bot

Une fois lancé, sur Telegram:

```
/start                    ← Menu d'accueil
/add_account cristiano    ← Ajouter un compte
/list_accounts            ← Voir la liste
/status                   ← État du bot
```

---

## 📁 Fichiers importants

```
bot.py                 ← Bot Telegram principal
tiktok_monitor.py      ← Détection des lives
.env                   ← Configuration (À CRÉER)
config/accounts.json   ← Comptes sauvegardés
logs/bot.log          ← Historique
```

---

## 📚 Documentation

| Doc | Utilité | Temps |
|-----|---------|-------|
| **[POSTGRES_INTEGRATION.md](POSTGRES_INTEGRATION.md)** | Résumé intégration Neon | 5 min |
| **[QUICKSTART.md](QUICKSTART.md)** | Démarrage rapide | 5 min |
| **[INSTALLATION.md](INSTALLATION.md)** | Installation détaillée | 15 min |
| **[SETUP_TOKEN.md](SETUP_TOKEN.md)** | Configurer Telegram | 5 min |
| **[NEON_SETUP.md](NEON_SETUP.md)** | Configurer PostgreSQL | 10 min |
| **[MIGRATION.md](MIGRATION.md)** | Migrer JSON→PostgreSQL | 10 min |
| **[RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)** | Déployer sur Railway | 10 min |
| **[README.md](README.md)** | Complète | 30 min |
| **[EXAMPLES.md](EXAMPLES.md)** | Cas d'usage | 15 min |
| **[FAQ.md](FAQ.md)** | Q/R | 10 min |
| **[ADVANCED.md](ADVANCED.md)** | Avancé | 30 min |
| **[REFERENCE.md](REFERENCE.md)** | Cheat sheet | 2 min |

---

## ✨ Ce que le bot fait

✅ Monitore automatiquement les comptes TikTok
✅ Détecte en temps réel quand ils font un live  
✅ Envoie une notification instantanée sur Telegram
✅ Permet de gérer les comptes via Telegram
✅ Stockage persistant en PostgreSQL (Neon)
✅ Interface intuitive avec boutons
✅ Logs détaillés pour debugging
✅ **Prêt à déployer sur Railway!**

---

## 🎯 Workflow typique

```
1. Démarrer le bot
   python bot.py

2. Sur Telegram, ajouter des comptes
   /add_account account1
   /add_account account2
   /add_account account3

3. Attendre les notifications
   🎬 @account1 EST EN LIVE!

4. Cliquer pour regarder sur TikTok
   [Ouvrir sur TikTok]
```

---

## ⚡ Commandes principales

```
/start              → Menu
/help              → Aide
/add_account @user → Ajouter
/remove @user      → Retirer
/list_accounts     → Lister
/status            → État
```

---

## 🆘 Problèmes rapides?

**"Bot doesn't respond"**
→ Vérifier `.env` et chat_id: [FAQ.md](FAQ.md)

**"Module not found"**
→ `pip install -r requirements.txt`

**"Token invalide"**
→ [SETUP_TOKEN.md](SETUP_TOKEN.md)

**Autre question?**
→ [FAQ.md](FAQ.md) a les réponses!

---

## 🔐 Important!

⚠️ **Ne jamais partager** votre `TELEGRAM_BOT_TOKEN`
⚠️ **Garder `.env` privé** (pas de GitHub!)
⚠️ **Vérifier les noms d'utilisateur** (sans @)

---

## 🌍 Déployer en production

Prêt à mettre le bot 24/7 sur le cloud?

**Railway est la solution la plus simple:**
- ✅ Gratuit pour commencer (~$5/mois après)
- ✅ Déploiement automatique depuis GitHub
- ✅ Gestion des variables en GUI
- ✅ Logs en temps réel
- ✅ Processus 24/7

**[→ Lire RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)** pour déployer en 10 minutes!

---

| Composant | Statut |
|-----------|--------|
| Bot Telegram | ✅ OK |
| Détection TikTok | ✅ OK |
| Notifications | ✅ OK |
| Documentation | ✅ Excellente |
| Prêt à l'emploi | ✅ OUI! |

---

## 🚀 Prêt à commencer?

### Si vous avez 5 minutes:
**→ [Allez à QUICKSTART.md](QUICKSTART.md)**

### Si vous avez 15 minutes:
**→ [Allez à INSTALLATION.md](INSTALLATION.md)**

### Si vous avez plus de temps:
**→ [Allez à INDEX.md](INDEX.md) pour voir toute la doc**

---

## 💡 Conseil pro

Avant de lancer le bot, vérifiez votre setup:

```bash
python check_setup.py
```

Ça va vérifier que tout est OK! ✅

---

## 📞 Besoin de spécifiques?

| Je veux... | Lire |
|-----------|------|
| Démarrer vite | [QUICKSTART.md](QUICKSTART.md) |
| Tout installer | [INSTALLATION.md](INSTALLATION.md) |
| Configurer Telegram | [SETUP_TOKEN.md](SETUP_TOKEN.md) |
| Voir des exemples | [EXAMPLES.md](EXAMPLES.md) |
| Poser des questions | [FAQ.md](FAQ.md) |
| Ajouter des features | [ADVANCED.md](ADVANCED.md) |
| Vue d'ensemble | [INDEX.md](INDEX.md) |
| Aide rapide | [REFERENCE.md](REFERENCE.md) |

---

## 🎉 Bonne chance!

Le bot est **prêt à l'emploi** et **totalement configurable**.

**Bienvenue dans votre nouvelle routine de monitoring TikTok! 🎬**

---

**Questions? Commencez par [QUICKSTART.md](QUICKSTART.md)!** 🚀
