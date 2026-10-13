import os

from dotenv import load_dotenv
from flask import Flask
from flask_bcrypt import Bcrypt

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "clave-por-defecto-secreta")
app.config["DATABASE"] = os.getenv("DB_NAME", "biblioteca")
bcrypt = Bcrypt(app)

from flask_app.controllers.libros import libros_bp
from flask_app.controllers.usuarios import usuarios_bp

app.register_blueprint(usuarios_bp)
app.register_blueprint(libros_bp)