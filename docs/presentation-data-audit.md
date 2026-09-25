# Auditoria de dados da apresentação

Auditoria realizada em 24 de setembro de 2026 antes da implementação da nova apresentação. O recorte publicado contém somente candidaturas com `registration_status = Deferido`.

| Indicador | Valor confirmado | Arquivo usado como fonte | Observação ou limitação |
| --- | ---: | --- | --- |
| Candidaturas no recorte atual | 7 | `data/candidates.json` | Todos os sete registros atuais estão deferidos. O oitavo registro citado em materiais antigos foi removido do recorte após indeferimento. |
| Planos oficiais no recorte atual | 7 | `data/candidates.json` e `data/generated/extraction_manifest.json` | Há um plano associado a cada candidatura deferida. O manifesto preserva oito extrações históricas, incluindo uma candidatura fora do recorte. |
| Páginas analisadas no recorte atual | 311 | `data/generated/extraction_manifest.json` | Soma das páginas dos sete documentos associados às candidaturas atuais: 8 + 86 + 30 + 8 + 106 + 66 + 7. O total histórico de oito documentos é 318. |
| Temas | 7 | `data/questions.json` | Sete valores distintos no campo `theme`. |
| Perguntas publicadas | 7 | `data/questions.json` e `/api/bootstrap` | O bootstrap expõe as sete perguntas do arquivo publicado. |
| Participantes da pesquisa própria | 135 | `data/research_evidence.json` | Amostra por conveniência; não representa todo o eleitorado de Pernambuco. |
| Documentos processados por OCR | 1 | `data/generated/extraction_manifest.json` | Apenas `raquel-lyra-55.pdf` registra método `ocr-tesseract-por`. |
| Evidências revisadas e aprovadas | 41 | `data/reviewed/evidence/guilherme_fonseca.reviewed.json` | Registros com `review_status = approved`. O manifesto de publicação da matriz continua pendente e não permite afirmar que toda a base passou por revisão humana. |
| Evidências pendentes elegíveis | 52 | `data/generated/evidence/*.generated.json` e arquivos revisados | São 29 de Camila e 23 de Victor Assis. As 41 de Guilherme possuem versão revisada aprovada. Outras 27 pendências históricas pertencem à candidatura indeferida e não entram na apresentação. |
| Testes aprovados antes da implementação | 120 | execução de `.\.venv\Scripts\python.exe -m pytest -q` | Resultado da linha de base em 24/09/2026. O total final deve ser informado após os novos testes. |

Após a inclusão dos testes da apresentação, a validação final passou a **135 testes aprovados**. A apresentação mostra “Mais de 100 testes automatizados” e informa 135 como o total exato da validação atual.

## Divergências resolvidas

- **7 ou 8 candidaturas:** 7 é o total atual elegível. O manifesto histórico ainda contém oito documentos.
- **311 ou 318 páginas:** 311 pertencem aos sete planos do recorte atual; 318 incluem o documento histórico da candidatura indeferida.
- **135 ou 136 participantes:** o arquivo de pesquisa registra `sample_size: 135`; não há fonte atual para 136.
- **5 ou 7 perguntas:** `data/questions.json` e o bootstrap contêm 7 perguntas.
- **79 ou 52 evidências pendentes:** 79 é o total ainda não revisado dos três pilotos históricos; 52 pertencem a candidaturas atualmente elegíveis.

## Escopo e fontes externas

Não foi localizada fonte registrada que comprove a frase “517 candidatos a deputado estadual”. A apresentação usa a formulação conservadora: “Em uma eleição completa, o eleitor ainda precisa lidar com centenas de candidaturas para diferentes cargos.” Deputados não fazem parte do recorte atual do MVP.

A pesquisa própria, a pesquisa Quaest referente ao Rio de Janeiro e a reportagem nacional da Veja de 2018 são apresentadas como contextos distintos. Nenhum percentual externo é generalizado para Pernambuco.

## URL pública

Os arquivos de implantação descrevem Netlify e Render, mas não confirmam de forma inequívoca um único domínio do frontend: `docs/deployment.md` contém um exemplo diferente do endereço fornecido no pedido. A aplicação centraliza o endereço em `VITE_PUBLIC_SITE_URL`; quando ausente, usa a origem atual do navegador. O exemplo de ambiente é `https://voto-consciente.netlify.app`.

## Integridade dos arquivos protegidos — antes

| Arquivo | SHA-256 antes |
| --- | --- |
| `scoring.py` | `8d40d85428646c8f80dce63ffc8d7e244f5600cab4df8d93247449280a04c81d` |
| `data/candidates.json` | `56c0a501270d95e5dc9d9506da1b8593b849f5f48ab976e3cfa515994f73097d` |
| `data/questions.json` | `ef317931d6ac8075072bb29cf3d14a3a18d237fc33492a5223fe3311dc371bea` |
| `data/research_evidence.json` | `ebed1621ca2511e9044a7bb0224dbe2b0120732a5f3c33bf6f95123242fef587` |
| `data/generated/extraction_manifest.json` | `37e3ba1f0f4502289619b781749d9884b92f1c9be917922c6e6ac9b795340e61` |
| `data/reviewed/published_matrix_manifest.json` | `a346e1747ee60ed6da01af68f0836fb1b6f77c073790f9f73aa4da428fb88268` |
| `data/reviewed/evidence/guilherme_fonseca.reviewed.json` | `9a767c9bb1a0e4e5ff569f0d43cc810114517efe818a5c993237ce9ac09d575f` |

Os PDFs já possuem hashes individuais no manifesto de extração. A verificação final deve confirmar que todos os valores acima permanecem iguais.

## Integridade dos arquivos protegidos — depois

Na verificação final, todos os hashes da tabela “antes” permaneceram idênticos. A implementação não alterou o motor matemático, os dados políticos, os manifestos, as evidências revisadas nem os PDFs.
