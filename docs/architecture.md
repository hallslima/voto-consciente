# Arquitetura

O frontend React/Vite carrega o bootstrap da API FastAPI e envia `answers` e `weights` para `/api/results`. O backend valida o payload com Pydantic, valida a matriz e chama `scoring.calculate_results`. Python calcula ICT, cobertura, memória e ordenação; o React apenas apresenta esses resultados.

JSON mantém perguntas, candidaturas, matriz e pesquisa própria. Fotos e PDFs são ativos públicos versionados. A preparação inicial com apoio do Gemini ocorreu offline e não é executada pelo runtime.

Fluxo: planos oficiais -> preparação inicial declarada pela equipe -> perguntas e matriz JSON -> bootstrap -> questionário -> payload validado -> resultado determinístico -> cards, barras, radar e fontes.
