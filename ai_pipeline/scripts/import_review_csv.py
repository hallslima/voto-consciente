from __future__ import annotations

import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ai_pipeline.scripts.export_review_csv import CANDIDATES, FIELDS, IMMUTABLE_FIELDS


DECISION_FIELDS = FIELDS[14:]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _error(row: int, field: str, message: str, evidence_id: str = "") -> dict:
    return {"row": row, "evidence_id": evidence_id, "field": field, "error": message}


def _canonical_limitations(value: object) -> str:
    if isinstance(value, str):
        value = json.loads(value)
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value):
        raise ValueError("limitations deve ser uma lista de textos em JSON")
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _expected_immutable(original: dict, candidate_name: str) -> dict[str, str]:
    expected = {field: str(original.get(field, "")) for field in IMMUTABLE_FIELDS}
    expected["candidate_name"] = candidate_name
    expected["limitations"] = _canonical_limitations(original.get("limitations", []))
    return expected


def _immutable_digest(values: dict[str, str]) -> str:
    canonical = json.dumps(values, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _decision(row: dict[str, str]) -> dict[str, str]:
    return {"evidence_id": row.get("evidence_id", ""), **{field: row.get(field, "").strip() for field in DECISION_FIELDS}}


def _schema_errors(decision: dict, validator: Draft202012Validator, row_number: int) -> list[dict]:
    errors = []
    for issue in sorted(validator.iter_errors(decision), key=lambda item: list(item.path)):
        field = str(next(iter(issue.path), "decision"))
        errors.append(_error(row_number, field, issue.message, decision.get("evidence_id", "")))
    for field, value in decision.items():
        if field != "evidence_id" and value.startswith(("=", "+", "-", "@")):
            errors.append(_error(row_number, field, "fórmulas não são permitidas", decision["evidence_id"]))
    reviewed_at = decision.get("reviewed_at", "")
    try:
        datetime.fromisoformat(reviewed_at.replace("Z", "+00:00"))
        if "T" not in reviewed_at:
            raise ValueError
    except ValueError:
        if not any(error["field"] == "reviewed_at" for error in errors):
            errors.append(_error(row_number, "reviewed_at", "deve ser data e hora ISO 8601", decision["evidence_id"]))
    return errors


def _summary(rows: list[dict[str, str]]) -> dict:
    decisions = Counter(row.get("document_decision", "").strip() for row in rows)
    eligibility = Counter(row.get("matrix_eligibility", "").strip() for row in rows)
    jurisdictions = Counter(row.get("predominant_jurisdiction", "").strip() for row in rows)
    reviewers = sorted({row.get("reviewer", "").strip() for row in rows if row.get("reviewer", "").strip()})
    return {
        "total_rows": len(rows), "approved": decisions["approved"], "rejected": decisions["rejected"],
        "needs_correction": decisions["needs_correction"], "eligible": eligibility["yes"],
        "not_eligible": eligibility["no"], "needs_adjustment": eligibility["needs_adjustment"],
        "jurisdictions": {key: jurisdictions[key] for key in ("state", "federal", "municipal", "shared", "uncertain")},
        "reviewers": reviewers,
    }


def _write_report(path: Path, candidate_id: str, csv_path: Path, rows: list[dict], errors: list[dict], status: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    report = {
        "candidate_id": candidate_id, "imported_file": csv_path.as_posix(), "imported_at": _now(),
        **_summary(rows), "error_count": len(errors), "errors": errors, "status": status,
    }
    path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def import_candidate(candidate_id: str, root: Path = ROOT, csv_path: Path | None = None) -> tuple[Path | None, Path]:
    if candidate_id not in CANDIDATES:
        raise ValueError(f"candidato não suportado: {candidate_id}")
    candidate_name, csv_name = CANDIDATES[candidate_id]
    csv_path = csv_path or root / "data/reviewed/review-csv" / csv_name
    source_path = root / "data/generated/evidence" / f"{candidate_id}.generated.json"
    output_path = root / "data/reviewed/evidence" / f"{candidate_id}.reviewed.json"
    report_path = root / "data/reviewed/review-reports" / f"{candidate_id.replace('_', '-')}-import-report.json"
    schema = json.loads((root / "ai_pipeline/schemas/review_decision.schema.json").read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    source = json.loads(source_path.read_text(encoding="utf-8"))
    originals = {record["evidence_id"]: record for record in source["records"]}
    errors: list[dict] = []
    rows: list[dict[str, str]] = []

    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=";")
        if reader.fieldnames != FIELDS:
            errors.append(_error(1, "header", "cabeçalho ou ordem de colunas inválida"))
        rows = list(reader)
    if len(rows) != len(originals):
        errors.append(_error(0, "rows", f"esperadas {len(originals)} linhas; encontradas {len(rows)}"))

    seen: set[str] = set()
    for number, row in enumerate(rows, start=2):
        evidence_id = row.get("evidence_id", "")
        if evidence_id in seen:
            errors.append(_error(number, "evidence_id", "evidence_id duplicado", evidence_id))
            continue
        seen.add(evidence_id)
        original = originals.get(evidence_id)
        if original is None:
            errors.append(_error(number, "evidence_id", "evidence_id desconhecido", evidence_id))
            continue
        try:
            actual = {field: row.get(field, "") for field in IMMUTABLE_FIELDS}
            actual["limitations"] = _canonical_limitations(actual["limitations"])
            expected = _expected_immutable(original, candidate_name)
            if _immutable_digest(actual) != _immutable_digest(expected):
                for field in IMMUTABLE_FIELDS:
                    if actual[field] != expected[field]:
                        errors.append(_error(number, field, "coluna imutável foi alterada", evidence_id))
        except (ValueError, json.JSONDecodeError) as exc:
            errors.append(_error(number, "limitations", str(exc), evidence_id))
        errors.extend(_schema_errors(_decision(row), validator, number))
    for missing in originals.keys() - seen:
        errors.append(_error(0, "evidence_id", "registro ausente no CSV", missing))

    if errors:
        _write_report(report_path, candidate_id, csv_path, rows, errors, "rejected")
        return None, report_path

    reviewed_records, review_decisions = [], []
    for row in rows:
        decision = _decision(row)
        original = dict(originals[decision["evidence_id"]])
        documentary = decision["document_decision"]
        original.update({
            "review_status": {"approved": "approved", "rejected": "rejected", "needs_correction": "pending"}[documentary],
            "reviewer": decision["reviewer"], "reviewed_at": decision["reviewed_at"],
            "review_notes": f"Decisão documental: {documentary}. {decision['correction_notes']}".strip(),
        })
        reviewed_records.append(original)
        review_decisions.append(decision)

    payload = {**source, "records": reviewed_records, "review_decisions": review_decisions, "review_source": csv_path.as_posix()}
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(output_path)
    _write_report(report_path, candidate_id, csv_path, rows, [], "imported")
    return output_path, report_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Valida e importa decisões humanas de um CSV.")
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--candidate", choices=sorted(CANDIDATES))
    selection.add_argument("--all", action="store_true", help="importa as três candidaturas")
    args = parser.parse_args()
    failed = False
    candidate_ids = CANDIDATES if args.all else (args.candidate,)
    for candidate_id in candidate_ids:
        output, report = import_candidate(candidate_id)
        if output is None:
            failed = True
            print(f"ERRO: {candidate_id} rejeitado; consulte {report.relative_to(ROOT)}")
        else:
            print(f"OK: {candidate_id} importado em {output.relative_to(ROOT)}; relatório: {report.relative_to(ROOT)}")
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
