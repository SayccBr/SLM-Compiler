import re
from ollama import chat
from compiler_service import compilar

MODEL = 'slm-compiler'


def _extrair_codigo(texto):
    match = re.search(r'```(?:\w*)\n(.*?)```', texto, re.DOTALL)
    return match.group(1).strip() if match else None


def analisar(codigo):
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
