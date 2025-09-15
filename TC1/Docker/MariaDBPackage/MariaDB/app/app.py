from flask import Flask, jsonify
import mysql.connector
from mysql.connector import pooling, connect
from os import getenv
import sys
import os

# Load environment variables
MARIADB = os.getenv("MARIADB")
MARIADB_USER = os.getenv("MARIADB_USER")
MARIADB_PASS = os.getenv("MARIADB_PASS")
MARIADB_DB = os.getenv("MARIADB_DB")

app = Flask(__name__)

mariadb_pool = None

def init_pool():
    global mariadb_pool
    try:
        conn = connect(
            host=MARIADB,
            user=MARIADB_USER,
            password=MARIADB_PASS,
            charset="utf8mb4",
            collation="utf8mb4_general_ci"
        )
        cur = conn.cursor()
        cur.execute(f"""
            CREATE DATABASE IF NOT EXISTS {MARIADB_DB}
            DEFAULT CHARACTER SET utf8mb4
            DEFAULT COLLATE utf8mb4_general_ci;
        """)
        conn.commit()
        cur.close()
        conn.close()
        print(f"Base de datos {MARIADB_DB} creada o ya existente.")

        mariadb_pool = pooling.MySQLConnectionPool(
            pool_name="mariadb_pool",
            pool_size=5,
            host=MARIADB,
            user=MARIADB_USER,
            password=MARIADB_PASS,
            database=MARIADB_DB,
            charset="utf8mb4",
            collation="utf8mb4_general_ci",
            autocommit=True
        )
        print("Pool de conexiones MariaDB creado")

    except Exception as e:
        print(f"Error inicializando MariaDB: {e}")
        sys.exit(1)

def get_connection():
    global mariadb_pool
    if not mariadb_pool:
        init_pool()
    return mariadb_pool.get_connection()

def release_connection(conn):
    if conn:
        conn.close()


# list animals 
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

# list colors with animals 
@app.route("/colores", methods=["GET"])
def get_colores():
    conn = get_connection()
    try:
        if conn is None:
            return jsonify({"error": "No se pudo conectar a la base de datos"}), 500
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT a.color, GROUP_CONCAT(DISTINCT a.nombre SEPARATOR ', ') AS animales
                FROM animal a
                GROUP BY a.color;
            """)
            rows = cur.fetchall()
            return jsonify([{"animals": r[1], "color": r[0]} for r in rows])
        finally:
            cur.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        release_connection(conn)

# HEALTH CHECK ENDPOINT
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == "__main__":
    app.run(host='localhost', port=5000)