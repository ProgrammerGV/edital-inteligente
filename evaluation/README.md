# Protocolo de avaliação

Este protocolo descreve a v1. Para a geração local executada na v2, consulte [versões e critérios de revisão](versioning.md) e a [análise dos resultados](../docs/rag-local.md). Os relatórios da v1 foram preservados.

São 30 perguntas anotadas a partir do texto dos PDFs: dez de desenvolvimento e vinte de teste (15 respondíveis e cinco sem resposta). A página é a posição física no PDF, começando em 1. São aceitas páginas alternativas somente quando contêm a informação pedida. Os gabaritos resumem a fonte, sem corrigir o edital.

O documento é selecionado previamente em cada pergunta. Assim, o experimento mede a recuperação de páginas dentro de um edital, não a identificação automática do edital certo. O conjunto é pequeno, anotado durante a implementação e não constitui benchmark externo nem demonstra generalização. Há temas próximos entre desenvolvimento e teste; o teste é uma separação operacional, não uma validação independente.

1. Congele corpus, configurações e arquivos de perguntas antes da avaliação final.
2. Execute `python scripts/evaluate.py --split dev`. Ajustes futuros usam apenas desenvolvimento.
3. Execute `python scripts/evaluate.py --split test`. O relatório registra SHA-256 do corpus e das perguntas. Não use os erros de teste para ajustar e reapresentar o mesmo teste como inédito.
4. Registre novas versões e novos conjuntos se houver mudanças posteriores.

**Métricas:** Hit@3 (alguma das três páginas contém a resposta) e MRR@3 (posição da primeira página relevante). Páginas duplicadas por sobreposição de trechos não contam duas vezes. Essas métricas não garantem que o trecho específico da página responda à pergunta; isso precisa de revisão.

**Latência:** preparação/carregamento do modelo em separado; consultas sequenciais com modelo já carregado. Hardware, versão Python e data ficam no relatório. Os resultados não são um SLA.

**Ausência de resposta:** o campo de abstenção mede o filtro de evidência (ou a abstenção do gerador quando habilitado). Em modo somente busca, retornar trechos não é responder à pergunta. Similaridade alta pode ocorrer mesmo quando a resposta não existe: esse erro deve aparecer no relatório.

**Geração:** opcional, com `--generate`. Sem Ollama operacional, não há métricas de qualidade de resposta. Os campos `manual_correctness` e `manual_source_support` permanecem nulos até revisão humana: marque 1 para correto/sustentado, 0 para incorreto/não sustentado, registre observação e calcule a média apenas dos casos revisados. Verificar substring literal automaticamente não substitui verificar relevância e completude.

Um teste com gerador simulado verifica a barreira contra saída inventada; não mede resistência de um LLM real à injeção de prompt. Documentos continuam sendo conteúdo não confiável.
