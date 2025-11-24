from flask import Flask, request, redirect, url_for, session, render_template
import asyncio
from app.database.models import init_db, seed_systems
from app.database import requests as dbreq
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "replace_with_real_secret_for_deploy"

# Ініціалізація БД перед першим запуском
asyncio.run(init_db())
asyncio.run(seed_systems())

# Простий "користувач" для демонстрації (не зберігаємо окремо акаунти)
USERS_STORE = {}  # demo only; in production — окрема таблиця

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in USERS_STORE:
            error = "Користувач вже існує"
        else:
            USERS_STORE[username] = generate_password_hash(password)
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
            return redirect(url_for("tasks"))
        else:
            error = "Невірний логін або пароль"
    return render_template("login.html", error=error)

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("home"))

# ---- Tasks CRUD ----
@app.route("/tasks")
def tasks():
    user = session.get("user")
    tasks_list = asyncio.run(dbreq.get_tasks())
    return render_template("tasks.html", tasks=tasks_list, user=user)

@app.route("/tasks/add", methods=["POST"])
def tasks_add():
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))
    
    title = request.form["title"]
    desc = request.form.get("description", "")
    asyncio.run(dbreq.create_task(title, desc))
    return redirect(url_for("tasks"))

@app.route("/tasks/delete/<int:task_id>")
def tasks_delete(task_id):
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))
    
    asyncio.run(dbreq.delete_task(task_id))
    return redirect(url_for("tasks"))

@app.route("/tasks/edit/<int:task_id>", methods=["GET", "POST"])
def tasks_edit(task_id):
    user = session.get("user")
    if not user:
        return redirect(url_for("login"))
    
    if request.method == "POST":
        title = request.form["title"]
        desc = request.form.get("description", "")
        asyncio.run(dbreq.update_task(task_id, title, desc))
        return redirect(url_for("tasks"))
    
    task = asyncio.run(dbreq.get_task_by_id(task_id))
    if not task:
        return "Task not found", 404
    
    return render_template("task_edit.html", task=task)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
