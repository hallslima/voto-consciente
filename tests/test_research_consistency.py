import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_official_research_values_are_consolidated_in_json():
    research = json.loads((ROOT / "data" / "research_evidence.json").read_text(encoding="utf-8"))
    results = {item.get("id"): item for item in research["results"]}
    assert research["sample_size"] == 136
    assert "consolidados e aprovados pela equipe" in research["publication_status"]
    assert results["candidate_awareness"] == {
        "id": "candidate_awareness",
        "indicator": "Conhecem pouco ou apenas algumas candidaturas",
        "percentage": 79.4,
    }
    assert results["proposal_awareness"] == {
        "id": "proposal_awareness",
        "indicator": "Dizem conhecer poucas propostas dos candidatos",
        "percentage": 40.4,
    }


def test_presentation_derives_research_by_stable_ids_without_number_copies():
    data = (ROOT / "src" / "presentation" / "presentationData.js").read_text(encoding="utf-8")
    component = (ROOT / "src" / "presentation" / "Presentation.jsx").read_text(encoding="utf-8")
    assert "import researchEvidence from '../../data/research_evidence.json'" in data
    assert "researchEvidence.sample_size" in data
    assert "researchResult('candidate_awareness')" in data
    assert "researchResult('proposal_awareness')" in data
    for copied in ("researchParticipants: 136", "value: 79.4", "value: 40.4"):
        assert copied not in data
        assert copied not in component


def test_old_research_results_are_not_published_as_final_values():
    files = [ROOT / "README.md", ROOT / "data" / "research_evidence.json"]
    files.extend((ROOT / "docs").rglob("*.md"))
    files.extend(path for path in (ROOT / "src").rglob("*") if path.suffix in {".js", ".jsx"})
    published = "\n".join(path.read_text(encoding="utf-8") for path in files)
    for obsolete in ('"sample_size": 135', "80.7", "80,7%", "97.8", "97,8%"):
        assert obsolete not in published


def test_current_delivery_has_no_active_pipeline_references():
    files = [ROOT / "README.md"]
    files.extend((ROOT / "docs").rglob("*.md"))
    files.extend(path for path in (ROOT / "src").rglob("*") if path.suffix in {".js", ".jsx"})
    published = "\n".join(path.read_text(encoding="utf-8") for path in files).casefold()
    for obsolete in ("pypdf", "tesseract", "manifesto", "review-csv", "data/reviewed"):
        assert obsolete not in published


def test_documented_scope_uses_seven_active_plans_and_311_pages():
    data = (ROOT / "src" / "presentation" / "presentationData.js").read_text(encoding="utf-8")
    audit = (ROOT / "docs" / "presentation-data-audit.md").read_text(encoding="utf-8")
    assert "candidacies: 7" in data
    assert "officialPlans: 7" in data
    assert "analyzedPages: 311" in data
    assert "| Candidaturas | 7 |" in audit
    assert "| Planos oficiais | 7 |" in audit
    assert "| Páginas dos documentos | 311 |" in audit
