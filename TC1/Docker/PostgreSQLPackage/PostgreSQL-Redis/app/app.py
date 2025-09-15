from flask import Flask, jsonify
import psycopg2
import psycopg2.pool
from os import getenv
import sys

# Load environment variables
POSTGRES = getenv("POSTGRES")
POSTGRES_USER = getenv("POSTGRES_USER")
POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD")
POSTGRES_DB = getenv("POSTGRES_DB")

app = Flask(__name__)

#DATABASE CONNECTION
pg_pool = None

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
    conn = get_connection()
    try:
        if conn is None:
            return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
        cur = conn.cursor()
        try:
            cur.execute("SELECT id, nombre FROM animal LIMIT 50;")
            rows = cur.fetchall()
            return jsonify([{"id": r[0], "nombre": r[1]} for r in rows])
        finally:
            cur.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        release_connection(conn)



#ANIMAL WITH HIGHEST SPEED
@app.route("/top-velocidad", methods=["GET"])
def top_velocidad():
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT a.nombre, i.velocidad_max_kmh
            FROM animal a
            JOIN info_extra i ON a.id = i.animal_id
            ORDER BY NULLIF(i.velocidad_max_kmh, '')::INT DESC
            LIMIT 5;
        """)
        rows = cur.fetchall()
        cur.close()
        return jsonify([{"nombre": r[0], "velocidad_max_kmh": r[1]} for r in rows])
    finally:
        release_connection(conn)



#HEALTH CHECK ENDPOINT
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == "__main__":
    app.run(host='localhost', port=5000)