from flask import Flask, request, jsonify, render_template
from compiler_service import compilar
from slm import analisar

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/compilar', methods=['POST'])
def api_compilar():
    return jsonify(compilar(request.json['codigo']))

@app.route('/api/analisar', methods=['POST'])
def api_analisar():
    return jsonify(analisar(request.json['codigo']))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
