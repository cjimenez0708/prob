-- Configuración inicial de charset
SET NAMES utf8mb4 COLLATE utf8mb4_general_ci;

-- Tabla de dietas
CREATE TABLE IF NOT EXISTS dieta (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tipo_dieta TEXT UNIQUE NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tabla de familias  
CREATE TABLE IF NOT EXISTS familia (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_familia TEXT UNIQUE NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tabla principal de animales
CREATE TABLE IF NOT EXISTS animal (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre TEXT NOT NULL,
    altura_cm TEXT,
    peso_kg TEXT,
    color TEXT,
    esperanza_vida_años TEXT,
    dieta_id INT,
    familia_id INT,
    FOREIGN KEY (dieta_id) REFERENCES dieta(id),
    FOREIGN KEY (familia_id) REFERENCES familia(id),
    INDEX idx_animal_dieta (dieta_id),
    INDEX idx_animal_familia (familia_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tabla de hábitats
CREATE TABLE IF NOT EXISTS habitat (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_habitat TEXT UNIQUE NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tabla de relación animal-hábitat (muchos a muchos)
CREATE TABLE IF NOT EXISTS animal_habitat (
    animal_id INT NOT NULL,
    habitat_id INT NOT NULL,
    PRIMARY KEY (animal_id, habitat_id),
    FOREIGN KEY (animal_id) REFERENCES animal(id) ON DELETE CASCADE,
    FOREIGN KEY (habitat_id) REFERENCES habitat(id) ON DELETE CASCADE,
    INDEX idx_animal_habitat_animal (animal_id),
    INDEX idx_animal_habitat_habitat (habitat_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tabla de predadores
CREATE TABLE IF NOT EXISTS predador (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre_predador TEXT UNIQUE NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- Tabla de relación animal-predador (muchos a muchos)
CREATE TABLE IF NOT EXISTS animal_predador (
    animal_id INT NOT NULL,
    predador_id INT NOT NULL,
    PRIMARY KEY (animal_id, predador_id),
    FOREIGN KEY (animal_id) REFERENCES animal(id) ON DELETE CASCADE,
    FOREIGN KEY (predador_id) REFERENCES predador(id) ON DELETE CASCADE,
    INDEX idx_animal_predador_animal (animal_id),
    INDEX idx_animal_predador_predador (predador_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
