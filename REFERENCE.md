# 🎯 Résumé et Référence Rapide

## Qu'est-ce que ce projet?

Un **bot Telegram** qui :
1. 🔍 **Monitore** les comptes TikTok (toutes les 5 min)
2. 🎬 **Détecte** quand ils font un live
3. 📲 **Envoie une notification** sur Telegram
4. 🎮 **Permet de gérer** les comptes en temps réel

---

## Installation en 4 étapes

```bash
# 1. Créer l'environnement
python -m venv venv
.\venv\Scripts\activate

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Configurer
copy .env.example .env
# Éditer .env

# 4. Lancer
python bot.py
```

---

## Référence rapide des commandes

```
/start                  Menu principal
/help                   Aide
/add_account @user      Ajouter un compte
/remove @user           Retirer un compte
/list_accounts          Voir tous les comptes
/status                 État du bot
```

---

## Navigation des fichiers

```
bot.py                  → Bot principal
tiktok_monitor.py       → Détection TikTok
.env                    → Configuration (à créer)
config/accounts.json    → Comptes sauvegardés
logs/bot.log            → Historique
```

---

## Documentation

| Fichier | Utilité |
|---------|---------|
| **INDEX.md** | Vue d'ensemble (vous êtes ici) |
| **QUICKSTART.md** | Démarrage en 5 min |
| **INSTALLATION.md** | Installation détaillée |
| **README.md** | Documentation complète |
| **SETUP_TOKEN.md** | Obtenir token Telegram |
| **NEON_SETUP.md** | Configurer PostgreSQL Neon |
| **RAILWAY_QUICK.md** | Déployer en 10 min (express) |
| **RAILWAY_DEPLOYMENT.md** | Déployer sur Railway (détails) |
| **EXAMPLES.md** | Cas d'usage |
| **FAQ.md** | Questions réponses |
| **ADVANCED.md** | Fonctionnalités avancées |

---

## Checklist rapide

- [ ] Python 3.8+ installé
- [ ] Venv activé
- [ ] Dépendances installées
- [ ] Token Telegram obtenu
- [ ] Chat ID trouvé
- [ ] `.env` rempli
- [ ] Bot lancé
- [ ] `/start` fonctionne
- [ ] Comptes ajoutés

---

## Aide rapide

**Bot ne répond pas?**
→ Vérifier `.env`, chat_id correct?

**Pas de notifications?**
→ Ajouter comptes: `/add_account username`

**Import error?**
→ `pip install -r requirements.txt`

**Plus d'infos?**
→ Lire [FAQ.md](FAQ.md)

---

## Fichier de config template

```ini
# .env
TELEGRAM_BOT_TOKEN=votre_token_ici
TELEGRAM_CHAT_ID=votre_chat_id_ici
LOG_LEVEL=INFO
```

---

## Ports et URLs

- Télégramme: via API oficial
- TikTok: via requests/web scraping
- Aucun port ouvert localement

---

## Limitations

- APIs TikTok changent souvent
- Certains comptes privés ne marchent pas
- Rate limit TikTok ~1000 req/h

---

## Prochaines étapes

1. **Démarrer:** [QUICKSTART.md](QUICKSTART.md)
2. **Configurer:** [SETUP_TOKEN.md](SETUP_TOKEN.md)
3. **Lancer:** `python bot.py`
4. **Utiliser:** `/add_account username`

---

**Questions?** → Consultez [FAQ.md](FAQ.md) ou relisez le doc pour votre cas.
