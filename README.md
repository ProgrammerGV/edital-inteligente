# Edital Inteligente

**Consulte editais públicos e confira as páginas que sustentam cada resultado.**

Aplicação local de IA aplicada: ingestão de PDFs, recuperação por TF-IDF e embeddings multilíngues, avaliação reproduzível e integração opcional com um LLM local. Evolução do [rastreador de editais](https://github.com/ProgrammerGV/INF032-Programa-o_Python/tree/main/projeto/rastreador-editais), por Gabriel Vinicius.

![Consulta real na aplicação](docs/demo.png)

## O que já faz

- Consulta cinco PDFs oficiais, com extração por página, URL e hash da versão utilizada.
- Compara busca por palavras (TF-IDF) e por significado (MiniLM multilíngue).
- Mostra trechos e abre a página física correspondente no PDF.
- Mantém a busca disponível quando a geração local não está operacional.
- Avalia recuperação e latência com dez perguntas de desenvolvimento e vinte de teste.

**Estado: busca avaliada e geração experimental.** Ollama com Llama 3.2 3B foi executado localmente, após experimentos com o 1B. No teste reservado, respondeu corretamente a **4/10 perguntas respondíveis**; apresentou três citações inadequadas e recusou outras três perguntas válidas. Recusou os **6/6 casos sem resposta**. A busca permanece como modo principal; a geração exige ativação e melhorias antes de ser apresentada como RAG completo. Veja a [avaliação, os erros e as latências](docs/rag-local.md). Foram integrados modelos pré-treinados; não foi treinado um LLM próprio.

## Executar no Windows

Requer Python 3.12+ com `python --version` funcional. O primeiro preparo instala dependências e baixa os PDFs; a opção semântica também baixa um modelo. Não há uso de API paga.

```powershell
# Na raiz do repositório:
.\scripts\start.ps1 -Semantic
# Abra http://127.0.0.1:5000
```

Caso o PowerShell bloqueie scripts, use os comandos Python abaixo, sem alterar políticas de segurança.

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-semantic.txt
.\.venv\Scripts\python scripts/download_corpus.py
.\.venv\Scripts\python scripts/build_corpus.py
.\.venv\Scripts\python scripts/download_model.py
.\.venv\Scripts\python app.py
```

Se um servidor de origem apresentar cadeia de certificados incompatível com o Python, use o download HTTPS nativo do Windows, mantendo a validação de certificados:

```powershell
New-Item -ItemType Directory -Force data/pdfs | Out-Null
Get-Content data/manifest.json -Raw | ConvertFrom-Json | ForEach-Object {
  Invoke-WebRequest -Uri $_.url -OutFile (Join-Path data/pdfs ($_.id + '.pdf'))
}
.\.venv\Scripts\python scripts/download_corpus.py
.\.venv\Scripts\python scripts/build_corpus.py
```

Depois do preparo, a aplicação não precisa de internet: o carregamento semântico usa arquivos locais. Para usar somente TF-IDF, instale `requirements.txt` e omita o download do modelo. O corpus extraído e os cinco PDFs oficiais do snapshot avaliado acompanham o código.

### Demonstração em servidor gratuito

O Blueprint `render.yaml` do [repositório do portfólio](https://github.com/ProgrammerGV/programmergv.github.io) prepara a versão TF-IDF, sem instalar MiniLM ou Ollama. O servidor lê a porta `PORT` e aceita `EDITAL_BIND_HOST=0.0.0.0` no ambiente de hospedagem; o padrão local continua em loopback. A demonstração está publicada em https://programmergv-edital-inteligente.onrender.com/ no plano Free, com busca TF-IDF e os cinco PDFs. O primeiro acesso após inatividade pode demorar enquanto o servidor desperta.

## Geração opcional

Instale [Ollama pela fonte oficial](https://ollama.com/download). Em outro terminal, mantenha o servidor local ativo:

```powershell
$env:OLLAMA_NO_CLOUD='1'
ollama serve
```

Com o serviço ativo, prepare o modelo e confira a disponibilidade:

```powershell
ollama pull llama3.2:3b
.\.venv\Scripts\python scripts/doctor.py
.\.venv\Scripts\python app.py
```

Se o aplicativo Ollama já estiver servindo a API local, não inicie uma segunda instância. A interface informa a disponibilidade e permite marcar “Consultar modelo local” para testar a geração experimental. A integração usa exclusivamente `127.0.0.1:11434`, sem envio a APIs externas. O download do 3B ocupa cerca de 2 GB; dependências, embeddings e runtime exigem espaço adicional. Na instalação portátil preparada nesta sessão, `../Iniciar.ps1` utiliza o runtime e os modelos em `work/`.

O modelo 1B é uma alternativa experimental com qualidade inferior observada no desenvolvimento: configure `$env:EDITAL_OLLAMA_MODEL='llama3.2:1b'` antes de iniciar a aplicação, após baixá-lo. Não misturar os resultados dos dois modelos.

Para limitar afirmações não sustentadas, o modelo gera JSON com um ID de evidência; o backend converte esse ID na citação literal. Cada trecho precisa existir na página recuperada e citar um ID válido. Não é uma síntese livre. Essa validação não garante que a citação seja relevante ou suficiente para responder; a conferência humana continua necessária. Há recusas por regras explícitas de escopo, por ausência de candidato apropriado e pelo próprio modelo, registradas separadamente.

## Arquitetura

```mermaid
flowchart LR
    A[PDFs oficiais + manifesto] --> B[Extração por página]
    B --> C[Trechos sobrepostos]
    C --> D[TF-IDF]
    C --> E[MiniLM local]
    Q[Pergunta + documento] --> D
    Q --> E
    D --> F[Top 3 páginas]
    E --> F
    F --> G[Interface com fontes]
    F --> J[Texto das páginas e 4 candidatos reranqueados]
    J --> H[Ollama local: ID ou recusa]
    H --> I[Validação de citação literal]
    I --> G
```

Não há OCR, treinamento de LLM, seleção automática de retificações ou validação de elegibilidade de candidatos. Há páginas com fontes/codificações imperfeitas e tabelas cuja ordem é prejudicada pela extração. Sempre conferir o PDF original e o órgão responsável.

## API

- `GET /api/documents`: documentos e disponibilidade dos arquivos do modelo semântico.
- `POST /api/ask`: `question` (5–600 caracteres), `method` (`tfidf` ou `semantic`), `document_id` opcional e `generate` booleano.
- Resposta: `answer`, `status`, `mode`, `sources`, `claims`, `generation_attempted` e `latency_ms`.
- `GET /documents/<id>.pdf`: PDF local; a interface usa `#page=N`.
- Sem modelo semântico: HTTP 503 explícito, sem substituição silenciosa do método. Sem geração: fontes preservadas e estado `generation_unavailable`.

Exemplo:

```json
{"question":"Qual é o valor mensal da bolsa?","document_id":"ifba-dgcom-2025","method":"tfidf","generate":false}
```

## Testes e avaliação

```powershell
python -m pip install -r requirements-dev.txt
python -m pytest -q
python scripts/evaluate.py --split dev
python scripts/evaluate.py --split test
# Nova avaliação de geração: nomes próprios, sem substituir os relatórios v1.
python scripts/evaluate_rag.py --split dev-v2 --methods tfidf --output minha-execucao-dev.json
python scripts/evaluate_rag.py --split test-v2 --methods tfidf --output minha-execucao-test.json
```

Consulte [o protocolo](evaluation/README.md), o [versionamento dos experimentos](evaluation/versioning.md), os [relatórios reais](reports/) e o [artigo técnico v1](docs/artigo.md). Similaridade não é probabilidade de correção. Hit@3 mede recuperação de página, não acerto da resposta. A avaliação v2 registra revisão assistida, identificada como tal; revisão humana independente permanece pendente.

O servidor local usa Waitress e escuta apenas em loopback. Docker é uma alternativa para o modo TF-IDF (`docker build -t edital-inteligente .` e `docker run --rm -p 127.0.0.1:5000:5000 edital-inteligente`). A imagem não inclui MiniLM nem Ollama; esse caminho não substitui a avaliação local.

## Origem, progresso e limites

- [Origem e atribuição](ORIGIN.md)
- [Progresso e critérios de aceite](docs/progresso.md)
- [Roteiro de demonstração](docs/demo.md)
- [Modelo de embeddings](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2) — parâmetros pré-treinados, não treinamento próprio.


## GitHub Actions

Os testes são executados automaticamente em pushes e pull requests para `main`. Consulte [CI e publicação](docs/cicd.md) para o funcionamento e o estado da integração com o Render.
