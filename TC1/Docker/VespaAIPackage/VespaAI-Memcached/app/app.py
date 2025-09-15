from flask import Flask, jsonify
import os
from vespa.application import Vespa

app = Flask(__name__)



@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200




if __name__ == "__main__":
    app.run(host='localhost', port=5000)