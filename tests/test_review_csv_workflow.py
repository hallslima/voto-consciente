import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys

import pytest

from ai_pipeline.scripts.consolidate_matrix import approved
from ai_pipeline.scripts.export_review_csv import CANDIDATES, FIELDS, IMMUTABLE_FIELDS, export_candidate
from ai_pipeline.scripts.import_review_csv import import_candidate


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {"jeremias": 27, "camila": 29, "victor_assis": 23}


def prepare(tmp_path: Path, candidate_id: str = "jeremias") -> Path:
    source_dir = tmp_path / "data/generated/evidence"
    schema_dir = tmp_path / "ai_pipeline/schemas"
    source_dir.mkdir(parents=True, exist_ok=True)
    schema_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / "data/generated/evidence" / f"{candidate_id}.generated.json", source_dir)
    shutil.copy(ROOT / "ai_pipeline/schemas/review_decision.schema.json", schema_dir)
    return export_candidate(candidate_id, tmp_path)


def read_rows(path: Path):
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle, delimiter=";"))


def write_rows(path: Path, values, fields=FIELDS):
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter=";", lineterminator="\n")
        writer.writeheader()
        writer.writerows(values)


def completed_rows(path: Path):
    values = read_rows(path)
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


def import_values(tmp_path, values, candidate_id="jeremias"):
    path = tmp_path / "data/reviewed/review-csv" / CANDIDATES[candidate_id][1]
    write_rows(path, values)
    return import_candidate(candidate_id, tmp_path)


def report_data(report: Path):
    return json.loads(report.read_text(encoding="utf-8"))


@pytest.mark.parametrize(("candidate_id", "count"), EXPECTED.items())
def test_export_has_expected_count(candidate_id, count, tmp_path):
    assert len(read_rows(prepare(tmp_path, candidate_id))) == count


def test_export_header_order_bom_accents_and_quoted_newlines(tmp_path):
    path = prepare(tmp_path)
    raw = path.read_bytes()
    assert raw.startswith(b"\xef\xbb\xbf")
    assert next(csv.reader(path.open(encoding="utf-8-sig", newline=""), delimiter=";")) == FIELDS
    assert "Saúde pública" in raw.decode("utf-8-sig")
    assert '"• Construção de um novo Hospital' in raw.decode("utf-8-sig")
    assert "\npernambucana" in raw.decode("utf-8-sig")


def test_export_is_stably_sorted_and_has_unique_ids(tmp_path):
    values = read_rows(prepare(tmp_path))
    ids = [row["evidence_id"] for row in values]
    assert len(ids) == len(set(ids))
    assert [(row["theme"].casefold(), row["page"], row["evidence_id"]) for row in values] == sorted(
        [(row["theme"].casefold(), row["page"], row["evidence_id"]) for row in values]
    )


def test_limitations_are_reversible_without_loss(tmp_path):
    path = prepare(tmp_path)
    exported = {row["evidence_id"]: json.loads(row["limitations"]) for row in read_rows(path)}
    source = json.loads((tmp_path / "data/generated/evidence/jeremias.generated.json").read_text(encoding="utf-8"))
    assert exported == {row["evidence_id"]: row["limitations"] for row in source["records"]}


@pytest.mark.parametrize("field", IMMUTABLE_FIELDS)
def test_every_immutable_column_change_is_rejected(tmp_path, field):
    path = prepare(tmp_path)
    values = completed_rows(path)
    values[0][field] = "[]" if field == "limitations" else f"alterado-{values[0][field]}"
    output, report = import_values(tmp_path, values)
    assert output is None
    assert field in {error["field"] for error in report_data(report)["errors"]}


def test_changed_evidence_id_is_unknown_and_original_is_missing(tmp_path):
    values = completed_rows(prepare(tmp_path))
    values[0]["evidence_id"] = "id-inexistente"
    output, report = import_values(tmp_path, values)
    messages = [error["error"] for error in report_data(report)["errors"]]
    assert output is None and "evidence_id desconhecido" in messages and "registro ausente no CSV" in messages


def test_duplicate_id_is_rejected(tmp_path):
    values = completed_rows(prepare(tmp_path))
    values[1]["evidence_id"] = values[0]["evidence_id"]
    output, report = import_values(tmp_path, values)
    assert output is None
    assert any(error["error"] == "evidence_id duplicado" for error in report_data(report)["errors"])


def test_removed_row_is_rejected(tmp_path):
    values = completed_rows(prepare(tmp_path))[:-1]
    output, report = import_values(tmp_path, values)
    assert output is None
    assert any(error["field"] == "rows" for error in report_data(report)["errors"])


@pytest.mark.parametrize(
    ("updates", "expected_field"),
    [
        ({"document_decision": "maybe"}, "document_decision"),
        ({"reviewer": ""}, "reviewer"),
        ({"reviewed_at": "23/09/2026"}, "reviewed_at"),
        ({"excerpt_matches_page": "no"}, "excerpt_matches_page"),
        ({"summary_preserves_meaning": "no"}, "summary_preserves_meaning"),
        ({"theme_is_correct": "no"}, "theme_is_correct"),
        ({"evidence_level_is_correct": "no"}, "evidence_level_is_correct"),
        ({"document_decision": "rejected", "correction_notes": ""}, "correction_notes"),
        ({"document_decision": "needs_correction", "correction_notes": ""}, "correction_notes"),
        ({"matrix_eligibility": "no", "eligibility_justification": ""}, "eligibility_justification"),
        ({"matrix_eligibility": "needs_adjustment", "eligibility_justification": ""}, "eligibility_justification"),
        ({"predominant_jurisdiction": "uncertain", "eligibility_justification": ""}, "eligibility_justification"),
        ({"reviewer": "=HYPERLINK('x')"}, "reviewer"),
    ],
)
def test_invalid_decision_is_rejected(tmp_path, updates, expected_field):
    values = completed_rows(prepare(tmp_path))
    values[0].update(updates)
    output, report = import_values(tmp_path, values)
    assert output is None
    assert expected_field in {error["field"] for error in report_data(report)["errors"]}


def test_valid_import_is_atomic_preserves_source_and_reports_totals(tmp_path):
    path = prepare(tmp_path)
    values = completed_rows(path)
    values[0].update({"matrix_eligibility": "no", "eligibility_justification": "Competência federal."})
    values[1].update({"document_decision": "rejected", "correction_notes": "Trecho não sustenta o resumo."})
    values[2].update({"document_decision": "needs_correction", "correction_notes": "Corrigir tema."})
    source = tmp_path / "data/generated/evidence/jeremias.generated.json"
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    output, report = import_values(tmp_path, values)
    assert output and hashlib.sha256(source.read_bytes()).hexdigest() == before
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert len(payload["records"]) == len(payload["review_decisions"]) == 27
    assert payload["records"][0]["review_status"] == "approved"
    assert payload["records"][2]["review_status"] == "pending"
    summary = report_data(report)
    assert summary["status"] == "imported" and summary["approved"] == 25
    assert summary["rejected"] == 1 and summary["needs_correction"] == 1 and summary["not_eligible"] == 1
    assert not output.with_suffix(".json.tmp").exists()
    assert payload["records"][0] not in approved(payload["records"], payload["review_decisions"])


def test_invalid_import_creates_report_but_no_partial_output(tmp_path):
    values = completed_rows(prepare(tmp_path))
    values[0]["reviewer"] = ""
    output, report = import_values(tmp_path, values)
    assert output is None and report.exists()
    assert report.parent.name == "review-reports"
    assert report_data(report)["status"] == "rejected"
    assert not (tmp_path / "data/reviewed/evidence/jeremias.reviewed.json").exists()


def test_export_cli_requires_expected_flags(tmp_path):
    completed = subprocess.run(
        [sys.executable, str(ROOT / "ai_pipeline/scripts/export_review_csv.py"), "--help"],
        cwd=tmp_path, capture_output=True, text=True, check=False,
    )
    assert completed.returncode == 0
    assert "--candidate" in completed.stdout and "--all" in completed.stdout


def test_runtime_does_not_consume_csv_or_reports_and_manifest_stays_pending():
    runtime = (ROOT / "app.py").read_text(encoding="utf-8") + "\n" + "\n".join(
        path.read_text(encoding="utf-8") for path in (ROOT / "src").rglob("*") if path.is_file()
    )
    assert "review-csv" not in runtime and "review-reports" not in runtime
    manifest = json.loads((ROOT / "data/reviewed/published_matrix_manifest.json").read_text(encoding="utf-8"))
    assert manifest["approval_status"] == "pending" and manifest["reviewed_files"] == []


def test_repository_exports_keep_all_79_decisions_blank_and_no_reviewed_outputs():
    total = 0
    for candidate_id, (_, filename) in CANDIDATES.items():
        values = read_rows(ROOT / "data/reviewed/review-csv" / filename)
        assert len(values) == EXPECTED[candidate_id]
        assert all(all(not row[field] for field in FIELDS[14:]) for row in values)
        assert not (ROOT / "data/reviewed/evidence" / f"{candidate_id}.reviewed.json").exists()
        total += len(values)
    assert total == 79
