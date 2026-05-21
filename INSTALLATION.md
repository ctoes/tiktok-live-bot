# 📚 Guide Complet d'Installation

## 🚀 Installation rapide (5 minutes)

### Étape 1: Télécharger le projet
```bash
cd c:\bot\Live
```

### Étape 2: Créer l'environnement virtuel
```bash
python -m venv venv
```

### Étape 3: Activer l'environnement
**Sur Windows:**
```bash
.\venv\Scripts\activate
```

**Sur Linux/Mac:**
```bash
source venv/bin/activate
```

### Étape 4: Installer les dépendances
```bash
pip install -r requirements.txt
```

### Étape 5: Configurer la base de données Neon

1. **Créer un compte Neon:** https://neon.tech
2. **Créer un projet** et copier la connection string
3. **[Lire le guide Neon complet](NEON_SETUP.md)**

### Étape 6: Configurer le token Telegram
1. **Lire:** [SETUP_TOKEN.md](SETUP_TOKEN.md)
2. **Copier:** `copy .env.example .env` (Windows) ou `cp .env.example .env` (Linux/Mac)
3. **Éditer:** Ouvrir `.env` et remplir:
   - `TELEGRAM_BOT_TOKEN=` (votre token)
   - `TELEGRAM_CHAT_ID=` (votre ID)
   - `DATABASE_URL=` (votre connection Neon)

### Étape 7: Démarrer le bot
**Windows:**
```bash
run.bat
```
ou
```bash
python bot.py
```

**Linux/Mac:**
```bash
./run.sh
```
ou
```bash
python3 bot.py
```

---

## ✅ Vérification du fonctionnement

Une fois le bot démarré, vous devriez voir:
```
✅ Bot démarré et prêt à monitorer!
🔍 Vérification des comptes...
```

Puis sur Telegram:
1. Envoyer `/start` à votre bot
2. Vous devez voir un menu avec des boutons
3. Tester `/add_account` pour ajouter un compte

---

## 📖 Commandes de base

### Pour l'utilisateur (sur Telegram)

| Commande | Effet |
|----------|-------|
| `/start` | Menu principal |
| `/help` | Affiche l'aide |
| `/list_accounts` | Voir tous les comptes |
| `/add_account @username` | Ajouter un compte |
| `/remove_account @username` | Retirer un compte |
| `/status` | Voir le statut |

### Pour le développeur (en terminal)

```bash
# Activer l'environnement virtuel
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Installer des packages supplémentaires
pip install <nom-du-package>

# Voir les logs
tail -f logs/bot.log  # Linux/Mac
Get-Content logs/bot.log -Wait  # Windows PowerShell

# Désactiver l'environnement virtuel
deactivate
```

---

## 🔧 Configurations communes

### Augmenter la fréquence de vérification à 60 secondes

Dans `bot.py`, ligne 30:
```python
MONITOR_INTERVAL = 60  # Au lieu de 300
```

### Désactiver les logs détaillés

Dans `.env`:
```
LOG_LEVEL=WARNING
```

### Ajouter plusieurs comptes au démarrage

Éditer `config/accounts.json`:
```json
{
  "accounts": [
    {"username": "account1", "user_id": null, "added_date": "2024-01-01T12:00:00", "last_checked": null, "is_live": false},
    {"username": "account2", "user_id": null, "added_date": "2024-01-01T12:00:00", "last_checked": null, "is_live": false},
    {"username": "account3", "user_id": null, "added_date": "2024-01-01T12:00:00", "last_checked": null, "is_live": false}
  ]
}
```

---

## 🆘 Troubleshooting

### Erreur: "TELEGRAM_BOT_TOKEN not configured"
**Solution:**
- Vérifier que `.env` existe
- Vérifier que `TELEGRAM_BOT_TOKEN=` a une valeur
- Redémarrer le bot

### Erreur: "No module named 'telegram'"
**Solution:**
- Vérifier que l'environnement virtuel est activé
- Relancer: `pip install -r requirements.txt`

### Bot démarre mais ne répond pas
**Solution:**
- Vérifier que le `TELEGRAM_CHAT_ID` est correct
- Envoyer un message au bot (pour l'initialiser)
- Vérifier les logs: `logs/bot.log`

### Pas de notifications de live
**Solutions possibles:**
- Les API TikTok changent souvent
- Vérifier les noms d'utilisateur (sans @)
- Vérifier que les comptes existent réellement
- Augmenter la fréquence de vérification

---

## 📁 Structure finale

Après l'installation, vous aurez:

```
c:\bot\Live\
├── venv/                        # Environnement virtuel
├── bot.py                      # ✅ Bot principal
├── tiktok_monitor.py           # ✅ Module TikTok
├── requirements.txt            # ✅ Dépendances
├── .env                        # ✅ Configuration (à créer)
├── .env.example               # Exemple
├── README.md                  # Documentation principale
├── SETUP_TOKEN.md             # Guide tokens
├── INSTALLATION.md            # Ce fichier
├── run.bat                    # Script Windows
├── run.sh                     # Script Linux/Mac
├── config/
│   └── accounts.json          # Comptes sauvegardés
└── logs/
    └── bot.log                # Fichier de log
```

---

## 🎯 Prochaines étapes

1. **Installation:** Suivez les 6 étapes ci-dessus
2. **Configuration:** Lire [SETUP_TOKEN.md](SETUP_TOKEN.md)
3. **Lancer:** `python bot.py`
4. **Ajouter des comptes:** `/add_account username`
5. **Attendre les lives!** 🎬

---

## 💡 Conseils

- Garder le bot en local ou sur un serveur 24/7 pour la détection continue
- Les comptes privés ne marchent pas toujours
- Le détail des comptes se sauvegarde dans `config/accounts.json`
- Les logs détaillés aident au debugging

---

**Besoin d'aide? Relisez [README.md](README.md) pour plus de détails!**
