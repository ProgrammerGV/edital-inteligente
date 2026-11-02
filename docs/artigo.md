# Quando a busca por palavras supera embeddings: um experimento com editais

**Gabriel Vinicius · 2 de novembro de 2026**

> Este artigo registra a versão v1 de recuperação, preservada em `v0.1-retrieval`. A integração local foi executada posteriormente e tem [avaliação própria na v2](rag-local.md); os números e as pendências descritos abaixo pertencem ao experimento original.

Encontrar um edital é diferente de encontrar a informação certa dentro dele. A partir de um rastreador de publicações, implementei, com assistência de IA, uma aplicação local para consultar PDFs e apresentar a origem de cada trecho recuperado.

## Pergunta do experimento

Uma busca semântica multilíngue recupera páginas relevantes melhor que TF-IDF em um corpus pequeno de editais de estágio em português?

O corpus reúne cinco PDFs oficiais do IFBA e do IF Baiano, totalizando 55 páginas com texto e 225 trechos. São versões históricas, identificadas por URL e SHA-256. O projeto não verifica automaticamente novas retificações nem indica se a seleção ainda está aberta.

## Implementação

A extração usa `pypdf` e mantém a página física do arquivo. Cada página é dividida em janelas de até 95 palavras, com sobreposição de 20, sem misturar documentos ou páginas. A primeira referência de comparação usa TF-IDF com unigramas e bigramas. A segunda usa `paraphrase-multilingual-MiniLM-L12-v2`, executado em CPU, com embeddings normalizados e produto escalar.

Os três primeiros resultados precisam ser páginas distintas: três janelas sobrepostas da mesma página não contam como três evidências diferentes. Títulos foram excluídos da representação textual para que seu vocabulário repetido não favorecesse todas as páginas do mesmo arquivo.

O modelo MiniLM tem um limite próprio de tokens; trechos podem ser truncados no encoder. A extração também apresentou caracteres imperfeitos e ordenação de tabelas. São limitações concretas desta configuração, não problemas resolvidos pelo uso de embeddings.

## Avaliação

Foram anotadas dez perguntas de desenvolvimento e vinte de teste. Das perguntas de teste, 15 têm resposta e cinco solicitam informações ausentes, como a nota de um candidato depois da seleção. O documento é selecionado previamente: o experimento mede recuperação de páginas dentro dele.

| Métrica de teste | TF-IDF | MiniLM |
|---|---:|---:|
| Páginas relevantes recuperadas no top 3 | 15/15 | 14/15 |
| Hit@3 | 100% | 93,3% |
| MRR@3 | 0,833 | 0,856 |
| Latência mediana da consulta | 1,83 ms | 70,02 ms |
| Latência p95 da consulta | 2,11 ms | 110,00 ms |
| Filtro de baixa evidência nos cinco casos sem resposta | 2/5 | 0/5 |

No desenvolvimento, o Hit@3 foi 90% para TF-IDF e 70% para MiniLM. Os relatórios completos registram cada pergunta, páginas recuperadas, latências, configuração do ambiente e hashes do corpus e das perguntas. O preparo inicial semântico levou aproximadamente 58 segundos na execução de teste; está separado da latência das consultas.

Os resultados são de uma única execução local, sem controle de carga do computador. Não foram ajustados limiares a partir do conjunto final. O conjunto é pequeno, criado durante a implementação, com temas próximos entre desenvolvimento e teste. Não é um benchmark externo nem evidência de generalização.

## O que os resultados permitem concluir

Neste conjunto, TF-IDF teve maior cobertura no top 3 e menor latência. MiniLM apresentou MRR ligeiramente maior: quando encontrou a resposta, em geral a página relevante ficou bem posicionada. Isso não sustenta a afirmação de que um método é universalmente melhor.

Há uma falha mais importante que a diferença de ranking: recuperar texto parecido quando a informação não existe. O MiniLM retornou evidências com similaridade suficiente nos cinco casos sem resposta. TF-IDF também falhou em identificar três deles. Logo, um limiar fixo de similaridade é insuficiente para decidir se a pergunta pode ser respondida.

Hit@3 avalia página, não o trecho exato, completude ou interpretação. Não foram atribuídas notas de qualidade de resposta: a geração com Llama 3.2 1B não estava operacional neste ambiente. Os campos de revisão humana continuam sem preenchimento.

## Geração e confiabilidade

A integração opcional com Ollama recebe apenas os trechos recuperados e pede citações literais em JSON. O backend rejeita IDs de fontes desconhecidos e textos que não aparecem nelas. Sem o modelo disponível, a interface preserva a busca e informa a indisponibilidade.

Esse contrato reduz a superfície de texto livre sem comprovação. Ele não demonstra que o modelo resiste a ataques nem que uma citação é relevante. O teste de injeção usa um gerador simulado e verifica somente a rejeição de uma saída inventada. Não houve teste de resistência com um LLM real.

## Próximos experimentos

Avaliar ausência de resposta com exemplos mais variados, revisar a relevância dos trechos e testar recuperação híbrida são próximos passos. Os erros do conjunto final podem orientar hipóteses, mas não devem ser usados para ajustar o sistema e apresentar o mesmo conjunto como um novo teste independente. Uma nova versão exigirá novos casos de avaliação.

A contribuição atual é uma aplicação reproduzível e um experimento com resultados e limitações registrados. Não há evidência de uso em produção, treinamento próprio de LLM ou economia de horas reais.

Fontes técnicas: [modelo MiniLM](https://huggingface.co/sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2), [TF-IDF no scikit-learn](https://scikit-learn.org/stable/modules/feature_extraction.html#text-feature-extraction), [Ollama e Llama 3.2 1B](https://ollama.com/library/llama3.2:1b). PDFs e versões: [manifesto do corpus](../data/manifest.json). Evidência completa: [relatório de teste](../reports/test-results.json).
