Documentación de Imágenes y Configuración en values.yaml
Este proyecto soporta diferentes imágenes de base de datos y variantes con Memcached o Redis como mecanismos de cache.
El cambio de imagen se realiza modificando el archivo values.yaml en la sección correspondiente al despliegue de la API.

Imágenes Disponibles
Imágenes Disponibles
Servicio	Imagen Base	Memcached	Redis
ChromaDB	usuario/chroma	usuario/chroma-memcached	usuario/chroma-redis
Elasticsearch	usuario/elasticsearch	usuario/elasticsearch-memcached	usuario/elasticsearch-redis
MariaDB	usuario/mariadb	usuario/mariadb-memcached	usuario/mariadb-redis
PostgreSQL	usuario/postgresql	usuario/postgresql-memcached	usuario/postgresql-redis
Nota: Reemplaza usuario por tu nombre de usuario en DockerHub (ejemplo: mydockeruser/mariadb).

Configuración en values.yaml
En el archivo values.yaml, se define la imagen que utilizará el despliegue.
La sección típica es la siguiente:

config:
  flask:
    enabled: true
    name: flasktest
    replicas: 10
    image: usuario/imagen
Ejemplo: Usar ChromaDB con Memcached
config:
  flask:
    enabled: true
    name: flasktest
    replicas: 10
    image: usuario/chroma-memcached
Dataset de Prueba: Información de Animales
Este apartado describe el dataset utilizado como prueba en el proyecto.
El dataset proporciona información general sobre diversas especies animales, abarcando datos físicos, ecológicos, taxonómicos y de comportamiento.

Fuente original: Animal Information Dataset - Kaggle

1. Descripción General
El dataset reúne un conjunto de características asociadas a distintos animales, como su altura, peso, dieta, hábitat, depredadores, estado de conservación, entre otros.
Este recurso fue empleado como dataset de prueba para validar funcionalidades en el proyecto, ya que contiene datos variados que permiten realizar consultas, análisis y visualizaciones desde distintos enfoques.

Estructura del Dataset
El dataset está compuesto por diversas columnas (atributos) que describen a cada animal. A continuación se detalla el glosario columna por columna:

Columna	Descripción
Animal	Nombre del animal.
Height (cm)	Rango de altura en centímetros del animal.
Weight (kg)	Rango de peso en kilogramos del animal.
Color	Colores comunes asociados a la apariencia del animal.
Lifespan (years)	Promedio de años de vida del animal.
Diet	Tipo de dieta que sigue principalmente (Ejemplo: carnívoro, herbívoro).
Habitat	Hábitat o entorno natural donde suele encontrarse el animal.
Predators	Depredadores o enemigos naturales del animal.
Average Speed (km/h)	Velocidad promedio en kilómetros por hora.
Countries Found	Países o regiones donde el animal es comúnmente encontrado.
Conservation Status	Estado de conservación según organismos especializados (Ejemplo: En peligro).
Family	Familia taxonómica a la que pertenece el animal.
Gestation Period (days)	Rango en días del período de gestación o embarazo.
Top Speed (km/h)	Velocidad máxima alcanzable en kilómetros por hora.
Social Structure	Estructura social o comportamiento (Ejemplo: solitario, en grupo).
Offspring per Birth	Número típico de crías por evento reproductivo.
Esquema Relacional del Dataset de Animales - MariaDB
Este apartado describe la estructura de base de datos SQL diseñada para almacenar el dataset de prueba sobre animales.
La implementación sigue un modelo relacional normalizado, con separación de entidades principales y relaciones uno a muchos y muchos a muchos.

Tablas Principales
Tabla animal
Contiene los datos básicos de cada animal.

Columna	Tipo	Descripción
id	INT (PK, AI)	Identificador único del animal.
nombre	TEXT	Nombre del animal.
altura_cm	TEXT	Altura del animal en centímetros (puede ser rango).
peso_kg	TEXT	Peso del animal en kilogramos (puede ser rango).
color	TEXT	Colores característicos.
esperanza_vida_años	TEXT	Promedio de vida en años.
dieta_id	INT (FK)	Referencia a la tabla dieta.
familia_id	INT (FK)	Referencia a la tabla familia.
Tabla dieta
Define los diferentes tipos de dietas (Carnívoro, Herbívoro, Omnívoro, etc.).

Columna	Tipo	Descripción
id	INT (PK, AI)	Identificador único.
tipo_dieta	TEXT (UNIQUE)	Tipo de dieta.
Tabla familia
Almacena la clasificación taxonómica a nivel de familia.

Columna	Tipo	Descripción
id	INT (PK, AI)	Identificador único.
nombre_familia	TEXT (UNIQUE)	Nombre de la familia taxonómica.
Tabla habitat
Define los diferentes hábitats donde los animales pueden encontrarse.

Columna	Tipo	Descripción
id	INT (PK, AI)	Identificador único.
nombre_habitat	TEXT (UNIQUE)	Nombre del hábitat.
Relación con animal: muchos a muchos, gestionado mediante la tabla animal_habitat.

Tabla predador
Lista de depredadores que pueden tener los animales.

Columna	Tipo	Descripción
id	INT (PK, AI)	Identificador único.
nombre_predador	TEXT (UNIQUE)	Nombre del depredador.
Relación con animal: muchos a muchos, gestionado mediante la tabla animal_predador.

Tablas Relacionales (Muchos a Muchos)
Tabla animal_habitat
Asocia a cada animal con uno o más hábitats.

Columna	Tipo	Descripción
animal_id	INT (FK)	Referencia a animal.
habitat_id	INT (FK)	Referencia a habitat.
Clave primaria compuesta: (animal_id, habitat_id)
Incluye ON DELETE CASCADE para mantener integridad referencial.

Tabla animal_predador
Relaciona a los animales con sus depredadores.

Columna	Tipo	Descripción
animal_id	INT (FK)	Referencia a animal.
predador_id	INT (FK)	Referencia a predador.
Clave primaria compuesta: (animal_id, predador_id)
Incluye ON DELETE CASCADE.

Tabla de Información Adicional
Tabla info_extra
Guarda atributos complementarios de cada animal.

Columna	Tipo	Descripción
animal_id	INT (PK, FK)	Referencia a animal.
velocidad_prom_kmh	TEXT	Velocidad promedio (km/h).
velocidad_max_kmh	TEXT	Velocidad máxima (km/h).
paises_encontrado	TEXT	Países/regiones donde se encuentra.
estado_conservacion	TEXT	Estado de conservación (ejemplo: En peligro).
gestacion_dias	TEXT	Período de gestación en días.
estructura_social	TEXT	Tipo de estructura social (ejemplo: solitario, grupo).
crias_por_parto	TEXT	Número de crías típicas por parto.
Índices
Para optimizar las consultas, se crean índices en claves foráneas y relaciones:

idx_animal_dieta → sobre animal(dieta_id)
idx_animal_familia → sobre animal(familia_id)
idx_animal_habitat_animal → sobre animal_habitat(animal_id)
idx_animal_habitat_habitat → sobre animal_habitat(habitat_id)
idx_animal_predador_animal → sobre animal_predador(animal_id)
idx_animal_predador_predador → sobre animal_predador(predador_id)
Modelo Relacional (Resumen)
Un animal pertenece a una dieta y una familia.
Un animal puede habitar en uno o varios hábitats.
Un animal puede tener uno o varios depredadores.
Un animal tiene información adicional única en info_extra.
Endpoints de prueba
Base URL: http://localhost:30080/

Esta API permite consultar información sobre animales y sus características.

Endpoints
1. Health Check
GET /health

Verifica que el servicio está activo y funcionando.

Request: GET http://localhost:30080/health

Response: { "status": "healthy" }

Código de estado: 200 OK

2. Listar Animales
GET /animales

Devuelve los primeros 50 animales registrados en la base de datos.

Request: GET http://localhost:30080/animales

Response exitoso (200 OK): [ {"id": 1, "nombre": "Tigre"}, {"id": 2, "nombre": "León"}, ... ]

Response de error (500 Internal Server Error): { "error": "No se pudo conectar a la base de datos" }

Notas:

Utiliza un pool de conexiones a PostgreSQL.
Se asegura de cerrar el cursor y devolver la conexión al pool.
3. Animales listados por su color
GET /colores

Devuelve los animales organizados por sus colores.

Request: GET http://localhost:30080/colores

Response exitoso (200 OK): [ { "animals": "Uakari", "color": "Bald, Red" } ]

Response de error (500 Internal Server Error): { "error": "No se pudo conectar a la base de datos" }

Resumen de Endpoints
Endpoint	Método	Descripción	Response Ejemplo	Código Estado
/health	GET	Verifica que el servicio está activo	{"status": "healthy"}	200
/animales	GET	Lista los primeros 50 animales	[{"id":1,"nombre":"Tigre"},...]	200 / 500
/colores	GET	Lista los colores y los animales	[{"animals":"Guepardo","color":"grey"},...]	200 / 500
Recomendaciones
Mantener consistencia en los nombres de las imagenes a utilizar: servicio-cache (-memcached, -redis).
Utiliza variables de entorno que permitan las parametrizacion de los datos necesarios para las bases de datos
Conclusión
Este dataset sirvió como recurso de prueba para el proyecto debido a su diversidad de atributos, lo cual permitió validar distintos procesos de manejo y análisis de información.
Gracias a la variedad de datos incluidos, fue posible simular escenarios realistas y robustos dentro del entorno de desarrollo.
