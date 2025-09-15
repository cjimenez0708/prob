from flask import Flask, jsonify
import os

app = Flask(__name__)


@app.route("/", methods=['GET'])
def hello_world():
    return "<p>Hello, World!</p>"

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200



if __name__ == "__main__":
    app.run(host='localhost', port=5000)