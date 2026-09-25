# Voto Consciente Pernambuco

Aplicação acadêmica que compara as prioridades informadas pelo eleitor com propostas documentadas nos planos de governo das sete candidaturas incluídas no recorte atual para o Governo de Pernambuco.

- MVP: https://voto-consciente.netlify.app/
- Apresentação: https://voto-consciente.netlify.app/?modo=apresentacao

## Problema, objetivo e escopo

Planos de governo extensos e pouco padronizados dificultam a comparação entre propostas. O projeto organiza um recorte documental para relacionar as prioridades do usuário a posições previamente estruturadas. A ferramenta mostra correspondência temática: não recomenda voto, não avalia a viabilidade das propostas e não prevê seu cumprimento.

O MVP abrange sete candidaturas, sete planos ativos, 311 páginas de documentos, sete temas e sete perguntas sobre o Governo de Pernambuco. Outros cargos não fazem parte do recorte.

## Pesquisa exploratória

A pesquisa atual consolidada pela equipe considera 136 participantes. Entre eles, 79,4% conhecem pouco ou apenas algumas candidaturas e 40,4% dizem conhecer poucas propostas dos candidatos. A amostra foi obtida por conveniência: os resultados descrevem o grupo participante e não podem ser generalizados para todo o eleitorado de Pernambuco.

`data/research_evidence.json` é a fonte estruturada oficial desses resultados e preserva a metodologia, as limitações e os demais indicadores da pesquisa.

## Arquitetura e tecnologias

```text
Planos oficiais do TSE
        ↓
Agente de IA generativa supervisionado
        ↓
Organização dos temas e propostas
        ↓
Perguntas e matriz em JSON
        ↓
Questionário em React
        ↓
Cálculo determinístico em Python
        ↓
Resultados, cobertura e fontes
```

- React e Vite: questionário, resultados e apresentação integrada.
- FastAPI e Pydantic: API e validação das entradas.
- Python: motor matemático determinístico.
- JSON: perguntas, candidaturas, matriz e pesquisa.
- Pytest: testes automatizados.
- Netlify e Render: configuração de publicação do frontend e da API.

O frontend solicita os dados à API, envia respostas e pesos para `/api/results` e apresenta o retorno calculado por `scoring.py`. Fotos e PDFs ficam em `public` e são publicados como arquivos estáticos.

## Metodologia e papel da IA

Na preparação inicial dos dados, a equipe utilizou um agente de IA generativa, baseado no Gemini e operado em ambiente de notebook. O agente apoiou a leitura, a organização e a comparação dos planos de governo. A equipe definiu as instruções, os temas e os critérios utilizados e consolidou os resultados nos arquivos JSON do projeto. Esse processo aconteceu antes da publicação do MVP.

Durante o uso do questionário, nenhum agente de IA é executado. As respostas são comparadas com uma matriz previamente preparada, e o resultado é calculado por regras matemáticas determinísticas em Python.

**Agente de IA generativa supervisionado pela equipe.** Tecnologia do agente: Gemini em ambiente de notebook. O repositório preserva os dados finais utilizados pelo MVP, mas não contém o histórico integral das interações realizadas com o agente de IA durante a preparação inicial.

## Motor matemático

```text
ICT(c) = 100 × soma(peso(q) × compatibilidade(c,q)) / soma(pesos válidos)
```

As compatibilidades previamente estruturadas são `0`, `0,5` ou `1`; os pesos informados pelo usuário são `1`, `2` ou `3`. “Não tenho opinião” não participa do cálculo. Tema sem posição documentada fica fora do denominador da candidatura e reduz a cobertura, sem receber automaticamente nota zero.

- Correspondência: proximidade entre as respostas e as propostas documentadas.
- Cobertura: proporção dos temas respondidos para os quais existe posição classificada.

Os resultados são ordenados por ICT, pontos em temas de prioridade máxima e nome. O tamanho do plano não interfere no resultado.

## Fontes

- Planos de governo e dados eleitorais disponíveis no TSE.
- PDFs associados às sete candidaturas, disponíveis na própria interface.
- Pesquisa exploratória descrita em `data/research_evidence.json` e `docs/research-evidence.md`.
- Referências institucionais e trabalhos relacionados em `docs/sources.md`.

## Privacidade

Não existe banco de dados de respostas, login ou perfil do eleitor. As escolhas permanecem no estado temporário da interface, são enviadas à API somente para o cálculo e não são gravadas pela aplicação. O código não usa `localStorage`, `sessionStorage` ou cookies para guardar respostas.

Essa descrição se limita ao comportamento da aplicação. Políticas e logs operacionais da infraestrutura do Netlify e do Render devem ser verificados nos respectivos serviços.

## Integrantes

- Hallisson Lima
- Rodrigo Monteiro
- Lucas Kamel
- Thamyres Costa
- Ben-Hur Cavalcanti

## Instalação e execução local

```powershell
python -m pip install -r requirements.txt
npm install
```

API:

```powershell
python -m uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Frontend, em outro terminal:

```powershell
npm run dev -- --host 127.0.0.1
```

O modo de apresentação fica disponível em `http://127.0.0.1:5173/?modo=apresentacao`.

## Testes

```powershell
.\.venv\Scripts\python.exe -m pytest -v
npm.cmd run build
git diff --check
```

A suíte cobre motor matemático, API, matriz, ativos, privacidade, interface, apresentação e implantação. A quantidade deve ser lida da coleta do Pytest, e não mantida manualmente no frontend.

## Implantação

- Netlify: `npm run build`, publicando `dist/`.
- Render: instalação de `requirements.txt` e inicialização com Uvicorn.
- `VITE_API_BASE_URL`: endereço configurável da API; a URL pública real não está fixada no repositório.
- `VITE_PUBLIC_SITE_URL`: endereço do MVP usado pelos QR Codes.
- `FRONTEND_ORIGINS`: origens autorizadas pela API.

As configurações demonstram como publicar o sistema, mas não comprovam por si só o estado operacional dos serviços.

## Limitações

- A preparação inicial ocorreu fora do código e não possui rastreabilidade técnica completa.
- A matriz representa apenas propostas documentadas.
- A ferramenta não avalia qualidade, viabilidade ou cumprimento das propostas.
- Ausência documental não significa posição contrária.
- A pesquisa usa amostra por conveniência e não representa todo o eleitorado.
- Links externos e o estado dos serviços publicados podem mudar.

## Trabalhos futuros

- Ampliar a rastreabilidade metodológica da preparação dos dados.
- Avaliar a expansão do questionário e do recorte somente após nova validação documental.
- Melhorar os links oficiais específicos de cada candidatura.
- Avaliar a necessidade de retirar do bootstrap as URLs da pesquisa, hoje não consumidas pelo frontend.
