# Geração de perguntas candidatas

**Versão do prompt:** `generate-questions-v1.0.0`

## Objetivo

Gerar rascunhos neutros de perguntas e alternativas a partir de contrastes documentados.

## Fontes permitidas e entrada

Use somente contrastes aprovados e suas evidências completas. Entrada JSON: `theme`, `contrasts`, `candidate_ids`, `generation_mode`, `model`, `generated_at`. Não use preferências do grupo, notícias, plataformas externas ou conhecimento do modelo.

## Saída JSON

Retorne somente um array. Cada objeto contém `question_candidate_id`, `theme`, `text`, `alternatives` (`alternative_id`, `text`, `evidence_ids`), `candidate_ids`, `source_evidence`, `limitations`, `ambiguities`, `prompt_version`, `model`, `generated_at`, `review_status`, `reviewed_at`, `reviewer`, `review_notes`. `source_evidence` preserva todos os campos obrigatórios do schema, incluindo candidato, página, trecho e SHA-256.

Campos obrigatórios de cada evidência: `evidence_id`, `candidate_id`, `theme`, `subtheme`, `evidence_level`, `neutral_summary`, `original_excerpt`, `page`, `source_file`, `source_sha256`, `target_population`, `proposed_action`, `limitations`, `prompt_version`, `model`, `generated_at`, `review_status`, `reviewed_at`, `reviewer`, `review_notes`.

Use IDs estáveis `<theme_slug>-question-<sequencial>` e alternativas `A`, `B`, `C`...; use `prompt_version: "generate-questions-v1.0.0"`, status `pending`, revisão e revisor nulos.

## Regras

- Cada alternativa precisa de ao menos um `evidence_id` aprovado; não citar candidato ou partido no texto.
- Ausência de evidência não vira alternativa nem posição. Registre candidaturas/temas ausentes em `limitations`.
- Não inferir, combinar ações incompatíveis ou esconder ambiguidade; registre dúvida em `ambiguities`.
- Não publicar, inserir em `questions.json` ou atribuir compatibilidades automaticamente.
- Revisão humana obrigatória deve conferir neutralidade, pergunta dupla, cobertura, fontes, páginas e trechos.
