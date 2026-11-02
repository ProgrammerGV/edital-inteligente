# Progresso e evidências

Atualização: 02/11/2026. Estados: **A fazer → Em andamento → Em validação → Concluído**. Manter no máximo uma tarefa em andamento. Uma tarefa só é concluída quando seu critério de aceite tem evidência verificável.

| Frente | Estado | Evidência / próximo aceite |
|---|---|---|
| Origem do rastreador | Concluído | `ORIGIN.md`; dez testes originais aprovados e página inicial HTTP 200 |
| Corpus de cinco editais | Concluído | `data/manifest.json`, hashes, 55 páginas e 225 trechos |
| Busca por palavras | Concluído | Implementação e relatório de teste: Hit@3 15/15 |
| Busca semântica local | Concluído | MiniLM em CPU; relatório de teste: Hit@3 14/15 |
| API e casos de falha | Concluído | 23 testes aprovados; contratos e fontes por página |
| Avaliação final | Concluído | `reports/test-results.json`, com 20 casos, sem notas de resposta inventadas |
| Artigo técnico | Concluído | `docs/artigo.md`, incluindo falhas de ausência de resposta |
| Interface e demonstração | Em validação | Conferir consulta real, fonte e comportamento sem modelo |
| Geração com Llama 3.2 | A fazer | Ollama não instalado; executar integração real e avaliar relevância das citações |
| Revisão humana das respostas | A fazer | Depende de geração real; preencher corretude e sustentação, sem presumir notas |
| Detecção de informação ausente | A fazer | Criar novos exemplos de desenvolvimento e um novo conjunto final antes de ajustar |
| Domínio do projeto para entrevista | Em andamento | Gabriel explicar código, métricas, limites e uma falha, sem apoio do assistente |

## Marcos

- 02–04/11: ambiente, origem e corpus.
- 05–08/11: extração e recuperação.
- 09–11/11: geração local e tratamento de falhas.
- 12–14/11: avaliação e demonstração.
- 15–16/11: revisão dos perfis e candidatura.

As entregas de software foram antecipadas nesta implementação; os marcos continuam úteis para estudo, validação pessoal e melhorias. Não converter implementação assistida em alegação de domínio já demonstrado.
