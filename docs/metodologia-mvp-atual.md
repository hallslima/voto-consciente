# Metodologia atual do MVP

## Fonte dos dados

O projeto utiliza planos oficiais registrados no Tribunal Superior Eleitoral (TSE). Os PDFs são mantidos no repositório e podem ser abertos pela interface para consulta; eles não são processados durante o questionário. O MVP também apresenta fotos e informações eleitorais das candidaturas e uma pesquisa exploratória realizada pela equipe.

## Preparação inicial

A equipe informa que utilizou o Gemini, em uma etapa offline, como apoio para:

- diagnóstico dos planos;
- mapeamento temático;
- diagnóstico de comparabilidade;
- análise das propostas;
- elaboração da matriz consolidada;
- construção das perguntas e alternativas;
- preparação do Índice de Correspondência Temática (ICT).

Os arquivos originais dessa etapa não estão integralmente versionados no repositório. Por isso, a origem é declarada pela equipe, mas ainda possui limitação de rastreabilidade técnica.

O Gemini foi utilizado como apoio na preparação inicial e offline das informações. Nenhuma inteligência artificial analisa as respostas durante o uso. Os resultados são calculados por regras matemáticas fixas.

## Aplicação publicada

A execução normal utiliza somente:

- `data/questions.json`;
- `data/candidates.json`;
- `data/research_evidence.json`;
- `app.py`;
- `scoring.py`.

`app.py` carrega os JSONs e expõe o questionário e os resultados. O frontend envia as respostas e os pesos para a API. `scoring.py` consulta a matriz já estruturada e devolve pontuação, ICT, cobertura e memória de cálculo.

`data/research_evidence.json` registra a pesquisa consolidada com 136 participantes. Os indicadores finais destacados são 79,4% que conhecem pouco ou apenas algumas candidaturas e 40,4% que dizem conhecer poucas propostas dos candidatos. A amostra é de conveniência, descreve apenas o grupo participante e não representa todo o eleitorado de Pernambuco.

## Papel da IA

> A inteligência artificial foi utilizada como apoio na preparação inicial dos dados. Nenhum modelo de IA é consultado durante o preenchimento do questionário ou o cálculo dos resultados.

## Cálculo

> O resultado é calculado por código Python, utilizando pesos definidos pelo usuário e correspondências previamente estruturadas na matriz.

A correspondência total vale `1`, a parcial vale `0,5` e uma abordagem diferente vale `0`. “Não tenho opinião” não entra no cálculo. A cobertura informa em quantos temas respondidos existe uma posição documentada para a candidatura. Uma lacuna reduz a cobertura, mas não recebe automaticamente zero no ICT.

## Limitações

- A matriz atual não possui rastreabilidade completa por `evidence_id`.
- A preparação inicial ocorreu fora do código da aplicação.
- A ferramenta não avalia viabilidade jurídica, técnica ou financeira.
- A ferramenta não prevê o cumprimento das propostas.
- Ausência de proposta documentada não significa posição contrária.
- O resultado representa correspondência temática, não recomendação de voto.
- A pesquisa própria utiliza amostra por conveniência.
