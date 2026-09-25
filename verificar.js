#!/usr/bin/env node
/*
 * Verificação automática do projeto Jarvis.
 * Roda sozinha a cada atualização no GitHub (via GitHub Actions, de graça
 * para repositórios públicos) e confere, antes de publicar:
 *   1) se o JavaScript dentro de index.html e baixar.html tem sintaxe válida
 *      (evita que o app pare de funcionar por um erro de digitação no código);
 *   2) se manifest.json é um JSON válido;
 *   3) se, quando index.html muda, a versão do cache em sw.js também foi
 *      atualizada — senão o celular/computador pode ficar "preso" numa
 *      versão antiga do app mesmo depois de publicar a nova (o efeito de
 *      "travado"/desatualizado que já aconteceu neste projeto).
 * Não precisa de nenhuma conta, chave ou serviço pago: só usa o Node.js que
 * o próprio GitHub Actions já tem instalado.
 */
const fs = require('fs');
const path = require('path');
const vm = require('vm');
const { execSync } = require('child_process');

const ROOT = path.join(__dirname, '..');
let erros = 0;
let avisos = 0;

function erro(msg){ console.error('❌ ' + msg); erros++; }
function aviso(msg){ console.warn('⚠️  ' + msg); avisos++; }
function ok(msg){ console.log('✅ ' + msg); }

function extrairScripts(html){
  const scripts = [];
  const re = /<script(?![^>]*\bsrc=)[^>]*>([\s\S]*?)<\/script>/gi;
  let m;
  while ((m = re.exec(html))) scripts.push(m[1]);
  return scripts;
}

function checarSintaxeJS(arquivo){
  const caminho = path.join(ROOT, arquivo);
  if (!fs.existsSync(caminho)){ aviso(`${arquivo} não encontrado, pulando.`); return; }
  const html = fs.readFileSync(caminho, 'utf8');
  const scripts = extrairScripts(html);
  if (!scripts.length){ aviso(`${arquivo}: nenhum <script> inline encontrado.`); return; }
  scripts.forEach((code, i) => {
    if (!code.trim()) return;
    try{
      new vm.Script(code, { filename: `${arquivo}#script${i + 1}` });
      ok(`${arquivo}: script ${i + 1} com sintaxe válida.`);
    }catch(e){
      erro(`${arquivo}: erro de sintaxe no script ${i + 1} — ${e.message}`);
    }
  });
}

function checarJSON(arquivo){
  const caminho = path.join(ROOT, arquivo);
  if (!fs.existsSync(caminho)){ aviso(`${arquivo} não encontrado, pulando.`); return; }
  try{
    JSON.parse(fs.readFileSync(caminho, 'utf8'));
    ok(`${arquivo}: JSON válido.`);
  }catch(e){
    erro(`${arquivo}: JSON inválido — ${e.message}`);
  }
}

function versaoAnteriorDe(arquivo){
  try{ return execSync(`git show HEAD^:${arquivo}`, { cwd: ROOT, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }); }
  catch{ return null; }
}

function checarCacheAtualizado(){
  const caminhoSw = path.join(ROOT, 'sw.js');
  const caminhoHtml = path.join(ROOT, 'index.html');
  if (!fs.existsSync(caminhoSw) || !fs.existsSync(caminhoHtml)){
    aviso('sw.js ou index.html não encontrados, pulando checagem de cache.');
    return;
  }
  const swAtual = fs.readFileSync(caminhoSw, 'utf8');
  const htmlAtual = fs.readFileSync(caminhoHtml, 'utf8');
  const swAnterior = versaoAnteriorDe('sw.js');
  const htmlAnterior = versaoAnteriorDe('index.html');
  if (swAnterior === null || htmlAnterior === null){
    aviso('Sem commit anterior para comparar (primeiro commit ou histórico raso) — pulando checagem de cache.');
    return;
  }
  const versaoAtual = (swAtual.match(/CACHE\s*=\s*['"]([^'"]+)['"]/) || [])[1];
  const versaoAnterior = (swAnterior.match(/CACHE\s*=\s*['"]([^'"]+)['"]/) || [])[1];
  const htmlMudou = htmlAtual !== htmlAnterior;
  const versaoMudou = versaoAtual !== versaoAnterior;
  if (htmlMudou && !versaoMudou){
    erro('index.html mudou nesta atualização, mas a versão do cache em sw.js continua a mesma ' +
      `(${versaoAtual || '?'}). Sem isso, o app instalado pode ficar preso na versão antiga. ` +
      'Aumente o número em `const CACHE = \'jarvis-vN\';` dentro de sw.js.');
  } else if (htmlMudou && versaoMudou){
    ok(`sw.js: versão do cache foi atualizada (${versaoAnterior || '?'} → ${versaoAtual || '?'}).`);
  } else {
    ok('sw.js: index.html não mudou nesta atualização, versão do cache não precisava mudar.');
  }
}

console.log('— Verificação automática do Jarvis —\n');
checarSintaxeJS('index.html');
checarSintaxeJS('baixar.html');
checarJSON('manifest.json');
checarCacheAtualizado();

console.log(`\nResumo: ${erros} erro(s), ${avisos} aviso(s).`);
if (erros > 0){
  console.error('\nA verificação falhou. Corrija os erros acima antes de publicar.');
  process.exit(1);
}
console.log('\nTudo certo — pode publicar com tranquilidade.');
