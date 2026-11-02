# Origem e evolução

O projeto evolui o **Rastreador de Editais de Concursos**, de Gabriel Vinicius (`ProgrammerGV`):

- Repositório: https://github.com/ProgrammerGV/INF032-Programa-o_Python
- Diretório: `projeto/rastreador-editais`
- Commit inspecionado: `84768f449f233ddff86711e6fbf52369a23f1a68`

O original já reúne coleta de páginas, filtros por palavras, painel Flask, histórico e notificações opcionais. Também contém integração opcional com Gemini (`src/ai_extractor.py`) para extração estruturada e resumos. A existência desse código foi verificada; sua operação com uma API real não foi validada nesta tarefa.

Neste repositório, foi adaptada a normalização de texto de `src/utils.py` e mantida a organização em aplicação Flask e módulos de processamento. A ingestão por página, os dois mecanismos de busca, o contrato de citações, o avaliador e a interface foram implementados para este projeto. Configurações, chaves e dados operacionais do original não foram copiados.

O novo fluxo não aciona notificações nem depende da API do Gemini. Os PDFs são obtidos de fontes oficiais, com URL e SHA-256 em `data/manifest.json`. São snapshots históricos para avaliação e podem não refletir retificações posteriores.

O repositório original consultado não continha uma licença explícita. A publicação pública não implica concessão de licença de terceiros. Uma licença para distribuição deste código deverá ser definida pelo titular. As licenças dos modelos e dependências permanecem as de seus autores.

Implementação preparada com assistência de IA. Avaliações automáticas e pontos ainda não validados são descritos separadamente; assistência de IA não substitui a compreensão do código por quem apresenta o projeto.
