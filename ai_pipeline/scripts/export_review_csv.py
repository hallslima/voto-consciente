from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CANDIDATES = {
    "jeremias": ("Professor Jeremias do Banco", "jeremias-review.csv"),
    "camila": ("Professora Camila", "camila-review.csv"),
    "victor_assis": ("Victor Assis", "victor-assis-review.csv"),
}
FIELDS = [
    "evidence_id", "candidate_id", "candidate_name", "theme", "subtheme",
    "evidence_level", "neutral_summary", "proposed_action", "target_population",
    "original_excerpt", "page", "source_file", "source_sha256", "limitations",
    "document_decision", "excerpt_matches_page", "summary_preserves_meaning",
    "theme_is_correct", "evidence_level_is_correct", "predominant_jurisdiction",
    "matrix_eligibility", "eligibility_justification", "correction_notes", "reviewer",
    "reviewed_at",
]
DECISION_FIELDS = FIELDS[14:]
IMMUTABLE_FIELDS = FIELDS[:14]


def _page_key(value: object) -> tuple:
    parts = re.split(r"(\d+)", str(value).casefold())
    return tuple(int(part) if part.isdigit() else part for part in parts)


def _record_key(record: dict) -> tuple:
    return (str(record["theme"]).casefold(), _page_key(record["page"]), record["evidence_id"])


def export_candidate(candidate_id: str, root: Path = ROOT) -> Path:
    if candidate_id not in CANDIDATES:
        raise ValueError(f"candidato não suportado: {candidate_id}")
    candidate_name, filename = CANDIDATES[candidate_id]
    source = root / "data/generated/evidence" / f"{candidate_id}.generated.json"
    destination = root / "data/reviewed/review-csv" / filename
    payload = json.loads(source.read_text(encoding="utf-8"))
    records = sorted(payload["records"], key=_record_key)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter=";", lineterminator="\n")
        writer.writeheader()
        for record in records:
            row = {field: record.get(field, "") for field in FIELDS}
            row["candidate_name"] = candidate_name
            row["limitations"] = json.dumps(record.get("limitations", []), ensure_ascii=False)
            for field in DECISION_FIELDS:
                row[field] = ""
            writer.writerow(row)
    return destination


def main() -> None:
    parser = argparse.ArgumentParser(description="Exporta evidências pendentes para revisão humana em CSV.")
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--candidate", choices=sorted(CANDIDATES))
    selection.add_argument("--all", action="store_true", help="exporta as três candidaturas")
    args = parser.parse_args()
    candidate_ids = CANDIDATES if args.all else (args.candidate,)
    for candidate_id in candidate_ids:
        path = export_candidate(candidate_id)
        print(f"OK: {candidate_id} exportado para {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
