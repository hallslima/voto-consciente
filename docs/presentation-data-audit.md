# Auditoria de dados da apresentação

Atualizada em 25 de setembro de 2026. O recorte publicado contém somente candidaturas com `registration_status = Deferido`.

| Indicador | Valor confirmado | Fonte atual | Observação |
| --- | ---: | --- | --- |
| Candidaturas | 7 | `data/candidates.json` | Todos os registros atuais estão deferidos. |
| Planos oficiais | 7 | `data/candidates.json` e PDFs em `public/documents/government-plans/` | Cada candidatura possui um PDF local associado. |
| Páginas dos documentos | 311 | PDFs em `public/documents/government-plans/` | Total dos sete documentos do recorte atual. Os PDFs ficam disponíveis para consulta e não são processados durante o questionário. |
| Temas | 7 | `data/questions.json` | Sete temas distintos. |
| Perguntas publicadas | 7 | `data/questions.json` e `/api/bootstrap` | O bootstrap expõe as sete perguntas. |
| Participantes da pesquisa | 136 | `data/research_evidence.json` | Resultado consolidado pela equipe; amostra por conveniência. |
| Conhecem pouco ou apenas algumas candidaturas | 79,4% | `data/research_evidence.json` | Descreve o grupo participante; não representa todo o eleitorado. |
| Dizem conhecer poucas propostas dos candidatos | 40,4% | `data/research_evidence.json` | Descreve o grupo participante; não representa todo o eleitorado. |

## Divergências resolvidas

- O MVP atual possui sete candidaturas deferidas.
- Os sete PDFs associados somam 311 páginas.
- A pesquisa registra 136 participantes e usa como indicadores oficiais 79,4% e 40,4%.
- O questionário publicado possui sete perguntas.

Fotos e PDFs sem vínculo com as sete candidaturas foram retirados do diretório público. O inventário publicado possui sete fotos e sete planos ativos.

## Limitação de rastreabilidade

A preparação inicial com apoio do Gemini foi informada pela equipe, mas seus artefatos originais não estão integralmente versionados. A apresentação não descreve essa preparação como automaticamente reproduzível ou completamente rastreável.
