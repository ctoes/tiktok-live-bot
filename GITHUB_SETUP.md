# 📦 Préparer le code pour GitHub (Railway)

Avant de déployer sur Railway, vous devez avoir votre code sur GitHub.

## 1️⃣ Créer un repo GitHub

### Si vous n'avez pas de compte GitHub:

1. Aller sur: https://github.com
2. Cliquer **Sign up**
3. Créer un compte gratuit
4. Vérifier l'email

### Créer un nouveau repo:

1. Cliquer le **+** en haut à droite
2. **New repository**
3. Nommer le repo: `tiktok-bot-live`
4. **Public** (pour Railway)
5. **Create repository**

## 2️⃣ Configuration locale

### Initialiser Git dans le dossier du bot:

```bash
cd c:\bot\Live

# Initialiser git
git init

# Ajouter tous les fichiers
git add .

# Créer un commit initial
git commit -m "Initial commit: TikTok Live Monitor Bot"
```

### Ajouter le repo distant:

```bash
# Remplacer YOUR_USERNAME par votre username GitHub
# et YOUR_REPO par le nom du repo

git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Voir que ça a marché
git remote -v
```

### Envoyer sur GitHub:

```bash
# Version moderne (recommended)
git branch -M main
git push -u origin main

# Ou si vous avez une clé SSH configurée
# git push -u origin main
```

## 3️⃣ Vérifier le fichier .gitignore

Assurez-vous que `.gitignore` contient:

```
.env
.env.local
.env.*.local
```

**⚠️ IMPORTANT:** Les variables sensibles ne doivent JAMAIS être commitées!

Vérifier que `.env` n'est pas pushé:

```bash
# Voir les fichiers trackés
git ls-files

# Si .env est listé, l'ajouter à .gitignore et faire:
git rm --cached .env
git commit -m "Remove .env from tracking"
git push
```

## 4️⃣ Fichiers essentiels pour Railway

Railway détecte automatiquement les fichiers. Vérifiez que vous avez:

| Fichier | Nécessaire |
|---------|-----------|
| `requirements.txt` | ✅ OUI |
| `Procfile` | ✅ OUI (inclus) |
| `bot.py` | ✅ OUI |
| `tiktok_monitor.py` | ✅ OUI |
| `database.py` | ✅ OUI |
| `.gitignore` | ✅ OUI |
| `.env` | ❌ NON (ne pas commiter) |

## 5️⃣ Déployer sur Railway

Une fois le code sur GitHub:

1. Aller sur: https://railway.app
2. Cliquer **+ New Project**
3. **Deploy from GitHub repo**
4. Sélectionner votre repo `tiktok-bot-live`
5. Configurer les variables (voir RAILWAY_DEPLOYMENT.md)
6. C'est en live! 🚀

## 🔄 Mise à jour du code

Chaque fois que vous faites des changements:

```bash
# Voir les changements
git status

# Ajouter les changements
git add .

# Créer un commit
git commit -m "Description des changements"

# Pousser sur GitHub
git push origin main
```

Railway redéploiera automatiquement en ~30-60 secondes!

## 🆘 Troubleshooting

### "fatal: not a git repository"

Assurez-vous que vous êtes dans le bon dossier:

```bash
cd c:\bot\Live
git status
```

### "Permission denied (publickey)"

Vous avez besoin d'une clé SSH ou d'un token GitHub:

**Option 1: Utiliser HTTPS avec token**

```bash
# Générer un token sur GitHub:
# Settings → Developer settings → Personal access tokens → Generate new token

# Utiliser le token:
git remote set-url origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/YOUR_REPO.git

# Puis push
git push origin main
```

**Option 2: Configurer SSH**

https://docs.github.com/en/authentication/connecting-to-github-with-ssh

### ".env est commité accidentellement"

```bash
# Ajouter à .gitignore
echo ".env" >> .gitignore

# Supprimer du tracking
git rm --cached .env

# Commit
git commit -m "Remove .env from version control"

# Push
git push origin main
```

## 📝 Avant le push

Checklist avant de pousser sur GitHub:

- [ ] Tous les fichiers Python sont présents
- [ ] `requirements.txt` est à jour
- [ ] `Procfile` est présent
- [ ] `.env` n'est PAS commité
- [ ] `.gitignore` inclut `.env`
- [ ] Code teste localement
- [ ] Logs sensibles supprimés
- [ ] API keys/tokens pas dans le code

## 🎯 Après le push

1. ✅ Vérifier le repo sur GitHub
2. ✅ Aller sur Railway.app
3. ✅ Deploy from GitHub
4. ✅ Sélectionner le repo
5. ✅ Configurer variables
6. ✅ En live! 🚀

---

**Besoin d'aide Git?** Consulter [RAILWAY_DEPLOYMENT.md](RAILWAY_DEPLOYMENT.md)

**Besoin d'aide GitHub?** https://docs.github.com
