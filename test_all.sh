#!/bin/bash

echo "🔍 Перевірка проекту..."
echo ""

# Перевірка Python версії
echo "1️⃣ Python версія:"
python3 --version
echo ""

# Перевірка залежностей
echo "2️⃣ Встановлені пакети:"
pip list | grep -E "aiogram|flask|sqlalchemy|aiosqlite" || echo "❌ Деякі пакети не встановлені!"
echo ""

# Перевірка бази даних
echo "3️⃣ Перевірка бази даних:"
if [ -f "/app/db.sqlite3" ]; then
    echo "✅ База даних існує: /app/db.sqlite3"
    ls -lh /app/db.sqlite3
else
    echo "⚠️  База даних не знайдена. Створюємо..."
    cd /app && python3 -c "import asyncio; from app.database.models import init_db, seed_systems; asyncio.run(init_db()); asyncio.run(seed_systems()); print('✅ База даних створена!')"
fi
echo ""

# Перевірка структури
echo "4️⃣ Перевірка структури проекту:"
for file in bot.py webapp.py config.py requirements.txt; do
    if [ -f "/app/$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file - НЕ ЗНАЙДЕНО!"
    fi
done

for dir in app templates static; do
    if [ -d "/app/$dir" ]; then
        echo "✅ $dir/"
    else
        echo "❌ $dir/ - НЕ ЗНАЙДЕНО!"
    fi
done
echo ""

# Перевірка Supervisor
echo "5️⃣ Статус сервісів (Supervisor):"
sudo supervisorctl status | grep -E "telegram_bot|webapp"
echo ""

# Перевірка веб-додатку
echo "6️⃣ Тест веб-додатку:"
if curl -s http://127.0.0.1:5000/ | grep -q "VideoSecurity"; then
    echo "✅ Веб-додаток працює на http://127.0.0.1:5000"
else
    echo "❌ Веб-додаток не відповідає"
fi
echo ""

# Перевірка даних в БД
echo "7️⃣ Перевірка даних в базі:"
cd /app && python3 << 'EOF'
import asyncio
from app.database.requests import get_all_systems

async def check():
    systems = await get_all_systems()
    if len(systems) > 0:
        print(f"✅ У базі {len(systems)} систем відеоспостереження")
        for sys in systems:
            print(f"   - {sys.name}: {sys.price}$")
    else:
        print("⚠️  База порожня!")

asyncio.run(check())
EOF
echo ""

# Підсумок
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 ПІДСУМОК:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🤖 Telegram бот:"
echo "   Статус: $(sudo supervisorctl status telegram_bot | awk '{print $2}')"
echo "   Логи: /var/log/supervisor/telegram_bot.*.log"
echo ""
echo "🌐 Веб-додаток:"
echo "   Статус: $(sudo supervisorctl status webapp | awk '{print $2}')"
echo "   URL: http://127.0.0.1:5000"
echo "   Логи: /var/log/supervisor/webapp.*.log"
echo ""
echo "💾 База даних:"
echo "   Файл: /app/db.sqlite3"
echo "   Розмір: $(du -h /app/db.sqlite3 2>/dev/null | cut -f1 || echo 'N/A')"
echo ""
echo "📚 Документація:"
echo "   README.md - Англійською"
echo "   ІНСТРУКЦІЯ.md - Українською"
echo ""
echo "✅ Перевірка завершена!"
