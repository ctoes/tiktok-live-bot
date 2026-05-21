# 🎯 Guide de Démarrage Rapide

## 👋 Bienvenue!

Vous avez un bot TikTok Live Monitor complet et prêt à l'emploi.

## 📚 Par donde commencer?

### Vous êtes pressé? (5 minutes)
→ Lisez [INSTALLATION.md](INSTALLATION.md) - Installation rapide

### Vous voulez les détails complets?
→ Lisez [README.md](README.md) - Documentation complète

### Vous voulez des exemples concrets?
→ Lisez [EXAMPLES.md](EXAMPLES.md) - Cas d'usage réels

### Vous avez des questions sur Telegram?
→ Lisez [SETUP_TOKEN.md](SETUP_TOKEN.md) - Guide token Telegram

### Vous êtes développeur?
→ Lisez [ADVANCED.md](ADVANCED.md) - Configuration avancée

---

## 🚀 Installation express (copier-coller)

### 1. Ouvrir CMD/Terminal

```bash
cd c:\bot\Live
```

### 2. Environnement virtuel

```bash
python -m venv venv
.\venv\Scripts\activate
```

### 3. Dépendances

```bash
pip install -r requirements.txt
```

### 4. Configuration Neon

**Créer un compte:** https://neon.tech
- Créer un projet
- Copier la connection string

**[Guide détaillé Neon](NEON_SETUP.md)**

### 5. Configuration

```bash
copy .env.example .env
```
Éditer `.env` avec:
- Votre TELEGRAM_BOT_TOKEN
- Votre TELEGRAM_CHAT_ID
- Votre DATABASE_URL (Neon)

### 6. Lancer le bot

```bash
python bot.py
```

### 7. Ajouter compte (sur Telegram)

```
/add_account username
```

**C'est tout! ✅**

---

## 🎬 Flux de base

```
┌─────────────────┐
│  Démarrer bot   │
│  python bot.py  │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│  Ajouter comptes    │
│  /add_account @user │
└────────┬────────────┘
         │
         ▼
┌──────────────────────┐
│  Bot vérifie chaque  │
│  5 minutes si LIVE   │
└────────┬─────────────┘
         │
         ▼
┌──────────────────────┐
│  Notification Telegram│
│  🎬 @user EST EN LIVE│
└──────────────────────┘
```

---

## 📋 Fichiers importants

| Fichier | Rôle |
|---------|------|
| `bot.py` | 🤖 Bot principal |
| `tiktok_monitor.py` | 📡 Détection TikTok |
| `.env` | 🔑 Configuration (à créer) |
| `config/accounts.json` | 📝 Liste des comptes |
| `logs/bot.log` | 📊 Historique |

---

## 🎮 Commandes Telegram essentielles

| Commande | Effet |
|----------|-------|
| `/start` | Menu |
| `/add @user` | Ajouter un compte |
| `/remove @user` | Retirer un compte |
| `/list_accounts` | Voir tous les comptes |
| `/status` | État du bot |

---

## ⚡ Raccourcis

### Démarrage rapide script

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
./run.sh
```

---

## 🆘 Problèmes courants

### "Bot doesn't respond"
- Vérifier que TELEGRAM_CHAT_ID est correct dans `.env`

### "Module not found"
```bash
pip install -r requirements.txt
```

### "Token not configured"
- Éditez `.env` et ajoutez votre TELEGRAM_BOT_TOKEN

### "API Error"
- Les APIs TikTok changent parfois, code peut nécessiter mise à jour

---

## 📞 Besoin d'aide immédiate?

1. **Installation:** [INSTALLATION.md](INSTALLATION.md)
2. **Token Telegram:** [SETUP_TOKEN.md](SETUP_TOKEN.md)
3. **Exemples:** [EXAMPLES.md](EXAMPLES.md)
4. **Code:** [README.md](README.md)
5. **Avancé:** [ADVANCED.md](ADVANCED.md)

---

## 🎯 Prochaines étapes

- [ ] Installation de Python/dépendances
- [ ] Configuration du token Telegram
- [ ] Lancement du bot
- [ ] Ajouter les premiers comptes
- [ ] Tester avec `/start`
- [ ] Attendre un live! 🎬

---

**Prêt? Commencez par [INSTALLATION.md](INSTALLATION.md)!** 🚀
