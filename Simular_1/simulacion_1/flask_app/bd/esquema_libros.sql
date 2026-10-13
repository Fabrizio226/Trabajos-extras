CREATE DATABASE IF NOT EXISTS biblioteca
	CHARACTER SET utf8mb4
	COLLATE utf8mb4_unicode_ci;

USE biblioteca;

CREATE TABLE IF NOT EXISTS usuarios (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	nombre VARCHAR(80) NOT NULL,
	apellido VARCHAR(80) NOT NULL,
	correo VARCHAR(254) NOT NULL,
	password VARCHAR(255) NOT NULL,
	creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (id),
	UNIQUE KEY uq_usuarios_correo (correo)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS libros (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	titulo VARCHAR(160) NOT NULL,
	autor VARCHAR(120) NOT NULL,
	genero VARCHAR(60) NOT NULL,
	fecha_publicacion DATE NOT NULL,
	descripcion VARCHAR(2000) NOT NULL DEFAULT '',
	usuario_id INT UNSIGNED NOT NULL,
	creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (id),
	KEY ix_libros_usuario (usuario_id),
	KEY ix_libros_titulo (titulo),
	CONSTRAINT fk_libros_usuario FOREIGN KEY (usuario_id)
		REFERENCES usuarios (id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS favoritos (
	id INT UNSIGNED NOT NULL AUTO_INCREMENT,
	libro_id INT UNSIGNED NOT NULL,
	usuario_id INT UNSIGNED NOT NULL,
	creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (id),
	UNIQUE KEY uq_favorito_usuario_libro (usuario_id, libro_id),
	KEY ix_favoritos_libro (libro_id),
	CONSTRAINT fk_favoritos_libro FOREIGN KEY (libro_id)
		REFERENCES libros (id) ON DELETE CASCADE,
	CONSTRAINT fk_favoritos_usuario FOREIGN KEY (usuario_id)
		REFERENCES usuarios (id) ON DELETE CASCADE
) ENGINE=InnoDB;
