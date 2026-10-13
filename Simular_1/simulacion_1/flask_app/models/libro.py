from flask import current_app

from flask_app.config.mysqlconnection import connectToMySQL


class Libro:
	@staticmethod
	def _db():
		return connectToMySQL(current_app.config["DATABASE"])

	@classmethod
	def listar_propios(cls, usuario_id):
		return cls._db().query_db(
			"SELECT libros.*, COUNT(DISTINCT favoritos.id) AS cantidad_favoritos "
			"FROM libros LEFT JOIN favoritos ON favoritos.libro_id = libros.id "
			"WHERE libros.usuario_id = %(usuario_id)s GROUP BY libros.id "
			"ORDER BY libros.fecha_publicacion DESC, libros.id DESC",
			{"usuario_id": usuario_id},
		) or []

	@classmethod
	def listar_comunidad(cls, usuario_id, busqueda=""):
		return cls._db().query_db(
			"SELECT libros.*, usuarios.nombre AS creador_nombre, usuarios.apellido AS creador_apellido, "
			"COUNT(DISTINCT favoritos.id) AS cantidad_favoritos "
			"FROM libros JOIN usuarios ON usuarios.id = libros.usuario_id "
			"LEFT JOIN favoritos ON favoritos.libro_id = libros.id "
			"WHERE libros.usuario_id <> %(usuario_id)s AND "
			"(libros.titulo LIKE %(busqueda)s OR libros.autor LIKE %(busqueda)s) "
			"GROUP BY libros.id ORDER BY libros.fecha_publicacion DESC, libros.id DESC",
			{"usuario_id": usuario_id, "busqueda": f"%{busqueda}%"},
		) or []

	@classmethod
	def buscar_por_id(cls, libro_id):
		resultados = cls._db().query_db(
			"SELECT libros.*, usuarios.nombre AS creador_nombre, usuarios.apellido AS creador_apellido, "
			"COUNT(DISTINCT favoritos.id) AS cantidad_favoritos "
			"FROM libros JOIN usuarios ON usuarios.id = libros.usuario_id "
			"LEFT JOIN favoritos ON favoritos.libro_id = libros.id "
			"WHERE libros.id = %(id)s GROUP BY libros.id LIMIT 1",
			{"id": libro_id},
		)
		return resultados[0] if resultados else None

	@classmethod
	def crear(cls, datos):
		return cls._db().query_db(
			"INSERT INTO libros (titulo, autor, genero, fecha_publicacion, descripcion, usuario_id) "
			"VALUES (%(titulo)s, %(autor)s, %(genero)s, %(fecha_publicacion)s, %(descripcion)s, %(usuario_id)s)",
			datos,
		)

	@classmethod
	def actualizar(cls, libro_id, datos):
		return cls._db().query_db(
			"UPDATE libros SET titulo = %(titulo)s, autor = %(autor)s, genero = %(genero)s, "
			"fecha_publicacion = %(fecha_publicacion)s, descripcion = %(descripcion)s "
			"WHERE id = %(id)s AND usuario_id = %(usuario_id)s",
			{**datos, "id": libro_id},
		)

	@classmethod
	def eliminar(cls, libro_id, usuario_id):
		return cls._db().query_db(
			"DELETE FROM libros WHERE id = %(id)s AND usuario_id = %(usuario_id)s",
			{"id": libro_id, "usuario_id": usuario_id},
		)

	@classmethod
	def listar_favoritos(cls, usuario_id):
		return cls._db().query_db(
			"SELECT libros.*, usuarios.nombre AS creador_nombre, usuarios.apellido AS creador_apellido, "
			"COUNT(DISTINCT total_favoritos.id) AS cantidad_favoritos, "
			"MAX(favoritos.creado_en) AS favorito_desde "
			"FROM favoritos JOIN libros ON libros.id = favoritos.libro_id "
			"JOIN usuarios ON usuarios.id = libros.usuario_id "
			"LEFT JOIN favoritos AS total_favoritos ON total_favoritos.libro_id = libros.id "
			"WHERE favoritos.usuario_id = %(usuario_id)s GROUP BY libros.id "
			"ORDER BY favorito_desde DESC",
			{"usuario_id": usuario_id},
		) or []

	@classmethod
	def usuarios_que_favoritaron(cls, libro_id):
		return cls._db().query_db(
			"SELECT usuarios.id, usuarios.nombre, usuarios.apellido "
			"FROM favoritos JOIN usuarios ON usuarios.id = favoritos.usuario_id "
			"WHERE favoritos.libro_id = %(libro_id)s ORDER BY favoritos.creado_en",
			{"libro_id": libro_id},
		) or []

	@classmethod
	def ids_favoritos(cls, usuario_id):
		resultados = cls._db().query_db(
			"SELECT libro_id FROM favoritos WHERE usuario_id = %(usuario_id)s",
			{"usuario_id": usuario_id},
		) or []
		return {fila["libro_id"] for fila in resultados}

	@classmethod
	def es_favorito(cls, libro_id, usuario_id):
		resultados = cls._db().query_db(
			"SELECT id FROM favoritos WHERE libro_id = %(libro_id)s AND usuario_id = %(usuario_id)s LIMIT 1",
			{"libro_id": libro_id, "usuario_id": usuario_id},
		)
		return bool(resultados)

	@classmethod
	def alternar_favorito(cls, libro_id, usuario_id):
		if cls.es_favorito(libro_id, usuario_id):
			return cls._db().query_db(
				"DELETE FROM favoritos WHERE libro_id = %(libro_id)s AND usuario_id = %(usuario_id)s",
				{"libro_id": libro_id, "usuario_id": usuario_id},
			)
		return cls._db().query_db(
			"INSERT INTO favoritos (libro_id, usuario_id) VALUES (%(libro_id)s, %(usuario_id)s)",
			{"libro_id": libro_id, "usuario_id": usuario_id},
		)
