import re
from ollama import chat
from compiler_service import compilar

# Módulo que fornece análise inteligente com IA: integra Ollama (modelo SLM)
# Dois modos: 1) analisar() - detecta erros no compilador e sugere correções
#            2) chat_livre() - conversa livre sem passar pelo compilador
MODEL = 'slm-compiler'


def _extrair_codigo(texto):
    # Função auxiliar: busca bloco de código markdown (```...```) na resposta da IA
    # Por quê: A resposta da IA contém explicação + código, precisamos extrair apenas o código
    match = re.search(r'```(?:\w*)\n(.*?)```', texto, re.DOTALL)
    return match.group(1).strip() if match else None


def analisar(codigo):
     # FUNÇÃO PRINCIPAL: Analisa código SLM e sugere correções usando IA
     # Lógica: Se compilação OK → responde "válido"
     #         Se compilação ERRO → envia erros para IA elaborar sugestões + código corrigido
    resultado = compilar(codigo)

    if resultado['status'] == 'ok':
        return {'resposta': '✅ Código válido! Nenhum erro encontrado.', 'codigo_corrigido': None}

    erros_fmt = '\n'.join(f'• {e}' for e in resultado['erros'])
    prompt = (
        f"O código abaixo possui erros:\n\n```\n{codigo}\n```\n\n"
        f"Erros do compilador:\n{erros_fmt}\n\n"
        "Explique os erros e forneça o código corrigido."
    )

    resposta = chat(
        model=MODEL,
        messages=[{'role': 'user', 'content': prompt}]
    ).message.content

    return {
        'resposta': resposta,
        'codigo_corrigido': _extrair_codigo(resposta)
    }


def chat_livre(mensagem):
    # FUNÇÃO: Conversa livre com IA - aceita qualquer pergunta/solicitação
    # Por quê: Modo "chat" sem restrição de compilação - para perguntas gerais sobre a linguagem/compilador
    resposta = chat(
        model=MODEL,
        messages=[{'role': 'user', 'content': mensagem}]
    ).message.content

    return {
        'resposta': resposta,
        'codigo_corrigido': _extrair_codigo(resposta)
    }


def completar(codigo):
    # FUNÇÃO: Completa código SLM usando IA
    # Por quê: Permite ao usuário escrever um trecho de código e pedir para a IA
    prompt = (
        "Continue o código abaixo respeitando as regras da linguagem.\n"
        "Retorne APENAS o trecho que vem a seguir, sem repetir o que já existe:\n\n"
        f"```\n{codigo}\n```"
    )
    resposta = chat(
        model=MODEL,
        messages=[{'role': 'user', 'content': prompt}]
    ).message.content

    return {'sugestao': _extrair_codigo(resposta) or resposta.strip()}
