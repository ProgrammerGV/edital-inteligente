# Versões dos experimentos

## v1 — recuperação

Os arquivos `dev.json`, `test.json`, `reports/dev-results.json` e `reports/test-results.json` foram preservados. O código e o corpus originais são recuperáveis pela tag `v0.1-retrieval` (commit `7380944`). Não executar o avaliador antigo sobre o mesmo nome de relatório para substituir esses resultados.

## v2 — geração de citações locais

Os conjuntos novos são `dev-v2.json` (12 perguntas) e `test-v2.json` (16 perguntas: dez respondíveis e seis sem resposta). Foram preparados antes de executar o LLM nesta versão. Gabaritos e páginas vêm dos mesmos cinco PDFs; portanto, não são corpus nem anotação independentes. As perguntas de teste não são usadas para ajustar prompts após observar suas respostas.

O corpus ganhou a classificação explícita `document_type=opening_notice`; o texto e os PDFs permanecem os mesmos. Uma regra de escopo recusa consultas de resultados individuais quando os documentos selecionados são somente editais de abertura. Esse mecanismo é uma política de produto documentada, não uma inferência aprendida. As métricas devem distinguir recusas por escopo de recusas feitas pelo modelo.

Na geração, a recuperação continua selecionando três páginas. O sistema consulta o texto completo dessas páginas para formar quatro candidatos literais, sem trechos que contenham outro candidato da mesma página. Quando MiniLM está instalado, o reranqueamento usa 70% similaridade semântica e 30% TF-IDF; caso contrário, usa apenas TF-IDF e registra isso no relatório. Esse reranqueamento é compartilhado pelos dois métodos iniciais de recuperação: as métricas de geração não são uma comparação de pipelines puramente lexical versus puramente semântico.

O LLM escolhe somente o melhor ID ou recusa a pergunta. O backend recupera a citação exata pelo ID e valida sua presença na página. Não há síntese livre nem permissão para executar instruções contidas em documentos. No primeiro experimento de desenvolvimento foram usados dez candidatos e até duas citações. Recusas indevidas e citações extras observadas nesse experimento motivaram a redução e o reranqueamento; o relatório dessa primeira execução foi preservado.

O corte de similaridade para geração é 0,02 em TF-IDF e 0,20 em MiniLM. São filtros heurísticos fixados antes da avaliação final, não probabilidades. Os cortes originais de busca isolada permanecem 0,12 e 0,35. A definição de cobertura da geração é distinta do Hit@3 da v1.

Cada execução tem nome próprio, data, SHA-256 das perguntas, do corpus e dos arquivos de implementação, além do digest do modelo. `--resume` só continua arquivos da mesma implementação. Falhas do serviço não contam como abstenção correta.

A análise de corretude desta entrega pode ser feita pelo assistente comparando gabarito, resposta e página. Nesse caso, registrar `reviewer` e `independent_human_review=false`. Isso não é revisão humana independente; os campos de revisão assistida devem permanecer separados dos campos antigos de avaliação humana.

Casos artificiais de injeção de prompt são avaliados à parte. A rejeição de comandos conhecidos e citações inventadas não prova imunidade geral a ataques.
