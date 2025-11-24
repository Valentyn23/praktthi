from flask import Flask, request, redirect, url_for, session, render_template_string
import asyncio
from app.database.models import init_db
from app.database import requests as dbreq
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "replace_with_real_secret_for_deploy"

# Простий "користувач" для демонстрації (не зберігаємо окремо акаунти — використовуємо tg_id як username)
# Ініціалізація БД перед першим запуском
asyncio.run(init_db())

HOME_HTML = """
<h1>Вітаю в WebApp — Підбір систем відеоспостереження</h1>
<p><a href="/about">Про додаток</a> | <a href="/tasks">Завдання (To-Do)</a> | <a href="/login">Login</a> | <a href="/register">Register</a></p>
"""

ABOUT_HTML = """
<h1>Про додаток</h1>
<p>Це демонстраційний веб-інтерфейс для практичної роботи. Дані зберігаються у SQLite.</p>
<p><a href="/">На головну</a></p>
"""

# ---- Auth: дуже простий (email/password stored in session only for demo) ----
USERS_STORE = {}  # demo only; in production — окрема таблиця

@app.route("/")
def home():
    return render_template_string(HOME_HTML)

@app.route("/about")
def about():
    return render_template_string(ABOUT_HTML)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in USERS_STORE:
            return "Користувач вже існує"
        USERS_STORE[username] = generate_password_hash(password)
        return redirect(url_for("login"))
    return '''
      <form method="post">
        Username (use any string): <input name="username"><br>
        Password: <input name="password" type="password"><br>
        <button type="submit">Register</button>
      </form>
    '''

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        u = request.form["username"]
        p = request.form["password"]
        if u in USERS_STORE and check_password_hash(USERS_STORE[u], p):
            session["user"] = u
            return redirect(url_for("tasks"))
        else:
            return "Невірний логін/пароль"
    return '''
      <form method="post">
        Username: <input name="username"><br>
        Password: <input name="password" type="password"><br>
        <button type="submit">Login</button>
      </form>
    '''

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

# ---- Tasks CRUD ----
@app.route("/tasks")
def tasks():
    user = session.get("user")
    tasks = asyncio.run(dbreq.get_tasks())
    tasks_html = "<ul>"
    for t in tasks:
        tasks_html += f"<li>{t.title} - {t.description} " \
                      f"[<a href='/tasks/edit/{t.id}'>edit</a>] [<a href='/tasks/delete/{t.id}'>delete</a>]</li>"
    tasks_html += "</ul>"
    add_form = '''
      <h3>Додати завдання</h3>
      <form method="post" action="/tasks/add">
        Title: <input name="title"><br>
        Description: <input name="description"><br>
        <button type="submit">Add</button>
      </form>
    '''
    return render_template_string(f"<h1>Tasks</h1>{tasks_html}{add_form}<p><a href='/'>На головну</a></p>")

@app.route("/tasks/add", methods=["POST"])
def tasks_add():
    title = request.form["title"]
    desc = request.form["description"]
    asyncio.run(dbreq.create_task(title, desc))
    return redirect(url_for("tasks"))

@app.route("/tasks/delete/<int:task_id>")
def tasks_delete(task_id):
    asyncio.run(dbreq.delete_task(task_id))
    return redirect(url_for("tasks"))

@app.route("/tasks/edit/<int:task_id>", methods=["GET", "POST"])
def tasks_edit(task_id):
    if request.method == "POST":
        title = request.form["title"]
        desc = request.form["description"]
        asyncio.run(dbreq.update_task(task_id, title, desc))
        return redirect(url_for("tasks"))
    task = asyncio.run(dbreq.get_task_by_id(task_id))
    if not task:
        return "Task not found"
    return render_template_string(f'''
      <h1>Edit Task</h1>
      <form method="post">
        Title: <input name="title" value="{task.title}"><br>
        Description: <input name="description" value="{task.description or ''}"><br>
        <button type="submit">Save</button>
      </form>
    ''')

if __name__ == "__main__":
    app.run(debug=True, port=5000)
