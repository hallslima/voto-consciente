# Metodologia atual do MVP

## Fonte dos dados

O projeto utiliza planos oficiais registrados no Tribunal Superior Eleitoral (TSE). Os PDFs são mantidos no repositório e podem ser abertos pela interface para consulta; eles não são processados durante o questionário. O MVP também apresenta fotos e informações eleitorais das candidaturas e uma pesquisa exploratória realizada pela equipe.

```text
Planos oficiais do TSE
→ agente de IA generativa supervisionado
→ organização dos temas e propostas
→ perguntas e matriz em JSON
→ questionário
→ cálculo determinístico
→ resultados e fontes
```

## Preparação inicial

A preparação foi realizada com um **agente de IA generativa supervisionado pela equipe**. Na preparação inicial dos dados, a equipe utilizou um agente de IA generativa, baseado no Gemini e operado em ambiente de notebook. O agente apoiou a leitura, a organização e a comparação dos planos de governo. A equipe definiu as instruções, os temas e os critérios utilizados e consolidou os resultados nos arquivos JSON do projeto. Esse processo aconteceu antes da publicação do MVP.

O agente apoiou, de forma supervisionada e offline:

- diagnóstico inicial dos planos de governo;
- mapeamento dos temas;
- organização das propostas por tema e subtema;
- produção de resumos neutros;
- localização de trechos, páginas e fontes;
- identificação das ações propostas e das limitações;
- apoio à consolidação da matriz de propostas;
- apoio à formulação das perguntas e alternativas.

Essas atividades não foram totalmente autônomas, e as decisões finais permaneceram sob responsabilidade da equipe. Tecnologia do agente: Gemini em ambiente de notebook.

O repositório preserva os dados finais utilizados pelo MVP, mas não contém o histórico integral das interações realizadas com o agente de IA durante a preparação inicial.

Durante o uso do questionário, nenhum agente de IA é executado. As respostas são comparadas com uma matriz previamente preparada, e o resultado é calculado por regras matemáticas determinísticas em Python.

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

> Agente de IA generativa supervisionado pela equipe. Baseado no Gemini, foi utilizado somente na preparação offline dos dados. Nenhuma IA é executada durante o questionário ou no cálculo dos resultados.

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
