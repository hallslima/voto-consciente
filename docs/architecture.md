# Arquitetura

O frontend React/Vite carrega o bootstrap da API FastAPI e envia `answers` e `weights` para `/api/results`. O backend valida o payload com Pydantic, valida a matriz e chama `scoring.calculate_results`. Python calcula ICT, cobertura, memória e ordenação; o React apenas apresenta esses resultados.

JSON mantém perguntas, candidaturas, matriz e pesquisa própria. Fotos e PDFs são ativos públicos versionados. Um agente de IA generativa supervisionado pela equipe apoiou somente a preparação offline. Tecnologia do agente: Gemini em ambiente de notebook. Nenhuma IA é executada durante o questionário ou no cálculo dos resultados.

Fluxo: planos oficiais do TSE -> agente de IA generativa supervisionado -> organização dos temas e propostas -> perguntas e matriz em JSON -> questionário -> cálculo determinístico -> resultados e fontes.
