# Piloto de evidências — Guilherme Fonseca

## Escopo e fonte

- Fonte exclusiva: `data/generated/extracted-text/guilherme_fonseca.json`
- Arquivo original registrado: `guilherme-fonseca-16.pdf`
- SHA-256: `ddad81bd495da44f7265519d745e4cb51133ea67256b9ef51e64d46fdc653f41`
- Páginas analisadas: 1 a 8 (numeração física preservada)
- Prompt: `ai_pipeline/prompts/01_extract_candidate_evidence.md`
- Versão: `extract-evidence-v1.0.0`
- Status na geração: `pending`

## Evidências encontradas por tema

- Saúde pública: 6
- Educação: 9
- Segurança pública: 10
- Mobilidade e transporte: 5
- Saneamento: 1
- Emprego e renda: 7
- Assistência social e combate à fome: 3

Total: 41 registros.

## Temas sem evidência

Nenhum.

Ausência de evidência não deve ser interpretada como posição contrária.

## Validação

Os registros devem ser validados por `proposal_evidence.schema.json` e `validate_evidence.py`. Erros encontrados antes da entrega: nenhum após a validação estrutural final.

## Limitações

- O identificador real do modelo não estava disponível e foi registrado como `unavailable`; isso não representa um nome de modelo.
- O conteúdo deriva apenas do texto extraído e pode conservar falhas da extração do PDF.
- Trechos originais foram recortados literalmente, sem correção silenciosa.
- Ausências de público, meta, prazo, recursos ou forma de execução estão registradas por evidência.
- A geração permaneceu isolada até a decisão humana; a cópia revisada foi criada somente após a aprovação explícita.

## Instruções para revisão humana

Conferir cada registro contra a página física indicada e revisar: literalidade do trecho, enquadramento no tema permitido, consolidação de repetições, nível de evidência, neutralidade do resumo, ação proposta, público e limitações.

- Aprovar somente quando trecho e página forem confirmados, o tema estiver correto, o nível seguir os critérios do prompt e resumo/limitações não acrescentarem inferências.
- Rejeitar quando o trecho não sustentar uma proposta, estiver associado ao tema errado ou não puder ser confirmado na fonte.
- Solicitar correção quando houver problema sanável de recorte, página, consolidação, nível, redação neutra ou limitação ausente.

A revisão humana foi registrada na seção seguinte; o manifesto geral da matriz permanece `pending`.

## Resultado da revisão humana

- Revisor: Hallisson Lima
- Data da revisão: 2026-09-23T02:52:56Z
- Registros revisados: 41
- Aprovados: 41
- Rejeitados: 0
- Pendentes neste piloto: 0
- Aprovações com ressalva metodológica: 2 (`guilherme_fonseca-saude-publica-004` e `guilherme_fonseca-emprego-e-renda-007`)
- Arquivo revisado: `data/reviewed/evidence/guilherme_fonseca.reviewed.json`

Os níveis de evidência foram preservados. A quantidade de ações reunidas não elevou nenhum nível. O manifesto geral da matriz continua `pending`, pois somente uma das oito candidaturas foi revisada.
