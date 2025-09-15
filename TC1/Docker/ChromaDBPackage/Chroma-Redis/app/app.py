from flask import Flask, jsonify
import os
import chromadb

app = Flask(__name__)

CHROMA_URL = os.getenv("CHROMA_URL", "http://databases-chromadb:8000")

@app.route("/", methods=['GET'])
def hello_world():
    DATA=os.getenv('PROMETHEUSENDPOINT')
    return "<p>Hello, "+ DATA +"World!</p>"

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

@app.route("/chromadb", methods=['GET'])
def chroma():
    client = chromadb.HttpClient(
    host="databases-chromadb",  # nombre del servicio Kubernetes
    port=8000
    )
    # Crear colección de prueba
    collection = client.get_or_create_collection(name="coleccion_prueba2")
    return jsonify({"coleccion": collection.name})

@app.route("/colecciones", methods=['GET'])
def listar_colecciones():
    client = chromadb.HttpClient(
        host="databases-chromadb",
        port=8000
    )

    # Obtener todas las colecciones
    colecciones = client.list_collections()

    # Extraer solo los nombres
    nombres = [c.name for c in colecciones]

    return jsonify({"colecciones": nombres})


if __name__ == "__main__":
    app.run(host='localhost', port=5000)