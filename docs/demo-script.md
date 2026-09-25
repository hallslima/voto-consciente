# Roteiro de demonstração do MVP

## 1. Preparação antes da apresentação — 5 minutos

- Usar a branch `main` atualizada e confirmar `git status --short`.
- Fechar aplicações que exibam notificações e conectar o computador à energia.
- Confirmar que Python, dependências e `node_modules` estão disponíveis.
- Executar `python -m pytest -q` e `cmd /c npm run build`.
- Abrir o backend, o frontend e `http://localhost:8000/api/health` antes da apresentação.
- Manter os PDFs locais; a demonstração principal não depende da internet.

## 2. Iniciar no Windows

Terminal 1 — backend:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app:app --reload --port 8000
```

Terminal 2 — frontend:

```powershell
cmd /c npm run dev -- --host 127.0.0.1
```

URLs:

- Frontend: `http://127.0.0.1:5173`
- API: `http://127.0.0.1:8000`
- Saúde da API: `http://127.0.0.1:8000/api/health`
- Documentação da API: `http://127.0.0.1:8000/docs`

## 3. Sequência de demonstração — 6 a 8 minutos

1. **Abertura — 40 s:** mostrar o aviso metodológico e explicar que não há recomendação de voto.
2. **Como funciona — 50 s:** percorrer planos oficiais, preparação inicial com apoio do Gemini, JSON, questionário e cálculo determinístico.
3. **Indicadores — 40 s:** apresentar candidaturas, planos, perguntas, temas e pesquisa própria.
4. **Questionário — 2 min:** escolher uma alternativa por tema, variar pesos e marcar pelo menos um tema como “Não tenho opinião”.
5. **Resultado — 1 min:** destacar os três primeiros, ICT e cobertura como indicadores diferentes.
6. **Investigação — 1,5 min:** selecionar uma candidatura, mostrar radar, memória, fonte, página e PDF.
7. **Revisão — 30 s:** voltar às respostas sem perder escolhas; depois mostrar o botão para refazer do zero.

## 4. Respostas sugeridas para a simulação

Use um perfil fictício e variado, sem anunciar preferência eleitoral:

- Saúde: alternativa B, peso 3.
- Educação: alternativa C, peso 2.
- Segurança: alternativa B, peso 2.
- Mobilidade: alternativa A, peso 3.
- Saneamento: “Não tenho opinião”.
- Emprego e renda: alternativa C, peso 1.
- Assistência social: alternativa A, peso 2.

O resultado esperado é uma lista de sete candidaturas deferidas ordenada deterministicamente, com três destaques. Não antecipe um nome: explique que a ordem decorre das respostas, pesos e posições documentadas disponíveis.

## 5. Pontos essenciais

- Compatibilidades possíveis: 0, 0,5 e 1; pesos: 1, 2 e 3.
- “Não tenho opinião” fica fora do cálculo.
- Tema sem evidência fica fora do denominador daquela candidatura e reduz cobertura.
- ICT mede correspondência; cobertura mede quanto foi possível comparar.
- A IA organiza dados antes do uso; não escolhe candidatura nem calcula o ranking em tempo real.
- A preparação inicial ocorreu fora do código da aplicação e possui limitação de rastreabilidade técnica.

## 6. Planos alternativos

### Sem internet

O questionário, a API, fotos e planos são locais. Evite abrir o link externo do TSE; use “Abrir plano analisado”. A fonte Google Fonts pode cair para a fonte local do sistema sem impedir o uso.

### Backend indisponível

Verifique `http://127.0.0.1:8000/api/health`, encerre o terminal com `Ctrl+C` e execute novamente o comando do backend. Se não recuperar, use a apresentação integrada e explique o fluxo com as telas já abertas, sem inventar resultados.

### Frontend indisponível

Reinicie com `cmd /c npm run dev -- --host 127.0.0.1`. Como alternativa, após um build já validado, execute `cmd /c npm run preview -- --host 127.0.0.1` e abra a URL informada pelo Vite.

## 7. Checklist final

- [ ] API responde `ok: true`.
- [ ] Frontend abre sem tela vazia ou erro no console.
- [ ] Sete perguntas e oito candidaturas carregam.
- [ ] Fotos e PDFs locais abrem.
- [ ] Resultado mostra top 3, barras, radar, detalhes, ICT e cobertura.
- [ ] Layout foi conferido em desktop e largura móvel.
- [ ] Nenhuma decisão humana foi preenchida.
- [ ] Manifesto e matriz permanecem inalterados.
- [ ] Plano alternativo está disponível.
