#!/bin/bash
# Script de démarrage du TikTok Live Monitor Bot (Linux/Mac)

echo ""
echo "====================================="
echo " TikTok Live Monitor Bot"
echo "====================================="
echo ""

# Vérifier si l'environnement virtuel existe
if [ ! -d "venv" ]; then
    echo "Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activer l'environnement virtuel
source venv/bin/activate

# Vérifier si .env existe
if [ ! -f ".env" ]; then
    echo ""
    echo "ATTENTION: Fichier .env non trouvé!"
    echo ""
    echo "Créer .env à partir de .env.example:"
    echo "cp .env.example .env"
    echo ""
    echo "Puis éditer .env et ajouter:"
    echo "  - TELEGRAM_BOT_TOKEN"
    echo "  - TELEGRAM_CHAT_ID"
    echo ""
    exit 1
fi

# Installer les dépendances si nécessaire
echo "Vérification des dépendances..."
pip install -r requirements.txt --quiet

# Démarrer le bot
echo ""
echo "Démarrage du bot..."
echo ""
python3 bot.py
