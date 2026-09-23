from __future__ import annotations

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


REQUIRED_AUDIT_FIELDS = {
    "evidence_id", "candidate_id", "source_file", "source_sha256",
    "prompt_version", "model", "generated_at", "review_status",
    "reviewed_at", "reviewer", "review_notes",
}


def validate_records(records: list[dict], schema: dict) -> list[str]:
    errors = []
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for index, record in enumerate(records):
        errors.extend(f"registro {index}: {error.message}" for error in validator.iter_errors(record))
    return errors


def validate_audit(record: dict) -> list[str]:
    """Apply publication rules in addition to the structural JSON Schema."""
    errors = []
    missing = REQUIRED_AUDIT_FIELDS - record.keys()
    if missing:
        errors.append(f"campos de auditoria ausentes: {sorted(missing)}")
        return errors

    for field in REQUIRED_AUDIT_FIELDS - {"reviewed_at", "reviewer"}:
        value = record.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            errors.append(f"campo obrigatório vazio: {field}")

    if not str(record.get("page") or "").strip():
        errors.append("registro sem página ou indicação clara de seção")
    if not str(record.get("original_excerpt") or "").strip():
        errors.append("registro sem trecho original")
    if len(str(record.get("source_sha256") or "")) != 64:
        errors.append("registro sem hash SHA-256 válido")

    status = record.get("review_status")
    if status not in {"pending", "approved", "rejected"}:
        errors.append(f"status desconhecido: {status!r}")
    if status == "approved":
        if not str(record.get("reviewer") or "").strip():
            errors.append("registro aprovado sem revisor")
        if not str(record.get("reviewed_at") or "").strip():
            errors.append("registro aprovado sem data de revisão")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("records", type=Path)
    parser.add_argument("--schema", type=Path, default=Path(__file__).parents[1] / "schemas" / "proposal_evidence.schema.json")
    args = parser.parse_args()
    records = json.loads(args.records.read_text(encoding="utf-8"))
    if isinstance(records, dict) and isinstance(records.get("records"), list):
        records = records["records"]
    elif isinstance(records, dict):
        records = [records]
    schema = json.loads(args.schema.read_text(encoding="utf-8"))
    errors = validate_records(records, schema)
    for index, record in enumerate(records):
        errors.extend(f"registro {index}: {error}" for error in validate_audit(record))
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"OK: {len(records)} evidência(s) válida(s).")


if __name__ == "__main__":
    main()
