# Dicionário de dados

`questions.json`: `id`, `theme`, `text` e `options`; cada opção tem `id` e `text`.

`candidates.json`: `id`, `name`, `party`, `number`, `registration_status`, `photo_url`, `profile_url`, `official_data_url`, `local_plan_url`, `plan_document`, `social_links` e `positions`. Cada posição tem `primary_option`, `compatibility`, `evidence_level`, `summary`, `source` e `page`.

Evidência: `candidate_id`, `theme`, `subtheme`, `evidence_level`, `neutral_summary`, `original_excerpt`, `page`, `source_file`, `target_population`, `proposed_action`, `limitations`, `review_status` e `reviewer`.

Auditoria: `candidate_id`, `source_file`, `source_sha256`, `prompt_version`, `model`, `generated_at`, `reviewed_at`, `reviewer` e `status`.

Pesquisa: `sample_size`, `sampling_method`, `geographic_focus`, `results`, `limitations`, `form_url` e `spreadsheet_url`.
