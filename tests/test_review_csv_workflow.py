import csv
import hashlib
import json
from pathlib import Path
import shutil

import pytest

from ai_pipeline.scripts.export_review_csv import CANDIDATES, FIELDS, export_candidate
from ai_pipeline.scripts.import_review_csv import import_candidate
from ai_pipeline.scripts.consolidate_matrix import approved


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {"jeremias": 27, "camila": 29, "victor_assis": 23}


def prepare(tmp_path: Path, candidate_id: str = "jeremias") -> Path:
    source_dir = tmp_path / "data/generated/evidence"
    source_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / "data/generated/evidence" / f"{candidate_id}.generated.json", source_dir)
    return export_candidate(candidate_id, tmp_path)


def rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=";"))


def write_rows(path: Path, values):
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, delimiter=";", lineterminator="\n")
        writer.writeheader()
        writer.writerows(values)


def valid_rows(path: Path):
    values = rows(path)
    for row in values:
        row.update({
            "document_decision": "approved", "excerpt_matches_page": "yes",
            "summary_preserves_meaning": "yes", "theme_is_correct": "yes",
            "evidence_level_is_correct": "yes", "predominant_jurisdiction": "state",
            "matrix_eligibility": "yes", "eligibility_justification": "",
            "correction_notes": "", "reviewer": "Revisora Humana",
            "reviewed_at": "2026-09-23T14:30:00-03:00",
        })
    return values


def error_fields(report: Path):
    return {item["field"] for item in json.loads(report.read_text(encoding="utf-8"))["errors"]}


def test_export_counts_bom_semicolon_and_portuguese(tmp_path):
    for candidate_id, count in EXPECTED.items():
        path = prepare(tmp_path, candidate_id)
        raw = path.read_bytes()
        assert raw.startswith(b"\xef\xbb\xbf")
        assert b";" in raw
        text = raw.decode("utf-8-sig")
        assert any(char in text for char in "áéíóúãç")
        assert len(rows(path)) == count
        assert all(not row["document_decision"] for row in rows(path))


@pytest.mark.parametrize(
    ("field", "value"),
    [("theme", "Tema adulterado"), ("source_sha256", "0" * 64)],
)
def test_protected_evidence_change_is_rejected(tmp_path, field, value):
    path = prepare(tmp_path)
    values = valid_rows(path)
    values[0][field] = value
    write_rows(path, values)
    output, report = import_candidate("jeremias", tmp_path)
    assert output is None
    assert field in error_fields(report)
    assert not (tmp_path / "data/reviewed/evidence/jeremias.reviewed.json").exists()


@pytest.mark.parametrize(
    ("updates", "expected_field"),
    [
        ({"document_decision": "maybe"}, "document_decision"),
        ({"reviewer": ""}, "reviewer"),
        ({"reviewed_at": "23/09/2026"}, "reviewed_at"),
        ({"excerpt_matches_page": ""}, "excerpt_matches_page"),
        ({"document_decision": "rejected", "correction_notes": ""}, "correction_notes"),
        ({"matrix_eligibility": "no", "eligibility_justification": ""}, "eligibility_justification"),
    ],
)
def test_invalid_human_decisions_are_rejected(tmp_path, updates, expected_field):
    path = prepare(tmp_path)
    values = valid_rows(path)
    values[0].update(updates)
    write_rows(path, values)
    output, report = import_candidate("jeremias", tmp_path)
    assert output is None
    assert expected_field in error_fields(report)


def test_valid_import_preserves_original_and_keeps_noneligible_approved(tmp_path):
    path = prepare(tmp_path)
    values = valid_rows(path)
    values[0]["matrix_eligibility"] = "no"
    values[0]["eligibility_justification"] = "Competência exclusivamente federal."
    write_rows(path, values)
    source = tmp_path / "data/generated/evidence/jeremias.generated.json"
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    output, report = import_candidate("jeremias", tmp_path)
    assert output is not None
    assert not report.exists()
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    imported = json.loads(output.read_text(encoding="utf-8"))["records"]
    assert len(imported) == 27
    assert imported[0]["review_status"] == "approved"
    assert imported[0]["matrix_eligibility"] == "no"
    assert imported[0]["eligibility_justification"]
    assert imported[0] not in approved(imported)


def test_workflow_is_isolated_from_runtime_and_matrix():
    runtime = (ROOT / "app.py").read_text(encoding="utf-8") + "\n" + "\n".join(
        path.read_text(encoding="utf-8") for path in (ROOT / "src").rglob("*") if path.is_file()
    )
    assert "review-csv" not in runtime
    assert "reviewed/evidence" not in runtime
    manifest = json.loads((ROOT / "data/reviewed/published_matrix_manifest.json").read_text(encoding="utf-8"))
    assert manifest["approval_status"] == "pending"
    assert manifest["reviewed_files"] == []


def test_repository_exports_keep_all_79_decisions_blank():
    total = 0
    for candidate_id, (_, filename) in CANDIDATES.items():
        path = ROOT / "data/reviewed/review-csv" / filename
        values = rows(path)
        assert len(values) == EXPECTED[candidate_id]
        assert all(not row["document_decision"] for row in values)
        total += len(values)
    assert total == 79
