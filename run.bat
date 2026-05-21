@echo off
REM Script de démarrage du TikTok Live Monitor Bot

echo.
echo =====================================
echo  TikTok Live Monitor Bot
echo =====================================
echo.

REM Vérifier si l'environnement virtuel existe
if not exist "venv\" (
    echo Création de l'environnement virtuel...
    python -m venv venv
)

REM Activer l'environnement virtuel
call venv\Scripts\activate.bat

REM Vérifier si .env existe
if not exist ".env" (
    echo.
    echo ATTENTION: Fichier .env non trouvé!
    echo.
    echo Créer .env à partir de .env.example:
    echo copy .env.example .env
    echo.
    echo Puis éditer .env et ajouter:
    echo   - TELEGRAM_BOT_TOKEN
    echo   - TELEGRAM_CHAT_ID
    echo.
    pause
    exit /b 1
)

REM Installer les dépendances si nécessaire
echo Vérification des dépendances...
pip install -r requirements.txt --quiet

REM Démarrer le bot
echo.
echo Démarrage du bot...
echo.
python bot.py

pause
