# Fluxo de revisão humana por CSV

## Finalidade e responsabilidades

O fluxo permite que integrantes designados confiram as evidências documentais sem editar JSON. O exportador apenas prepara planilhas: ele nunca aprova, rejeita ou infere decisões. Cada revisor humano é responsável por conferir o trecho na página indicada, preencher seu nome real e registrar a data e hora da revisão.

Aprovação documental e elegibilidade para a matriz são decisões diferentes. `document_decision=approved` significa que trecho, resumo, tema e nível foram conferidos. `matrix_eligibility=yes` é uma decisão adicional sobre uso na matriz. Uma evidência pode ser documentalmente aprovada e não elegível; ela permanece na base revisada, vinculada à justificativa, mas a consolidação a exclui.

## Exportação

Execute na raiz do projeto:

```powershell
.\.venv\Scripts\python.exe ai_pipeline\scripts\export_review_csv.py --candidate jeremias
.\.venv\Scripts\python.exe ai_pipeline\scripts\export_review_csv.py --candidate camila
.\.venv\Scripts\python.exe ai_pipeline\scripts\export_review_csv.py --candidate victor_assis
.\.venv\Scripts\python.exe ai_pipeline\scripts\export_review_csv.py --all
```

Os arquivos ficam em `data/reviewed/review-csv/`, com uma evidência por linha, ordem estável, UTF-8 com BOM e separador ponto e vírgula. Listas em `limitations` usam JSON, uma serialização reversível que não perde itens.

## Excel e Google Sheets

No Excel, abra ou importe o arquivo escolhendo UTF-8 e ponto e vírgula. Preserve UTF-8, mantenha o separador `;`, não altere cabeçalhos, não ordene apenas uma coluna isoladamente e salve como **CSV UTF-8**. Não use fórmulas nas células de decisão.

No Google Sheets, escolha **Arquivo > Importar > Fazer upload**, desative a conversão automática de texto e selecione ponto e vírgula como separador. Ao concluir, baixe novamente como CSV e confira a codificação antes da importação.

As colunas 1 a 14 são imutáveis: `evidence_id`, `candidate_id`, `candidate_name`, `theme`, `subtheme`, `evidence_level`, `neutral_summary`, `proposed_action`, `target_population`, `original_excerpt`, `page`, `source_file`, `source_sha256` e `limitations`.

Somente as colunas 15 a 25 podem ser preenchidas: `document_decision`, as quatro confirmações, `predominant_jurisdiction`, `matrix_eligibility`, `eligibility_justification`, `correction_notes`, `reviewer` e `reviewed_at`.

## Valores e regras

- `document_decision`: `approved`, `needs_correction` ou `rejected`.
- Confirmações: `yes` ou `no`.
- `predominant_jurisdiction`: `state`, `federal`, `municipal`, `shared` ou `uncertain`.
- `matrix_eligibility`: `yes`, `no` ou `needs_adjustment`.
- `reviewed_at`: data e hora ISO 8601, como `2026-09-23T14:30:00-03:00`.

Uma aprovação exige `yes` nas quatro confirmações. `needs_correction` e `rejected` exigem `correction_notes`. Elegibilidade `no` ou `needs_adjustment`, e competência `uncertain`, exigem `eligibility_justification`. Revisor, data, competência e elegibilidade são sempre obrigatórios.

Exemplo fictício: uma proposta documentada de atribuição exclusivamente federal pode receber `document_decision=approved`, quatro confirmações `yes`, `predominant_jurisdiction=federal`, `matrix_eligibility=no` e uma justificativa objetiva. Isso não publica a evidência.

## Importação e mensagens de erro

```powershell
.\.venv\Scripts\python.exe ai_pipeline\scripts\import_review_csv.py --candidate jeremias
.\.venv\Scripts\python.exe ai_pipeline\scripts\import_review_csv.py --candidate camila
.\.venv\Scripts\python.exe ai_pipeline\scripts\import_review_csv.py --candidate victor_assis
.\.venv\Scripts\python.exe ai_pipeline\scripts\import_review_csv.py --all
```

O importador compara canonicamente todas as colunas imutáveis com o JSON gerado, valida as decisões pelo schema e acumula todos os erros. Os relatórios ficam em `data/reviewed/review-reports/` e indicam linha, campo e motivo, além das contagens da tentativa.

Mensagens como `coluna imutável foi alterada`, `evidence_id duplicado`, `registro ausente no CSV` ou falhas de enumeração indicam o que corrigir. Corrija apenas a planilha, preserve todas as linhas e execute novamente. Nenhum JSON parcial é criado.

Quando todas as linhas são válidas, o arquivo é promovido para `data/reviewed/evidence/`. Os dados documentais permanecem intactos; `needs_correction` continua `pending`; rejeitados são preservados como `rejected`; decisões de competência e elegibilidade ficam em uma estrutura vinculada por `evidence_id`.

## Neutralidade e limitações

O revisor deve avaliar somente o conteúdo documental, sem inferir intenção, viabilidade, qualidade política ou informação externa. `correction_notes` deve descrever objetivamente a divergência. `eligibility_justification` deve tratar apenas da competência e do possível uso na matriz.

O CSV não substitui consulta ao documento original, não resolve ambiguidades políticas e não publica na matriz. A publicação exige etapa separada e autorização explícita. É proibida qualquer aprovação automática ou preenchimento de decisão pelo script.
