from flask import Flask, request, jsonify, render_template
from compiler_service import compilar
from slm import analisar, chat_livre, completar

# Servidor web Flask que atua como orquestrador central, roteiando requisições HTTP para os serviços
# de compilação (executa código SLM) e análise inteligente (sugere correções via IA)
app = Flask(__name__)

@app.route('/')
def index():
    # Retorna a página principal da interface web
    return render_template('index.html')

@app.route('/api/compilar', methods=['POST'])
def api_compilar():
    # Endpoint que recebe código SLM, executa o compilador (lexer → parser → interpretador)
    # e retorna status, erros ou saída de execução
    return jsonify(compilar(request.json['codigo']))

@app.route('/api/analisar', methods=['POST'])
def api_analisar():
    # Endpoint que usa IA (Ollama) para analisar erros encontrados na compilação
    # e retorna explicação dos problemas + código corrigido (se detectado)
    return jsonify(analisar(request.json['codigo']))

@app.route('/api/chat', methods=['POST'])
def api_chat():
    # Endpoint de conversa livre com IA - recebe qualquer pergunta/solicitação
    # e delega direto para o modelo Ollama sem passar pelo compilador
    return jsonify(chat_livre(request.json['mensagem']))

@app.route('/api/completar', methods=['POST'])
def api_completar():
    # Endpoint que usa IA (Ollama) para completar código
    return jsonify(completar(request.json['codigo']))

if __name__ == '__main__':
    app.run(debug=True, port=5000)
