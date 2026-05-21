# 🚀 Railway Déploiement - 10 minutes

**La manière la plus rapide de mettre votre bot 24/7 sur le cloud!**

## ⚡ 5 étapes rapides

### 1️⃣ Créer un compte Railway (2 min)

```
1. Aller sur: https://railway.app
2. Cliquer "Login" → "GitHub"
3. Authoriser Railway
4. ✅ Connecté!
```

### 2️⃣ Déployer le bot (2 min)

```
1. Cliquer "+ New Project"
2. "Deploy from GitHub repo"
3. Sélectionner votre repo (tiktok-bot)
4. Cliquer "Deploy"
⏳ Attendre 1-2 min...
✅ Déployé!
```

### 3️⃣ Ajouter les variables (2 min)

Dans le dashboard Railway:

```
App → Variables → Ajouter:

TELEGRAM_BOT_TOKEN=votre_token
TELEGRAM_CHAT_ID=votre_id
DATABASE_URL=votre_neon_url
LOG_LEVEL=INFO
```

### 4️⃣ Vérifier les logs (1 min)

```
Voir "View Logs"
Chercher: ✅ Bot démarré et prêt à monitorer!
```

### 5️⃣ Tester sur Telegram (1 min)

```
Envoyer: /start
Vous devez voir le menu!
```

**C'est en live! 🎉**

---

## 📲 C'est tout!

| Étape | Temps |
|-------|-------|
| 1. Créer compte | 2 min |
| 2. Déployer | 2 min |
| 3. Variables | 2 min |
| 4. Vérifier logs | 1 min |
| 5. Tester | 1 min |
| **TOTAL** | **~10 min** |

---

## 🎯 Maintenant quoi?

✅ Bot est en live 24/7
✅ Railway redémarre automatiquement en cas de crash
✅ Logs en temps réel visible
✅ Variables gérées en sécurité

Chaque fois que vous `git push`, Railway redéploie automatiquement!

---

## ❌ Problèmes?

**"Bot not running"**
- Vérifier dans Logs quelle erreur
- Vérifier TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID

**"Database error"**
- Vérifier DATABASE_URL est correct
- Vérifier format SSL: `?sslmode=require`

**"Variables not updating"**
- Redémarrer l'app (Settings → Stop → Start)

---

**Pour plus de détails: [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)**

**Prêt? Allez sur https://railway.app!** 🚀
