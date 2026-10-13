from functools import wraps
from datetime import date, datetime

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from flask_app.models.libro import Libro

libros_bp = Blueprint("libros", __name__, url_prefix="/libros")
GENEROS = (
	"Novela", "Romance", "Ciencia ficción", "Fantasía", "Misterio", "Aventura",
	"Historia", "Biografía", "Ensayo", "Poesía", "Otro",
)


def requiere_sesion(vista):
	@wraps(vista)
	def protegida(*args, **kwargs):
		if not session.get("usuario_id"):
			flash("Inicia sesión para continuar.", "warning")
			return redirect(url_for("usuarios.login"))
		return vista(*args, **kwargs)

	return protegida


def libro_propietario(libro_id):
	libro = Libro.buscar_por_id(libro_id)
	if not libro:
		abort(404)
	if libro["usuario_id"] != session["usuario_id"]:
		abort(403)
	return libro


def validar_libro(formulario):
	datos = {
		"titulo": formulario.get("titulo", "").strip(),
		"autor": formulario.get("autor", "").strip(),
		"genero": formulario.get("genero", "").strip(),
		"fecha_publicacion": formulario.get("fecha_publicacion", "").strip(),
		"descripcion": formulario.get("descripcion", "").strip(),
	}
	errores = []
	if len(datos["titulo"]) < 2 or len(datos["titulo"]) > 160:
		errores.append("El título debe tener entre 2 y 160 caracteres.")
	if len(datos["autor"]) < 2 or len(datos["autor"]) > 120:
		errores.append("El autor debe tener entre 2 y 120 caracteres.")
	if datos["genero"] not in GENEROS:
		errores.append("Selecciona un género de la lista.")
	try:
		fecha = datetime.strptime(datos["fecha_publicacion"], "%Y-%m-%d").date()
		if fecha > date.today():
			errores.append("La fecha de publicación no puede ser futura.")
	except ValueError:
		errores.append("Ingresa una fecha de publicación válida.")
	if len(datos["descripcion"]) < 10 or len(datos["descripcion"]) > 2000:
		errores.append("La descripción debe tener entre 10 y 2000 caracteres.")
	for error in errores:
		flash(error, "danger")
	return datos, not errores


@libros_bp.get("")
@libros_bp.get("/")
@requiere_sesion
def catalogo():
	return render_template(
		"libros/index.html",
		libros=Libro.listar_propios(session["usuario_id"]),
		comunidad=Libro.listar_comunidad(session["usuario_id"]),
	)


@libros_bp.get("/explorar")
@requiere_sesion
def explorar():
	busqueda = request.args.get("q", "").strip()[:100]
	return render_template(
		"libros/comunidad.html",
		libros=Libro.listar_comunidad(session["usuario_id"], busqueda),
		favoritos=Libro.ids_favoritos(session["usuario_id"]),
		busqueda=busqueda,
	)


@libros_bp.route("/nuevo", methods=["GET", "POST"])
@requiere_sesion
def nuevo():
	valores = {"titulo": "", "autor": "", "genero": "", "fecha_publicacion": "", "descripcion": ""}
	if request.method == "POST":
		valores, valido = validar_libro(request.form)
		if valido:
			libro_id = Libro.crear({**valores, "usuario_id": session["usuario_id"]})
			if libro_id:
				flash("El libro se añadió a la biblioteca.", "success")
				return redirect(url_for("libros.detalles", libro_id=libro_id))
			flash("No se pudo guardar el libro. Inténtalo de nuevo.", "danger")
	return render_template(
		"libros/nuevo.html",
		valores=valores,
		generos=GENEROS,
		fecha_maxima=date.today().isoformat(),
	)


@libros_bp.get("/<int:libro_id>")
@requiere_sesion
def detalles(libro_id):
	libro = Libro.buscar_por_id(libro_id)
	if not libro:
		abort(404)
	return render_template(
		"libros/detalles.html",
		libro=libro,
		es_favorito=Libro.es_favorito(libro_id, session["usuario_id"]),
		usuarios_favoritos=Libro.usuarios_que_favoritaron(libro_id),
	)


@libros_bp.route("/<int:libro_id>/editar", methods=["GET", "POST"])
@requiere_sesion
def editar(libro_id):
	libro = libro_propietario(libro_id)
	if request.method == "POST":
		datos, valido = validar_libro(request.form)
		if valido:
			if Libro.actualizar(libro_id, {**datos, "usuario_id": session["usuario_id"]}) is not False:
				flash("Los cambios se guardaron.", "success")
				return redirect(url_for("libros.detalles", libro_id=libro_id))
			flash("No se pudieron guardar los cambios.", "danger")
		libro.update(datos)
	return render_template("libros/editar.html", libro=libro, generos=GENEROS)


@libros_bp.post("/<int:libro_id>/eliminar")
@requiere_sesion
def eliminar(libro_id):
	libro_propietario(libro_id)
	if Libro.eliminar(libro_id, session["usuario_id"]) is not False:
		flash("El libro se eliminó de la biblioteca.", "success")
	else:
		flash("No se pudo eliminar el libro.", "danger")
	return redirect(url_for("libros.catalogo"))


@libros_bp.get("/favoritos")
@requiere_sesion
def favoritos():
	return render_template("libros/favoritos.html", libros=Libro.listar_favoritos(session["usuario_id"]))


@libros_bp.post("/<int:libro_id>/favorito")
@requiere_sesion
def alternar_favorito(libro_id):
	if not Libro.buscar_por_id(libro_id):
		abort(404)
	if Libro.alternar_favorito(libro_id, session["usuario_id"]) is False:
		flash("No se pudo actualizar tu lista de favoritos.", "danger")
	else:
		flash("Tu lista de favoritos se actualizó.", "success")
	return redirect(url_for("libros.catalogo"))
