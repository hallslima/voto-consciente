import json
from pathlib import Path
import subprocess
import sys

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ai_pipeline.scripts.consolidate_matrix import approved
from ai_pipeline.scripts.validate_review_decisions import is_promotable, promotion_errors
from ai_pipeline.scripts.validate_evidence import validate_audit, validate_records


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def valid_record(**changes):
    record = {
        "evidence_id": "example_candidate-health-001",
        "candidate_id": "example_candidate",
        "theme": "Saúde",
        "subtheme": "Gestão",
        "evidence_level": 3,
        "neutral_summary": "Resumo neutro.",
        "original_excerpt": "Trecho literal do documento.",
        "page": "p. 1",
        "source_file": "example-plan.pdf",
        "source_sha256": "a" * 64,
        "target_population": "Público geral",
        "proposed_action": "Ação documentada.",
        "limitations": ["Exemplo de teste"],
        "prompt_version": "extract-evidence-v1.0.0",
        "model": "example-model",
        "generated_at": "2026-01-01T00:00:00Z",
        "review_status": "approved",
        "reviewed_at": "2026-01-02T00:00:00Z",
        "reviewer": "Revisor de teste",
        "review_notes": "Conferido para o teste.",
    }
    record.update(changes)
    return record


def schema():
    return load_json(ROOT / "ai_pipeline" / "schemas" / "proposal_evidence.schema.json")


def errors(record):
    return validate_records([record], schema()) + validate_audit(record)


def test_candidate_assets_are_associated_and_exist():
    candidates = load_json(ROOT / "data" / "candidates.json")
    assert len(candidates) == 8
    for candidate in candidates:
        photo = ROOT / "public" / candidate["photo_url"].lstrip("/")
        plan = ROOT / "public" / candidate["local_plan_url"].lstrip("/")
        assert photo.is_file()
        assert plan.is_file()
        assert candidate["official_data_url"] != candidate["local_plan_url"]
        assert candidate["plan_document"].endswith(".pdf")


def test_evidence_schema_is_valid_and_accepts_complete_record():
    Draft202012Validator.check_schema(schema())
    validator = Draft202012Validator(schema(), format_checker=FormatChecker())
    assert list(validator.iter_errors(valid_record())) == []
    assert validate_audit(valid_record()) == []


def test_required_field_cannot_be_empty():
    assert errors(valid_record(candidate_id=""))


def test_invalid_evidence_level_is_rejected():
    assert errors(valid_record(evidence_level=4))


def test_approved_record_requires_reviewer():
    messages = errors(valid_record(reviewer=""))
    assert any("revisor" in message for message in messages)


def test_approved_record_requires_review_date():
    messages = errors(valid_record(reviewed_at=None))
    assert any("data de revisão" in message for message in messages)


def test_missing_hash_is_rejected():
    record = valid_record()
    record.pop("source_sha256")
    assert errors(record)


def test_missing_page_and_excerpt_are_rejected():
    messages = errors(valid_record(page="", original_excerpt=""))
    assert any("página" in message for message in messages)
    assert any("trecho original" in message for message in messages)


def test_unknown_status_is_rejected():
    messages = errors(valid_record(review_status="draft"))
    assert any("status desconhecido" in message for message in messages)


def test_validation_cli_executes_audit_rules(tmp_path):
    record = valid_record(review_notes="")
    records_file = tmp_path / "records.json"
    records_file.write_text(json.dumps([record]), encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, str(ROOT / "ai_pipeline" / "scripts" / "validate_evidence.py"), str(records_file)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode != 0
    assert "campo obrigatório vazio: review_notes" in completed.stderr


def test_consolidation_keeps_only_approved_records():
    records = [
        valid_record(evidence_id="candidate-theme-001", review_status="approved"),
        valid_record(evidence_id="candidate-theme-002", review_status="pending", reviewer=None, reviewed_at=None),
        valid_record(evidence_id="candidate-theme-003", review_status="rejected"),
    ]
    assert [item["evidence_id"] for item in approved(records)] == ["candidate-theme-001"]


def test_examples_are_valid_but_explicitly_fictitious():
    generated = load_json(ROOT / "data" / "generated" / "example.generated.json")
    reviewed = load_json(ROOT / "data" / "reviewed" / "example.reviewed.json")
    assert errors(generated) == []
    assert errors(reviewed) == []
    assert "EXEMPLO FICTÍCIO" in generated["review_notes"]
    assert "EXEMPLO FICTÍCIO" in reviewed["review_notes"]


def test_runtime_does_not_consume_generated_reviewed_or_examples():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "data/generated" not in source
    assert "data/reviewed" not in source
    assert "example.generated.json" not in source
    assert "example.reviewed.json" not in source
    assert 'load_json("questions.json")' in source
    assert 'load_json("candidates.json")' in source


def extraction_manifest():
    return load_json(ROOT / "data" / "generated" / "extraction_manifest.json")


def extracted_documents():
    folder = ROOT / "data" / "generated" / "extracted-text"
    return {path.stem: load_json(path) for path in folder.glob("*.json")}


def guilherme_pilot():
    return load_json(ROOT / "data" / "generated" / "evidence" / "guilherme_fonseca.generated.json")


def guilherme_reviewed():
    return load_json(ROOT / "data" / "reviewed" / "evidence" / "guilherme_fonseca.reviewed.json")


def small_plan_pilots():
    folder = ROOT / "data" / "generated" / "evidence"
    return {
        candidate_id: load_json(folder / f"{candidate_id}.generated.json")
        for candidate_id in ("jeremias", "camila", "victor_assis")
    }


def test_eight_original_pdfs_and_extractions_are_present():
    pdfs = list((ROOT / "public" / "documents" / "government-plans").glob("*.pdf"))
    assert len(pdfs) == 8
    assert len(extracted_documents()) == 8


def test_extracted_hashes_are_valid_and_distinct():
    hashes = [document["source_sha256"] for document in extracted_documents().values()]
    assert len(hashes) == 8
    assert len(set(hashes)) == 8
    assert all(len(value) == 64 and all(char in "0123456789abcdef" for char in value) for value in hashes)


def test_extracted_pages_preserve_physical_numbering():
    for document in extracted_documents().values():
        numbers = [page["page_number"] for page in document["pages"]]
        assert numbers == list(range(1, document["page_count"] + 1))


def test_extraction_is_associated_with_correct_candidate():
    candidates = load_json(ROOT / "data" / "candidates.json")
    documents = extracted_documents()
    for candidate in candidates:
        document = documents[candidate["id"]]
        assert document["candidate_id"] == candidate["id"]
        assert document["source_file"] == candidate["plan_document"]


def test_extraction_manifest_contains_eight_records():
    manifest = extraction_manifest()
    assert manifest["document_count"] == 8
    assert len(manifest["documents"]) == 8
    assert {item["candidate_id"] for item in manifest["documents"]} == set(extracted_documents())


def test_every_page_records_extraction_method():
    allowed = {"pypdf", "ocr-tesseract", "ocr-tesseract-por"}
    for document in extracted_documents().values():
        assert document["pages"]
        assert all(page["extraction_method"] in allowed for page in document["pages"])


def test_raquel_ocr_preserves_106_physical_pages():
    documents = extracted_documents()
    document = documents["raquel_lyra"]
    assert document["page_count"] == 106
    assert len(document["pages"]) == 106
    assert [page["page_number"] for page in document["pages"]] == list(range(1, 107))


def test_raquel_ocr_method_and_language_are_recorded():
    document = extracted_documents()["raquel_lyra"]
    manifest_entry = next(item for item in extraction_manifest()["documents"] if item["candidate_id"] == "raquel_lyra")
    assert document["extraction_method"] == "ocr-tesseract-por"
    assert document["language"] == "por"
    assert document["dpi"] == 300
    assert all(page["extraction_method"] == "ocr-tesseract-por" for page in document["pages"])
    assert all(page["language"] == "por" for page in document["pages"])
    assert manifest_entry["extraction_method"] == "ocr-tesseract-por"
    assert manifest_entry["language"] == "por"
    assert manifest_entry["status"] in {"complete", "complete_with_warnings"}


def test_raquel_ocr_contains_text_on_internal_sample_pages():
    pages = {page["page_number"]: page for page in extracted_documents()["raquel_lyra"]["pages"]}
    for page_number in (5, 15, 25, 40, 53, 70, 90, 100):
        assert pages[page_number]["character_count"] >= 50
        assert pages[page_number]["text"].strip()


def test_raquel_low_extraction_pages_are_signalled_for_manual_review():
    document = extracted_documents()["raquel_lyra"]
    low_pages = [page for page in document["pages"] if page["character_count"] < 50]
    assert low_pages
    assert all(page["manual_review_required"] is True for page in low_pages)
    assert all(page["quality"] == "low-extraction-review" for page in low_pages)
    assert document["manual_review_pages"] == [page["page_number"] for page in low_pages]
    assert document["manual_review_page_count"] == len(low_pages)


def test_raquel_original_hash_is_preserved_after_ocr():
    document = extracted_documents()["raquel_lyra"]
    assert document["source_sha256"] == "3041874e9c767aa94d623b2e62ff85ccfa62949c70ea9f07dc6876e8a7483850"
    assert document["original_pdf_unchanged"] is True


def test_extracted_files_are_not_consumed_by_runtime():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "extracted-text" not in source
    assert "extraction_manifest.json" not in source


def test_original_pdfs_match_hashes_recorded_before_and_after_extraction():
    import hashlib

    for document in extracted_documents().values():
        pdf = ROOT / document["source_path"]
        current_hash = hashlib.sha256(pdf.read_bytes()).hexdigest()
        assert current_hash == document["source_sha256"]
        assert document["original_pdf_unchanged"] is True


def test_guilherme_pilot_records_remain_pending_without_reviewer():
    records = guilherme_pilot()["records"]
    assert records
    assert all(record["review_status"] == "pending" for record in records)
    assert all(record["reviewed_at"] is None for record in records)
    assert all(record["reviewer"] is None for record in records)


def test_guilherme_pilot_records_have_page_and_literal_excerpt():
    source = extracted_documents()["guilherme_fonseca"]
    pages = {f"p. {page['page_number']}": page["text"] for page in source["pages"]}
    for record in guilherme_pilot()["records"]:
        assert record["page"] in pages
        assert record["original_excerpt"]
        assert record["original_excerpt"] in pages[record["page"]]


def test_guilherme_pilot_hash_matches_extraction_manifest():
    manifest_entry = next(
        item for item in extraction_manifest()["documents"] if item["candidate_id"] == "guilherme_fonseca"
    )
    records = guilherme_pilot()["records"]
    assert all(record["source_sha256"] == manifest_entry["source_sha256"] for record in records)


def test_guilherme_pilot_candidate_and_themes_are_limited_to_allowed_values():
    allowed_themes = {question["theme"] for question in load_json(ROOT / "data" / "questions.json")}
    records = guilherme_pilot()["records"]
    assert all(record["candidate_id"] == "guilherme_fonseca" for record in records)
    assert {record["theme"] for record in records} <= allowed_themes
    assert set(guilherme_pilot()["absence_report"]) == set()


def test_guilherme_generated_evidence_is_not_consumed_by_runtime():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    frontend = "\n".join(path.read_text(encoding="utf-8") for path in (ROOT / "src").rglob("*.*") if path.is_file())
    for forbidden in ("guilherme_fonseca.generated.json", "data/generated/evidence", "generation-audit"):
        assert forbidden not in source
        assert forbidden not in frontend


def test_guilherme_reviewed_file_has_41_approved_records_with_complete_review_audit():
    records = guilherme_reviewed()["records"]
    assert len(records) == 41
    assert all(record["review_status"] == "approved" for record in records)
    assert all(record["reviewer"] == "Hallisson Lima" for record in records)
    assert all(record["reviewed_at"] for record in records)


def test_guilherme_review_preserves_content_hashes_and_pages():
    generated = {record["evidence_id"]: record for record in guilherme_pilot()["records"]}
    reviewed = {record["evidence_id"]: record for record in guilherme_reviewed()["records"]}
    assert generated.keys() == reviewed.keys()
    protected_fields = {
        "evidence_id", "candidate_id", "theme", "subtheme", "evidence_level",
        "neutral_summary", "original_excerpt", "page", "source_file", "source_sha256",
        "target_population", "proposed_action", "limitations", "prompt_version", "model", "generated_at",
    }
    for evidence_id, original in generated.items():
        approved = reviewed[evidence_id]
        assert {field: approved[field] for field in protected_fields} == {
            field: original[field] for field in protected_fields
        }


def test_guilherme_reviewed_file_does_not_publish_or_modify_matrix_automatically():
    manifest = load_json(ROOT / "data" / "reviewed" / "published_matrix_manifest.json")
    assert manifest["approval_status"] == "pending"
    assert manifest["published_at"] is None
    assert manifest["reviewed_files"] == []
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    assert "guilherme_fonseca.reviewed.json" not in source
    assert "data/reviewed/evidence" not in source


def test_small_plan_pilots_have_correct_candidate_hash_and_source_isolation():
    manifests = {item["candidate_id"]: item for item in extraction_manifest()["documents"]}
    for candidate_id, pilot in small_plan_pilots().items():
        records = pilot["records"]
        assert records
        assert all(record["candidate_id"] == candidate_id for record in records)
        assert all(record["source_sha256"] == manifests[candidate_id]["source_sha256"] for record in records)
        assert all(record["source_file"] == manifests[candidate_id]["source_file"] for record in records)
        assert {record["candidate_id"] for record in records} == {candidate_id}


def test_small_plan_pilots_remain_pending_without_reviewers():
    for pilot in small_plan_pilots().values():
        assert all(record["review_status"] == "pending" for record in pilot["records"])
        assert all(record["reviewer"] is None for record in pilot["records"])
        assert all(record["reviewed_at"] is None for record in pilot["records"])


def test_small_plan_pilot_pages_and_excerpts_exist_in_own_sources():
    sources = extracted_documents()
    for candidate_id, pilot in small_plan_pilots().items():
        pages = {f"p. {page['page_number']}": page["text"] for page in sources[candidate_id]["pages"]}
        for record in pilot["records"]:
            assert record["page"] in pages
            assert record["original_excerpt"] in pages[record["page"]]


def test_small_plan_pilot_themes_and_absence_reports_are_allowed():
    allowed = {question["theme"] for question in load_json(ROOT / "data" / "questions.json")}
    for pilot in small_plan_pilots().values():
        assert {record["theme"] for record in pilot["records"]} <= allowed
        assert {item["theme"] for item in pilot["absence_report"]} <= allowed


def test_small_plan_pilots_are_not_reviewed_or_consumed_by_runtime():
    reviewed_folder = ROOT / "data" / "reviewed" / "evidence"
    runtime = (ROOT / "app.py").read_text(encoding="utf-8") + "\n" + "\n".join(
        path.read_text(encoding="utf-8") for path in (ROOT / "src").rglob("*.*") if path.is_file()
    )
    for candidate_id in small_plan_pilots():
        assert not (reviewed_folder / f"{candidate_id}.reviewed.json").exists()
        assert f"{candidate_id}.generated.json" not in runtime


def test_review_packets_have_exact_counts_and_blank_pending_decisions():
    expected = {"jeremias": 27, "camila": 29, "victor_assis": 23}
    packet_names = {"jeremias": "jeremias-review.md", "camila": "camila-review.md", "victor_assis": "victor-assis-review.md"}
    decision_folder = ROOT / "data" / "reviewed" / "review-decisions"
    for candidate_id, count in expected.items():
        packet = (ROOT / "docs" / "review-packets" / packet_names[candidate_id]).read_text(encoding="utf-8")
        assert sum(line.startswith("## ") and line[3:4].isdigit() for line in packet.splitlines()) == count
        model = load_json(decision_folder / f"{candidate_id}.review.json")
        assert model["candidate_id"] == candidate_id
        assert model["expected_evidence_count"] == count
        assert len(model["decisions"]) == count
        assert model["overall_status"] == "pending"
        assert model["review_completed_at"] is None
        assert all(decision["review_status"] == "pending" for decision in model["decisions"])
        assert all(decision["documentary_decision"] is None for decision in model["decisions"])
        assert all(decision["reviewer_name"] is None for decision in model["decisions"])
        assert all(decision["reviewed_at"] is None for decision in model["decisions"])
        assert all(decision["matrix_eligibility"] is None for decision in model["decisions"])


def test_blank_review_decisions_cannot_be_promoted():
    decision_folder = ROOT / "data" / "reviewed" / "review-decisions"
    for path in decision_folder.glob("*.review.json"):
        for decision in load_json(path)["decisions"]:
            assert is_promotable(decision) is False
            errors = promotion_errors(decision)
            assert "decisão documental deve ser approved" in errors
            assert "nome do revisor ausente" in errors
            assert "data da revisão ausente" in errors
            assert "decisão de elegibilidade ausente ou inválida" in errors


def test_review_promotion_requires_eligibility_justification_when_needed():
    complete = {
        "documentary_decision": "approved",
        "reviewer_name": "Revisor Humano",
        "reviewed_at": "2026-09-23T12:00:00-03:00",
        "predominant_competence": "state",
        "matrix_eligibility": "yes",
        "eligibility_justification": "",
    }
    assert is_promotable(complete) is True
    for eligibility in ("no", "needs_adjustment"):
        decision = {**complete, "matrix_eligibility": eligibility}
        assert is_promotable(decision) is False
        assert "justificativa de elegibilidade obrigatória" in promotion_errors(decision)
        decision["eligibility_justification"] = "Justificativa preenchida pelo revisor."
        assert is_promotable(decision) is True


def test_review_packets_do_not_promote_evidence_or_change_matrix_manifest():
    manifest = load_json(ROOT / "data" / "reviewed" / "published_matrix_manifest.json")
    assert manifest["approval_status"] == "pending"
    assert manifest["reviewed_files"] == []
    reviewed_evidence = ROOT / "data" / "reviewed" / "evidence"
    for candidate_id in ("jeremias", "camila", "victor_assis"):
        assert not (reviewed_evidence / f"{candidate_id}.reviewed.json").exists()
        assert all(record["review_status"] == "pending" for record in small_plan_pilots()[candidate_id]["records"])
