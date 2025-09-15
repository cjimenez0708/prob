from flask import Flask, jsonify
import chromadb
from chromadb.utils import embedding_functions
from os import getenv
import sys

# Variables de entorno
CHROMA_ENDPOINT = getenv("CHROMA_ENDPOINT", "http://localhost:8000")
CHROMA_COLLECTION = getenv("CHROMA_COLLECTION", "animals")
CHROMA_EMBED_MODEL = getenv("CHROMA_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

app = Flask(__name__)
chroma_collection = None

def init_chroma():
    global chroma_collection
    try:
        host = CHROMA_ENDPOINT.replace("http://", "").replace("https://", "").split(":")[0]
        client = chromadb.HttpClient(host=host, port=8000)
        
        embed_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=CHROMA_EMBED_MODEL
        )
        chroma_collection = client.get_or_create_collection(
            name=CHROMA_COLLECTION,
            embedding_function=embed_fn,
            metadata={"hnsw:space": "cosine"}
        )
        print(f"Colección Chroma inicializada: {CHROMA_COLLECTION}")
        return True
    except Exception as e:
        print(f"Error inicializando Chroma: {e}")
        return False

def get_collection():
    global chroma_collection
    if not chroma_collection:
        if not init_chroma():
            return None
    return chroma_collection

# list animals 
@app.route("/animales", methods=["GET"])
def get_animales():
    try:
        collection = get_collection()
        if not collection:
            return jsonify({"error": "No se pudo conectar a ChromaDB"}), 500
        
        results = collection.get(include=["metadatas"])
        
        animales = []
        for metadata in results["metadatas"]:
            animales.append({
                "nombre": metadata.get("name", "N/A")
            })
        
        return jsonify(animales)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# list colors with animals 
@app.route("/colores", methods=["GET"])
def get_colores():
    try:
        collection = get_collection()
        if not collection:
            return jsonify({"error": "No se pudo conectar a ChromaDB"}), 500
        
        results = collection.get(include=["metadatas"])
        
        colores_dict = {}
        for metadata in results["metadatas"]:
            color = metadata.get("color", "N/A")
            nombre = metadata.get("name", "N/A")
            
            if color not in colores_dict:
                colores_dict[color] = []
            colores_dict[color].append(nombre)
        
        colores_list = []
        for color, animales_list in colores_dict.items():
            colores_list.append({
                "color": color,
                "animals": ", ".join(animales_list)  
            })
        
        return jsonify(colores_list)
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# HEALTH CHECK ENDPOINT
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

if __name__ == "__main__":
    init_chroma()
    app.run(host='localhost', port=5000)