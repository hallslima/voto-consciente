# Identificação de contrastes

**Versão do prompt:** `identify-contrasts-v1.0.0`

## Objetivo

Identificar diferenças observáveis entre abordagens documentadas, sem avaliar qual é melhor.

## Fontes permitidas e entrada

Use apenas grupos consolidados e aprovados, contendo registros completos do schema. A entrada JSON informa `theme`, `candidate_ids`, `groups`, `model` e `generated_at`. Não use reputação, partido, notícias, conhecimento externo ou ausência como posição política.

## Saída JSON

Retorne somente JSON com `prompt_version`, `model`, `generated_at`, `theme`, `contrasts`, `absence_report` e `limitations`. Cada contraste contém `contrast_id`, `description`, `candidate_ids`, `evidence_ids` e `source_evidence`. `source_evidence` preserva candidato analisado, página, trecho original e todos os demais campos obrigatórios de `proposal_evidence.schema.json`.

Campos obrigatórios de cada evidência: `evidence_id`, `candidate_id`, `theme`, `subtheme`, `evidence_level`, `neutral_summary`, `original_excerpt`, `page`, `source_file`, `source_sha256`, `target_population`, `proposed_action`, `limitations`, `prompt_version`, `model`, `generated_at`, `review_status`, `reviewed_at`, `reviewer`, `review_notes`.

Use `contrast_id` estável `<theme_slug>-contrast-<sequencial>` e `prompt_version: "identify-contrasts-v1.0.0"`.

## Regras

- Toda afirmação deve apontar para `evidence_ids`; não inferir contraste além das ações literais.
- Linguagem ambígua, escopo diferente ou propostas parcialmente comparáveis deve ser descrito em `limitations`.
- Candidatura sem evidência entra em `absence_report` e não pode ser apresentada como contrária às demais.
- Não usar enquadramento moral, recomendação, ranking ou intensidade não documentada.
- Todos os contrastes ficam pendentes de revisão humana obrigatória das fontes, páginas, trechos e neutralidade.
