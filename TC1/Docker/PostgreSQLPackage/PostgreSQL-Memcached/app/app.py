from flask import Flask, jsonify
import psycopg2
import psycopg2.pool
from os import getenv
import os, json
import sys
from pymemcache.client.base import Client

# Load environment variables
POSTGRES = getenv("POSTGRES")
POSTGRES_USER = getenv("POSTGRES_USER")
POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD")
POSTGRES_DB = getenv("POSTGRES_DB")

app = Flask(__name__)


#Variables para memcached
MEMCACHED_HOST = os.getenv("MEMCACHED_HOST", "localhost")
MEMCACHED_PORT = int(os.getenv("MEMCACHED_PORT", "11211"))
CACHE_TTL_SECONDS = 60

memcached = Client(("databases-memcached", 11211))

#DATABASE CONNECTION
pg_pool = None

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

# Initialize connection pool
def init_pool():
    global pg_pool
    try:
        pg_pool = psycopg2.pool.SimpleConnectionPool(
            minconn=1,
            maxconn=5,
            host=POSTGRES,
            user=POSTGRES_USER,
            password=POSTGRES_PASSWORD,
            database=POSTGRES_DB
        )
        print("Pool de conexiones PostgreSQL creado")
    except Exception as e:
        print(f"Error creando pool PostgreSQL: {e}")
        sys.exit(1)

# Get a connection from the pool
def get_connection():
    global pg_pool
    if not pg_pool:
        init_pool()
    return pg_pool.getconn()

# Release a connection back to the pool
def release_connection(conn):
    global pg_pool
    if pg_pool and conn:
        pg_pool.putconn(conn)

#list animals
@app.route("/animales", methods=["GET"])
def get_animales():
    
    cache_key = "animales-nombre"

    #Busca en caché
    cached = cache_get(cache_key)
    if cached is not None:
            return jsonify({"source": "cache", "data": cached}) #Caché Hit
    
    #En caso de caché miss, abre conexion con bd y consulta
    conn = get_connection()
    try:
        if conn is None:
            return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
        cur = conn.cursor()
        try:
                cur.execute("SELECT id, nombre FROM animal LIMIT 50;")
                rows = cur.fetchall()
                animales = [{"id": r[0], "nombre": r[1]} for r in rows]
                
                #Guarda en la caché despues de haber consultado BD
                cache_set(cache_key, animales, CACHE_TTL_SECONDS)
                return jsonify({"source": "db", "data": animales})
        finally:
            cur.close()
    except Exception as e:
        
        return jsonify({"error": str(e)}), 500
    finally:
        release_connection(conn)



#list colors with animals
@app.route("/colores", methods=["GET"])
def get_colores():

    cache_key = "animales-colores"

    #Busca en caché
    cached = cache_get(cache_key)
    if cached is not None:
            return jsonify({"source": "cache", "data": cached}) #Caché Hit


    #En caso de caché miss, abre conexion con bd y consulta
    conn = get_connection()
    try:
        if conn is None:
            return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT a.color, STRING_AGG(DISTINCT a.nombre, ', ') AS animales
                FROM animal a
                GROUP BY a.color;
            """)
            rows = cur.fetchall()
            colores = [{"animals": r[1], "color": r[0]} for r in rows]

            #Guarda en la caché despues de haber consultado BD
            cache_set(cache_key, colores, CACHE_TTL_SECONDS)
            return jsonify({"source": "db", "data": colores})   # Devolver la lista de colores con sus animales
        
        finally:
            cur.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        release_connection(conn)
        

#HEALTH CHECK ENDPOINT
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == "__main__":
    app.run(host='localhost', port=5000)