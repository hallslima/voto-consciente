# Metodologia operacional de IA

## Princípios

A IA é opcional e atua somente antes da publicação. Ela não recebe respostas dos usuários, não calcula ICT, não altera compatibilidades e não publica perguntas. Cada evidência mantém ID, candidato, trecho literal, página/seção, arquivo, SHA-256, prompt, modelo e datas. Somente uma pessoa pode aprovar um registro.

Fluxo obrigatório:

```text
PDF oficial → extração → geração assistida → validação → revisão humana
→ aprovação → consolidação → manifesto e publicação
```

Saídas pendentes ficam em `data/generated/`; aprovadas ficam em `data/reviewed/`. Os arquivos `example.*.json` são fictícios e nunca são entrada do runtime ou de uma publicação real.

## 1. PDF oficial e extração

Confirme manualmente a candidatura e a origem oficial do PDF. Extraia texto por página e calcule o hash:

```powershell
.\.venv\Scripts\python.exe ai_pipeline\scripts\extract_pdf_text.py public\documents\government-plans\ARQUIVO.pdf --output data\generated\CANDIDATO.extracted.json
```

Se `ocr_required` for `true`, interrompa o fluxo e registre a limitação. OCR não faz parte desta etapa.

## 2. Geração assistida

Envie a extração de apenas um plano ao prompt `01_extract_candidate_evidence.md`. Informe `candidate_id`, nome, arquivo, SHA-256, páginas, temas, modelo e data UTC. Grave somente `records` em:

```text
data/generated/CANDIDATO.evidence.json
```

Registre a versão exata do prompt e do modelo. Não copie o exemplo fictício para uma execução real.

## 3. Validação

Valide a lista de registros gerada:

```powershell
.\.venv\Scripts\python.exe ai_pipeline\scripts\validate_evidence.py data\generated\CANDIDATO.evidence.json
```

O comando executa o JSON Schema e `validate_audit()`. Ele bloqueia campos vazios, nível inválido, página/trecho/hash ausentes, status desconhecido e aprovação sem revisor ou data.

## 4. Revisão humana

Uma pessoa confere no PDF original: candidato, trecho, página/seção, tema, subtema, nível, resumo, público, ação, limitações e hash. Registros ainda não decididos permanecem `pending`. Rejeitados recebem `rejected` e notas. Aprovados devem receber:

```json
{
  "review_status": "approved",
  "reviewed_at": "DATA UTC ISO-8601",
  "reviewer": "IDENTIFICAÇÃO REAL DO REVISOR",
  "review_notes": "DECISÃO E LIMITAÇÕES"
}
```

Não invente nomes ou datas. Após a conferência, grave o arquivo real em `data/reviewed/` e execute novamente o validador.

## 5. Consolidação

Consolide explicitamente um arquivo revisado. O script descarta tudo que não seja `approved`:

```powershell
.\.venv\Scripts\python.exe ai_pipeline\scripts\consolidate_matrix.py data\reviewed\CANDIDATO.reviewed.json data\reviewed\CANDIDATO.approved.json
```

Use os prompts 2 e 3 apenas sobre registros aprovados. Preserve `evidence_id`, página, trecho e hash em todas as etapas.

## 6. Perguntas candidatas

Gere apenas rascunhos pendentes:

```powershell
.\.venv\Scripts\python.exe ai_pipeline\scripts\generate_question_candidates.py data\reviewed\EVIDENCIAS.approved.json data\generated\questions.candidates.json
```

Os prompts 4 e 5 apoiam geração e revisão de viés. Nenhum comando altera `data/questions.json`; essa promoção exige decisão humana documentada.

## 7. Manifesto e publicação

Antes de publicar, atualize `data/reviewed/published_matrix_manifest.json` com versão, data, revisores reais, arquivos revisados, SHA-256, perguntas vinculadas por `evidence_id`, limitações e aprovação. Calcule cada hash com:

```powershell
Get-FileHash data\reviewed\ARQUIVO.reviewed.json -Algorithm SHA256
```

Enquanto faltarem registros reais revisados, mantenha `approval_status: "pending"`, `published_at: null`, revisores e arquivos vazios. Um manifesto pendente não comprova a origem da matriz atual e não autoriza publicação.

## 8. Verificação do projeto

```powershell
.\.venv\Scripts\python.exe -m pytest -v
npm.cmd run build
```

Riscos que sempre exigem conferência humana: alucinação, omissão, viés, página incorreta, falsa equivalência, OCR imperfeito e perda de vínculo entre pergunta e evidência.
