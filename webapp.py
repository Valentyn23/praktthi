from flask import Flask, request, redirect, url_for, session, render_template
import asyncio
import logging
from logging.handlers import RotatingFileHandler
import os
from app.database.models import init_db, seed_systems
from app.database import requests as dbreq
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "replace_with_real_secret_for_deploy"

# Налаштування логування
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Формат логів
log_format = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Логування в файл з ротацією
file_handler = RotatingFileHandler(
    os.path.join(log_dir, 'webapp.log'),
    maxBytes=5*1024*1024,  # 5MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(log_format)

# Логування в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(log_format)

# Налаштування логера
app.logger.addHandler(file_handler)
app.logger.addHandler(console_handler)
app.logger.setLevel(logging.INFO)

logger = logging.getLogger(__name__)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)

# Ініціалізація БД перед першим запуском
logger.info("========================================")
logger.info("Ініціалізація веб-додатку...")
try:
    asyncio.run(init_db())
    asyncio.run(seed_systems())
    logger.info("База даних успішно ініціалізована")
except Exception as e:
    logger.error(f"Помилка ініціалізації БД: {e}", exc_info=True)

# Простий "користувач" для демонстрації (не зберігаємо окремо акаунти)
USERS_STORE = {}  # demo only; in production — окрема таблиця

@app.route("/")
def home():
    logger.info(f"Відвідування головної сторінки. IP: {request.remote_addr}")
    return render_template("home.html")

@app.route("/about")
def about():
    logger.info(f"Відвідування сторінки 'Про нас'. IP: {request.remote_addr}")
    return render_template("about.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in USERS_STORE:
            error = "Користувач вже існує"
            logger.warning(f"Спроба реєстрації існуючого користувача: {username}")
        else:
            USERS_STORE[username] = generate_password_hash(password)
            logger.info(f"Новий користувач зареєстрований: {username}")
            return redirect(url_for("login"))
    return render_template("register.html", error=error)

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        if u in USERS_STORE and check_password_hash(USERS_STORE[u], p):
            session["user"] = u
            logger.info(f"Користувач увійшов: {u}")
            return redirect(url_for("tasks"))
        else:
            error = "Невірний логін або пароль"
            logger.warning(f"Невдала спроба входу: {u}")
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    user = session.get("user")
    if user:
        logger.info(f"Користувач вийшов: {user}")
    session.pop("user", None)
    return redirect(url_for("home"))

# ---- Tasks CRUD ----
@app.route("/tasks")
def tasks():
    user = session.get("user")
    logger.info(f"Перегляд списку завдань. Користувач: {user}")
    tasks_list = asyncio.run(dbreq.get_tasks())
    return render_template("tasks.html", tasks=tasks_list, user=user)

@app.route("/tasks/add", methods=["POST"])
def tasks_add():
    user = session.get("user")
    if not user:
        logger.warning("Спроба додати завдання без авторизації")
        return redirect(url_for("login"))
    
    title = request.form["title"]
    desc = request.form.get("description", "")
    asyncio.run(dbreq.create_task(title, desc))
    logger.info(f"Додано нове завдання: '{title}' користувачем {user}")
    return redirect(url_for("tasks"))

@app.route("/tasks/delete/<int:task_id>")
def tasks_delete(task_id):
    user = session.get("user")
    if not user:
        logger.warning(f"Спроба видалити завдання #{task_id} без авторизації")
        return redirect(url_for("login"))
    
    asyncio.run(dbreq.delete_task(task_id))
    logger.info(f"Видалено завдання #{task_id} користувачем {user}")
    return redirect(url_for("tasks"))

@app.route("/tasks/edit/<int:task_id>", methods=["GET", "POST"])
def tasks_edit(task_id):
    user = session.get("user")
    if not user:
        logger.warning(f"Спроба редагувати завдання #{task_id} без авторизації")
        return redirect(url_for("login"))
    
    if request.method == "POST":
        title = request.form["title"]
        desc = request.form.get("description", "")
        asyncio.run(dbreq.update_task(task_id, title, desc))
        logger.info(f"Оновлено завдання #{task_id} користувачем {user}")
        return redirect(url_for("tasks"))
    
    task = asyncio.run(dbreq.get_task_by_id(task_id))
    if not task:
        logger.error(f"Завдання #{task_id} не знайдено")
        return "Task not found", 404
    
    return render_template("task_edit.html", task=task)

if __name__ == "__main__":
    logger.info("Запуск Flask веб-сервера на порту 5000...")
    logger.info("========================================")
    app.run(debug=True, port=5001, host='0.0.0.0')