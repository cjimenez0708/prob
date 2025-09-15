from flask import Flask, jsonify
from elasticsearch import Elasticsearch
from os import getenv
import sys
import os, json
from pymemcache.client.base import Client

app = Flask(__name__)


# Elasticsearch configuration from environment variables
ES_HOST = getenv("ELASTIC", "localhost")
ES_PORT = getenv("ES_PORT", "9200")
ES_USER = getenv("ELASTIC_USER", "elastic")
ES_PASSWORD = getenv("ELASTIC_PASS", "changeme")

# Index name for animals in Elasticsearch
INDEX_NAME = "animals"


#Variables para memcached
MEMCACHED_HOST = os.getenv("MEMCACHED_HOST", "localhost")
MEMCACHED_PORT = int(os.getenv("MEMCACHED_PORT", "11211"))
CACHE_TTL_SECONDS = 60

memcached = Client(("databases-memcached", 11211))


def cache_get(key):
    try:
        raw = memcached.get(key)
        if not raw:
            return None
        
        return json.loads(raw.decode("utf-8"))
    except Exception:
        return None

def cache_set(key: str, value: dict, ttl: int = CACHE_TTL_SECONDS):
    try:
        memcached.set(key, json.dumps(value), expire=ttl)
    except Exception:
        pass


# Database connection
def get_connection():
    try:
        conn = Elasticsearch(
            [f"http://{ES_HOST}:{ES_PORT}"],
            basic_auth=(ES_USER, ES_PASSWORD)
        ) # Crear conexión a Elasticsearch
        if not conn.ping(): #chequear si la conexión es exitosa
            raise Exception("No se pudo conectar a Elasticsearch")
        return conn # Devolver la conexión
    except Exception as e:
        print(f"Error creando conexión Elasticsearch: {e}")
        sys.exit(1)


# List all the animals
@app.route("/animales", methods=["GET"])
def get_animales():

    cache_key = "animales-nombre"

    #Busca en caché
    cached = cache_get(cache_key)
    if cached is not None:
            return jsonify({"source": "cache", "data": cached}) #Caché Hit

    #En caso de caché miss, abre conexion con bd y consulta
    conn = get_connection() # Obtener conexión a Elasticsearch
    try:
        res = conn.search(index=INDEX_NAME, size=50, query={"match_all": {}})
        animals = [{"id": hit["_id"], "nombre": hit["_source"]["name"]} for hit in res["hits"]["hits"]]

        #Guarda en la caché despues de haber consultado BD
        cache_set(cache_key, animals, CACHE_TTL_SECONDS)
        return jsonify({"source": "db", "data": animals})   # Devolver la lista de animales
    
    except Exception as e:
        if e.info and 'index_not_found_exception' in e.info['error']['type']:
            return jsonify({"error": "Debe cargar la base de datos"}), 404
        return jsonify({"error": str(e)}), 500

@app.route("/colores", methods=["GET"])
def get_colores():

    cache_key = "animales-colores"

    #Busca en caché
    cached = cache_get(cache_key)
    if cached is not None:
            return jsonify({"source": "cache", "data": cached}) #Caché Hit

    #En caso de caché miss, abre conexion con bd y consulta
    conn = get_connection() # Obtener conexión a Elasticsearch
    query = {
        "size": 0,
        "aggs": {
            "por_color": {
            "terms": {
                "field": "color",
                "size": 100
            },
            "aggs": {
                "nombres_animales": {
                "top_hits": {
                    "_source": ["name"],
                    "size": 100
                }
                }
            }
            }
        }
    }
    # Realizar la búsqueda con agregaciones
    try:
        res = conn.search(index="animals", body=query)
        # Procesar los resultados
        result = []
        for bucket in res["aggregations"]["por_color"]["buckets"]:
            color = bucket["key"]
            animales = [hit["_source"]["name"] for hit in bucket["nombres_animales"]["hits"]["hits"]]
            result.append({
                "color": color,
                "animals": animales
            })

        #Guarda en la caché despues de haber consultado BD
        cache_set(cache_key, result, CACHE_TTL_SECONDS)
        return jsonify({"source": "db", "data": result}) # Devolver la lista de colores con sus animales

    except Exception as e:
        if getattr(e, "info", None) and 'index_not_found_exception' in e.info.get('error', {}).get('type', ''):
            return jsonify({"error": "Debe cargar la base de datos"}), 404
        return jsonify({"error": str(e)}), 500

# Health check endpoint
@app.route("/health", methods=["GET"])
def health_check():
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
