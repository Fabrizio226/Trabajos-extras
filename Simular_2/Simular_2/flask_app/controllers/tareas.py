from datetime import date, datetime
from functools import wraps

from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for
from pymysql.err import IntegrityError

from flask_app.models.categoria import Categoria
from flask_app.models.tarea import Tarea

tareas_bp = Blueprint("tareas", __name__)
PRIORIDADES = ("Alta", "Media", "Baja")
ESTADOS = ("Pendiente", "En progreso", "Completada")


def requiere_sesion(vista):
    @wraps(vista)
    def protegida(*args, **kwargs):
        if not session.get("usuario_id"):
            flash("Inicia sesión para continuar.", "warning")
            return redirect(url_for("usuarios.acceso"))
        return vista(*args, **kwargs)

    return protegida


def tarea_propietaria(tarea_id):
    tarea = Tarea.buscar_por_id(tarea_id, session["usuario_id"])
    if not tarea:
        abort(404)
    return tarea


def validar_tarea(formulario, usuario_id):
    datos = {
        "titulo": formulario.get("titulo", "").strip(),
        "categoria_id": formulario.get("categoria_id", "").strip(),
        "prioridad": formulario.get("prioridad", "").strip(),
        "fecha_limite": formulario.get("fecha_limite", "").strip(),
        "descripcion": formulario.get("descripcion", "").strip(),
    }
    errores = []
    if not 3 <= len(datos["titulo"]) <= 160:
        errores.append("El título debe tener entre 3 y 160 caracteres.")
    try:
        datos["categoria_id"] = int(datos["categoria_id"])
        if not Categoria.buscar_por_id(datos["categoria_id"], usuario_id):
            errores.append("Selecciona una categoría válida.")
    except (TypeError, ValueError):
        errores.append("Selecciona una categoría válida.")
        datos["categoria_id"] = None
    if datos["prioridad"] not in PRIORIDADES:
        errores.append("Selecciona una prioridad válida.")
    try:
        fecha = datetime.strptime(datos["fecha_limite"], "%Y-%m-%d").date()
        if fecha < date.today():
            errores.append("La fecha límite no puede ser pasada.")
    except ValueError:
        errores.append("Ingresa una fecha límite válida.")
    if not 10 <= len(datos["descripcion"]) <= 2000:
        errores.append("La descripción debe tener entre 10 y 2000 caracteres.")
    for error in errores:
        flash(error, "danger")
    return datos, not errores


@tareas_bp.get("/tareas")
@requiere_sesion
def listar():
    usuario_id = session["usuario_id"]
    filtros = {
        "q": request.args.get("q", "").strip()[:100],
        "categoria_id": request.args.get("categoria_id", "").strip(),
        "estado": request.args.get("estado", "").strip(),
        "prioridad": request.args.get("prioridad", "").strip(),
    }
    if filtros["estado"] not in ESTADOS:
        filtros["estado"] = ""
    if filtros["prioridad"] not in PRIORIDADES:
        filtros["prioridad"] = ""
    categorias = Categoria.listar(usuario_id)
    categoria_ids = {str(categoria["id"]) for categoria in categorias}
    if filtros["categoria_id"] not in categoria_ids:
        filtros["categoria_id"] = ""
    return render_template(
        "tareas/index.html",
        tareas=Tarea.listar(usuario_id, filtros),
        categorias=categorias,
        filtros=filtros,
        resumen=Tarea.resumen(usuario_id),
        proximas=Tarea.proximas(usuario_id),
        estados=ESTADOS,
        prioridades=PRIORIDADES,
        hoy=date.today(),
    )


@tareas_bp.get("/libros")
@tareas_bp.get("/libros/")
def ruta_anterior_biblioteca():
    return redirect(url_for("tareas.listar"))


@tareas_bp.route("/tareas/nueva", methods=["GET", "POST"])
@requiere_sesion
def nueva():
    usuario_id = session["usuario_id"]
    valores = {
        "titulo": "",
        "categoria_id": "",
        "prioridad": "",
        "fecha_limite": "",
        "descripcion": "",
    }
    categorias = Categoria.listar(usuario_id)
    if request.method == "POST":
        valores, valido = validar_tarea(request.form, usuario_id)
        if valido:
            tarea_id = Tarea.crear({**valores, "usuario_id": usuario_id})
            flash("La tarea se creó correctamente.", "success")
            return redirect(url_for("tareas.detalle", tarea_id=tarea_id))
    return render_template(
        "tareas/formulario.html",
        titulo_pagina="Nueva Tarea",
        valores=valores,
        categorias=categorias,
        prioridades=PRIORIDADES,
        fecha_minima=date.today().isoformat(),
    )


@tareas_bp.get("/tareas/<int:tarea_id>")
@requiere_sesion
def detalle(tarea_id):
    tarea = tarea_propietaria(tarea_id)
    return render_template("tareas/detalle.html", tarea=tarea)


@tareas_bp.route("/tareas/<int:tarea_id>/editar", methods=["GET", "POST"])
@requiere_sesion
def editar(tarea_id):
    tarea = tarea_propietaria(tarea_id)
    categorias = Categoria.listar(session["usuario_id"])
    if request.method == "POST":
        datos, valido = validar_tarea(request.form, session["usuario_id"])
        if valido:
            Tarea.actualizar(
                tarea_id,
                {**datos, "usuario_id": session["usuario_id"]},
            )
            flash("Los cambios se guardaron.", "success")
            return redirect(url_for("tareas.detalle", tarea_id=tarea_id))
        tarea.update(datos)
    return render_template(
        "tareas/formulario.html",
        titulo_pagina="Editar Tarea",
        valores=tarea,
        categorias=categorias,
        prioridades=PRIORIDADES,
        fecha_minima=date.today().isoformat(),
    )


@tareas_bp.post("/tareas/<int:tarea_id>/completar")
@requiere_sesion
def completar(tarea_id):
    tarea = tarea_propietaria(tarea_id)
    if tarea["estado"] == "Completada":
        flash("Esta tarea ya está completada.", "info")
    else:
        Tarea.cambiar_estado(tarea_id, "Completada", session["usuario_id"])
        flash("La tarea se marcó como completada.", "success")
    return redirect(url_for("tareas.detalle", tarea_id=tarea_id))


@tareas_bp.route("/tareas/<int:tarea_id>/eliminar", methods=["GET", "POST"])
@requiere_sesion
def eliminar(tarea_id):
    tarea = tarea_propietaria(tarea_id)
    if request.method == "GET":
        return render_template(
            "confirmar_eliminacion.html",
            tipo="tarea",
            nombre=tarea["titulo"],
            accion=request.path,
            volver=url_for("tareas.detalle", tarea_id=tarea_id),
        )
    Tarea.eliminar(tarea_id, session["usuario_id"])
    flash("La tarea se eliminó.", "success")
    return redirect(url_for("tareas.listar"))


@tareas_bp.get("/categorias")
@requiere_sesion
def categorias():
    return render_template(
        "categorias/index.html",
        categorias=Categoria.listar(session["usuario_id"]),
    )


@tareas_bp.route("/categorias/nueva", methods=["GET", "POST"])
@requiere_sesion
def nueva_categoria():
    return formulario_categoria()


@tareas_bp.route("/categorias/<int:categoria_id>/editar", methods=["GET", "POST"])
@requiere_sesion
def editar_categoria(categoria_id):
    categoria = Categoria.buscar_por_id(categoria_id, session["usuario_id"])
    if not categoria:
        abort(404)
    return formulario_categoria(categoria)


def formulario_categoria(categoria=None):
    nombre = categoria["nombre"] if categoria else ""
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        if not 3 <= len(nombre) <= 60:
            flash("El nombre debe tener entre 3 y 60 caracteres.", "danger")
        elif Categoria.existe_nombre(
            nombre,
            session["usuario_id"],
            categoria["id"] if categoria else None,
        ):
            flash("Ya tienes una categoría con ese nombre.", "danger")
        else:
            if categoria:
                Categoria.actualizar(categoria["id"], nombre, session["usuario_id"])
                flash("La categoría se actualizó.", "success")
            else:
                Categoria.crear(nombre, session["usuario_id"])
                flash("La categoría se creó.", "success")
            return redirect(url_for("tareas.categorias"))
    return render_template(
        "categorias/formulario.html",
        categoria=categoria,
        nombre=nombre,
    )


@tareas_bp.route("/categorias/<int:categoria_id>/eliminar", methods=["GET", "POST"])
@requiere_sesion
def eliminar_categoria(categoria_id):
    categoria = Categoria.buscar_por_id(categoria_id, session["usuario_id"])
    if not categoria:
        abort(404)
    if request.method == "GET":
        return render_template(
            "confirmar_eliminacion.html",
            tipo="categoría",
            nombre=categoria["nombre"],
            accion=request.path,
            volver=url_for("tareas.categorias"),
        )
    try:
        eliminadas = Categoria.eliminar(categoria_id, session["usuario_id"])
    except IntegrityError:
        flash("No se puede borrar una categoría que todavía tiene tareas.", "danger")
    else:
        if eliminadas:
            flash("La categoría se eliminó.", "success")
        else:
            flash("No se pudo eliminar la categoría.", "danger")
    return redirect(url_for("tareas.categorias"))
