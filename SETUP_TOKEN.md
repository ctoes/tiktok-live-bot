# 🔑 Configuration du Telegram Bot Token

## Étapes pour obtenir un Telegram Bot Token

### 1. Créer un bot avec BotFather

1. Ouvrir **Telegram** sur votre téléphone ou desktop
2. Chercher **@BotFather** (c'est un bot officiel Telegram)
3. Cliquer pour l'ajouter à vos chats

### 2. Créer un nouveau bot

1. Envoyer le message `/newbot`
2. BotFather va vous demander un **nom** pour le bot
   - Exemple: `MyTikTokLiveBot`
3. Ensuite un **nom d'utilisateur** unique (doit finir par `_bot` ou `Bot`)
   - Exemple: `mytiktok_live_bot`

### 3. Récupérer le TOKEN

Après les étapes précédentes, BotFather vous enverra un message comme:

```
✅ Done! Congratulations on your new bot. You will find it at https://t.me/mytiktok_live_bot. You can now add a description, about section and profile picture for your bot, see /help for a list of commands. By the way, I noticed you resolved the host name thats great. Keep it up! ;)

Use this token to access the HTTP API:
1234567890:ABCDefGHIJKlmnoPQRSTuvwxyzABCDefGHI
```

**Copiez ce token (la longue chaîne de caractères)** et collez-le dans `.env`:

```
TELEGRAM_BOT_TOKEN=1234567890:ABCDefGHIJKlmnoPQRSTuvwxyzABCDefGHI
```

---

## Obtenir votre Chat ID

### Méthode 1: Via l'API (Rapide)

1. Envoyer un message à votre bot sur Telegram
2. Remplacer `TOKEN` par votre token dans cette URL:
   ```
   https://api.telegram.org/botTOKEN/getUpdates
   ```
3. Ouvrir l'URL dans un navigateur
4. Chercher `"chat":{"id":` suivi d'un nombre
   - Exemple: `"chat":{"id":123456789}`

5. Copier ce nombre dans `.env`:
   ```
   TELEGRAM_CHAT_ID=123456789
   ```

### Méthode 2: Via @userinfobot

1. Envoyer un message à **@userinfobot** sur Telegram
2. Il vous répondra avec votre **User ID**
3. C'est ce nombre qu'il faut dans `TELEGRAM_CHAT_ID`

---

## Exemple de fichier .env complet

```ini
TELEGRAM_BOT_TOKEN=1234567890:ABCDefGHIJKlmnoPQRSTuvwxyzABCDefGHI
TELEGRAM_CHAT_ID=123456789
LOG_LEVEL=INFO
```

---

## Sécurité

⚠️ **IMPORTANT:**
- Ne **JAMAIS** partager votre `TELEGRAM_BOT_TOKEN`
- Ne **JAMAIS** le mettre sur GitHub ou un dépôt public
- Garder le fichier `.env` privé
- Si vous révélez accidentellement le token, refaites `/newbot` dans BotFather

---

## Tester la configuration

Après avoir configuré `.env`, vous pouvez tester:

```bash
python bot.py
```

Le bot doit afficher:
```
✅ Bot démarré et prêt à monitorer!
```

Puis envoyez `/start` à votre bot sur Telegram pour confirmer! 🎉
