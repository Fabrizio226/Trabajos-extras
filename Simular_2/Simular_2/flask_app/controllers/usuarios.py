import re

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from flask_app import bcrypt
from flask_app.models.usuario import Usuario

usuarios_bp = Blueprint("usuarios", __name__)
CORREO_VALIDO = re.compile(r"[^\s@]+@[^\s@]+\.[^\s@]+")


@usuarios_bp.route("/")
def inicio():
    if session.get("usuario_id"):
        return redirect(url_for("tareas.listar"))
    return redirect(url_for("usuarios.acceso"))


@usuarios_bp.route("/acceso", methods=["GET", "POST"])
@usuarios_bp.route("/login", methods=["GET", "POST"])
@usuarios_bp.route("/registro", methods=["GET", "POST"])
def acceso():
    if session.get("usuario_id"):
        return redirect(url_for("tareas.listar"))
    valores = {
        campo: request.form.get(campo, "").strip()
        for campo in ("nombre", "apellido", "correo")
    }
    if request.method == "POST":
        accion = request.form.get("accion")
        if accion == "registro":
            return registrar(valores)
        if accion == "login":
            return iniciar_sesion()
        flash("Selecciona una acción válida.", "danger")
    return render_template("autenticar/index.html", valores=valores)


def registrar(valores):
    password = request.form.get("password", "")
    confirmacion = request.form.get("confirmacion", "")
    errores = []
    if not 2 <= len(valores["nombre"]) <= 80:
        errores.append("El nombre debe tener entre 2 y 80 caracteres.")
    if not 2 <= len(valores["apellido"]) <= 80:
        errores.append("El apellido debe tener entre 2 y 80 caracteres.")
    if not CORREO_VALIDO.fullmatch(valores["correo"]):
        errores.append("Ingresa un correo electrónico válido.")
    if len(password) < 8:
        errores.append("La contraseña debe tener al menos 8 caracteres.")
    if password != confirmacion:
        errores.append("Las contraseñas no coinciden.")
    correo = valores["correo"].lower()
    if CORREO_VALIDO.fullmatch(correo) and Usuario.buscar_por_correo(correo):
        errores.append("Ya existe una cuenta con ese correo.")
    if errores:
        for error in errores:
            flash(error, "danger")
        return render_template("autenticar/index.html", valores=valores)

    usuario_id = Usuario.crear({
        **valores,
        "correo": correo,
        "password": bcrypt.generate_password_hash(password).decode("utf-8"),
    })
    session.clear()
    session["usuario_id"] = usuario_id
    session["usuario_nombre"] = valores["nombre"]
    flash("Tu cuenta está lista. Crea tu primera tarea.", "success")
    return redirect(url_for("tareas.listar"))


def iniciar_sesion():
    correo = request.form.get("correo", "").strip().lower()
    password = request.form.get("password", "")
    usuario = Usuario.buscar_por_correo(correo) if correo else None
    if usuario and bcrypt.check_password_hash(usuario["password"], password):
        session.clear()
        session["usuario_id"] = usuario["id"]
        session["usuario_nombre"] = usuario["nombre"]
        flash("Has iniciado sesión.", "success")
        return redirect(url_for("tareas.listar"))
    flash("Correo o contraseña incorrectos.", "danger")
    return render_template("autenticar/index.html")


@usuarios_bp.post("/logout")
def logout():
    session.clear()
    flash("Has cerrado sesión.", "info")
    return redirect(url_for("usuarios.acceso"))
