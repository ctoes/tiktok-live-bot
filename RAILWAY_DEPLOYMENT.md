# 🚀 Déploiement sur Railway

Railway est une plateforme cloud simple pour déployer des applications Python.

**Avantages:**
- ✅ Gratuit pour commencer (~$5/mois après)
- ✅ Déploiement automatique depuis GitHub
- ✅ Gestion des variables d'environnement (GUI)
- ✅ Logs en temps réel
- ✅ PostgreSQL inclus (optionnel)
- ✅ Support des processus 24/7
- ✅ Scaling automatique

## 1️⃣ Prérequis

- Un compte GitHub (avec le repo du bot)
- Un compte Railway (gratuit)
- Un compte Neon PostgreSQL (gratuit)

## 2️⃣ Créer un compte Railway

1. Aller sur: https://railway.app
2. Cliquer **"Login"** → **"GitHub"**
3. Authoriser Railway à accéder à vos repos GitHub
4. ✅ Connecté!

## 3️⃣ Créer un nouveau projet

1. Dans le dashboard Railway, cliquer **"+ New Project"**
2. Choisir **"Deploy from GitHub repo"**
3. Sélectionner le repo avec votre bot
4. Railway va detecter automatiquement que c'est Python
5. Cliquer **"Deploy"**

## 4️⃣ Configurer les variables d'environnement

Dans le dashboard Railway:

1. Aller dans votre projet
2. Cliquer sur l'app Python
3. Aller dans l'onglet **Variables**
4. Ajouter les variables:

```
TELEGRAM_BOT_TOKEN=votre_token_ici
TELEGRAM_CHAT_ID=votre_chat_id_ici
DATABASE_URL=postgresql://...@neon.tech/database?sslmode=require
LOG_LEVEL=INFO
```

**⚠️ IMPORTANT:** 
- Pas de guillemets autour des valeurs
- Pas d'espaces
- DATABASE_URL doit être exactement comme fourni par Neon

## 5️⃣ Vérifier le déploiement

### Via Railway Dashboard

1. Cliquer sur le projet
2. Voir l'onglet **"Deployments"**
3. Le déploiement doit être **"Success"** (vert)
4. Status doit être **"Running"**

### Voir les logs

1. Dans l'app, cliquer **"View Logs"**
2. Chercher: `✅ Bot démarré et prêt à monitorer!`

Les logs en temps réel montrent ce que le bot fait.

### Tester le bot

Sur Telegram:
```
/start
```

Vous devez voir le menu et pouvoir ajouter des comptes.

## 6️⃣ Configuration post-déploiement

### Auto-redémarrage

Railway redémarre automatiquement si:
- L'app crash
- Le serveur redémarre
- Vous poussez du code GitHub

### Logs permanents

Tous les logs sont sauvegardés dans Railway:
- Voir dans l'onglet **Logs**
- Télécharger les anciens logs

### Scaling

- Railway scale automatiquement
- Pour plus de puissance: modifier le plan

## 📊 Coûts

| Plan | Prix | Utilisation |
|------|------|-------------|
| Free trial | $5 credit | 1 mois gratuit |
| Pay as you go | $0.50/GB ram/h | Le plus courant |
| Pro | $20/mois | Si beaucoup de comptes |

**Notre bot:** ~$1-2/mois avec Neon gratuit

## 🔄 Mise à jour du code

### Via GitHub (automatique)

1. Faire un changement au code localement
2. `git push origin main`
3. Railway détecte le changement
4. Redéploie automatiquement (~1 min)

### Sans GitHub (manuel)

Railway CLI:
```bash
# Installer Railway CLI
npm install -g @railway/cli

# Se connecter
railway login

# Déployer
railway up
```

## 🛑 Arrêter/Redémarrer

### Via Dashboard

1. Cliquer sur le projet
2. Cliquer **Settings**
3. **Stop** (arrête l'app)
4. **Start** (redémarre)

### Via CLI

```bash
railway down   # Arrête
railway up     # Redémarre
```

## 📈 Monitorer l'utilisation

Railway affiche:
- **CPU Usage** - Utilisation processeur
- **Memory** - RAM utilisée
- **Network** - Bande passante
- **Logs** - Historique complet

Exemple d'utilisation bot TikTok:
- CPU: ~1-5%
- RAM: ~100-200 MB
- Bandwidth: ~10-50 MB/jour

## 🆘 Troubleshooting

### "Deployment failed"

Voir les logs pour l'erreur:

```
ERROR: Cannot find module XYZ
```

**Solution:** Assurez-vous que `requirements.txt` est à jour

### "Bot not responding"

1. Vérifier dans Logs que bot a démarré
2. Vérifier variables d'environnement sont correctes
3. Vérifier TELEGRAM_CHAT_ID est bon

### "Database connection error"

1. Vérifier DATABASE_URL dans Railway
2. Vérifier que la DB Neon est active
3. Vérifier format SSL: `?sslmode=require`

### "Logs vides ou timeout"

Possible que le bot crash au démarrage:
1. Vérifier les dernières lignes de logs
2. Vérifier TELEGRAM_BOT_TOKEN
3. Vérifier DATABASE_URL

## 🔐 Sécurité

### Variables d'environnement

✅ **JAMAIS** à commiter dans GitHub:
```bash
# .gitignore
.env
.env.local
```

✅ **Utiliser** Railway pour stocker les secrets:
- Dashboard → Variables
- Pas dans le code

✅ Si leak accidentelle:
1. Créer nouveau Telegram Bot (BotFather)
2. Mettre à jour TELEGRAM_BOT_TOKEN dans Railway
3. Créer nouveau password Neon
4. Mettre à jour DATABASE_URL

## 📝 Fichiers necessaires

Railway détecte automatiquement:

- ✅ `requirements.txt` - Dépendances Python
- ✅ `Procfile` - Commande de démarrage (inclus)
- ✅ `.gitignore` - Fichiers à ignorer (inclus)
- ⚠️ `.env` - NE PAS commiter (inclus dans .gitignore)

## 🚀 Déploiement avec Railway CLI

Alternative au GitHub automatic:

### Installation

```bash
npm install -g @railway/cli
```

### Déploiement

```bash
# Depuis le répertoire du bot
cd c:\bot\Live

# Se connecter
railway login

# Créer un nouveau projet
railway init

# Ajouter variables
railway variables:set TELEGRAM_BOT_TOKEN=your_token
railway variables:set TELEGRAM_CHAT_ID=your_id
railway variables:set DATABASE_URL=your_db_url

# Déployer
railway up
```

## 📱 Dashboard Railway

Après déploiement:

**URL:** https://dashboard.railway.app

**Que vous pouvez faire:**
- Voir l'état de l'app
- Lire les logs en temps réel
- Gérer les variables
- Voir l'utilisation des ressources
- Redémarrer l'app
- Modifier le plan pricing
- Intégrer les domaines
- Activer auto-deploy

## 💡 Tips & Tricks

### 1. Logs en temps réel

```bash
railway logs -f  # Follow logs (comme tail -f)
```

### 2. Voir les variables

```bash
railway variables
```

### 3. Arrêter temporairement

```bash
railway down
```

### 4. Connaitre le statut

```bash
railway status
```

### 5. Shell distant

```bash
railway shell
```

Exécuter des commandes sur le serveur distant!

## 🎯 Prochaines étapes

1. ✅ Créer compte Railway
2. ✅ Connecter repo GitHub
3. ✅ Configurer variables
4. ✅ Déployer
5. ✅ Tester sur Telegram
6. ✅ Voir les logs
7. ✅ C'est en live! 🎉

## 📞 Support Railway

- **Docs:** https://docs.railway.app
- **Discord:** https://discord.gg/railway
- **Status:** https://status.railway.app

## Alternative à Railway

Si Railway ne vous plaît pas:

- **Heroku** - Ancien choix (maintenant payant)
- **Replit** - Simple pour les scripts
- **PythonAnywhere** - Spécialisé Python
- **VPS** - Google Cloud, AWS, Linode, etc.

---

**Prêt à déployer? Allez sur https://railway.app!** 🚀
