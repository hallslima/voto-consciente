from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
GENERATED = ROOT / "data/generated/evidence/guilherme_fonseca.generated.json"
REVIEWED = ROOT / "data/reviewed/evidence/guilherme_fonseca.reviewed.json"
AUDIT = ROOT / "data/generated/evidence/guilherme_fonseca.generation-audit.json"
REPORT = ROOT / "docs/pilot-evidence-guilherme.md"
REVIEWER = "Hallisson Lima"
BASE_NOTE = "Registro aprovado após conferência humana de trecho, página, resumo, tema e nível no documento original."
SPECIAL_NOTES = {
    "guilherme_fonseca-saude-publica-004": (
        "Registro aprovado com escopo abrangente. O trecho reúne ações relacionadas à produção pública pelo LAFEPE, "
        "expansão da rede e trabalhadores da saúde. A revisão considerou que o agrupamento preserva a abordagem integrada "
        "apresentada no documento. A repetição de ações não gera pontuação adicional."
    ),
    "guilherme_fonseca-emprego-e-renda-007": (
        "Registro aprovado com caráter transversal. O trecho reúne acesso ao emprego, formação, inclusão e direitos. "
        "A revisão considerou que o agrupamento preserva a abordagem integrada do documento. Elementos externos ao tema "
        "principal não geram pontuação adicional."
    ),
}
REVIEW_FIELDS = {"review_status", "reviewer", "reviewed_at", "review_notes"}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def main() -> None:
    generated = json.loads(GENERATED.read_text(encoding="utf-8"))
    if len(generated["records"]) != 41:
        raise ValueError(f"Esperados 41 registros; encontrados {len(generated['records'])}.")

    reviewed_at = utc_now()
    reviewed = deepcopy(generated)
    for record in reviewed["records"]:
        record["review_status"] = "approved"
        record["reviewer"] = REVIEWER
        record["reviewed_at"] = reviewed_at
        extra = SPECIAL_NOTES.get(record["evidence_id"])
        record["review_notes"] = BASE_NOTE if extra is None else f"{BASE_NOTE} {extra}"

    for before, after in zip(generated["records"], reviewed["records"], strict=True):
        changed = {key for key in before if before[key] != after[key]}
        if changed != REVIEW_FIELDS:
            raise RuntimeError(f"Campos inesperados alterados em {before['evidence_id']}: {sorted(changed)}")
        if after["evidence_level"] != before["evidence_level"]:
            raise RuntimeError(f"Nível alterado em {before['evidence_id']}.")

    REVIEWED.parent.mkdir(parents=True, exist_ok=True)
    REVIEWED.write_text(json.dumps(reviewed, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    audit.update({
        "review_status": "approved",
        "reviewed_count": 41,
        "approved_count": 41,
        "rejected_count": 0,
        "pending_count": 0,
        "reviewer": REVIEWER,
        "reviewed_at": reviewed_at,
        "methodological_qualification_count": 2,
        "methodological_qualifications": [
            {"evidence_id": evidence_id, "review_note": note}
            for evidence_id, note in SPECIAL_NOTES.items()
        ],
        "reviewed_output": REVIEWED.relative_to(ROOT).as_posix(),
    })
    AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    report = REPORT.read_text(encoding="utf-8")
    report = report.replace("- Status de todos os registros: `pending`", "- Status na geração: `pending`")
    report = report.replace(
        "- Nenhum registro foi revisado, aprovado ou movido para `data/reviewed`.",
        "- A geração permaneceu isolada até a decisão humana; a cópia revisada foi criada somente após a aprovação explícita.",
    )
    report = report.replace(
        "A aprovação exige preenchimento posterior de revisor e data de revisão. Este piloto permanece integralmente `pending`.",
        "A revisão humana foi registrada na seção seguinte; o manifesto geral da matriz permanece `pending`.",
    )
    marker = "\n## Resultado da revisão humana\n"
    if marker in report:
        report = report.split(marker, 1)[0].rstrip() + "\n"
    review_section = f"""

## Resultado da revisão humana

- Revisor: {REVIEWER}
- Data da revisão: {reviewed_at}
- Registros revisados: 41
- Aprovados: 41
- Rejeitados: 0
- Pendentes neste piloto: 0
- Aprovações com ressalva metodológica: 2 (`guilherme_fonseca-saude-publica-004` e `guilherme_fonseca-emprego-e-renda-007`)
- Arquivo revisado: `data/reviewed/evidence/guilherme_fonseca.reviewed.json`

Os níveis de evidência foram preservados. A quantidade de ações reunidas não elevou nenhum nível. O manifesto geral da matriz continua `pending`, pois somente uma das oito candidaturas foi revisada.
"""
    REPORT.write_text(report.rstrip() + review_section, encoding="utf-8")
    print(f"Revisão registrada: 41 aprovados por {REVIEWER} em {reviewed_at}.")


if __name__ == "__main__":
    main()
