import sys
from io import StringIO
from Compiler import MyLexer, MyParser, Interpretador

# Módulo que orquestra o pipeline de compilação: tokenização (lexer) → parsing (parser) → execução (interpretador)
# Captura erros em cada etapa e retorna status + mensagens para o front-end

def _capturar(fn):
    # Função auxiliar que executa uma função capturando sua saída (stdout/stderr), resultado e exceções
    # Por quê: permite isolar erros do compilador sem quebrar o servidor
    buf = StringIO()
    old = sys.stdout, sys.stderr
    sys.stdout = sys.stderr = buf
    result, exc = None, None
    try:
        result = fn()
    except Exception as e:
        exc = e
    finally:
        sys.stdout, sys.stderr = old
    return result, buf.getvalue(), exc


def compilar(codigo):
    # FUNÇÃO PRINCIPAL: Executa o pipeline completo do compilador
    # Etapas: 1) Lexer tokeniza o código em tokens
    #         2) Parser constrói árvore de sintaxe abstrata (AST)
    #         3) Interpretador executa a AST
    # Retorna: { status: 'ok'|'erro', erros: [], saida: string }
    lexer, parser = MyLexer(), MyParser()

    tokens, saida, _  = _capturar(lambda: list(lexer.tokenize(codigo)))
    erros = [l for l in saida.splitlines() if l.strip()]

    ast, saida, _ = _capturar(lambda: parser.parse(iter(tokens)))
    erros += [l for l in saida.splitlines() if l.strip()]

    if erros or not ast:
        return {'status': 'erro', 'erros': erros or ['[ERRO] Código inválido'], 'saida': ''}

    _, saida, exc = _capturar(lambda: Interpretador().executar(ast))

    erros_exec = [l for l in saida.splitlines() if '[ERRO' in l]
    saida_ok   = '\n'.join(l for l in saida.splitlines() if '[ERRO' not in l)

    if exc:
        erros_exec.append(f'[ERRO SEMANTICA] {exc}')

    if erros_exec:
        return {'status': 'erro', 'erros': erros_exec, 'saida': ''}

    return {'status': 'ok', 'erros': [], 'saida': saida_ok}
