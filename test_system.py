#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт тестування системи SecureVision
Перевіряє всі компоненти перед запуском
"""

import sys
import os
from pathlib import Path

def print_header(text):
    print(f"\n{'='*50}")
    print(f"  {text}")
    print('='*50)

def test_python_version():
    """Перевірка версії Python"""
    print_header("Перевірка Python")
    version = sys.version_info
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ ПОМИЛКА: Потрібен Python 3.8+")
        return False
    return True

def test_imports():
    """Перевірка імпортів"""
    print_header("Перевірка модулів")
    
    modules = [
        ('aiogram', 'Aiogram 3.x'),
        ('flask', 'Flask'),
        ('sqlalchemy', 'SQLAlchemy'),
        ('aiosqlite', 'aiosqlite'),
        ('aiohttp', 'aiohttp'),
        ('werkzeug', 'Werkzeug'),
    ]
    
    all_ok = True
    for module, name in modules:
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - НЕ ВСТАНОВЛЕНО")
            all_ok = False
    
    return all_ok

def test_files():
    """Перевірка наявності файлів"""
    print_header("Перевірка файлів")
    
    required_files = [
        'bot.py',
        'webapp.py',
        'config.py',
        'requirements.txt',
        'app/handlers.py',
        'app/keyboards.py',
        'app/payment.py',
        'app/database/models.py',
        'app/database/requests.py',
        'templates/home.html',
        'templates/about.html',
        'templates/tasks.html',
    ]
    
    all_ok = True
    for file in required_files:
        path = Path(file)
        if path.exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - НЕ ЗНАЙДЕНО")
            all_ok = False
    
    return all_ok

def test_config():
    """Перевірка конфігурації"""
    print_header("Перевірка конфігурації")
    
    try:
        import config
        
        if hasattr(config, 'BOT_TOKEN'):
            token = config.BOT_TOKEN
            if token and len(token) > 10:
                print(f"✅ BOT_TOKEN: {token[:10]}...")
            else:
                print("⚠️  BOT_TOKEN виглядає підозріло коротким")
        else:
            print("❌ BOT_TOKEN не знайдено в config.py")
            return False
        
        if hasattr(config, 'DATABASE_URL'):
            print(f"✅ DATABASE_URL: {config.DATABASE_URL}")
        else:
            print("❌ DATABASE_URL не знайдено")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Помилка читання config.py: {e}")
        return False

def test_database():
    """Перевірка бази даних"""
    print_header("Перевірка бази даних")
    
    try:
        import asyncio
        from app.database.models import init_db, seed_systems
        
        async def check_db():
            await init_db()
            await seed_systems()
            return True
        
        result = asyncio.run(check_db())
        print("✅ База даних ініціалізована")
        print("✅ Початкові дані завантажені")
        return result
    except Exception as e:
        print(f"❌ Помилка бази даних: {e}")
        return False

def test_templates():
    """Перевірка шаблонів"""
    print_header("Перевірка HTML шаблонів")
    
    templates = ['home.html', 'about.html', 'tasks.html', 'login.html', 'register.html']
    all_ok = True
    
    for template in templates:
        path = Path('templates') / template
        if path.exists():
            size = path.stat().st_size
            print(f"✅ {template} ({size} bytes)")
        else:
            print(f"❌ {template} - НЕ ЗНАЙДЕНО")
            all_ok = False
    
    return all_ok

def test_logs_dir():
    """Перевірка папки логів"""
    print_header("Перевірка папки логів")
    
    logs_dir = Path('logs')
    if logs_dir.exists():
        print(f"✅ Папка logs/ існує")
        
        # Перевірка логів
        log_files = list(logs_dir.glob('*.log'))
        if log_files:
            print(f"📋 Знайдено логів: {len(log_files)}")
            for log_file in log_files:
                size = log_file.stat().st_size
                print(f"   - {log_file.name} ({size} bytes)")
        else:
            print("ℹ️  Лог файлів ще немає (з'являться після запуску)")
    else:
        print("ℹ️  Папка logs/ буде створена при запуску")
    
    return True

def main():
    """Головна функція"""
    print("\n" + "="*50)
    print("   SecureVision - Тестування системи")
    print("="*50)
    
    tests = [
        ("Python версія", test_python_version),
        ("Модулі Python", test_imports),
        ("Файли проекту", test_files),
        ("Конфігурація", test_config),
        ("База даних", test_database),
        ("HTML шаблони", test_templates),
        ("Папка логів", test_logs_dir),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Критична помилка в тесті '{name}': {e}")
            results.append((name, False))
    
    # Підсумок
    print_header("ПІДСУМОК")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ ПРОЙДЕНО" if result else "❌ ПОМИЛКА"
        print(f"{status}: {name}")
    
    print(f"\nРезультат: {passed}/{total} тестів пройдено")
    
    if passed == total:
        print("\n🎉 Всі перевірки пройдено успішно!")
        print("💡 Можна запускати систему:")
        print("   - Windows: start.bat")
        print("   - Linux/Mac: ./start.sh")
        print("   - Універсально: python run_local.py")
        return 0
    else:
        print("\n⚠️  Деякі перевірки не пройдено!")
        print("Виправте помилки перед запуском системи")
        return 1

if __name__ == '__main__':
    sys.exit(main())
