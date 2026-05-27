let codigoCorrigido = null;
let modo = 'codigo'; // 'codigo' | 'texto'

// Interface frontal com dois painéis: editor (esquerda) e resposta (direita)
// Captura elementos DOM para manipulação e oferece dois modos: compilação ou conversa com IA
const editor     = document.getElementById('editor');
const painelResp = document.getElementById('resposta');
const btnAplicar = document.getElementById('btn-aplicar');
const btnCompilar = document.getElementById('btn-compilar');
const badge      = document.getElementById('status-badge');

const PLACEHOLDER = {
    codigo: '# Escreva seu código aqui...\ninteiro x = 10:\nimprimir x:',
    texto:  'Exemplos:\n— "Quais são os tokens dessa linguagem?"\n— "Faça uma função fibonacci recursiva"\n— "Estou tendo erro nesse código: [cole aqui]"\n— "Me explique como o compiler funciona"'
};

function setModo(novo) {
    // FUNÇÃO: Alterna entre modo "código" (compilação) e "texto" (chat com IA)
    // Por quê: Mesma interface, mas comportamentos radicalmente diferentes
    modo = novo;
    document.getElementById('tab-codigo').className = novo === 'codigo' ? 'ativo' : '';
    document.getElementById('tab-texto').className  = novo === 'texto'  ? 'ativo' : '';
    btnCompilar.style.display = novo === 'codigo' ? 'inline-block' : 'none';
    document.getElementById('btn-slm').textContent = novo === 'codigo' ? '⬡ Analisar SLM' : '⬡ Enviar';
    editor.className   = novo === 'texto' ? 'texto' : '';
    editor.placeholder = PLACEHOLDER[novo];
    editor.value = '';
    resetResposta();
}

function setBadge(estado, texto) {
    // Atualiza o badge de status (ok/erro/aguardando) no topo da página
    badge.className = `badge ${estado}`;
    badge.textContent = texto;
}

function resetResposta() {
    // Limpa o painel de resposta - volta ao estado inicial
    painelResp.className = '';
    painelResp.textContent = 'Pronto.';
    btnAplicar.style.display = 'none';
    codigoCorrigido = null;
}

function setLoading(sim) {
    // Ativa/desativa modo loading - desabilita botões e mostra "Processando..."
    // Por quê: Evita cliques múltiplos enquanto aguarda resposta do servidor
    document.querySelectorAll('button').forEach(b => b.disabled = sim);
    if (sim) {
        painelResp.className = '';
        painelResp.textContent = 'Processando...';
        setBadge('load', 'aguardando');
    }
}

async function post(rota, body) {
    // Função auxiliar: faz requisição POST JSON para o servidor
    // Por quê: Centraliza lógica de comunicação, facilita mudança de formato
    const res = await fetch(rota, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    return res.json();
}

async function compilar() {
    // FUNÇÃO: Envia código para compilação no servidor
    // Etapas: 1) Ativa loading 2) POST /api/compilar 3) Exibe resultado (ok ou erros)
    setLoading(true);
    const data = await post('/api/compilar', { codigo: editor.value });

    if (data.status === 'ok') {
        painelResp.className = 'ok';
        painelResp.textContent = data.saida || '✅ Compilado com sucesso!';
        setBadge('ok', 'ok');
    } else {
        painelResp.className = 'erro';
        painelResp.textContent = data.erros.join('\n');
        setBadge('erro', 'erro');
    }

    btnAplicar.style.display = 'none';
    codigoCorrigido = null;
    setLoading(false);
}

// Unifica analisar (código) e chat livre (texto)
async function enviar() {
    // FUNÇÃO PRINCIPAL: Rota unificada para análise de código OU conversa com IA
    // Lógica: if modo === 'codigo' → /api/analisar (com compilação)
    //         else → /api/chat (sem compilação)
    setLoading(true);

    const rota = modo === 'codigo' ? '/api/analisar' : '/api/chat';
    const body = modo === 'codigo'
        ? { codigo: editor.value }
        : { mensagem: editor.value };

    const data = await post(rota, body);

    painelResp.className = '';
    painelResp.textContent = data.resposta;
    codigoCorrigido = data.codigo_corrigido;
    btnAplicar.style.display = codigoCorrigido ? 'inline-block' : 'none';
    setBadge(codigoCorrigido ? 'erro' : 'ok', codigoCorrigido ? 'corrigido' : 'ok');
    setLoading(false);
}

function aplicar() {
    // Aplicar código corrigido sugerido pela IA ao editor
    // Por quê: Permite o usuário copiar sugestão com um clique
    if (!codigoCorrigido) return;

    // Atualiza visual para modo código SEM chamar setModo (que limpa o editor)
    modo = 'codigo';
    document.getElementById('tab-codigo').className = 'ativo';
    document.getElementById('tab-texto').className  = '';
    btnCompilar.style.display = 'inline-block';
    document.getElementById('btn-slm').textContent  = '⬡ Analisar SLM';
    editor.className   = '';
    editor.placeholder = PLACEHOLDER['codigo'];

    editor.value = codigoCorrigido;
    btnAplicar.style.display = 'none';
    codigoCorrigido = null;
    setBadge('ok', 'aplicado');
}