import sys
from io import StringIO
from Compiler import MyLexer, MyParser, Interpretador


def _capturar(fn):
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
