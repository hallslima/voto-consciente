# Revisão de viés

**Versão do prompt:** `review-bias-v1.0.0`

## Objetivo

Produzir parecer assistido sobre neutralidade e rastreabilidade de uma pergunta candidata, sem aprová-la automaticamente.

## Fontes permitidas e entrada

Use apenas a pergunta candidata, alternativas, IDs e evidências completas fornecidas na entrada JSON. Não consulte fontes externas e não use opinião política ou conhecimento do modelo. A entrada inclui `question_candidate`, `source_evidence`, `model` e `generated_at`.

## Saída JSON

Retorne somente JSON com `review_id`, `question_candidate_id`, `candidate_ids`, `checks` (`leading_language`, `double_barreled`, `moral_framing`, `candidate_reference`, `unsupported_alternative`, `ambiguous_wording`), `findings`, `source_evidence`, `limitations`, `prompt_version`, `model`, `generated_at`, `review_status`, `reviewed_at`, `reviewer`, `review_notes`. `source_evidence` preserva os campos obrigatórios do schema, especialmente candidato, página, trecho original e hash.

Campos obrigatórios de cada evidência: `evidence_id`, `candidate_id`, `theme`, `subtheme`, `evidence_level`, `neutral_summary`, `original_excerpt`, `page`, `source_file`, `source_sha256`, `target_population`, `proposed_action`, `limitations`, `prompt_version`, `model`, `generated_at`, `review_status`, `reviewed_at`, `reviewer`, `review_notes`.

Use `review_id` estável `<question_candidate_id>-bias-review-<sequencial>`, `prompt_version: "review-bias-v1.0.0"` e sempre `review_status: "pending"`, `reviewed_at: null`, `reviewer: null`.

## Regras

- Compare cada alternativa somente com seus `evidence_ids`; não infira intenção ou equivalência.
- Ausência de evidência gera `unsupported_alternative: true`, nunca aprovação implícita.
- Ambiguidades e limitações devem ser descritas, não resolvidas por reescrita silenciosa.
- O modelo pode sugerir correção, mas não pode marcar `approved`, publicar ou alterar perguntas/evidências.
- A decisão final exige revisão humana obrigatória com nome, data e notas.
