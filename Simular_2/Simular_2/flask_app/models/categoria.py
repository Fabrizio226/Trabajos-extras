from flask import current_app

from flask_app.config.mysqlconnection import connectToMySQL


class Categoria:
    @staticmethod
    def _db():
        return connectToMySQL(current_app.config["DATABASE"])

    @classmethod
    def listar(cls, usuario_id):
        return cls._db().query_db(
            "SELECT categorias.*, COUNT(tareas.id) AS cantidad_tareas "
            "FROM categorias LEFT JOIN tareas ON tareas.categoria_id = categorias.id "
            "WHERE categorias.usuario_id = %(usuario_id)s "
            "GROUP BY categorias.id ORDER BY categorias.nombre",
            {"usuario_id": usuario_id},
        )

    @classmethod
    def buscar_por_id(cls, categoria_id, usuario_id):
        resultados = cls._db().query_db(
            "SELECT id, nombre, usuario_id FROM categorias "
            "WHERE id = %(id)s AND usuario_id = %(usuario_id)s LIMIT 1",
            {"id": categoria_id, "usuario_id": usuario_id},
        )
        return resultados[0] if resultados else None

    @classmethod
    def existe_nombre(cls, nombre, usuario_id, excluir_id=None):
        resultados = cls._db().query_db(
            "SELECT id FROM categorias WHERE usuario_id = %(usuario_id)s "
            "AND nombre = %(nombre)s AND (%(excluir_id)s IS NULL OR id <> %(excluir_id)s) LIMIT 1",
            {"nombre": nombre, "usuario_id": usuario_id, "excluir_id": excluir_id},
        )
        return bool(resultados)

    @classmethod
    def crear(cls, nombre, usuario_id):
        return cls._db().query_db(
            "INSERT INTO categorias (nombre, usuario_id) VALUES (%(nombre)s, %(usuario_id)s)",
            {"nombre": nombre, "usuario_id": usuario_id},
        )

    @classmethod
    def actualizar(cls, categoria_id, nombre, usuario_id):
        return cls._db().query_db(
            "UPDATE categorias SET nombre = %(nombre)s "
            "WHERE id = %(id)s AND usuario_id = %(usuario_id)s",
            {"nombre": nombre, "id": categoria_id, "usuario_id": usuario_id},
        )

    @classmethod
    def eliminar(cls, categoria_id, usuario_id):
        return cls._db().query_db(
            "DELETE FROM categorias WHERE id = %(id)s AND usuario_id = %(usuario_id)s",
            {"id": categoria_id, "usuario_id": usuario_id},
        )
