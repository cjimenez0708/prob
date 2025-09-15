-- Creación de tablas para el dataset de animales

-- Tabla de dietas
CREATE TABLE IF NOT EXISTS dieta (
    id SERIAL PRIMARY KEY,
    tipo_dieta TEXT UNIQUE NOT NULL
);

-- Tabla de familias
CREATE TABLE IF NOT EXISTS familia (
    id SERIAL PRIMARY KEY,
    nombre_familia TEXT UNIQUE NOT NULL
);

-- Tabla principal de animales
CREATE TABLE IF NOT EXISTS animal (
    id SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    altura_cm TEXT,
    peso_kg TEXT,
    color TEXT,
    esperanza_vida_años TEXT,
    dieta_id INT,
    familia_id INT,
    FOREIGN KEY (dieta_id) REFERENCES dieta(id),
    FOREIGN KEY (familia_id) REFERENCES familia(id)
);

-- Tabla de hábitats
CREATE TABLE IF NOT EXISTS habitat (
    id SERIAL PRIMARY KEY,
    nombre_habitat TEXT UNIQUE NOT NULL
);

-- Tabla de relación animal-hábitat (muchos a muchos)
CREATE TABLE IF NOT EXISTS animal_habitat (
    animal_id INT NOT NULL,
    habitat_id INT NOT NULL,
    PRIMARY KEY (animal_id, habitat_id),
    FOREIGN KEY (animal_id) REFERENCES animal(id) ON DELETE CASCADE,
    FOREIGN KEY (habitat_id) REFERENCES habitat(id) ON DELETE CASCADE
);

-- Tabla de predadores
CREATE TABLE IF NOT EXISTS predador (
    id SERIAL PRIMARY KEY,
    nombre_predador TEXT UNIQUE NOT NULL
);

-- Tabla de relación animal-predador (muchos a muchos)
CREATE TABLE IF NOT EXISTS animal_predador (
    animal_id INT NOT NULL,
    predador_id INT NOT NULL,
    PRIMARY KEY (animal_id, predador_id),
    FOREIGN KEY (animal_id) REFERENCES animal(id) ON DELETE CASCADE,
    FOREIGN KEY (predador_id) REFERENCES predador(id) ON DELETE CASCADE
);

-- Tabla de información adicional
CREATE TABLE IF NOT EXISTS info_extra (
    animal_id INT PRIMARY KEY,
    velocidad_prom_kmh TEXT,
    velocidad_max_kmh TEXT,
    paises_encontrado TEXT,
    estado_conservacion TEXT,
    gestacion_dias TEXT,
    estructura_social TEXT,
    crias_por_parto TEXT,
    FOREIGN KEY (animal_id) REFERENCES animal(id) ON DELETE CASCADE
);

-- Crear índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_animal_dieta ON animal(dieta_id);
CREATE INDEX IF NOT EXISTS idx_animal_familia ON animal(familia_id);
CREATE INDEX IF NOT EXISTS idx_animal_habitat_animal ON animal_habitat(animal_id);
CREATE INDEX IF NOT EXISTS idx_animal_habitat_habitat ON animal_habitat(habitat_id);
CREATE INDEX IF NOT EXISTS idx_animal_predador_animal ON animal_predador(animal_id);
CREATE INDEX IF NOT EXISTS idx_animal_predador_predador ON animal_predador(predador_id);