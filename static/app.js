let codigoCorrigido = null;

const editor     = document.getElementById('editor');
const painelResp = document.getElementById('resposta');
const btnAplicar = document.getElementById('btn-aplicar');
const badge      = document.getElementById('status-badge');

function setBadge(estado, texto) {
    badge.className = `badge ${estado}`;
    badge.textContent = texto;
}

function setLoading(sim) {
    document.querySelectorAll('button').forEach(b => b.disabled = sim);
    if (sim) {
        painelResp.className = '';
        painelResp.textContent = 'Processando...';
        setBadge('load', 'aguardando');
    }
}

async function post(rota) {
    const res = await fetch(rota, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ codigo: editor.value })
    });
    return res.json();
}

async function compilar() {
    setLoading(true);
    const data = await post('/api/compilar');

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

async function analisar() {
    setLoading(true);
    const data = await post('/api/analisar');

    painelResp.className = '';
    painelResp.textContent = data.resposta;
    codigoCorrigido = data.codigo_corrigido;

    btnAplicar.style.display = codigoCorrigido ? 'inline-block' : 'none';
    setBadge(codigoCorrigido ? 'erro' : 'ok', codigoCorrigido ? 'corrigido' : 'ok');
    setLoading(false);
}

function aplicar() {
    if (codigoCorrigido) {
        editor.value = codigoCorrigido;
        btnAplicar.style.display = 'none';
        setBadge('ok', 'aplicado');
    }
}
