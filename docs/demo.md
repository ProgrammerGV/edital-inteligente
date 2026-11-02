# Demonstração: consulta com evidências

## v2 — experimento de geração

O modo principal continua sendo busca. Para testar a geração, confira `scripts/doctor.py` e marque a opção de modelo local. A interface a deixa desativada por padrão por causa dos erros medidos.

`rag-demo.mp4` contém duas capturas reais de desenvolvimento, oito segundos por cena, sem gravação contínua: consulta sobre recesso e recusa de vale-refeição pelo filtro de candidatos (sem chamada ao LLM nessa recusa). `rag-demo.srt` descreve as cenas. Não é vídeo de desempenho nem representação dos 16 casos finais. O exemplo positivo levou 54,9 segundos incluindo o primeiro preparo semântico na aplicação; o corte de oito segundos não representa essa espera.

Esses exemplos não substituem o resultado final: **4/10 perguntas respondíveis atendidas corretamente**, três citações inadequadas e três recusas indevidas; **6/6 casos sem resposta recusados**. Veja a [análise completa](rag-local.md). Capturas em `rag-demo.png` e `rag-no-answer.png`.

## v1 — busca avaliada

1. Inicie a aplicação e mostre os cinco documentos e o aviso de corpus histórico.
2. Selecione “IFBA DGCOM — Estágio superior 01/2025”.
3. Pergunte “Qual é o valor mensal da bolsa para vinte horas semanais?” usando TF-IDF.
4. Mostre o trecho e abra a página 2 do PDF. O valor do documento é R$ 787,98, neste snapshot.
5. Troque para MiniLM e repita a consulta; compare as fontes e explique que os escores não têm escalas diretamente comparáveis.
6. Pergunte “Qual foi a nota final do primeiro colocado nesta seleção?”. O edital não contém esse resultado. Se a busca retornar páginas parecidas, explique a falha: encontrar termos relacionados não resolve ausência de resposta.
7. Sem um documento selecionado, pergunte “Qual é o prazo?”. Mostre a solicitação para esclarecer o edital.
8. Se Ollama não estiver ativo, mostre o estado de geração indisponível. Não apresente uma busca como resposta gerada.

O vídeo deve mostrar a aplicação real, sem substituir falhas por resultados ilustrativos. Não habilitar notificações do rastreador original nem exibir credenciais durante a gravação.

## Material produzido

`demo.mp4` é uma sequência de três capturas reais da aplicação, com seis segundos por cena: biblioteca/formulário, consulta semântica com fonte e pergunta ambígua. Não é uma gravação contínua nem um vídeo de desempenho. `demo.srt` contém a descrição das cenas. O tempo mostrado na consulta pertence àquela execução, não à duração da cena.

A entrega HTTP dos PDFs é testada. O visualizador PDF do navegador integrado não exibiu a página durante a inspeção; use um navegador com leitor de PDF ou baixe o arquivo para conferir. A captura do PDF do LinkedIn recebida não integra este repositório.
