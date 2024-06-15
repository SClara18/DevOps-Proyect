from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_socketio import SocketIO, emit
import subprocess

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
login_manager = LoginManager(app)
login_manager.login_view = 'login'
socketio = SocketIO(app)

class User(UserMixin):
    def __init__(self, id, email, password, user):
        self.id = id
        self.email = email
        self.password = password
        self.user = user

users = [
    User(1, "saul.clara@example.com", "admin1234", "Saul Clara"),
    User(2, "natalia.castro@example.com", "admin1234", "Natalia Castro"),
    User(3, "admin@example.com", "admin1234", "Admin"),
    User(4, "externo@example.com", "admin1234", "Externo"),
]

@login_manager.user_loader
def load_user(user_id):
    for user in users:
        if user.id == int(user_id):
            return user
    return None

@app.route('/assets/<path:filename>')
def custom_static(filename):
    return send_from_directory('templates/assets', filename)

@app.route("/")
def redirect_to_home_or_login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    else:
        return redirect(url_for("login"))

@app.route("/home")
@login_required
def home():
    return render_template("index.html", users=users)

@app.route("/marketplace")
@login_required
def market():
    return render_template("tab-panel.html")

@app.route("/robots")
@login_required
def robots():
    return render_template("robots.html")

@app.route("/status")
@login_required
def robots_status():
    return render_template("Robot-action.html")

@app.route("/all")
@login_required
def all_robots():
    return render_template("All-Robots.html")

@app.route("/create")
@login_required
def create():
    return render_template("create.html")

@app.route("/dashboards")
@login_required
def dash():
    return render_template("/dashboards.html")

@app.route("/terminal")
@login_required
def terminal():
    return render_template("terminal.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", error=None)
    else:
        email = request.form.get("email")
        password = request.form.get("password")

        user = find_user(email)
        if user is None or user.password != password:
            error = "Invalid email or password. Please try again."
            return render_template("login.html", error=error)

        login_user(user)
        return redirect(url_for("home"))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("redirect_to_home_or_login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("table.html", error=None)
    else:
        email = request.form.get("email")
        password = request.form.get("password")
        username = request.form.get("username")

        # Verificar si el usuario ya existe
        if find_user(email):
            error = "User with this email already exists. Please choose a different email."
            return render_template("register.html", error=error, users=users)

        # Crear un nuevo usuario
        new_user = User(len(users) + 1, email, password, username)
        users.append(new_user)

        # Autenticar al nuevo usuario
        login_user(new_user)
        return redirect(url_for("home"))

def find_user(email):
    for user in users:
        if user.email == email:
            return user
    return None

@socketio.on('terminal_input')
def handle_terminal_input(json):
    command = json['data']

    try:
        # Ejecuta el comando y captura la salida
        result = subprocess.check_output(command, shell=True, text=True)
    except subprocess.CalledProcessError as e:
        # Captura errores si el comando no se ejecuta correctamente
        result = f"Error al ejecutar el comando: {e}"

    # Emite la salida al cliente
    emit('terminal_output', {'data': result})

if __name__ == "__main__":
    socketio.run(app, debug=True)
