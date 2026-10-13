import re

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from flask_app import app, bcrypt
from flask_app.models.usuario import Usuario

usuarios_bp = Blueprint("usuarios", __name__)


@usuarios_bp.route("/")
def inicio():
	if session.get("usuario_id"):
		return redirect(url_for("libros.catalogo"))
	return redirect(url_for("usuarios.login"))


@usuarios_bp.route("/login", methods=["GET", "POST"])
def login():
	if session.get("usuario_id"):
		return redirect(url_for("libros.catalogo"))
	if request.method == "POST":
		correo = request.form.get("correo", "").strip().lower()
		password = request.form.get("password", "")
		usuario = Usuario.buscar_por_correo(correo) if correo else None
		if usuario and bcrypt.check_password_hash(usuario["password"], password):
			session.clear()
			session["usuario_id"] = usuario["id"]
			session["usuario_nombre"] = usuario["nombre"]
			flash("Qué bueno verte de nuevo.", "success")
			return redirect(url_for("libros.catalogo"))
		flash("Correo o contraseña incorrectos.", "danger")
	return render_template("autenticar/index.html")


@usuarios_bp.route("/registro", methods=["GET", "POST"])
def registro():
	if session.get("usuario_id"):
		return redirect(url_for("libros.catalogo"))
	valores = {campo: request.form.get(campo, "").strip() for campo in ("nombre", "apellido", "correo")}
	if request.method == "POST":
		password = request.form.get("password", "")
		confirmacion = request.form.get("confirmacion", "")
		errores = []
		if len(valores["nombre"]) < 2 or len(valores["nombre"]) > 80:
			errores.append("El nombre debe tener entre 2 y 80 caracteres.")
		if len(valores["apellido"]) < 2 or len(valores["apellido"]) > 80:
			errores.append("El apellido debe tener entre 2 y 80 caracteres.")
		if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", valores["correo"]):
			errores.append("Ingresa un correo electrónico válido.")
		if len(password) < 8:
			errores.append("La contraseña debe tener al menos 8 caracteres.")
		if password != confirmacion:
			errores.append("Las contraseñas no coinciden.")
		if re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", valores["correo"]) and Usuario.buscar_por_correo(valores["correo"].lower()):
			errores.append("Ya existe una cuenta con ese correo.")
		if errores:
			for error in errores:
				flash(error, "danger")
		else:
			usuario_id = Usuario.crear({
				**valores,
				"correo": valores["correo"].lower(),
				"password": bcrypt.generate_password_hash(password).decode("utf-8"),
			})
			if usuario_id:
				session["usuario_id"] = usuario_id
				session["usuario_nombre"] = valores["nombre"]
				flash("Tu cuenta está lista. Añade el primer libro a tu biblioteca.", "success")
				return redirect(url_for("libros.catalogo"))
			flash("No se pudo crear la cuenta. Revisa si el correo ya está registrado.", "danger")
	return render_template("autenticar/index.html", valores=valores)


@usuarios_bp.post("/logout")
def logout():
	session.clear()
	flash("Has cerrado sesión.", "info")
	return redirect(url_for("usuarios.login"))
