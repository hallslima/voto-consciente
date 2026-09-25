# Voto Consciente Pernambuco

Aplicação que compara as prioridades informadas pelo eleitor com propostas documentadas nos planos de governo das candidaturas analisadas. A ferramenta apresenta correspondência temática e não recomenda voto, não avalia viabilidade e não prevê o cumprimento das propostas.

## Objetivo

Facilitar a comparação entre respostas do usuário e posições previamente estruturadas a partir dos planos oficiais do Tribunal Superior Eleitoral (TSE). Os PDFs permanecem disponíveis na interface para consulta.

## Arquitetura

```text
Planos oficiais do TSE
        ↓
Preparação inicial dos dados com apoio do Gemini
        ↓
Perguntas e matriz estruturadas em JSON
        ↓
Questionário em React
        ↓
Cálculo determinístico em Python
        ↓
Resultados, cobertura e fontes
```

O frontend React/Vite solicita os dados à API FastAPI, envia respostas e pesos para `/api/results` e exibe a resposta. O cálculo fica exclusivamente em `scoring.py`.

## Dados utilizados

- `data/questions.json`: sete perguntas e suas alternativas.
- `data/candidates.json`: candidaturas deferidas, matriz de compatibilidade, resumos, páginas e fontes.
- `data/research_evidence.json`: pesquisa exploratória da equipe e suas limitações.
- `public/assets/candidates/`: fotos das candidaturas.
- `public/documents/government-plans/`: PDFs oficiais disponíveis para consulta.

## Papel da inteligência artificial

A equipe informa que utilizou o Gemini como apoio offline na preparação inicial: diagnóstico dos planos, organização temática, comparação das propostas e estruturação das perguntas e da matriz. Os artefatos originais dessa etapa não estão integralmente versionados, o que limita sua rastreabilidade técnica.

Nenhum modelo de IA é consultado durante o preenchimento do questionário ou o cálculo dos resultados.

## Funcionamento do ICT

```text
ICT(c) = 100 × soma(peso(q) × compatibilidade(c,q)) / soma(pesos válidos)
```

As compatibilidades são previamente estruturadas como `0`, `0,5` ou `1`. Os pesos informados pelo usuário são `1`, `2` ou `3`. “Não tenho opinião” não participa do cálculo. Tema sem posição documentada fica fora do denominador e reduz a cobertura; isso não significa posição contrária.

Os resultados são ordenados por ICT, pontos de prioridade e nome, conforme o motor Python.

## Execução local

```powershell
python -m pip install -r requirements.txt
npm install
```

Inicie a API:

```powershell
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Em outro terminal, inicie o frontend:

```powershell
npm run dev -- --host 127.0.0.1
```

## Testes

```powershell
$pytestTemp = Join-Path (Get-Location) ".pytest_cache\local-temp"
.\.venv\Scripts\python.exe -m pytest -v --basetemp "$pytestTemp"
npm.cmd run build
```

A suíte preservada cobre cálculo, API, matriz, ativos públicos, interface, apresentação e implantação.

## Implantação

- Netlify: build do frontend com `npm run build`, publicando `dist/`.
- Render: instalação de `requirements.txt` e inicialização com Uvicorn.
- `VITE_API_BASE_URL`: endereço público da API.
- `VITE_PUBLIC_SITE_URL`: endereço público do MVP usado pelos QR Codes.
- `FRONTEND_ORIGINS`: origens permitidas pela API.

## Limitações

- A preparação inicial ocorreu fora do código da aplicação e não possui rastreabilidade técnica completa por `evidence_id`.
- A matriz representa propostas documentadas; não mede qualidade ou viabilidade.
- A ferramenta não prevê cumprimento das propostas.
- Ausência de proposta documentada não significa posição contrária.
- O resultado representa correspondência temática, não recomendação de voto.
- A pesquisa própria utiliza amostra por conveniência e não representa todo o eleitorado.

## Estrutura principal

```text
data/
├── questions.json
├── candidates.json
└── research_evidence.json

public/
├── assets/candidates/
└── documents/government-plans/

src/
├── presentation/
├── main.jsx
├── api.js
└── styles.css

tests/
app.py
scoring.py
validation.py
netlify.toml
render.yaml
```
