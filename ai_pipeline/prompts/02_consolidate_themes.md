# Consolidação temática

**Versão do prompt:** `consolidate-themes-v1.0.0`

## Objetivo

Agrupar evidências revisadas do mesmo candidato e tema sem perder a rastreabilidade de cada fonte.

## Fontes permitidas e entrada

Use somente registros JSON que já tenham sido validados pelo schema, com `review_status: "approved"`. A entrada contém `candidate_id`, registros completos de evidência e a lista de temas autorizados. Não consulte fontes externas nem texto não vinculado por ID.

## Saída JSON

Retorne somente JSON com `candidate_id`, `prompt_version`, `model`, `generated_at`, `groups` e `absence_report`. Cada grupo contém `group_id`, `candidate_id`, `theme`, `subtheme`, `evidence_ids` e `source_evidence`. Cada item de `source_evidence` preserva todos os campos obrigatórios do schema: `evidence_id`, candidato, tema, nível, resumo, trecho original, página, arquivo, SHA-256, público, ação, limitações, versão, modelo, datas e revisão.

Campos obrigatórios de cada evidência: `evidence_id`, `candidate_id`, `theme`, `subtheme`, `evidence_level`, `neutral_summary`, `original_excerpt`, `page`, `source_file`, `source_sha256`, `target_population`, `proposed_action`, `limitations`, `prompt_version`, `model`, `generated_at`, `review_status`, `reviewed_at`, `reviewer`, `review_notes`.

Use IDs estáveis `<candidate_id>-<theme_slug>-group-<sequencial>` e `prompt_version: "consolidate-themes-v1.0.0"`.

## Regras

- Não misture candidatos, não altere páginas, trechos, hashes ou decisões humanas e não transforme repetição em maior força de evidência.
- Tema sem evidência aprovada entra em `absence_report`; ausência nunca é evidência nem pontuação zero.
- Ambiguidades, divergências e textos incompletos permanecem em `limitations`; não resolva por inferência.
- Se os registros apontarem ações incompatíveis, mantenha grupos distintos e sinalize a ambiguidade.
- A consolidação permanece `pending` até revisão humana obrigatória dos agrupamentos e IDs de origem.
