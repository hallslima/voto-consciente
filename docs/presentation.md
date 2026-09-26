# Apresentação

A apresentação integrada ao React possui 14 slides com problema, evidências, objetivo, dados, metodologia, arquitetura, limitações e conclusão. O QR Code e o endereço público do MVP ficam concentrados no slide final.

O slide metodológico apresenta um agente de IA generativa supervisionado, baseado no Gemini e operado em ambiente de notebook. O agente aparece somente na preparação offline dos dados; o questionário e o cálculo determinístico não executam IA.

O slide **Evidências da necessidade** separa visualmente três recortes: pesquisa própria com 136 participantes e indicadores derivados de `data/research_evidence.json`; pesquisa Quaest referente ao Rio de Janeiro; e contexto histórico nacional de 2018. As ressalvas impedem a generalização das fontes externas ou da amostra por conveniência para o eleitorado de Pernambuco.

O QR Code da conclusão usa `VITE_PUBLIC_SITE_URL` com fallback para o domínio público atual e é acompanhado pelo endereço em texto.
