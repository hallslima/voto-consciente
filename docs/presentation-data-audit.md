# Auditoria de dados da apresentação

Atualizada em 25 de setembro de 2026. O recorte publicado contém somente candidaturas com `registration_status = Deferido`.

| Indicador | Valor confirmado | Fonte atual | Observação |
| --- | ---: | --- | --- |
| Candidaturas | 7 | `data/candidates.json` | Todos os registros atuais estão deferidos. |
| Planos oficiais | 7 | `data/candidates.json` e PDFs em `public/documents/government-plans/` | Cada candidatura possui um PDF local associado. |
| Páginas dos documentos | 311 | PDFs em `public/documents/government-plans/` | Total dos sete documentos do recorte atual. Os PDFs ficam disponíveis para consulta e não são processados durante o questionário. |
| Temas | 7 | `data/questions.json` | Sete temas distintos. |
| Perguntas publicadas | 7 | `data/questions.json` e `/api/bootstrap` | O bootstrap expõe as sete perguntas. |
| Participantes da pesquisa | 135 | `data/research_evidence.json` | Amostra por conveniência; não representa todo o eleitorado de Pernambuco. |

## Divergências resolvidas

- O MVP atual possui sete candidaturas deferidas.
- Os sete PDFs associados somam 311 páginas.
- A pesquisa registra 135 participantes.
- O questionário publicado possui sete perguntas.

Não há fonte registrada que comprove a frase “517 candidatos a deputado estadual”. A apresentação usa a formulação conservadora sobre centenas de candidaturas em uma eleição completa e esclarece que deputados não fazem parte do recorte.

## Limitação de rastreabilidade

A preparação inicial com apoio do Gemini foi informada pela equipe, mas seus artefatos originais não estão integralmente versionados. A apresentação não descreve essa preparação como automaticamente reproduzível ou completamente rastreável.
