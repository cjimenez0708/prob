import os
import kagglehub
from kagglehub import KaggleDatasetAdapter
import pandas as pd
from os import getenv
import psycopg2
import psycopg2.pool
import sys
import mysql.connector
from mysql.connector import pooling
from elasticsearch import Elasticsearch, helpers
import chromadb
from chromadb.utils import embedding_functions
from sentence_transformers import SentenceTransformer
import requests


# Variables de entorno
POSTGRES = getenv("POSTGRES")
POSTGRES_USER = getenv("POSTGRES_USER")
POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD")
POSTGRES_DB = getenv("POSTGRES_DB")

MARIADB = os.getenv("MARIADB")
MARIADB_USER = os.getenv("MARIADB_USER")
MARIADB_PASS = os.getenv("MARIADB_PASS")
MARIADB_DB = os.getenv("MARIADB_DB")

ELASTIC = getenv("ELASTIC")        
ELASTIC_USER = getenv("ELASTIC_USER")
ELASTIC_PASS = getenv("ELASTIC_PASS")
ES_PORT = getenv("ES_PORT", "9200")

CHROMA_ENDPOINT = getenv("CHROMA_ENDPOINT", "http://localhost:8000")
CHROMA_COLLECTION = getenv("CHROMA_COLLECTION", "animals")
CHROMA_EMBED_MODEL = getenv("CHROMA_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

VESPA_ENDPOINT = getenv("VESPA_ENDPOINT", "http://localhost:8081")
VESPA_COLLECTION = getenv("VESPA_COLLECTION", "animales")


print(f"POSTGRES: {POSTGRES}")
print(f"POSTGRES_USER: {POSTGRES_USER}")
print(f"POSTGRES_DB: {POSTGRES_DB}")
print(f"POSTGRES_PASSWORD: {POSTGRES_PASSWORD}")

print(f"MARIADB: {MARIADB}")
print(f"MARIADB_USER: {MARIADB_USER}")
print(f"MARIADB_DB: {MARIADB_DB}")
print(f"MARIADB_PASS: {MARIADB_PASS}")

print(f"ELASTIC: {ELASTIC}")
print(f"ELASTIC_USER: {ELASTIC_USER}")
print(f"ELASTIC_PASS: {ELASTIC_PASS}")
print(f"ES_PORT: {ES_PORT}")

print(f"CHROMA_ENDPOINT: {CHROMA_ENDPOINT}")
print(f"CHROMA_COLLECTION: {CHROMA_COLLECTION}")
print(f"CHROMA_EMBED_MODEL: {CHROMA_EMBED_MODEL}")

print(f"VESPA_ENDPOINT: {VESPA_ENDPOINT}")
print(f"VESPA_COLLECTION: {VESPA_COLLECTION}")

def load_dataset():
    try:
        df = kagglehub.load_dataset(
            KaggleDatasetAdapter.PANDAS,
            "iamsouravbanerjee/animal-information-dataset",
            "Animal Dataset.csv"
        )
        print(f"Dataset cargado: {len(df)} registros")
        return df
    except Exception as e:
        print(f"Error cargando dataset: {e}")
        raise

#---------------------------------------PostgreSQL-------------------------------------
# Crear pool de conexiones PostgreSQL
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

def execute_postgress_from_file():    
    # Construir la ruta al archivo
    script_dir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(script_dir, 'schemas', 'postgres.sql')    
    try:
        with open(schema_path, 'r', encoding='utf-8') as file:
            schema_sql = file.read()
        print("Archivo leído correctamente")
    except FileNotFoundError:
        print(f"Archivo no encontrado en: {schema_path}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    conn = pg_pool.getconn()
    cur = conn.cursor()
    
    try:
        cur.execute(schema_sql)
        conn.commit()
        print("Tablas creadas exitosamente en PostgreSQL")
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cur.close()
        pg_pool.putconn(conn)

def insert_data_postgres(df):    
    conn = pg_pool.getconn()
    cur = conn.cursor()
    
    try:
        for index, row in df.iterrows():
            cur.execute("""
                INSERT INTO dieta (tipo_dieta) VALUES (%s) 
                ON CONFLICT (tipo_dieta) DO NOTHING
            """, (row["Diet"],))
            cur.execute("SELECT id FROM dieta WHERE tipo_dieta=%s", (row["Diet"],))
            dieta_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO familia (nombre_familia) VALUES (%s) 
                ON CONFLICT (nombre_familia) DO NOTHING
            """, (row["Family"],))
            cur.execute("SELECT id FROM familia WHERE nombre_familia=%s", (row["Family"],))
            familia_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO animal (nombre, altura_cm, peso_kg, color, esperanza_vida_años, dieta_id, familia_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
            """, (
                row["Animal"], row["Height (cm)"], row["Weight (kg)"], row["Color"],
                row["Lifespan (years)"], dieta_id, familia_id
            ))
            animal_id = cur.fetchone()[0]

            habitats = [h.strip() for h in str(row["Habitat"]).split(",") if h.strip()]
            for h in habitats:
                if h and h.lower() != 'nan':
                    cur.execute("""
                        INSERT INTO habitat (nombre_habitat) VALUES (%s) 
                        ON CONFLICT (nombre_habitat) DO NOTHING
                    """, (h,))
                    cur.execute("SELECT id FROM habitat WHERE nombre_habitat=%s", (h,))
                    habitat_id = cur.fetchone()[0]
                    cur.execute("""
                        INSERT INTO animal_habitat (animal_id, habitat_id) VALUES (%s, %s) 
                        ON CONFLICT (animal_id, habitat_id) DO NOTHING
                    """, (animal_id, habitat_id))

            predadores = [p.strip() for p in str(row["Predators"]).split(",") if p.strip()]
            for p in predadores:
                if p and p.lower() != 'nan':
                    cur.execute("""
                        INSERT INTO predador (nombre_predador) VALUES (%s) 
                        ON CONFLICT (nombre_predador) DO NOTHING
                    """, (p,))
                    cur.execute("SELECT id FROM predador WHERE nombre_predador=%s", (p,))
                    predador_id = cur.fetchone()[0]
                    cur.execute("""
                        INSERT INTO animal_predador (animal_id, predador_id) VALUES (%s, %s) 
                        ON CONFLICT (animal_id, predador_id) DO NOTHING
                    """, (animal_id, predador_id))

            cur.execute("""
                INSERT INTO info_extra (animal_id, velocidad_prom_kmh, velocidad_max_kmh, paises_encontrado,
                estado_conservacion, gestacion_dias, estructura_social, crias_por_parto)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                animal_id, row["Average Speed (km/h)"], row["Top Speed (km/h)"], row["Countries Found"],
                row["Conservation Status"], row["Gestation Period (days)"], row["Social Structure"], row["Offspring per Birth"]
            ))

        conn.commit()
        print(f"Registros insertados exitosamente")
        return True
        
    except Exception as e:
        print(f"Error insertando datos: {e}")
        conn.rollback()
        return False
    finally:
        cur.close()
        pg_pool.putconn(conn)

#-------------------------------------Maria DB------------------------------------- 
mariadb_pool = None

# Crear conexion MariaDB
def conection_mariadb():
    global mariadb_pool
    try:
        # Conexión inicial sin base seleccionada
        conn = mysql.connector.connect(
            host=MARIADB,
            user=MARIADB_USER,
            password=MARIADB_PASS,
            charset="utf8mb4",
            collation="utf8mb4_general_ci"
        )
        cur = conn.cursor()
        # Crear la base de datos con charset y collation explícitos
        cur.execute(f"""
            CREATE DATABASE IF NOT EXISTS {MARIADB_DB}
            DEFAULT CHARACTER SET utf8mb4
            DEFAULT COLLATE utf8mb4_general_ci;
        """)
        conn.commit()
        cur.close()
        conn.close()
        print(f"Base de datos {MARIADB_DB} creada o ya existente.")
    except Exception as e:
        print(f"Error creando la base de datos: {e}")
        sys.exit(1)

    # Crear pool de conexiones 
    try:
        mariadb_pool = pooling.MySQLConnectionPool(
            pool_name="mariadb_pool",
            pool_size=5,
            host=MARIADB,
            user=MARIADB_USER,
            password=MARIADB_PASS,
            database=MARIADB_DB,
            charset='utf8mb4',
            collation='utf8mb4_general_ci',
            autocommit=True
        )
        print("Pool de conexiones MariaDB creado")
    except Exception as e:
        print(f"Error creando pool MariaDB: {e}")
        sys.exit(1)


def execute_MariaDB_from_file():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    schema_path = os.path.join(script_dir, 'schemas', 'mariadb.sql')    
    try:
        with open(schema_path, 'r', encoding='utf-8') as file:
            schema_sql = file.read()
        print("Archivo leído correctamente")
    except FileNotFoundError:
        print(f"Archivo no encontrado en: {schema_path}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False
    
    conn = mariadb_pool.get_connection()
    cur = conn.cursor()
    
    try:
        for statement in schema_sql.split(";"):
            stmt = statement.strip()
            if stmt:
                cur.execute(stmt)
        conn.commit()
        print("Tablas creadas exitosamente en MariaDB")
        return True
    except Exception as e:
        conn.rollback()
        print(f"Error creando tablas de MariaDB: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def insert_data_mariadb(df):
    conn = mariadb_pool.get_connection()
    cur = conn.cursor()
    try:
        for index, row in df.iterrows():
            cur.execute("""
                INSERT IGNORE INTO dieta (tipo_dieta) VALUES (%s)
            """, (row["Diet"],))
            cur.execute("SELECT id FROM dieta WHERE tipo_dieta=%s", (row["Diet"],))
            dieta_id = cur.fetchone()[0]

            cur.execute("""
                INSERT IGNORE INTO familia (nombre_familia) VALUES (%s)
            """, (row["Family"],))
            cur.execute("SELECT id FROM familia WHERE nombre_familia=%s", (row["Family"],))
            familia_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO animal (nombre, altura_cm, peso_kg, color, esperanza_vida_años, dieta_id, familia_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                row["Animal"], row["Height (cm)"], row["Weight (kg)"], row["Color"],
                row["Lifespan (years)"], dieta_id, familia_id
            ))
            animal_id = cur.lastrowid  

            habitats = [h.strip() for h in str(row["Habitat"]).split(",") if h.strip()]
            for h in habitats:
                if h and h.lower() != 'nan':
                    cur.execute("""
                        INSERT IGNORE INTO habitat (nombre_habitat) VALUES (%s)
                    """, (h,))
                    cur.execute("SELECT id FROM habitat WHERE nombre_habitat=%s", (h,))
                    habitat_id = cur.fetchone()[0]
                    cur.execute("""
                        INSERT IGNORE INTO animal_habitat (animal_id, habitat_id) VALUES (%s, %s)
                    """, (animal_id, habitat_id))

            predadores = [p.strip() for p in str(row["Predators"]).split(",") if p.strip()]
            for p in predadores:
                if p and p.lower() != 'nan':
                    cur.execute("""
                        INSERT IGNORE INTO predador (nombre_predador) VALUES (%s)
                    """, (p,))
                    cur.execute("SELECT id FROM predador WHERE nombre_predador=%s", (p,))
                    predador_id = cur.fetchone()[0]
                    cur.execute("""
                        INSERT IGNORE INTO animal_predador (animal_id, predador_id) VALUES (%s, %s)
                    """, (animal_id, predador_id))

            cur.execute("""
                INSERT INTO info_extra (animal_id, velocidad_prom_kmh, velocidad_max_kmh, paises_encontrado,
                estado_conservacion, gestacion_dias, estructura_social, crias_por_parto)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                animal_id, row["Average Speed (km/h)"], row["Top Speed (km/h)"], row["Countries Found"],
                row["Conservation Status"], row["Gestation Period (days)"], row["Social Structure"], row["Offspring per Birth"]
            ))

        conn.commit()
        print("Registros insertados exitosamente en MariaDB")
        return True

    except Exception as e:
        conn.rollback()
        print(f"Error insertando datos en MariaDB: {e}")
        return False
    finally:
        cur.close()
        conn.close()

#-------------------------------------Elastic Search-------------------------------------
# Crear conexión Elasticsearch
def get_connectionElastic():
    try:
        conn = Elasticsearch(
            [f"http://{ELASTIC}:{ES_PORT}"],
            basic_auth=(ELASTIC_USER, ELASTIC_PASS)
        )
        if not conn.ping():
            raise Exception("No se pudo conectar a Elasticsearch")
        return conn
    except Exception as e:
        print(f"Error creando conexión Elasticsearch: {e}")
        sys.exit(1)


def create_index_elastic():
    index_name = "animals"
    es = get_connectionElastic()
    if not es.indices.exists(index=index_name):
        es.indices.create(index=index_name, body={
            "mappings": {
                "properties": {
                    "name": {"type": "keyword"},
                    "height_cm": {"type": "keyword"},
                    "weight_kg": {"type": "keyword"},
                    "color": {"type": "keyword"},
                    "lifespan_years": {"type": "keyword"},
                    "diet": {"type": "keyword"},
                    "habitat": {"type": "text"},
                    "predators": {"type": "text"},
                    "average_speed_kmh": {"type": "keyword"},
                    "countries_found": {"type": "text"},
                    "conservation_status": {"type": "keyword"},
                    "family": {"type": "keyword"},
                    "gestation_period_days": {"type": "keyword"},
                    "top_speed_kmh": {"type": "keyword"},
                    "social_structure": {"type": "text"},
                    "offspring_per_birth": {"type": "keyword"}
                }
            }
        })
        print("Índice animal creado en ElasticSearch")
        return True
    else:
        print("Índice animals ya existe en ElasticSearch")
        return True

def insert_data_elastic(df):
    actions = []
    es = get_connectionElastic()
    for _, row in df.iterrows():
        doc = {
            "_index": "animals",
            "_source": {
                "name": row["Animal"],
                "height_cm": row["Height (cm)"],
                "weight_kg": row["Weight (kg)"],
                "color": row["Color"],
                "lifespan_years": row["Lifespan (years)"],
                "diet": row["Diet"],
                "habitat": row["Habitat"],
                "predators": row["Predators"],
                "average_speed_kmh": row["Average Speed (km/h)"],
                "countries_found": row["Countries Found"],
                "conservation_status": row["Conservation Status"],
                "family": row["Family"],
                "gestation_period_days": row["Gestation Period (days)"],
                "top_speed_kmh": row["Top Speed (km/h)"],
                "social_structure": row["Social Structure"],
                "offspring_per_birth": row["Offspring per Birth"]
            }
        }
        actions.append(doc)

    try:
        helpers.bulk(es, actions)
        print(f"{len(actions)} documentos insertados en ElasticSearch")
        return True
    except Exception as e:
        print(f"Error insertando en ElasticSearch: {e}")
        return False

#-------------------------------------ChromaDB-------------------------------------
chroma_collection = None

def init_chroma():
    global chroma_collection
    try:
        client = chromadb.HttpClient(host=CHROMA_ENDPOINT)
        embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=CHROMA_EMBED_MODEL
        )
        chroma_collection = client.get_or_create_collection(
            name=CHROMA_COLLECTION,
            embedding_function=embed_fn,
            metadata={"hnsw:space": "cosine"}
        )
        print(f"Colección Chroma lista: {CHROMA_COLLECTION}")
        return True
    except Exception as e:
        print(f"Error inicializando Chroma: {e}")
        return False

def upsert_data_chroma(df, batch_size=100):
    if chroma_collection is None:
        print("Colección Chroma no inicializada")
        return False
    try:
        # Prepara documentos y metadatos
        ids, docs, metas = [], [], []
        for i, row in df.iterrows():
            doc = (
                f"Animal: {row['Animal']}. Color: {row['Color']}. "
                f"Dieta: {row['Diet']}. Familia: {row['Family']}. "
                f"Hábitat: {row['Habitat']}. Predadores: {row['Predators']}. "
                f"Altura(cm): {row['Height (cm)']}, Peso(kg): {row['Weight (kg)']}. "
                f"Vida(años): {row['Lifespan (years)']}. "
                f"Velocidad prom(km/h): {row['Average Speed (km/h)']}, "
                f"Velocidad máx(km/h): {row['Top Speed (km/h)']}. "
                f"Países: {row['Countries Found']}. Conservación: {row['Conservation Status']}. "
                f"Estructura social: {row['Social Structure']}. "
                f"Gestación(días): {row['Gestation Period (days)']}. "
                f"Crias por parto: {row['Offspring per Birth']}."
            )
            meta = {
                "name": row["Animal"],
                "color": row["Color"],
                "diet": row["Diet"],
                "family": row["Family"],
                "habitat": row["Habitat"],
                "predators": row["Predators"],
                "height_cm": str(row["Height (cm)"]),
                "weight_kg": str(row["Weight (kg)"]),
                "lifespan_years": str(row["Lifespan (years)"]),
                "avg_speed_kmh": str(row["Average Speed (km/h)"]),
                "top_speed_kmh": str(row["Top Speed (km/h)"]),
                "countries_found": row["Countries Found"],
                "conservation_status": row["Conservation Status"],
                "social_structure": row["Social Structure"],
                "gestation_days": str(row["Gestation Period (days)"]),
                "offspring_per_birth": str(row["Offspring per Birth"])
            }
            ids.append(f"animal-{i}")
            docs.append(doc)
            metas.append(meta)

            if len(ids) >= batch_size:
                chroma_collection.upsert(ids=ids, documents=docs, metadatas=metas)
                ids, docs, metas = [], [], []

        if ids:
            chroma_collection.upsert(ids=ids, documents=docs, metadatas=metas)

        print("Documentos upsert en Chroma")
        return True
    except Exception as e:
        print(f"Error insertando en Chroma: {e}")
        return False

#-------------------------------------Vespa-------------------------------------

vespa_app = None
sentence_model = None

def init_vespa():
    global vespa_app, sentence_model
    try:
        sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
        print("Modelo sentence-transformers cargado para Vespa")
        
        health_url = f"{VESPA_ENDPOINT}/ApplicationStatus"
        response = requests.get(health_url, timeout=10)
        
        if response.status_code == 200:
            print(f"Vespa está disponible en: {VESPA_ENDPOINT}")
            vespa_app = {
                "endpoint": VESPA_ENDPOINT,
                "collection": VESPA_COLLECTION
            }
            return True
        else:
            print(f"Vespa no está disponible. Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"Error inicializando Vespa: {e}")
        return False


def generate_embedding_text_vespa(row):
    return (
        f"Animal: {row['Animal']}. Color: {row['Color']}. "
        f"Dieta: {row['Diet']}. Familia: {row['Family']}. "
        f"Hábitat: {row['Habitat']}. Predadores: {row['Predators']}. "
        f"Altura(cm): {row['Height (cm)']}, Peso(kg): {row['Weight (kg)']}. "
        f"Vida(años): {row['Lifespan (years)']}. "
        f"Velocidad prom(km/h): {row['Average Speed (km/h)']}, "
        f"Velocidad máx(km/h): {row['Top Speed (km/h)']}. "
        f"Países: {row['Countries Found']}. Conservación: {row['Conservation Status']}. "
        f"Estructura social: {row['Social Structure']}. "
        f"Gestación(días): {row['Gestation Period (days)']}. "
        f"Crias por parto: {row['Offspring per Birth']}."
    )

def safe_float(value):
    try:
        if isinstance(value, str):
            if '-' in value:
                parts = value.split('-')
                nums = [float(p) for p in parts if p.replace('.', '', 1).isdigit()]
                if len(nums) == 2:
                    return sum(nums) / 2
                else:
                    return None
            if value.replace('.', '', 1).isdigit():
                return float(value)
        return float(value)
    except Exception:
        return None


def insert_data_vespa(df, batch_size=100):
    if vespa_app is None or sentence_model is None:
        print("Vespa no inicializada")
        return False

    try:
        for i, row in df.iterrows():
            doc_text = generate_embedding_text_vespa(row)
            embedding = sentence_model.encode(doc_text).tolist()
            doc_id = f"animal-{i}"
            doc_url = f"{vespa_app['endpoint']}/document/v1/default/{vespa_app['collection']}/docid/{doc_id}"

            doc_payload = {
                "fields": {
                    "name": row["Animal"],
                    "color": row["Color"],
                    "diet": row["Diet"],
                    "family": row["Family"],
                    "habitat": row["Habitat"],
                    "predators": row["Predators"],
                    "height_cm": safe_float(row["Height (cm)"]) or 0.0,
                    "weight_kg": safe_float(row["Weight (kg)"]) or 0.0,
                    "lifespan_years": safe_float(row["Lifespan (years)"]) or 0.0,
                    "avg_speed_kmh": safe_float(row["Average Speed (km/h)"]) or 0.0,
                    "top_speed_kmh": safe_float(row["Top Speed (km/h)"]) or 0.0,
                    "countries_found": row["Countries Found"],
                    "conservation_status": row["Conservation Status"],
                    "social_structure": row["Social Structure"],
                    "gestation_days": safe_float(row["Gestation Period (days)"]) or 0.0,
                    "offspring_per_birth": safe_float(row["Offspring per Birth"]) or 0.0,
                    "description": doc_text,
                    "embedding": {"values": embedding}
                }
            }

            response = requests.post(
                doc_url,
                json=doc_payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            )

        print(f"Documentos insertados exitosamente en Vespa: {len(df)}")
        return True

    except Exception as e:
        print(f"Error insertando en Vespa: {e}")
        import traceback
        traceback.print_exc()
        return False
    

if __name__ == "__main__":    
    try:
        # Crear base de datos MariaDB si no existe
        conection_mariadb()
        # Ejecutar schema 
        if not execute_postgress_from_file():
            print("No se pudieron crear las tablas en PostgreSQL")
            sys.exit(1)

        elif not execute_MariaDB_from_file():
            print("No se pudieron crear las tablas en MariaDB")
            sys.exit(1)

        elif not create_index_elastic():
            print("No se pudo crear el índice en ElasticSearch")
            sys.exit(1)

        elif not init_chroma():
            print("No se pudo inicializar ChromaDB")
            sys.exit(1)

        elif not init_vespa():
            print("No se pudo inicializar Vespa")
            sys.exit(1)
        
        # Cargar dataset
        df = load_dataset()
        
        # Insertar datos
        if (insert_data_postgres(df) and insert_data_mariadb(df) 
        and insert_data_elastic(df) and upsert_data_chroma(df) and insert_data_vespa(df)):
            print("DataSeeder completado exitosamente en todas las bases")
        else:
            print("Error insertando datos")
            sys.exit(1)
            
    except Exception as e:
        print(f"Error general: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("DataSeeder terminado")
