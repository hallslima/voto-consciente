# Arquitetura

O frontend React/Vite carrega o bootstrap da API FastAPI e envia `answers` e `weights` para `/api/results`. O backend valida o payload com Pydantic, valida a matriz e chama `scoring.calculate_results`. Python calcula ICT, cobertura, memória e ordenação; o React apenas apresenta esses resultados.

JSON mantém perguntas, candidaturas, evidências revisadas e pesquisa própria. Fotos e PDFs são ativos públicos versionados. O pipeline de IA é offline e não é importado pelo runtime.

Fluxo: plano/documento -> matriz revisada -> bootstrap -> questionário -> payload validado -> resultado determinístico -> cards, barras, radar e evidências.
