const $ = id => document.getElementById(id);
function node(tag, text, cls) { const el=document.createElement(tag); if(text!==undefined)el.textContent=text; if(cls)el.className=cls; return el; }
function link(text, href) {const a=node('a',text);a.href=href;a.target='_blank';a.rel='noopener noreferrer';return a;}
let documents=[];
async function load(){
  try{
    const response=await fetch('/api/documents'); const data=await response.json(); if(!response.ok)throw new Error(data.error);
    documents=data.documents; $('count').textContent=documents.length; $('library').replaceChildren();
    for(const doc of documents){
      const option=node('option',doc.title);option.value=doc.id;$('document').append(option);
      const card=node('article',undefined,'doc-card');card.append(node('h3',doc.title));
      const meta=node('div',undefined,'doc-meta');meta.append(node('span',`${doc.pages} páginas`),link('Fonte ↗',doc.url));card.append(meta);$('library').append(card);
    }
    if(!data.semantic_installed){$('method').querySelector('[value=semantic]').disabled=true;$('method-note').textContent='Busca semântica pendente de instalação do modelo. A busca por palavras já está disponível.';}
  }catch(error){$('library').replaceChildren(node('p',error.message,'error'));$('submit').disabled=true;}
}
function showResult(data){
  const box=$('results');box.replaceChildren();
  const head=node('div',undefined,'result-head');head.append(node('strong',data.mode==='grounded_quotes'?'RESPOSTA COM CITAÇÕES':'EVIDÊNCIAS RECUPERADAS'),node('span',`${data.method==='tfidf'?'TF-IDF':'MiniLM'} · ${data.latency_ms} ms`));box.append(head,node('p',data.answer,'answer'));
  if(data.status==='needs_clarification')return;
  for(const source of data.sources){
    const card=node('article',undefined,'source');card.append(node('h3',`${source.title} · página ${source.page}`),node('p',source.text));
    const links=node('div',undefined,'source-links');links.append(link('Abrir página no PDF ↗',`/documents/${encodeURIComponent(source.document_id)}.pdf#page=${source.page}`),link('Conferir fonte oficial ↗',source.source_url),node('span',`Similaridade ${source.score.toFixed(3)}`));card.append(links);box.append(card);
  }
}
$('query-form').addEventListener('submit',async event=>{
  event.preventDefault();$('submit').disabled=true;$('results').replaceChildren(node('p','Buscando evidências… A primeira consulta semântica pode demorar mais.'));
  try{
    const response=await fetch('/api/ask',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:$('question').value,document_id:$('document').value||null,method:$('method').value,generate:$('generate').checked})});
    const data=await response.json();if(!response.ok)throw new Error(data.error||'Não foi possível concluir a consulta.');showResult(data);
  }catch(error){$('results').replaceChildren(node('p',error.message,'error'));}finally{$('submit').disabled=false;}
});
document.querySelectorAll('[data-question]').forEach(button=>button.addEventListener('click',()=>{$('question').value=button.dataset.question;$('question').focus();}));
load();
