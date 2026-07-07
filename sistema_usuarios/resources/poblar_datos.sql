USE usuarios_db;

-- a
INSERT IGNORE INTO roles (id, nombre) VALUES (1, 'ADMIN'), (2, 'USER');

-- a
INSERT IGNORE INTO usuarios (id, usuario, password, tipo_usuario_id) VALUES 
(1, 'admin', 'admin123', 1), -- Contraseña: admin123
(2, 'juan', 'juan123', 2);    -- Contraseña: juan123
