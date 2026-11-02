# Progresso e evidências

Atualização: 02/11/2026. Estados: **A fazer → Em andamento → Em validação → Concluído**. Manter no máximo uma tarefa em andamento. Uma tarefa só é concluída quando seu critério de aceite tem evidência verificável.

| Frente | Estado | Evidência / próximo aceite |
|---|---|---|
| Origem do rastreador | Concluído | `ORIGIN.md`; dez testes originais aprovados e página inicial HTTP 200 |
| Corpus de cinco editais | Concluído | `data/manifest.json`, hashes, 55 páginas e 225 trechos |
| Busca por palavras | Concluído | Implementação e relatório de teste: Hit@3 15/15 |
| Busca semântica local | Concluído | MiniLM em CPU; relatório de teste: Hit@3 14/15 |
| API e casos de falha | Concluído | 36 testes aprovados; contratos, fontes por página e entrega do PDF |
| Avaliação final de recuperação | Concluído | `reports/test-results.json`, com 20 casos, sem notas de resposta inventadas |
| Artigo técnico | Concluído | `docs/artigo.md`, incluindo falhas de ausência de resposta |
| Interface e demonstração | Em validação | Interface consultada com TF-IDF e MiniLM; vídeo em sequência de capturas reais. Conferência pessoal de Gabriel pendente |
| Execução e avaliação do LLM | Concluído | Ollama local, 1B e 3B executados; `reports/test-rag-v2-3b.json` |
| Qualidade da geração | A fazer | 4/10 respostas corretas; três citações inadequadas e três recusas indevidas. Geração experimental, desativada por padrão |
| Revisão assistida das respostas | Concluído | 12 casos de desenvolvimento por método e 16 finais; revisão identificada como assistência de IA |
| Revisão humana independente | A fazer | Gabriel conferir respostas, fontes e gabaritos; não confundir com as notas assistidas |
| Experimento de informação ausente | Concluído | Novos conjuntos v2 congelados; 6/6 recusas corretas por regras, filtro e modelo. Resultado limitado ao conjunto |
| Domínio do projeto para entrevista | Em andamento | Gabriel explicar código, métricas, limites e uma falha, sem apoio do assistente |

## Marcos

- 02–04/11: ambiente, origem e corpus.
- 05–08/11: extração e recuperação.
- 09–11/11: geração local e tratamento de falhas.
- 12–14/11: avaliação e demonstração.
- 15–16/11: revisão dos perfis e candidatura.

As entregas de software foram antecipadas nesta implementação; os marcos continuam úteis para estudo, validação pessoal e melhorias. Não converter implementação assistida em alegação de domínio já demonstrado.

## Acompanhamento público

As [13 issues](https://github.com/ProgrammerGV/edital-inteligente/issues?q=is%3Aissue) contêm requisito, prazo, aceite e evidência. O GitHub Project não foi criado porque a autenticação disponível não possui permissão `project`. Os estados continuam registrados em cada issue e nesta página; nenhuma permissão foi ampliada automaticamente.

## Resultado da geração v2

A busca permanece como entrega principal. A integração real foi executada, mas a qualidade de resposta precisa melhorar antes de apresentar RAG completo. [Artigo e análise das falhas](rag-local.md). Os relatórios antigos e a tag `v0.1-retrieval` preservam a avaliação v1.
