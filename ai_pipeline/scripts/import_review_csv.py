from __future__ import annotations

import argparse
import csv
from datetime import datetime
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ai_pipeline.scripts.export_review_csv import CANDIDATES, FIELDS


DOCUMENT_DECISIONS = {"approved", "needs_correction", "rejected"}
CONFIRMATIONS = {"yes", "no"}
JURISDICTIONS = {"state", "federal", "municipal", "shared", "uncertain"}
ELIGIBILITY = {"yes", "no", "needs_adjustment"}
PROTECTED = {
    "evidence_id", "candidate_id", "theme", "subtheme", "evidence_level",
    "neutral_summary", "original_excerpt", "page", "source_file", "source_sha256",
}
CONFIRMATION_FIELDS = {
    "excerpt_matches_page", "summary_preserves_meaning", "theme_is_correct",
    "evidence_level_is_correct",
}


def _iso8601(value: str) -> bool:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        return "T" in value
    except (TypeError, ValueError):
        return False


def _normal(value: object) -> str:
    return "" if value is None else str(value)


def validate_row(row: dict[str, str], original: dict, row_number: int) -> list[dict]:
    errors: list[dict] = []

    def add(field: str, message: str) -> None:
        errors.append({"row": row_number, "evidence_id": row.get("evidence_id", ""), "field": field, "error": message})

    for field in PROTECTED:
        if _normal(row.get(field)) != _normal(original.get(field)):
            add(field, "campo de evidência protegido foi alterado")
    decision = row.get("document_decision", "").strip()
    if decision not in DOCUMENT_DECISIONS:
        add("document_decision", "valor ausente ou inválido")
    for field in CONFIRMATION_FIELDS:
        value = row.get(field, "").strip()
        if value and value not in CONFIRMATIONS:
            add(field, "use yes ou no")
        if decision == "approved" and value not in CONFIRMATIONS:
            add(field, "confirmação obrigatória para approved")
    jurisdiction = row.get("predominant_jurisdiction", "").strip()
    if jurisdiction not in JURISDICTIONS:
        add("predominant_jurisdiction", "valor ausente ou inválido")
    eligibility = row.get("matrix_eligibility", "").strip()
    if eligibility not in ELIGIBILITY:
        add("matrix_eligibility", "valor ausente ou inválido")
    notes = row.get("correction_notes", "").strip()
    justification = row.get("eligibility_justification", "").strip()
    if decision in {"rejected", "needs_correction"} and not notes:
        add("correction_notes", f"obrigatório para {decision}")
    if eligibility in {"no", "needs_adjustment"} and not justification:
        add("eligibility_justification", f"obrigatória para elegibilidade {eligibility}")
    if jurisdiction == "uncertain" and not justification:
        add("eligibility_justification", "obrigatória para competência uncertain")
    if not row.get("reviewer", "").strip():
        add("reviewer", "não pode estar vazio")
    reviewed_at = row.get("reviewed_at", "").strip()
    if not reviewed_at or not _iso8601(reviewed_at):
        add("reviewed_at", "deve ser uma data ISO 8601 com data e hora")
    return errors


def import_candidate(candidate_id: str, root: Path = ROOT, csv_path: Path | None = None) -> tuple[Path | None, Path]:
    if candidate_id not in CANDIDATES:
        raise ValueError(f"candidato não suportado: {candidate_id}")
    _, csv_name = CANDIDATES[candidate_id]
    csv_path = csv_path or root / "data/reviewed/review-csv" / csv_name
    source_path = root / "data/generated/evidence" / f"{candidate_id}.generated.json"
    output_path = root / "data/reviewed/evidence" / f"{candidate_id}.reviewed.json"
    report_path = csv_path.with_suffix(".errors.json")
    source = json.loads(source_path.read_text(encoding="utf-8"))
    originals = {record["evidence_id"]: record for record in source["records"]}
    errors: list[dict] = []
    rows: list[dict[str, str]] = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        if reader.fieldnames != FIELDS:
            errors.append({"row": 1, "field": "header", "error": "cabeçalho ou ordem de colunas inválida"})
        rows = list(reader)
    if len(rows) != len(originals):
        errors.append({"row": 0, "field": "rows", "error": f"esperadas {len(originals)} linhas; encontradas {len(rows)}"})
    seen: set[str] = set()
    for number, row in enumerate(rows, start=2):
        evidence_id = row.get("evidence_id", "")
        if evidence_id in seen:
            errors.append({"row": number, "evidence_id": evidence_id, "field": "evidence_id", "error": "evidence_id duplicado"})
            continue
        seen.add(evidence_id)
        original = originals.get(evidence_id)
        if original is None:
            errors.append({"row": number, "evidence_id": evidence_id, "field": "evidence_id", "error": "evidence_id desconhecido"})
            continue
        errors.extend(validate_row(row, original, number))
    for missing in originals.keys() - seen:
        errors.append({"row": 0, "evidence_id": missing, "field": "evidence_id", "error": "registro ausente no CSV"})
    if errors:
        report = {"status": "rejected", "candidate_id": candidate_id, "error_count": len(errors), "errors": errors}
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return None, report_path

    reviewed_records = []
    for row in rows:
        original = dict(originals[row["evidence_id"]])
        decision = row["document_decision"].strip()
        original.update({
            "review_status": {"approved": "approved", "rejected": "rejected", "needs_correction": "pending"}[decision],
            "reviewer": row["reviewer"].strip(),
            "reviewed_at": row["reviewed_at"].strip(),
            "review_notes": row["correction_notes"].strip(),
            "document_decision": decision,
            "excerpt_matches_page": row["excerpt_matches_page"].strip(),
            "summary_preserves_meaning": row["summary_preserves_meaning"].strip(),
            "theme_is_correct": row["theme_is_correct"].strip(),
            "evidence_level_is_correct": row["evidence_level_is_correct"].strip(),
            "predominant_jurisdiction": row["predominant_jurisdiction"].strip(),
            "matrix_eligibility": row["matrix_eligibility"].strip(),
            "eligibility_justification": row["eligibility_justification"].strip(),
            "correction_notes": row["correction_notes"].strip(),
        })
        reviewed_records.append(original)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {**source, "records": reviewed_records, "review_source": csv_path.relative_to(root).as_posix()}
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if report_path.exists():
        report_path.unlink()
    return output_path, report_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Valida e importa decisões humanas de um CSV.")
    parser.add_argument("candidates", nargs="*", choices=sorted(CANDIDATES))
    args = parser.parse_args()
    failed = False
    for candidate_id in args.candidates or CANDIDATES:
        output, report = import_candidate(candidate_id)
        if output is None:
            failed = True
            print(f"ERRO: {candidate_id} rejeitado; consulte {report.relative_to(ROOT)}")
        else:
            print(f"OK: {candidate_id} importado em {output.relative_to(ROOT)}")
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
