# Requisitos originais da implementação

## Nota de rastreabilidade

O texto literal do primeiro pedido de implementação não está armazenado neste workspace nem no histórico Git disponível. Este documento preserva, sem completar lacunas por suposição, os requisitos recuperáveis da solicitação de auditoria e da etapa crítica de rastreabilidade confirmada pelo responsável do projeto.

Quando o texto original integral for recuperado, ele deve substituir esta reconstrução, mantendo esta nota no histórico de versão.

## Requisitos recuperados

1. Associar oito candidaturas às oito fotos e aos oito planos de governo.
2. Exibir as fotos nas áreas de resultado e disponibilizar os planos consultados.
3. Organizar o frontend em componentes e manter responsabilidades controladas em `src/main.jsx`.
4. Manter cinco prompts para extração, consolidação temática, contrastes, geração de perguntas e revisão de viés.
5. Validar evidências com JSON Schema e metadados completos de auditoria.
6. Separar saídas não revisadas em `data/generated/` e saídas revisadas em `data/reviewed/`.
7. Impedir que registros pendentes ou exemplos sejam consumidos pelo runtime.
8. Disponibilizar scripts de extração, validação, consolidação e geração de perguntas.
9. Documentar metodologia, arquitetura, fontes e limitações.
10. Preservar dados agregados e limitações da pesquisa própria.
11. Incluir a pesquisa própria na apresentação.
12. Classificar fontes externas e documentar trabalhos relacionados, incluindo o Tem Meu Voto.
13. Testar cálculo matemático, ativos e documentos.
14. Não armazenar segredos e manter a interface responsiva.
15. Manter o fluxo frontend/backend funcional e o README coerente.

## Primeira etapa crítica confirmada

- Tornar rastreável o processo do plano oficial até a publicação da matriz.
- Não alterar ICT, matriz de compatibilidade, perguntas publicadas ou design.
- Versionar prompts e exigir saída JSON, IDs, fontes, ausência, ambiguidade, proibição de inferência e revisão humana.
- Unificar evidência e auditoria em um schema.
- Bloquear aprovação sem revisor e data de revisão.
- Manter exemplos fictícios fora do runtime.
- Manter o manifesto como `pending` enquanto a revisão humana real não estiver comprovada.
- Não executar OCR, modularizar o frontend ou alterar a apresentação nesta etapa.
