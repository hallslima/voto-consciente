# Fluxo de revisão humana por CSV

Este fluxo permite revisar evidências sem editar JSON. A exportação não toma decisões, e a importação não publica nada na matriz nem altera as evidências geradas.

## Exportar

Na raiz do projeto, execute:

```powershell
python ai_pipeline/scripts/export_review_csv.py
```

Para exportar apenas um candidato, informe `jeremias`, `camila` ou `victor_assis`:

```powershell
python ai_pipeline/scripts/export_review_csv.py jeremias
```

Os arquivos são gravados em `data/reviewed/review-csv/`, em UTF-8 com BOM e separados por ponto e vírgula. As 79 decisões saem vazias.

## Preencher no Excel ou Google Sheets

No Excel em português, abra o CSV diretamente. Se o assistente de importação aparecer, selecione UTF-8 e delimitador ponto e vírgula. No Google Sheets, use **Arquivo > Importar > Fazer upload**, escolha ponto e vírgula como separador e não converta textos automaticamente.

Somente estas colunas de decisão devem ser preenchidas:

- `document_decision`: `approved`, `needs_correction` ou `rejected`;
- `excerpt_matches_page`, `summary_preserves_meaning`, `theme_is_correct` e `evidence_level_is_correct`: `yes` ou `no`;
- `predominant_jurisdiction`: `state`, `federal`, `municipal`, `shared` ou `uncertain`;
- `matrix_eligibility`: `yes`, `no` ou `needs_adjustment`;
- `eligibility_justification`, `correction_notes`, `reviewer` e `reviewed_at`.

Não altere `evidence_id`, `candidate_id`, `candidate_name`, `theme`, `subtheme`, `evidence_level`, `neutral_summary`, `proposed_action`, `target_population`, `original_excerpt`, `page`, `source_file`, `source_sha256` ou `limitations`. O importador compara os campos protegidos com o JSON original e rejeita adulterações.

`approved` confirma documentalmente o registro; `needs_correction` devolve-o para correção; `rejected` rejeita-o documentalmente. Aprovação documental não significa elegibilidade para a matriz. Um item aprovado com `matrix_eligibility=no` permanece na base revisada, com a justificativa, e não deve ser usado na matriz.

Informe o nome identificável do revisor em `reviewer`. Em `reviewed_at`, use data e hora ISO 8601, por exemplo `2026-09-23T14:30:00-03:00`. Itens aprovados exigem todas as quatro confirmações. `rejected` e `needs_correction` exigem `correction_notes`. Elegibilidade `no` ou `needs_adjustment`, e competência `uncertain`, exigem `eligibility_justification`.

## Importar e corrigir erros

Depois de salvar o CSV preservando UTF-8 e ponto e vírgula, execute:

```powershell
python ai_pipeline/scripts/import_review_csv.py
```

Também é possível importar somente um candidato:

```powershell
python ai_pipeline/scripts/import_review_csv.py victor_assis
```

O importador valida o arquivo inteiro antes de escrever o JSON revisado. Havendo qualquer erro, nenhum registro daquele arquivo é promovido e um relatório `*.errors.json` é criado ao lado do CSV, com linha, campo e motivo. Corrija o CSV e execute novamente. Um arquivo válido gera `data/reviewed/evidence/<candidato>.reviewed.json`; os JSONs gerados originais permanecem intactos.

## Neutralidade

Confira o trecho na página indicada e avalie se o resumo preserva o sentido literal. Não acrescente intenção, viabilidade, juízo de valor ou informação externa. Use `correction_notes` para apontar objetivamente a divergência e `eligibility_justification` apenas para fundamentar competência e entrada na matriz. Em dúvida sobre a competência, registre `uncertain` e explique a dúvida.
