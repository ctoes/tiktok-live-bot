# 🗄️ Configuration Neon PostgreSQL

## Qu'est-ce que Neon?

**Neon** est un service PostgreSQL serverless basé sur le cloud.
- Gratuit en development
- Scalable automatiquement
- Excellent pour les bots

## 1️⃣ Créer un compte Neon

1. Aller sur: https://neon.tech
2. Cliquer sur **"Sign Up"** 
3. Créer un compte (avec GitHub c'est plus facile)
4. Confirmer l'email

## 2️⃣ Créer un projet

1. Une fois connecté, cliquer **"New Project"**
2. Donner un nom: `tiktok-bot` (ou ce que vous voulez)
3. Choisir la région closest de vous
4. Cliquer **"Create Project"**

## 3️⃣ Récupérer la connection string

Après la création du projet:

1. Vous verrez la page du projet
2. Copier la **CONNECTION STRING** (elle ressemble à):
   ```
   postgresql://user:password@ep-project-name.neon.tech/database?sslmode=require
   ```
3. **IMPORTANT:** Cette string contient votre password!

## 4️⃣ Configurer dans .env

```bash
copy .env.example .env
```

Éditer `.env` et ajouter:

```ini
DATABASE_URL=postgresql://user:password@ep-project-name.neon.tech/database?sslmode=require
```

Remplacer par votre vraie connection string.

## 5️⃣ Initialiser la base de données

**Optionnel:** Tester la connexion

```bash
python check_setup.py
```

La base de données se crée automatiquement au premier lancement.

---

## 📊 Structure de la base de données

### Table: accounts
```sql
CREATE TABLE accounts (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    user_id TEXT,
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_checked TIMESTAMP,
    is_live BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Colonnes:**
- `id` - ID unique du compte
- `username` - Nom d'utilisateur TikTok
- `user_id` - ID TikTok (optionnel)
- `added_date` - Quand le compte a été ajouté
- `last_checked` - Dernière vérification
- `is_live` - Est actuellement en live?

---

### Table: live_history
```sql
CREATE TABLE live_history (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id),
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP,
    viewers_count INTEGER,
    stream_title TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Colonnes:**
- `id` - ID unique de la session
- `account_id` - Référence au compte
- `started_at` - Quand le live a commencé
- `ended_at` - Quand le live a terminé
- `viewers_count` - Nombre de spectateurs
- `stream_title` - Titre du live

---

### Table: bot_users
```sql
CREATE TABLE bot_users (
    id SERIAL PRIMARY KEY,
    telegram_user_id INTEGER UNIQUE NOT NULL,
    telegram_username TEXT,
    telegram_chat_id INTEGER,
    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Colonnes:**
- `id` - ID unique
- `telegram_user_id` - ID Telegram de l'utilisateur
- `telegram_username` - Nom Telegram
- `telegram_chat_id` - Chat ID pour les notifications
- `is_active` - Est actif?

---

## 🔐 Sécurité

### Ne jamais partager la connection string!

⚠️ La CONNECTION STRING contient votre mdp!

- Ne **JAMAIS** la mettre sur GitHub
- Ne **JAMAIS** la partager
- Garder `.env` privé

### Si leak accidentelle:

1. Aller dans Neon Dashboard
2. Settings → Connection string
3. Générer une nouvelle password
4. Mettre à jour `.env`

---

## 📞 Gestion de la base


### Voir les données dans Neon

1. Aller sur: https://console.neon.tech
2. Sélectionner votre projet
3. Cliquer sur **"SQL Editor"** en bas
4. Écrire des requêtes SQL:

```sql
-- Voir tous les comptes
SELECT * FROM accounts;

-- Voir les lives
SELECT * FROM live_history;

-- Voir les stats
SELECT COUNT(*) FROM accounts;
```

### Supprimer toutes les données

⚠️ **ATTENTION:** Ceci supprime TOUT!

```sql
DELETE FROM live_history;
DELETE FROM accounts;
DELETE FROM bot_users;
```

---

## 🚀 Prochaines étapes

1. Créer compte Neon
2. Créer projet database
3. Copier connection string
4. Ajouter à `.env`
5. Lancer le bot:
   ```bash
   pip install -r requirements.txt
   python bot.py
   ```

---

## Troubleshooting

### "Cannot connect to database"
- Vérifier la connection string dans `.env`
- Vérifier internet connection
- Vérifier que DATABASE_URL est correct

### "SSL error"
- Neon utilise SSL par défaut
- Le `?sslmode=require` est obligatoire
- Déjà inclus dans la connection string

### "UNIQUE violation"
- Le compte existe déjà
- Utiliser `/remove` pour le retirer d'abord

### Je veux réinitialiser les données

```sql
-- Dans Neon SQL Editor:
DROP TABLE IF EXISTS live_history;
DROP TABLE IF EXISTS accounts;
DROP TABLE IF EXISTS bot_users;
```

Puis relancer le bot pour recréer les tables.

---

## 📊 Services gratuits alternatifs

Si Neon ne vous plaît pas:

- **PostgreSQL local:** `postgresql://localhost/tiktok_bot`
- **MongoDB Atlas:** Nécessite changement du code
- **Supabase:** Alternative à Neon (également PostgreSQL)
- **Railway:** Simple pour le déploiement

---

**Configuration complète? Lancez le bot!** 🚀

Pour plus d'infos, consultez [README.md](README.md)
