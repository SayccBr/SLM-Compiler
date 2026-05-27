import sly
from sly import Lexer, Parser

# Módulo que implementa o compilador completo usando a biblioteca SLY (Sly Lex-Yacc)
# Três componentes: MyLexer (análise léxica), MyParser (análise sintática), Interpretador (execução)

# LEXER - Análise Léxica: Transforma texto em tokens (números, palavras-chave, operadores, etc)
# Por quê: O parser precisa de tokens estruturados, não de texto bruto
class MyLexer(Lexer):
    tokens = {
        'IF', 'ELIF', 'ELSE', 'WHILE', 'FOR', 'IN', 'MATCH', 'CASE',
        'AND', 'OR', 'NOT', 'TRUE', 'FALSE',
        'INT', 'FLOAT_TYPE', 'STRING_TYPE', 'BOOL', 'LIST_TYPE',
        'IMPRIMIR', 'RANGE', 'RECEBER', 'INTEIRO', 'CONCATENAR',
        'PLUS', 'MINUS', 'STAR', 'DIVIDE', 'MOD',
        'EQ', 'NE', 'LT', 'LE', 'GT', 'GE',
        'ASSIGN', 'COLON', 'COMMA', 'LPAREN', 'RPAREN',
        'LBRACE', 'RBRACE', 'LBRACKET', 'RBRACKET',
        'NUMBER', 'FLOAT_NUMBER', 'STRING_LITERAL', 'IDENTIFIER',
        'FUNC', 'RETORNAR'
    }
    ignore = ' \t'
    ignore_comment = r'#.*'

    RESERVED = {
        'se': 'IF',
        'senaose': 'ELIF',
        'senao': 'ELSE',
        'enquanto': 'WHILE',
        'para': 'FOR',
        'em': 'IN',
        'escolha': 'MATCH',
        'caso': 'CASE',
        'e': 'AND',
        'ou': 'OR',
        'nao': 'NOT',
        'Verdadeiro': 'TRUE',
        'Falso': 'FALSE',
        'inteiro': 'INT',
        'real': 'FLOAT_TYPE',
        'texto': 'STRING_TYPE',
        'logico': 'BOOL',
        'lista': 'LIST_TYPE',
        'imprimir': 'IMPRIMIR',
        'intervalo': 'RANGE',
        'receber': 'RECEBER',
        'converter_int': 'INTEIRO',
        'concatenar': 'CONCATENAR',
        'funcao': 'FUNC',
        'retornar': 'RETORNAR'
    }

    EQ, NE, LE, GE = r'==', r'!=', r'<=', r'>='
    LT, GT, ASSIGN, PLUS, MINUS = r'<', r'>', r'=', r'\+', r'-'
    STAR, DIVIDE, MOD, COLON, COMMA = r'\*', r'/', r'%', r':', r','
    LPAREN, RPAREN = r'\(', r'\)'
    LBRACE, RBRACE = r'\{', r'\}'
    LBRACKET, RBRACKET = r'\[', r'\]'

    @_(r'\d+\.\d+')
    def FLOAT_NUMBER(self, t):
        t.value = float(t.value); return t

    @_(r'\d+')
    def NUMBER(self, t):
        t.value = int(t.value); return t

    @_(r'\"[^\"]*\"')
    def STRING_LITERAL(self, t):
        t.value = t.value[1:-1]; return t

    @_(r'[a-zA-Z_][a-zA-Z0-9_]*')
    def IDENTIFIER(self, t):
        t.type = self.RESERVED.get(t.value, 'IDENTIFIER'); return t

    @_(r'\n+')
    def newline(self, t):
        self.lineno += len(t.value)

    def error(self, t):
        char = t.value[0]
        print(f"[ERRO LEXICO] Linha {self.lineno}: Caractere ilegal '{char}'")
        print("   Dica: Caracteres válidos são números, letras, operadores (+, -, *, /, %), e símbolos (: , [ ] {{ }} ( ) = < > !)")
        self.index += 1

# PARSER
class MyParser(Parser):
    tokens = MyLexer.tokens

    # Precedência corrigida para evitar conflitos entre índices e operadores de comparação
    precedence = (
        ('left', 'OR'),
        ('left', 'AND'),
        ('right', 'NOT'),
        ('left', 'EQ', 'NE', 'LT', 'LE', 'GT', 'GE'),
        ('left', 'PLUS', 'MINUS'),
        ('left', 'STAR', 'DIVIDE', 'MOD'),
        ('right', 'UMINUS'),
        ('left', 'LBRACKET', 'LPAREN'),
    )

    @_('declaracao_lista')
    def programa(self, p): return p.declaracao_lista

    @_('declaracao_lista declaracao')
    def declaracao_lista(self, p): return p.declaracao_lista + [p.declaracao]

    @_('empty')
    def declaracao_lista(self, p): return []

    @_('comando_atribuicao', 'comando_imprimir', 'comando_if', 'comando_while',
       'comando_for', 'comando_match', 'comando_expressao', 'definicao_funcao', 'comando_retorno')
    def declaracao(self, p): return p[0]

    @_('FUNC IDENTIFIER LPAREN lista_parametros RPAREN LBRACE declaracao_lista RBRACE')
    def definicao_funcao(self, p): return ('func', p.IDENTIFIER, p.lista_parametros, p.declaracao_lista)

    @_('RETORNAR expressao COLON')
    def comando_retorno(self, p): return ('return', p.expressao)

    @_('IDENTIFIER LPAREN lista_argumentos RPAREN')
    def expressao(self, p): return ('call', p.IDENTIFIER, p.lista_argumentos)

    @_('lista_parametros COMMA IDENTIFIER')
    def lista_parametros(self, p): return p.lista_parametros + [p.IDENTIFIER]

    @_('IDENTIFIER')
    def lista_parametros(self, p): return [p.IDENTIFIER]

    @_('empty')
    def lista_parametros(self, p): return []

    @_('lista_argumentos COMMA expressao')
    def lista_argumentos(self, p): return p.lista_argumentos + [p.expressao]

    @_('expressao')
    def lista_argumentos(self, p): return [p.expressao]

    @_('empty')
    def lista_argumentos(self, p): return []

    @_('expressao COLON')
    def comando_expressao(self, p): return ('expr', p.expressao)

    @_('IDENTIFIER ASSIGN expressao COLON')
    def comando_atribuicao(self, p): return ('atrib', p.IDENTIFIER, p.expressao)

    @_('tipo IDENTIFIER ASSIGN expressao COLON')
    def comando_atribuicao(self, p): return ('atrib_tipo', p.tipo, p.IDENTIFIER, p.expressao)

    @_('IMPRIMIR expressao COLON')
    def comando_imprimir(self, p): return ('print', p.expressao)

    @_('IF expressao LBRACE declaracao_lista RBRACE elif_lista else_opt')
    def comando_if(self, p): return ('if', p.expressao, p.declaracao_lista, p.elif_lista, p.else_opt)

    @_('elif_lista ELIF expressao LBRACE declaracao_lista RBRACE')
    def elif_lista(self, p): return p.elif_lista + [('elif', p.expressao, p.declaracao_lista)]

    @_('empty')
    def elif_lista(self, p): return []

    @_('ELSE LBRACE declaracao_lista RBRACE', 'empty')
    def else_opt(self, p): return p.declaracao_lista if len(p) > 1 else None

    @_('WHILE expressao LBRACE declaracao_lista RBRACE')
    def comando_while(self, p): return ('while', p.expressao, p.declaracao_lista)

    @_('FOR IDENTIFIER IN RANGE LPAREN expressao RPAREN LBRACE declaracao_lista RBRACE')
    def comando_for(self, p): return ('for_range', p.IDENTIFIER, p.expressao, p.declaracao_lista)

    @_('MATCH expressao LBRACE case_lista RBRACE')
    def comando_match(self, p): return ('match', p.expressao, p.case_lista)

    @_('case_lista CASE expressao LBRACE declaracao_lista RBRACE')
    def case_lista(self, p): return p.case_lista + [('case', p.expressao, p.declaracao_lista)]

    @_('empty')
    def case_lista(self, p): return []

    @_('RECEBER LPAREN expressao RPAREN')
    def expressao(self, p): return ('receber', p.expressao)

    @_('INTEIRO LPAREN expressao RPAREN')
    def expressao(self, p): return ('inteiro', p.expressao)

    @_('CONCATENAR LPAREN expressao COMMA expressao RPAREN')
    def expressao(self, p): return ('concat', p.expressao0, p.expressao1)

    @_('expressao PLUS expressao', 'expressao MINUS expressao',
       'expressao STAR expressao', 'expressao DIVIDE expressao', 'expressao MOD expressao',
       'expressao EQ expressao', 'expressao NE expressao', 'expressao LT expressao',
       'expressao LE expressao', 'expressao GT expressao', 'expressao GE expressao',
       'expressao AND expressao', 'expressao OR expressao')
    def expressao(self, p): return ('binop', p[1], p.expressao0, p.expressao1)

    @_('NOT expressao', 'MINUS expressao %prec UMINUS')
    def expressao(self, p): return ('unary', p[0], p.expressao)

    @_('LPAREN expressao RPAREN')
    def expressao(self, p): return p.expressao

    @_('IDENTIFIER')
    def expressao(self, p): return ('var', p.IDENTIFIER)

    @_('NUMBER')
    def expressao(self, p): return ('int', p.NUMBER)

    @_('FLOAT_NUMBER')
    def expressao(self, p): return ('float', p.FLOAT_NUMBER)

    @_('STRING_LITERAL')
    def expressao(self, p): return ('string', p.STRING_LITERAL)

    @_('TRUE', 'FALSE')
    def expressao(self, p): return ('bool', p[0] == 'Verdadeiro')

    @_('LBRACKET lista_elementos RBRACKET')
    def expressao(self, p): return ('lista', p.lista_elementos)

    @_('expressao LBRACKET expressao RBRACKET')
    def expressao(self, p): return ('index', p.expressao0, p.expressao1)

    @_('lista_elementos COMMA expressao')
    def lista_elementos(self, p): return p.lista_elementos + [p.expressao]

    @_('expressao')
    def lista_elementos(self, p): return [p.expressao]

    @_('empty')
    def lista_elementos(self, p): return []

    @_('INT', 'FLOAT_TYPE', 'STRING_TYPE', 'BOOL', 'LIST_TYPE')
    def tipo(self, p):
        mapa_tipos = {'inteiro': 'int', 'real': 'float', 'texto': 'string', 'logico': 'bool', 'lista': 'list'}
        return mapa_tipos.get(p[0].lower(), p[0].lower())

    @_('')
    def empty(self, p): pass

    def error(self, p):
        if p:
            print(f"[ERRO PARSER] Linha {p.lineno}: Token inesperado '{p.value}'")
            print("   Dica: Verifique se falta ':' no final, ou se parênteses/chaves estão balanceados")
        else:
            print("[ERRO PARSER] Fim de arquivo inesperado")
            print("   Dica: Faltam chaves '}' ou parênteses ')' para fechar um bloco aberto")

# INTERPRETADOR - Execução: Navega pela AST e executa os comandos
# Por quê: Transforma a representação abstrata em ações concretas (calcular, imprimir, atribuir)
class Valor:
    def __init__(self, valor, tipo): self.valor, self.tipo = valor, tipo

class ReturnException(Exception):
    def __init__(self, valor): self.valor = valor

class Interpretador:
    def __init__(self):
        self.vars = {}
        self.funcoes = {}

    def executar(self, ast):
        # MÉTODO PRINCIPAL: Percorre todos os nós da AST (lista de comandos)
        # Executa cada comando sequencialmente, capturando ReturnException para funções
        if not ast: return
        try:
            for node in ast: self.executar_no(node)
        except ReturnException: pass

    def executar_no(self, node):
        # Executa um nó específico (comando, condicional, loop, etc)
        # Tipos: print, atrib (atribuição), if, while, for_range, match, func, return, expr
        if not node: return
        tag = node[0]
        if tag == 'print': print(self.avaliar(node[1]).valor)
        elif tag == 'atrib': self.vars[node[1]] = self.avaliar(node[2])
        elif tag == 'atrib_tipo':
            val = self.avaliar(node[3])
            if node[1] == 'int': val = Valor(int(val.valor), 'int')
            elif node[1] == 'float': val = Valor(float(val.valor), 'float')
            self.vars[node[2]] = val
        elif tag == 'if':
            if self.avaliar(node[1]).valor:
                for s in node[2]: self.executar_no(s)
            else:
                for e in node[3]:
                    if self.avaliar(e[1]).valor:
                        for s in e[2]: self.executar_no(s)
                        return
                if node[4]:
                    for s in node[4]: self.executar_no(s)
        elif tag == 'while':
            while self.avaliar(node[1]).valor:
                for s in node[2]: self.executar_no(s)
        elif tag == 'for_range':
            for i in range(self.avaliar(node[2]).valor):
                self.vars[node[1]] = Valor(i, 'int')
                for s in node[3]: self.executar_no(s)
        elif tag == 'match':
            v = self.avaliar(node[1]).valor
            for c in node[2]:
                if self.avaliar(c[1]).valor == v:
                    for s in c[2]: self.executar_no(s)
                    break
        elif tag == 'func':
            self.funcoes[node[1]] = (node[2], node[3])
        elif tag == 'return':
            raise ReturnException(self.avaliar(node[1]))
        elif tag == 'expr':
            self.avaliar(node[1])

    def avaliar(self, node):
        # MÉTODO CRÍTICO: Avalia uma expressão e retorna um Valor (valor + tipo)
        # Por quê: Separa avaliação de expressões da execução de comandos
        # Tipos: int, float, string, bool, var (variável), lista, index, operações, etc
        tag = node[0]
        if tag == 'int': return Valor(node[1], 'int')
        if tag == 'float': return Valor(node[1], 'float')
        if tag == 'string': return Valor(node[1], 'string')
        if tag == 'bool': return Valor(node[1], 'bool')
        if tag == 'var':
            if node[1] not in self.vars:
                raise NameError(f"Variável '{node[1]}' não foi declarada")
            return self.vars[node[1]]
        if tag == 'lista': return Valor([self.avaliar(e) for e in node[1]], 'lista')
        if tag == 'index':
            colecao = self.avaliar(node[1]).valor
            idx = self.avaliar(node[2]).valor
            item = colecao[idx]
            # Se for uma string nativa do Python, envelopa de volta na classe Valor
            if isinstance(item, str):
                return Valor(item, 'string')
            return item
        if tag == 'receber': return Valor(input(self.avaliar(node[1]).valor), 'string')
        if tag == 'inteiro': return Valor(int(self.avaliar(node[1]).valor), 'int')
        if tag == 'concat':
            return Valor(str(self.avaliar(node[1]).valor) + str(self.avaliar(node[2]).valor), 'string')
        if tag == 'binop':
            e, d = self.avaliar(node[2]).valor, self.avaliar(node[3]).valor
            op = node[1]
            if op == '+': res = e + d
            elif op == '-': res = e - d
            elif op == '*': res = e * d
            elif op == '/': res = e // d
            elif op == '%': res = e % d
            elif op == '==': res = e == d
            elif op == '!=': res = e != d
            elif op == '<': res = e < d
            elif op == '>': res = e > d
            elif op == '<=': res = e <= d
            elif op == '>=': res = e >= d
            elif op == 'e': res = e and d
            elif op == 'ou': res = e or d
            return Valor(res, 'int')
        if tag == 'unary':
            op = node[1]
            val = self.avaliar(node[2]).valor
            if op == 'nao': res = not val
            elif op == '-': res = -val
            return Valor(res, 'int' if op == '-' else 'bool')
        if tag == 'call':
            nome = node[1]
            args = [self.avaliar(a) for a in node[2]]
            if nome not in self.funcoes:
                raise NameError(f"Função '{nome}' não foi definida")
            params, corpo = self.funcoes[nome]
            old_vars = self.vars.copy()
            for p, a in zip(params, args): self.vars[p] = a
            resultado = Valor(None, 'none')
            try:
                for s in corpo: self.executar_no(s)
            except ReturnException as e:
                resultado = e.valor
            self.vars = old_vars
            # Garante que retornos booleanos puros ou objetos não quebrem a recursão
            if isinstance(resultado, Valor):
                return resultado
            elif isinstance(resultado, bool):
                return Valor(resultado, 'bool')
            else:
                return Valor(resultado, 'none')

import sys
from io import StringIO

def executar_codigo_web(codigo_fonte):
    # FUNÇÃO AUXILIAR: Executa o compilador completo e captura toda saída (print, erros)
    # Usada alternativamente quando compiler_service.py não está disponível
    # Retorna: string com toda a saída + mensagens de erro do interpretador
    """Executa o interpretador e captura tudo o que ele printar"""
    lexer = MyLexer()
    parser = MyParser()
    interp = Interpretador()

    # Redireciona o print do terminal para uma variável string
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()

    try:
        ast = parser.parse(lexer.tokenize(codigo_fonte))
        if ast:
            interp.executar(ast)
        else:
            print("[ERRO PARSER] Árvore vazia - existem erros lexicais/sintáticos acima")
    except ZeroDivisionError as e:
        print("[ERRO SEMANTICA] Divisão por zero!")
        print("   Dica: Verifique a operação de divisão (/) - denominador não pode ser 0")
    except IndexError as e:
        print("[ERRO SEMANTICA] Índice inválido em lista!")
        print("   Dica: Tentou acessar uma posição que não existe na lista")
    except NameError as e:
        print(f"[ERRO SEMANTICA] {str(e)}")
        print("   Dica: Certifique-se de que a variável/função foi declarada antes de usar")
    except Exception as e:
        print(f"[ERRO SEMANTICA] {str(e)}")
    finally:
        # Restaura o terminal original
        sys.stdout = old_stdout

    return redirected_output.getvalue()