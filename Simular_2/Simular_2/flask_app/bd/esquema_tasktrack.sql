CREATE DATABASE IF NOT EXISTS tasktrack
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE tasktrack;

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

CREATE TABLE IF NOT EXISTS categorias (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  nombre VARCHAR(60) NOT NULL,
  usuario_id INT UNSIGNED NOT NULL,
  creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uq_categorias_usuario_nombre (usuario_id, nombre),
  CONSTRAINT fk_categorias_usuario FOREIGN KEY (usuario_id)
    REFERENCES usuarios (id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS tareas (
  id INT UNSIGNED NOT NULL AUTO_INCREMENT,
  titulo VARCHAR(160) NOT NULL,
  categoria_id INT UNSIGNED NOT NULL,
  prioridad ENUM('Alta', 'Media', 'Baja') NOT NULL,
  fecha_limite DATE NOT NULL,
  estado ENUM('Pendiente', 'En progreso', 'Completada') NOT NULL DEFAULT 'Pendiente',
  descripcion VARCHAR(2000) NOT NULL DEFAULT '',
  usuario_id INT UNSIGNED NOT NULL,
  creado_en TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY ix_tareas_usuario_fecha (usuario_id, fecha_limite),
  KEY ix_tareas_categoria (categoria_id),
  CONSTRAINT fk_tareas_usuario FOREIGN KEY (usuario_id)
    REFERENCES usuarios (id) ON DELETE CASCADE,
  CONSTRAINT fk_tareas_categoria FOREIGN KEY (categoria_id)
    REFERENCES categorias (id) ON DELETE RESTRICT
) ENGINE=InnoDB;
