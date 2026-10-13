from flask import current_app

from flask_app.config.mysqlconnection import connectToMySQL


class Usuario:
    @staticmethod
    def _db():
        return connectToMySQL(current_app.config["DATABASE"])

    @classmethod
    def buscar_por_correo(cls, correo):
        resultados = cls._db().query_db(
            "SELECT id, nombre, apellido, correo, password FROM usuarios "
            "WHERE correo = %(correo)s LIMIT 1",
            {"correo": correo},
        )
        return resultados[0] if resultados else None

    @classmethod
    def crear(cls, datos):
        return cls._db().query_db(
            "INSERT INTO usuarios (nombre, apellido, correo, password) "
            "VALUES (%(nombre)s, %(apellido)s, %(correo)s, %(password)s)",
            datos,
        )
