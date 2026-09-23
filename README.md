# Voto Consciente Pernambuco

# Voto Consciente Pernambuco

Aplicação React para comparar prioridades pessoais com propostas documentadas nos planos de governo das candidaturas analisadas. O cálculo do Índice de Correspondência Temática (ICT) permanece determinístico e centralizado em Python; o React cuida da experiência de preenchimento, apresentação e leitura dos resultados.

O projeto não indica voto, não avalia caráter, competência, viabilidade ou cumprimento de propostas. Ele organiza evidências para facilitar uma investigação própria.

## Executar em desenvolvimento

Instale as dependências Python:

```bash
python -m pip install -r requirements.txt
```

Em um terminal, inicie a API:

```bash
uvicorn app:app --reload --port 8000
```

Em outro terminal, instale e inicie o frontend:

```bash
npm install
npm run dev
```

Abra o endereço informado pelo Vite, normalmente `http://localhost:5173`.

## Estrutura

- `app.py`: API FastAPI, validação do payload e serialização dos resultados.
- `scoring.py`: cálculo do ICT e memória de cálculo.
- `validation.py`: auditoria estrutural da matriz.
- `data/questions.json`: perguntas e alternativas.
- `data/candidates.json`: perfis, compatibilidades, resumos e fontes.
- `src/main.jsx`: apresentação, questionário, ranking, comparações e detalhes.
- `src/styles.css`: identidade visual responsiva da interface.
- `public/assets/candidates/`: oito fotos associadas por ID e número.
- `public/documents/government-plans/`: PDFs locais usados na análise.
- `ai_pipeline/`: prompts, schema e scripts offline de preparação da base.
- `docs/`: arquitetura, metodologia, fontes, pesquisa, apresentação e testes.
- `tests/test_scoring.py`: testes do cálculo e da matriz.

## Regra de cálculo

```text
ICT(c) = 100 × soma(peso(q) × compatibilidade(c,q)) / soma(peso(q))
```

A soma considera somente perguntas respondidas que possuem evidência classificada para a candidatura. A opção “Não tenho opinião formada” não entra no cálculo. Uma lacuna documental fica fora do denominador e reduz a cobertura, sem receber nota zero.

O resultado representa correspondência temática documentada, não indicação de voto.

## Papel da IA e dados revisados

A IA pode auxiliar a preparação offline: extração por plano, organização temática, identificação de contrastes e rascunho de perguntas. A equipe confere trechos, páginas, classificação, neutralidade e fontes. Saídas pendentes ficam em `data/generated/`; somente conteúdo revisado pode chegar à matriz publicada. O runtime não lê `data/generated/`, não envia respostas ao Gemini e nunca usa Gemini para o ranking.

O uso de Gemini é opcional. Variáveis disponíveis em `.env.example`: `GEMINI_API_KEY` e `GEMINI_MODEL`. Nenhuma chave é necessária para executar o MVP.

## Pesquisa própria

A apresentação inclui **Evidências da necessidade do projeto**, baseada em 135 respostas de uma pesquisa exploratória por amostra de conveniência em Pernambuco. Os percentuais descrevem apenas o grupo consultado e não representam todo o eleitorado pernambucano. Os dados e limitações estão em `data/research_evidence.json`.

## Testes

```bash
pytest
npm run build
```

O backend pode ser executado com `uvicorn app:app --reload --port 8000` e o frontend com `npm run dev`. A documentação detalhada está em `docs/`.

## Apresentação integrada

O menu **Apresentação** abre uma página de apresentação dentro do próprio site. Ela organiza a fala em doze slides:

1. Capa da apresentação.
2. Problema e relevância.
3. Pergunta de pesquisa, objetivo e recorte.
4. Dados utilizados.
5. Inteligência Artificial na construção da base.
6. Construção das perguntas e Modo Geral.
7. Arquitetura tecnológica.
8. Motor matemático, ICT e indicador de cobertura.
9. Exemplo prático de cálculo auditável.
10. Testes, validações e revisão humana.
11. Demonstração do MVP.
12. Conclusões, limitações, próximos passos e equipe.

O MVP atual utiliza somente o Modo Geral. O indicador de cobertura é calculado pelo campo `coverage` do motor Python: temas respondidos com evidência para a candidatura divididos pelo total de temas respondidos pelo usuário. Ele representa a cobertura do recorte respondido, não a cobertura integral do plano.

O botão final da apresentação retorna ao questionário real, permitindo apresentar a narrativa e demonstrar o MVP no mesmo endereço.
