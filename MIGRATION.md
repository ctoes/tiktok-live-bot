# 🔄 Migration JSON → PostgreSQL (Neon)

Si vous aviez déjà un bot avec configuration JSON et voulez migrer vers PostgreSQL (Neon).

## Avant la migration

Assurez-vous d'avoir :
- ✅ Un compte Neon créé
- ✅ Une database Neon configurée
- ✅ La CONNECTION STRING dans `.env`
- ✅ Les anciens comptes dans `config/accounts.json`

## Migration automatique (recommandée)

Créer un fichier `migrate_to_postgres.py`:

```python
import asyncio
import json
from dotenv import load_dotenv
from database import TikTokDatabase

async def migrate():
    """Migrer les comptes de JSON vers PostgreSQL"""
    load_dotenv()
    
    # Charger les anciens comptes
    with open('config/accounts.json', 'r') as f:
        data = json.load(f)
    
    accounts = data.get('accounts', [])
    
    if not accounts:
        print("❌ Aucun compte à migrer")
        return
    
    # Initialiser la base de données
    import os
    db = TikTokDatabase(os.getenv('DATABASE_URL'))
    await db.connect()
    
    print(f"📦 Migration de {len(accounts)} comptes...")
    
    # Migrer chaque compte
    for account in accounts:
        username = account['username']
        success = await db.add_account(username)
        
        if success:
            print(f"✅ {username}")
        else:
            print(f"⚠️  {username} (existe déjà?)")
    
    print("\n✅ Migration complète!")
    print("Vous pouvez maintenant supprimer config/accounts.json")
    
    await db.disconnect()

if __name__ == '__main__':
    asyncio.run(migrate())
```

Exécuter:
```bash
python migrate_to_postgres.py
```

## Migration manuelle

Si la migration auto ne marche pas :

### Étape 1: Lire vos anciens comptes

```python
import json

with open('config/accounts.json', 'r') as f:
    data = json.load(f)

for account in data['accounts']:
    print(account['username'])
```

### Étape 2: Les ajouter manuellement

```bash
# Lancer le bot
python bot.py

# Sur Telegram, ajouter les comptes un par un:
/add_account account1
/add_account account2
/add_account account3
```

Ou via Neon SQL:

```sql
INSERT INTO accounts (username) VALUES 
('account1'),
('account2'),
('account3');
```

## Vérifier la migration

### Via Python

```python
import asyncio
from database import TikTokDatabase
import os
from dotenv import load_dotenv

async def check():
    load_dotenv()
    db = TikTokDatabase(os.getenv('DATABASE_URL'))
    await db.connect()
    
    accounts = await db.get_all_accounts()
    print(f"Comptes dans PostgreSQL: {len(accounts)}")
    
    for acc in accounts:
        print(f"  - @{acc['username']}")
    
    await db.disconnect()

asyncio.run(check())
```

### Via Neon Dashboard

1. Aller sur https://console.neon.tech
2. SQL Editor
3. Exécuter:
```sql
SELECT COUNT(*) as total FROM accounts;
SELECT username FROM accounts;
```

## Après la migration

### Supprimer les anciens fichiers JSON (optionnel)

```bash
# Backup d'abord!
copy config/accounts.json config/accounts.json.backup

# Supprimer l'ancien
del config/accounts.json
```

### Mettre à jour le code (déjà fait!)

Le bot utilise maintenant PostgreSQL par défaut. Les fichiers JSON ne sont plus utilisés.

## Rollback (revenir au JSON)

Si quelque chose ne marche pas, vous pouvez revenir:

```bash
# Restaurer depuis backup
copy config/accounts.json.backup config/accounts.json

# Éditer bot.py pour utiliser JSON au lieu de PostgreSQL
```

## Troubleshooting

### "Connection refused"
- Vérifier que DATABASE_URL est correct
- Vérifier internet connection
- Vérifier que le compte Neon est créé

### "UNIQUE violation error"
- Le compte existe déjà dans PostgreSQL
- Vérifier avec: `SELECT * FROM accounts WHERE username = 'mon_compte';`
- Supprimer si besoin: `DELETE FROM accounts WHERE username = 'mon_compte';`

### Les comptes ne s'ajoutent pas
- Vérifier les logs
- Vérifier la connection DB
- Essayer via SQL directement

## Statistiques après migration

```bash
python
```

```python
import asyncio
from database import TikTokDatabase
import os
from dotenv import load_dotenv

async def stats():
    load_dotenv()
    db = TikTokDatabase(os.getenv('DATABASE_URL'))
    await db.connect()
    
    s = await db.get_stats()
    print(f"Total comptes: {s['total_accounts']}")
    print(f"En live maintenant: {s['live_accounts']}")
    print(f"Total sessions enregistrées: {s['total_live_sessions']}")
    
    await db.disconnect()

asyncio.run(stats())
```

---

**Migration complète? Continuez avec [README.md](README.md)!** 🎉
