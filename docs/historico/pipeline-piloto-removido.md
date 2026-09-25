# Pipeline piloto removido

> Documento histórico. Este pipeline não faz parte da versão atual do MVP.

## O que foi o piloto

Foi uma experiência metodológica separada para extração de PDFs, reconhecimento óptico de caracteres, hashes documentais, evidências estruturadas, validação técnica, revisão por CSV, decisão de elegibilidade e preparação de um manifesto de publicação.

## Por que foi removido

O piloto aumentava a complexidade do repositório sem participar da execução do produto. Seus scripts, dependências, artefatos e testes próprios não eram importados pelo backend nem pelo frontend.

## Relação com a matriz publicada

A auditoria realizada antes da remoção confirmou que o runtime lê as perguntas de `data/questions.json` e a matriz de `data/candidates.json`. Não havia identificadores ou outro vínculo técnico que comprovasse que os registros do piloto alimentavam esses arquivos.

## Recuperação

O conteúdo removido permanece recuperável no histórico do Git a partir do commit de origem `dbd70ff` (`Merge pull request #5 from hallslima/feat/apresentacao-react`).

## Data da remoção

25 de setembro de 2026.
