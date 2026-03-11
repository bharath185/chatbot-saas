"""
Minimal test app to check if Flask and basic routes work
Run this if main app.py has issues
"""

from flask import Flask, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET'])
def root():
    return jsonify({'message': 'Test API', 'status': 'running'}), 200

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200

@app.route('/api/health', methods=['GET'])
def api_health():
    return jsonify({'status': 'healthy', 'api': 'working'}), 200

@app.route('/api/test', methods=['POST'])
def test():
    return jsonify({'message': 'POST works'}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
