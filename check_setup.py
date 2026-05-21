#!/usr/bin/env python3
"""
Configuration checker - Verify that all setup is correct before running the bot
"""

import os
import sys
import json
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8+"""
    print("🔍 Vérification de la version Python...")
    if sys.version_info >= (3, 8):
        print(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor}")
        return True
    else:
        print(f"   ❌ Python {sys.version_info.major}.{sys.version_info.minor} (3.8+ requis)")
        return False

def check_env_file():
    """Check if .env file exists"""
    print("\n🔍 Vérification du fichier .env...")
    if os.path.exists('.env'):
        print("   ✅ .env trouvé")
        return True
    else:
        print("   ❌ .env manquant")
        print("      Créer: copy .env.example .env")
        return False

def check_env_variables():
    """Check if required env variables are set"""
    print("\n🔍 Vérification des variables d'environnement...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    all_good = True
    
    if token and token != 'your_telegram_bot_token_here':
        print("   ✅ TELEGRAM_BOT_TOKEN configuré")
    else:
        print("   ❌ TELEGRAM_BOT_TOKEN manquant ou invalide")
        all_good = False
    
    if chat_id:
        try:
            int(chat_id)
            print("   ✅ TELEGRAM_CHAT_ID configuré")
        except ValueError:
            print("   ❌ TELEGRAM_CHAT_ID invalide (doit être un nombre)")
            all_good = False
    else:
        print("   ❌ TELEGRAM_CHAT_ID manquant")
        all_good = False
    
    return all_good

def check_dependencies():
    """Check if all dependencies are installed"""
    print("\n🔍 Vérification des dépendances...")
    
    required_packages = [
        'telegram',
        'dotenv',
        'requests',
        'beautifulsoup4',
        'yt_dlp',
    ]
    
    all_good = True
    for package in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} manquant")
            all_good = False
    
    if not all_good:
        print("\n   Installer: pip install -r requirements.txt")
    
    return all_good

def check_directories():
    """Check if required directories exist"""
    print("\n🔍 Vérification des répertoires...")
    
    dirs = ['config', 'logs']
    for dir_name in dirs:
        if os.path.exists(dir_name):
            print(f"   ✅ {dir_name}/")
        else:
            os.makedirs(dir_name, exist_ok=True)
            print(f"   ✅ {dir_name}/ (créé)")
    
    return True

def check_files():
    """Check if required files exist"""
    print("\n🔍 Vérification des fichiers...")
    
    files = [
        'bot.py',
        'tiktok_monitor.py',
        'requirements.txt',
        'config/accounts.json',
    ]
    
    all_good = True
    for file_name in files:
        if os.path.exists(file_name):
            print(f"   ✅ {file_name}")
        else:
            if file_name == 'config/accounts.json':
                # Créer le fichier par défaut
                os.makedirs('config', exist_ok=True)
                with open(file_name, 'w') as f:
                    json.dump({
                        "accounts": [],
                        "settings": {
                            "check_interval": 300,
                            "max_retries": 3,
                            "timeout": 30
                        }
                    }, f, indent=2)
                print(f"   ✅ {file_name} (créé)")
            else:
                print(f"   ❌ {file_name} manquant")
                all_good = False
    
    return all_good

def main():
    """Run all checks"""
    print("""
╔════════════════════════════════════════╗
║   TikTok Live Bot - Configuration      ║
║            Checker                     ║
╚════════════════════════════════════════╝
    """)
    
    checks = [
        ("Python", check_python_version),
        (".env File", check_env_file),
        ("Variables", check_env_variables),
        ("Dépendances", check_dependencies),
        ("Répertoires", check_directories),
        ("Fichiers", check_files),
    ]
    
    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"   ❌ Erreur: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("RÉSUMÉ:")
    print("=" * 50)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for check_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
    
    print(f"\nRésultat: {passed}/{total} vérifications réussies")
    
    if passed == total:
        print("\n🎉 Tout est prêt! Vous pouvez lancer le bot:")
        print("   python bot.py")
        return 0
    else:
        print("\n⚠️  Certaines vérifications ont échoué.")
        print("Lire README.md ou FAQ.md pour plus d'infos.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
