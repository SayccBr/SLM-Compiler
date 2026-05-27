# SLM Compiler Assistant

Assistente de código local para uma linguagem de programação customizada em português, construída com [SLY](https://github.com/dabeaz/sly). Roda inteiramente offline via [Ollama](https://ollama.com) e expõe uma interface web simples via Flask.

---

## Estrutura do projeto

```
projeto/
├── Compiler.py           # Lexer, Parser e Interpretador (SLY)
├── Modelfile             # Configuração do modelo Ollama
├── app.py                # Servidor Flask — só rotas
├── compiler_service.py   # Wrapper do Compiler.py
├── slm.py                # Comunicação com o Ollama
├── requirements.txt
├── PIPELINE              # Diagrama do fluxo de requisições e integração
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── app.js
```

---

## Como funciona

### Pipeline

```
Browser
  │
  ├── POST /api/compilar  →  compiler_service.py
  │                               Lexer → Parser → Interpretador
  │                               retorna { status, saida, erros }
  │
  ├── POST /api/analisar  →  slm.py → analisar()
  │                               1. Roda o compiler primeiro
  │                               2. Se houver erro, monta prompt com o output do compiler
  │                               3. Envia para o modelo Ollama
  │                               retorna { resposta, codigo_corrigido }
  │
  └── POST /api/chat      →  slm.py → chat_livre()
                                  Envia a mensagem direta ao modelo (sem compilar)
                                  retorna { resposta, codigo_corrigido }
```

### Modos da interface

| Modo | Botões disponíveis | O que acontece |
|---|---|---|
| **código** | ▶ Compilar, ⬡ Analisar SLM | Compilar executa sem SLM. Analisar roda o compiler e passa os erros para o SLM. |
| **texto** | ⬡ Enviar | Mensagem em linguagem natural vai direto para o SLM sem passar pelo compiler. |

O botão **✓ Aplicar correção** aparece sempre que o SLM retornar um bloco de código na resposta — em qualquer modo. Ao clicar, o código corrigido é colocado no editor no modo código.

---

## Setup

### 1. Instalar dependências

```bash
pip install -r requirements.txt
```

### 2. Instalar e iniciar o Ollama

Baixe em [ollama.com](https://ollama.com) e instale normalmente.

```bash
# Baixar o modelo base
ollama pull qwen2.5-coder:7b
```

### 3. Criar o modelo customizado

```bash
ollama create slm-compiler -f Modelfile
```

Só precisa rodar esse comando uma vez. Se você editar o `Modelfile`, rode novamente para atualizar o modelo.

### 4. Rodar a aplicação

```bash
python app.py
```

Acesse [http://localhost:5000](http://localhost:5000).

---

## A linguagem

Linguagem 100% em português com sintaxe de blocos em `{ }` e `:` ao final de declarações simples.

```
# Tipos: inteiro, real, texto, logico, lista

funcao fatorial(n) {
    se n <= 1 {
        retornar 1:
    }
    retornar n * fatorial(n - 1):
}

imprimir fatorial(5):
```

Palavras-chave: `se` `senaose` `senao` `enquanto` `para` `em` `intervalo` `escolha` `caso` `funcao` `retornar` `imprimir` `receber` `converter_int` `concatenar`

---

## Tecnologias

| Camada | Tecnologia |
|---|---|
| Linguagem / Compilador | Python + SLY |
| Modelo de linguagem | qwen2.5-coder:7b via Ollama |
| Backend | Flask |
| Frontend | HTML + CSS + JS (vanilla) |
