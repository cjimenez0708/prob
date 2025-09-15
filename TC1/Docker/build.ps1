param (
    [Parameter(Mandatory = $true)]
    [string]$Username
)

# Login a Docker
docker login

# Ir a la carpeta FlaskApp
Set-Location FlaskApp

# Construir la imagen
docker build -t "$Username/flask-example" .

# Subir la imagen
docker push "$Username/flask-example"

#-------------------------INICIO DATASEEDER ----------------------------
Set-Location ../DataSeeder
docker build -t "$Username/dataseeder" .
docker push "$Username/dataseeder"
#-------------------------FIN DATASEEDER ----------------------------

#-------------------------CHROMADB ----------------------------
# Ir a la carpeta general ChromaDB
Set-Location ../ChromaDBPackage
#Ir la la carpeta ChromaDB
Set-Location ./ChromaDB
# Construir la imagen
docker build -t "$Username/chroma" .
# Subir la imagen
docker push "$Username/chroma"
#Carpeta de ChromaDB-Memcached
Set-Location ../Chroma-Memcached
# Construir la imagen
docker build -t "$Username/chroma-memcached" .
# Subir la imagen
docker push "$Username/chroma-memcached"
#Carpeta de ChromaDB-Redis
Set-Location ../Chroma-Redis
# Construir la imagen
docker build -t "$Username/chroma-redis" .
# Subir la imagen
docker push "$Username/chroma-redis"

#-------------------------FIN CHROMADB ----------------------------

#-------------------------INICIO ELASTICSEARCH ----------------------------

# Ir a la carpeta general Elasticsearch
Set-Location ../../ElasticSearchPackage

#Carpeta Elasticsearch
Set-Location ./Elasticsearch
docker build -t "$Username/elasticsearch" .
docker push "$Username/elasticsearch"

#ElasticSearch-Memcached
Set-Location ../ElasticSearch-Memcached
docker build -t "$Username/elasticsearch-memcached" .
docker push "$Username/elasticsearch-memcached"

#ElasticSearch-Redis
Set-Location ../ElasticSearch-Redis
docker build -t "$Username/elasticsearch-redis" .
docker push "$Username/elasticsearch-redis"

#-------------------------FIN ELASTICSEARCH ----------------------------

#-------------------------INICIO MARIA DB ----------------------------

# Ir a la carpeta general MariaDB
Set-Location ../../MariaDBPackage
#MariaDB
Set-Location ./MariaDB
docker build -t "$Username/mariadb" .
docker push "$Username/mariadb"

#MariaDB-Memcached
Set-Location ../MariaDB-Memcached
docker build -t "$Username/mariadb-memcached" .
docker push "$Username/mariadb-memcached"

#MariaDB-Redis
Set-Location ../MariaDB-Redis
docker build -t "$Username/mariadb-redis" .
docker push "$Username/mariadb-redis"
#-------------------------FIN MARIA DB ----------------------------

#-------------------------INICIO POSTGRESQL ----------------------------

# Ir a la carpeta general PostgreSQL
Set-Location ../../PostgreSQLPackage
#PostgreSQL
Set-Location ./PostgreSQL
docker build -t "$Username/postgresql" .
docker push "$Username/postgresql"

#PostgreSQL-Memcached
Set-Location ../PostgreSQL-Memcached
docker build -t "$Username/postgresql-memcached" .
docker push "$Username/postgresql-memcached"

#PostgreSQL-Redis
Set-Location ../PostgreSQL-Redis
docker build -t "$Username/postgresql-redis" .
docker push "$Username/postgresql-redis"
#-------------------------FIN POSTGRESQL ----------------------------


# Volver a la carpeta inicial
Set-Location ../..