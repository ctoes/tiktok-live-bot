# 🎬 TikTok Live Monitor Bot - Documentation Complète

> Un bot Telegram qui monitore automatiquement les comptes TikTok et envoie les directs (lives) en temps réel.

## 🚀 Démarrage rapide

### Pour les impatients (5 minutes)
```bash
cd c:\bot\Live
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Éditer .env avec votre token
python bot.py
```

Puis sur Telegram: `/add_account username`

**[→ Guide détaillé](INSTALLATION.md)**

---

## 📚 Documentation

### 📖 Pour débuter
- **[QUICKSTART.md](QUICKSTART.md)** - Guide de démarrage rapide (5 min)
- **[README.md](README.md)** - Documentation complète (détails)
- **[INSTALLATION.md](INSTALLATION.md)** - Installation étape par étape

### 🔑 Configuration
- **[SETUP_TOKEN.md](SETUP_TOKEN.md)** - Comment obtenir le token Telegram
- **.env.example** - Template de configuration

### 💡 Utilisation
- **[EXAMPLES.md](EXAMPLES.md)** - Cas d'usage concrets et exemples
- **[FAQ.md](FAQ.md)** - Questions fréquemment posées

### 🏗️ Développement
- **[ADVANCED.md](ADVANCED.md)** - Configuration avancée et extensions

---

## 📋 Structure du projet

```
c:\bot\Live/
├── 🤖 FICHIERS PRINCIPAUX
│   ├── bot.py                    # Bot Telegram principal
│   ├── tiktok_monitor.py         # Détection TikTok live
│   └── requirements.txt          # Dépendances Python
│
├── 📁 DOSSIERS
│   ├── config/                   # Configuration
│   │   └── accounts.json         # Comptes moniteurs (auto-créé)
│   ├── logs/                     # Historique
│   │   └── bot.log              # Detailed logs (auto-créé)
│   └── downloads/                # Vidéos téléchargées (auto-créé)
│
├── ⚙️ CONFIGURATION
│   ├── .env.example              # Template de config
│   ├── .env                      # Configuration réelle (À CRÉER)
│   └── .gitignore               # Pour ignorer les fichiers sensibles
│
├── 📚 DOCUMENTATION
│   ├── 📄 INDEX.md               # Ce fichier
│   ├── 📄 QUICKSTART.md          # Démarrage rapide
│   ├── 📄 README.md              # Documentation complète
│   ├── 📄 INSTALLATION.md        # Installation détaillée
│   ├── 📄 SETUP_TOKEN.md         # Guide token Telegram
│   ├── 📄 EXAMPLES.md            # Exemples et cas d'usage
│   ├── 📄 FAQ.md                 # Questions fréquentes
│   └── 📄 ADVANCED.md            # Fonctionnalités avancées
│
└── 🎯 SCRIPTS
    ├── run.bat                   # Lancer sur Windows
    └── run.sh                    # Lancer sur Linux/Mac
```

---

## 🎮 Commandes Telegram principales

```
/start              - Menu principal avec boutons
/help               - Affiche l'aide
/add_account @user  - Ajouter un compte TikTok
/remove @user       - Retirer un compte
/list_accounts      - Voir tous les comptes
/status             - État du bot
```

---

## ✨ Fonctionnalités

- ✅ **Monitoring automatique** toutes les 5 minutes
- ✅ **Détection de live** en temps réel
- ✅ **Notifications Telegram** immédiates
- ✅ **Gestion des comptes** via Telegram
- ✅ **Stockage persistant** en JSON
- ✅ **Interface interactive** avec boutons
- ✅ **Logs détaillés** pour debugging
- ✅ **Configuration flexible**

---

## 🗺️ Carte de navigation

### Je veux...

**Installer et lancer rapidement**
→ [QUICKSTART.md](QUICKSTART.md)

**Installer avec explicatif complet**
→ [INSTALLATION.md](INSTALLATION.md)

**Configurer mon token Telegram**
→ [SETUP_TOKEN.md](SETUP_TOKEN.md)

**Voir des exemples d'utilisation**
→ [EXAMPLES.md](EXAMPLES.md)

**Trouver réponses à mes questions**
→ [FAQ.md](FAQ.md)

**Ajouter des fonctionnalités**
→ [ADVANCED.md](ADVANCED.md)

**Lire tous les détails**
→ [README.md](README.md)

---

## 🎯 Cas d'usage typiques

### 1. Monitorer un ami qui stream
```
/add_account mon_ami
→ Vous recevez une notification quand il est en live
```

### 2. Tracker les comptes des competitors
```
/add_account competitor1
/add_account competitor2
/add_account competitor3
→ Notifications instantanées pour tous
```

### 3. Suivre les événements en direct
```
/add_account event_creator1
/add_account event_creator2
→ Aucun live n'échappera
```

---

## ⚡ Installation rapide (4 étapes)

### 1️⃣ Créer l'environnement
```bash
cd c:\bot\Live
python -m venv venv
.\venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac
```

### 2️⃣ Installer les dépendances
```bash
pip install -r requirements.txt
```

### 3️⃣ Configurer
```bash
copy .env.example .env  # Windows
# ou
cp .env.example .env    # Linux/Mac

# Éditer .env avec votre token et chat_id
# Voir SETUP_TOKEN.md pour obtenir le token
```

### 4️⃣ Lancer
```bash
python bot.py
```

**Done! ✅**

---

## 📊 Statut du projet

| Composant | Statut |
|-----------|--------|
| Bot Telegram | ✅ Complet |
| Monitoring TikTok | ✅ Fonctionnel |
| Gestion des comptes | ✅ Complète |
| Notifications | ✅ En place |
| Stockage | ✅ JSON |
| Documentation | ✅ Excellente |
| Logs | ✅ Détaillés |
| Interface | ✅ Intuitive |

---

## 📖 Table des matières détaillée

### Section 1: Démarrage
- [QUICKSTART.md](QUICKSTART.md) - 5 minutes pour démarrer
- [INSTALLATION.md](INSTALLATION.md) - Installation complète
- [SETUP_TOKEN.md](SETUP_TOKEN.md) - Configuration Telegram
- [NEON_SETUP.md](NEON_SETUP.md) - Configuration PostgreSQL (Neon)
- [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md) - Déploiement sur Railway

### Section 2: Utilisation
- [README.md](README.md) - Tous les détails
- [EXAMPLES.md](EXAMPLES.md) - Exemples concrets
- [FAQ.md](FAQ.md) - Questions fréquentes

### Section 3: Développement
- [ADVANCED.md](ADVANCED.md) - Fonctionnalités avancées
- [bot.py](bot.py) - Code source
- [tiktok_monitor.py](tiktok_monitor.py) - Moteur TikTok
- [database.py](database.py) - Module PostgreSQL

---

## 🔧 Maintenance

### Logs réguliers
```bash
tail -f logs/bot.log  # Suivre en temps réel
```

### Mise à jour des dépendances
```bash
pip install --upgrade -r requirements.txt
```

### Sauvegarde de la config
```bash
cp config/accounts.json config/accounts.json.backup
```

---

## ⚠️ Points importants

1. **Token Telegram:**
   - Garder `.env` secret
   - Ne pas partager le token
   - Si leak: créer nouveau bot

2. **Performance:**
   - Default: 5 min par vérification
   - 10-20 comptes: OK
   - 50+ comptes: peut être lent

3. **APIs TikTok:**
   - Changent souvent
   - Code peut nécessiter mises à jour
   - Respecter rate limits

---

## 🆘 Besoin d'aide?

| Question | Réponse |
|----------|---------|
| "Comment démarrer?" | Lire [QUICKSTART.md](QUICKSTART.md) |
| "Pas de notifs?" | Vérifier [FAQ.md](FAQ.md) Q9 |
| "Token invalide?" | Lire [SETUP_TOKEN.md](SETUP_TOKEN.md) |
| "Code ne marche pas?" | Vérifier [FAQ.md](FAQ.md) |
| "Besoin de plus?" | Lire [ADVANCED.md](ADVANCED.md) |

---

## 📞 Checklist de démarrage

- [ ] Python 3.8+ installé
- [ ] Dépendances installées (`requirements.txt`)
- [ ] Token Telegram obtenu
- [ ] Chat ID trouvé
- [ ] Fichier `.env` créé et rempli
- [ ] Bot lancé (`python bot.py`)
- [ ] Comptes ajoutés (`/add_account`)
- [ ] Test: `/start` sur Telegram
- [ ] Bot attend les lives!

---

## 🎉 Prêt à commencer?

**→ [Allez à QUICKSTART.md](QUICKSTART.md) pour commencer en 5 minutes!**

---

## 📄 Licences et attributions

- **Python Telegram Bot:** https://python-telegram-bot.org
- **yt-dlp:** https://github.com/yt-dlp/yt-dlp
- **Requests:** https://requests.readthedocs.io

---

**Dernière mise à jour:** 2024-01-15 ✨

**Version:** 1.0 - Stable

**Profitez de vos lives TikTok! 🎬**
