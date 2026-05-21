# ❓ Questions Fréquemment Posées (FAQ)

## Installation

### Q1: Où télécharger Python?
**R:** https://www.python.org (version 3.8+)

### Q2: Venv ne fonctionne pas
**R:** Essayez:
```bash
python -m venv venv  # Ou
python3 -m venv venv
```

### Q3: Pip install ne marche pas
**R:** Assurez-vous que venv est activé:
```bash
# Windows:
.\venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### Q4: "No module named telegram"
**R:** Réinstallez:
```bash
pip install --upgrade python-telegram-bot
```

---

## Token Telegram

### Q5: Où obtenir mon token Telegram?
**R:** Lire [SETUP_TOKEN.md](SETUP_TOKEN.md) - très détaillé

### Q6: Mon token ne marche pas
**R:** Vérifications:
1. Token copié entièrement?
2. Pas d'espaces au début/fin?
3. Format correct? `1234567890:ABCDefGHIJKlmnoPQRSTuvwxyzABCDefGHI`

### Q7: Comment obtenir mon CHAT_ID?
**R:** Deux méthodes dans [SETUP_TOKEN.md](SETUP_TOKEN.md):
- Via API (plus rapide)
- Via @userinfobot

### Q8: .env ne charge pas
**R:** Vérifier:
1. Fichier nommé exactement `.env` (pas `.env.txt`)
2. Dans le dossier `c:\bot\Live\`
3. Format correct: `CLES=valeur`

---

## Monitoring TikTok

### Q9: Pourquoi aucune notification?
**R:** Vérifications:
1. Bot lancé? (`✅ Bot démarré`)
2. Comptes ajoutés? (`/list_accounts`)
3. Chat_id correct? (tester `/start`)
4. Compte vraiment en live? (check TikTok)

### Q10: Comment ajouter un compte?
**R:** 3 façons:
```bash
/add @username
/add_account username
/start → ➕ Ajouter Compte
```

### Q11: Les API TikTok changent souvent?
**R:** Oui. Si ça ne marche plus:
1. Vérifier les logs: `logs/bot.log`
2. Lire [ADVANCED.md](ADVANCED.md)
3. Le code peut nécessiter une mise à jour

### Q12: Combien de comptes peuvent être suivis?
**R:** Illimité techniquement, mais:
- 10 comptes = OK (~50MB RAM)
- 50 comptes = correct (~100MB RAM)
- 200+ comptes = lent (ressources)

### Q13: Intervalle min de vérification?
**R:** Recommandé 60 secondes minimum
```python
# bot.py ligne 30
MONITOR_INTERVAL = 60  # 1 minute
```

---

## Telegram Bot

### Q14: Bot ne répond pas aux commandes
**R:** Solutions:
```bash
# 1. Redémarrer le bot:
# Ctrl+C puis:
python bot.py

# 2. Vérifier chat_id:
# Dans .env, est-ce correct?

# 3. Tester manuellement:
# Envoyer /help au bot
```

### Q15: Messages d'erreur cryptiques
**R:** Vérifier les logs:
```bash
tail -f logs/bot.log  # Linux/Mac
# Ou ouvrir logs/bot.log avec l'éditeur
```

### Q16: Comment arrêter le bot proprement?
**R:**
```bash
# Dans le terminal:
Ctrl+C

# Ça va arrêter proprement
```

### Q17: Bot se relance tout seul
**R:** Normal si vous utilisez `run.bat` ou `run.sh`
- Ils redémarrent en cas d'erreur
- Pour vraiment arrêter: fermer le terminal

---

## Configuration

### Q18: Changer la fréquence de vérification
**R:** Dans `bot.py` ligne 30:
```python
MONITOR_INTERVAL = 300  # Valeur en secondes
```

Exemples:
- 30 = chaque 30 secondes (CPU haute)
- 60 = chaque 1 minute (équilibré)
- 300 = chaque 5 minutes (économique)
- 600 = chaque 10 minutes (ultra économique)

### Q19: Réduire la verbosité des logs
**R:** Dans `.env`:
```
LOG_LEVEL=WARNING  # Au lieu de INFO
```

### Q20: Monitorer depuis plusieurs chats Telegram
**R:** Lire [ADVANCED.md](ADVANCED.md) section "Ajouter plusieurs chats"

---

## Performance

### Q21: Bot utilise trop de RAM
**R:** Solutions:
1. Réduire la fréquence: `MONITOR_INTERVAL = 600`
2. Retirer des comptes: `/remove @username`
3. Réduire les logs: `LOG_LEVEL=ERROR`

### Q22: Bot est lent
**R:** Causes possibles et solutions:
```
1. Trop de comptes?
   → Réduire à 10-20 comptes

2. Intervalle trop court?
   → Augmenter à 300s (5 min)

3. Internet lent?
   → Augmenter timeout dans code

4. Logs verbeux?
   → LOG_LEVEL=WARNING
```

### Q23: Comment monitorer 24/7?
**R:** Options:
1. **PC allumé 24/7** (simple)
2. **Serveur Linux** (mieux)
3. **Docker sur VPS** (professionnel)
4. **Task Scheduler Windows** (intermédiaire)

Lire [ADVANCED.md](ADVANCED.md) section "Déploiement en production"

---

## Erreurs courantes

### Q24: "Error: tiktok.com returned 429"
**R:** Limite de requêtes atteinte
Solution:
```python
MONITOR_INTERVAL = 600  # Augmentez
```

### Q25: "Error: Cannot connect to api.telegram.org"
**R:** Problème internet ou Token invalide
```bash
1. Vérifier connexion internet
2. Vérifier TELEGRAM_BOT_TOKEN dans .env
3. Redémarrer le bot
```

### Q26: "certifi.errors.SSLError"
**R:** Certificat SSL manquant (rare)
```bash
pip install --upgrade certifi
```

### Q27: "Invalid chat_id"
**R:** Chat_id incorrect
- Refaire la procédure dans [SETUP_TOKEN.md](SETUP_TOKEN.md)
- Vérifier dans .env qu'il n'y a pas d'espace

---

## Données

### Q28: Où sont sauvegardés les comptes?
**R:** `config/accounts.json` (fichier JSON)

### Q29: Puis-je éditer accounts.json manuellement?
**R:** Oui, mais format JSON doit être valide:
```json
{
  "accounts": [
    {
      "username": "user1",
      "user_id": null,
      "added_date": "2024-01-01T12:00:00",
      "last_checked": null,
      "is_live": false
    }
  ]
}
```

### Q30: Comment réinitialiser la configuration?
**R:**
```bash
# Supprimer le fichier:
del config/accounts.json  # Windows
rm config/accounts.json   # Linux/Mac

# Relancer le bot - nouveau accounts.json sera créé
python bot.py
```

---

## Sécurité

### Q31: Mon token est leakké?
**R:** Urgence!
1. Aller dans BotFather
2. `/mybots` → ton bot → Edit → Edit Token
3. Générer un nouveau token
4. Mettre à jour .env

### Q32: Quelqu'un peut voir mon .env?
**R:** Non, si:
1. `.env` n'est pas commité (vérifier `.gitignore`)
2. Fichier gardé localement
3. Permissions d'accès fichier OK

### Q33: Comment stocker les tokens en sécurité?
**R:** Options:
1. **Variables d'environnement Windows** (plus sûr)
2. **Fichier .env** (basique)
3. **Vault/Secrets Manager** (enterprise)

Lire [ADVANCED.md](ADVANCED.md) section "Sécurité avancée"

---

## Développement

### Q34: Comment ajouter des fonctionnalités?
**R:** Lire [ADVANCED.md](ADVANCED.md) section "Extensions possibles"

### Q35: Compatible avec quel Python?
**R:** Python 3.8+
- 3.8, 3.9, 3.10, 3.11, 3.12 ✅

### Q36: Puis-je utiliser Docker?
**R:** Oui! Lire [ADVANCED.md](ADVANCED.md) section "Avec Docker"

### Q37: Comment contribuer/améliorer?
**R:** Code open source, modifiez comme vous voulez!

---

## Support

### Q38: Qui contacter pour aide?
**R:** Documentation:
1. [README.md](README.md) - vue d'ensemble
2. [INSTALLATION.md](INSTALLATION.md) - installation
3. [EXAMPLES.md](EXAMPLES.md) - cas d'usage
4. [ADVANCED.md](ADVANCED.md) - fonctionnalités avancées
5. [SETUP_TOKEN.md](SETUP_TOKEN.md) - Telegram token

### Q39: Où reporter les bugs?
**R:** Vérifier les logs:
```bash
cat logs/bot.log
# Identifier le problème
```

### Q40: Autres questions?
**R:** Relisez [README.md](README.md) - très complet!

---

**Pas trouvé la réponse?** Cherchez dans les autres docs! 📚
