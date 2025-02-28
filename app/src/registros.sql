CREATE TABLE IF NOT EXISTS Usuarios (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_ VARCHAR(255) NOT NULL,
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMPTZ NULL,
    imagen_perfil VARCHAR(500) DEFAULT NULL
);

-- Crear tabla comentarios
CREATE TABLE IF NOT EXISTS comentarios (
    id SERIAL PRIMARY KEY,
    usuario_id INT NOT NULL,
    nombre_usuario VARCHAR(255) NOT NULL,
    contenido TEXT NOT NULL,
    fecha_creacion TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES Usuarios(id)
);

-- Crear tabla registro_ips
CREATE TABLE IF NOT EXISTS registro_ips (
    id SERIAL PRIMARY KEY,
    usuario_id INT,
    nombre VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45) NOT NULL,
    fecha_hora TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES Usuarios(id)
);
