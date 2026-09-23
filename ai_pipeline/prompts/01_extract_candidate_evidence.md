# Extração individual de evidências

**Versão do prompt:** `extract-evidence-v1.0.0`

## Objetivo

Extrair evidências verificáveis de um único plano de governo, sem comparar candidaturas e sem completar lacunas.

## Fontes permitidas e entrada

Use exclusivamente o texto do PDF indicado em `source_file`, acompanhado de `source_sha256`, páginas/seções, `candidate_id`, nome do candidato, temas autorizados, modelo e data UTC da execução. Não use internet, memória do modelo, notícias ou planos de outros candidatos.

Entrada JSON: `candidate_id`, `candidate_name`, `source_file`, `source_sha256`, `pages` (`page`, `text`), `allowed_themes`, `model`, `generated_at`.

## Saída JSON

Retorne somente um objeto JSON com `records` e `absence_report`. Cada item de `records` deve obedecer a `proposal_evidence.schema.json` e conter obrigatoriamente: `evidence_id`, `candidate_id`, `theme`, `subtheme`, `evidence_level`, `neutral_summary`, `original_excerpt`, `page`, `source_file`, `source_sha256`, `target_population`, `proposed_action`, `limitations`, `prompt_version`, `model`, `generated_at`, `review_status`, `reviewed_at`, `reviewer`, `review_notes`.

Use `evidence_id` estável no formato `<candidate_id>-<theme_slug>-<sequencial>`. Copie candidato, arquivo e hash da entrada. Use `prompt_version: "extract-evidence-v1.0.0"`, `review_status: "pending"`, `reviewed_at: null` e `reviewer: null`.

## Regras

- `page` deve conter número da página ou indicação clara da seção; `original_excerpt` deve ser transcrição literal.
- Não infira ação, público, intenção, causalidade ou posição ausente. Registre ambiguidades e contexto insuficiente em `limitations` e mantenha nível conservador.
- Não crie registro de evidência quando nada for localizado. Registre temas ausentes em `absence_report`, com tema, páginas pesquisadas e motivo.
- Evidência repetida não aumenta nível. OCR incerto, texto truncado ou localização duvidosa deve constar em `limitations`.
- Nenhuma saída é publicável sem revisão humana obrigatória do trecho, página, tema, nível, resumo e limitações.
