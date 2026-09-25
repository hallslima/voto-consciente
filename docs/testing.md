# Testes

`pytest` cobre opinião sem resposta, correspondência 0/0,5/1, pesos 1/2/3, ausência e cobertura, limites, ordenação e desempate. Também verifica validação do payload da API, consistência da pesquisa, apresentação, privacidade, deploy e inventário de ativos. `validation.py` verifica perguntas, alternativas, compatibilidades e alternativa principal.

Testes manuais: carregar bootstrap, responder um tema, usar pesos diferentes, conferir três primeiros, barras, radar, memória, foto nominal, PDF local, TSE, documento e página/seção; repetir em viewport móvel. Conferir sete associações de fotos e planos e os três recortes do slide de pesquisa.

Critérios de aceitação: ICT e cobertura permanecem determinísticos; respostas não são enviadas a IA; PDFs e fotos existem nos caminhos publicados; ausência é visível e não vira nota zero; não há segredo no repositório; `pytest` e `npm run build` passam.
