from flask import current_app

from flask_app.config.mysqlconnection import connectToMySQL


class Tarea:
    @staticmethod
    def _db():
        return connectToMySQL(current_app.config["DATABASE"])

    @classmethod
    def listar(cls, usuario_id, filtros=None):
        filtros = filtros or {}
        condiciones = ["tareas.usuario_id = %(usuario_id)s"]
        datos = {"usuario_id": usuario_id}
        if filtros.get("q"):
            condiciones.append("tareas.titulo LIKE %(busqueda)s")
            datos["busqueda"] = f"%{filtros['q']}%"
        if filtros.get("categoria_id"):
            condiciones.append("tareas.categoria_id = %(categoria_id)s")
            datos["categoria_id"] = filtros["categoria_id"]
        if filtros.get("estado"):
            condiciones.append("tareas.estado = %(estado)s")
            datos["estado"] = filtros["estado"]
        if filtros.get("prioridad"):
            condiciones.append("tareas.prioridad = %(prioridad)s")
            datos["prioridad"] = filtros["prioridad"]
        where = " AND ".join(condiciones)
        return cls._db().query_db(
            "SELECT tareas.*, categorias.nombre AS categoria_nombre "
            "FROM tareas JOIN categorias ON categorias.id = tareas.categoria_id "
            f"WHERE {where} ORDER BY tareas.fecha_limite IS NULL, tareas.fecha_limite, tareas.id DESC",
            datos,
        )

    @classmethod
    def buscar_por_id(cls, tarea_id, usuario_id):
        resultados = cls._db().query_db(
            "SELECT tareas.*, categorias.nombre AS categoria_nombre "
            "FROM tareas JOIN categorias ON categorias.id = tareas.categoria_id "
            "WHERE tareas.id = %(id)s AND tareas.usuario_id = %(usuario_id)s LIMIT 1",
            {"id": tarea_id, "usuario_id": usuario_id},
        )
        return resultados[0] if resultados else None

    @classmethod
    def crear(cls, datos):
        return cls._db().query_db(
            "INSERT INTO tareas "
            "(titulo, categoria_id, prioridad, fecha_limite, descripcion, usuario_id) "
            "VALUES (%(titulo)s, %(categoria_id)s, %(prioridad)s, %(fecha_limite)s, "
            "%(descripcion)s, %(usuario_id)s)",
            datos,
        )

    @classmethod
    def actualizar(cls, tarea_id, datos):
        return cls._db().query_db(
            "UPDATE tareas SET titulo = %(titulo)s, categoria_id = %(categoria_id)s, "
            "prioridad = %(prioridad)s, fecha_limite = %(fecha_limite)s, "
            "descripcion = %(descripcion)s "
            "WHERE id = %(id)s AND usuario_id = %(usuario_id)s",
            {**datos, "id": tarea_id},
        )

    @classmethod
    def cambiar_estado(cls, tarea_id, estado, usuario_id):
        return cls._db().query_db(
            "UPDATE tareas SET estado = %(estado)s "
            "WHERE id = %(id)s AND usuario_id = %(usuario_id)s",
            {"estado": estado, "id": tarea_id, "usuario_id": usuario_id},
        )

    @classmethod
    def eliminar(cls, tarea_id, usuario_id):
        return cls._db().query_db(
            "DELETE FROM tareas WHERE id = %(id)s AND usuario_id = %(usuario_id)s",
            {"id": tarea_id, "usuario_id": usuario_id},
        )

    @classmethod
    def resumen(cls, usuario_id):
        resultados = cls._db().query_db(
            "SELECT COUNT(*) AS total, "
            "SUM(estado = 'Pendiente') AS pendientes, "
            "SUM(estado = 'En progreso') AS en_progreso, "
            "SUM(estado = 'Completada') AS completadas "
            "FROM tareas WHERE usuario_id = %(usuario_id)s",
            {"usuario_id": usuario_id},
        )
        return resultados[0]

    @classmethod
    def proximas(cls, usuario_id, limite=3):
        return cls._db().query_db(
            "SELECT tareas.id, tareas.titulo, tareas.fecha_limite, "
            "DATEDIFF(tareas.fecha_limite, CURDATE()) AS dias_restantes "
            "FROM tareas WHERE tareas.usuario_id = %(usuario_id)s "
            "AND tareas.estado <> 'Completada' AND tareas.fecha_limite >= CURDATE() "
            "ORDER BY tareas.fecha_limite, tareas.id LIMIT %(limite)s",
            {"usuario_id": usuario_id, "limite": limite},
        )
