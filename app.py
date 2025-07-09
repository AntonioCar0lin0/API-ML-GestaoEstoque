from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # libera o acesso ao endpoint por qualquer origem (como seu back-end Node.js)

@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({"message": "API Flask conectada com sucesso ao back-end Node.js."})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
