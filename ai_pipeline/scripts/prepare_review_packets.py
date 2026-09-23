from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CONFIG = {
    "jeremias": {
        "name": "Professor Jeremias",
        "expected": 27,
        "packet": "jeremias-review.md",
        "decision": "jeremias.review.json",
    },
    "camila": {
        "name": "Professora Camila",
        "expected": 29,
        "packet": "camila-review.md",
        "decision": "camila.review.json",
    },
    "victor_assis": {
        "name": "Victor Assis",
        "expected": 23,
        "packet": "victor-assis-review.md",
        "decision": "victor_assis.review.json",
    },
}


def blank_decision(record: dict) -> dict:
    return {
        "evidence_id": record["evidence_id"],
        "documentary_decision": None,
        "excerpt_matches_page": None,
        "summary_preserves_meaning": None,
        "theme_correct": None,
        "level_correct": None,
        "predominant_competence": None,
        "matrix_eligibility": None,
        "eligibility_justification": "",
        "reviewer_notes": "",
        "reviewer_name": None,
        "reviewed_at": None,
        "review_status": "pending",
    }


def record_markdown(number: int, candidate_name: str, record: dict, pdf_path: str) -> str:
    limitations = "\n".join(f"- {item}" for item in record["limitations"]) or "- Nenhuma registrada."
    return f"""## {number}. `{record['evidence_id']}`

| Campo | Conteúdo |
|---|---|
| Candidato | {candidate_name} |
| Tema | {record['theme']} |
| Subtema | {record['subtheme']} |
| Nível de evidência | {record['evidence_level']} |
| Página física | {record['page']} |
| PDF | `{pdf_path}` |
| SHA-256 | `{record['source_sha256']}` |

**Resumo neutro:** {record['neutral_summary']}

**Ação proposta:** {record['proposed_action']}

**Público mencionado:** {record['target_population']}

**Trecho original:**

```text
{record['original_excerpt']}
```

**Limitações registradas:**

{limitations}

### Preenchimento humano

**Decisão documental:** [ ] aprovado  [ ] precisa de correção  [ ] rejeitado

**Correspondência do trecho com a página:** [ ] sim  [ ] não

**Resumo preserva o sentido:** [ ] sim  [ ] não

**Tema correto:** [ ] sim  [ ] não

**Nível correto:** [ ] sim  [ ] não

**Competência predominante:** [ ] estadual  [ ] federal  [ ] municipal  [ ] compartilhada  [ ] incerta

**Elegível para a matriz:** [ ] sim  [ ] não  [ ] depende de ajuste

**Justificativa da elegibilidade:**

> 

**Observações do revisor:**

> 

**Nome do revisor:** ________________________________________

**Data da revisão (ISO 8601):** ______________________________

---
"""


def main() -> None:
    packet_dir = ROOT / "docs/review-packets"
    decision_dir = ROOT / "data/reviewed/review-decisions"
    packet_dir.mkdir(parents=True, exist_ok=True)
    decision_dir.mkdir(parents=True, exist_ok=True)

    for candidate_id, config in CONFIG.items():
        evidence_path = ROOT / "data/generated/evidence" / f"{candidate_id}.generated.json"
        source_path = ROOT / "data/generated/extracted-text" / f"{candidate_id}.json"
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        source = json.loads(source_path.read_text(encoding="utf-8"))
        records = evidence["records"]
        if len(records) != config["expected"]:
            raise ValueError(f"{candidate_id}: esperados {config['expected']}, encontrados {len(records)}")
        if any(record["review_status"] != "pending" for record in records):
            raise ValueError(f"{candidate_id}: há evidência que não está pending")

        header = f"""# Pacote de revisão humana — {config['name']}

Este pacote contém **{len(records)} evidências ainda não revisadas**. Preencher o formulário não conclui a revisão nem promove automaticamente qualquer evidência.

## Regras de elegibilidade

- Aprovação documental e elegibilidade para a matriz são decisões distintas.
- Marcar como elegível quando houver ação dentro das competências do Governo de Pernambuco, atuação estadual indicada, adaptação clara ao estado ou competência compartilhada com participação estadual identificável.
- Marcar como não elegível quando a proposta depender exclusivamente do Governo Federal ou municipal, reproduzir programa nacional sem atuação estadual, não se relacionar claramente ao cargo de governador ou não permitir identificar ação aplicável a Pernambuco.
- Em dúvida, usar `depende de ajuste` ou competência `incerta`.
- Nenhuma evidência deve ser promovida sem decisão documental aprovada, revisor, data, decisão de elegibilidade e justificativa quando a elegibilidade for `não` ou `depende de ajuste`.

Fonte de evidências: `{evidence_path.relative_to(ROOT).as_posix()}`  
PDF: `{source['source_path']}`  
SHA-256: `{source['source_sha256']}`

---

"""
        body = "\n".join(
            record_markdown(index, config["name"], record, source["source_path"])
            for index, record in enumerate(records, start=1)
        )
        (packet_dir / config["packet"]).write_text(header + body, encoding="utf-8")

        decision_model = {
            "candidate_id": candidate_id,
            "candidate_name": config["name"],
            "source_evidence_file": evidence_path.relative_to(ROOT).as_posix(),
            "source_pdf": source["source_path"],
            "source_sha256": source["source_sha256"],
            "expected_evidence_count": config["expected"],
            "overall_status": "pending",
            "review_completed_at": None,
            "decisions": [blank_decision(record) for record in records],
        }
        (decision_dir / config["decision"]).write_text(
            json.dumps(decision_model, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
        print(f"{candidate_id}: {len(records)} itens preparados, status pending.")


if __name__ == "__main__":
    main()
