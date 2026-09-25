import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRESENTATION = ROOT / "src" / "presentation"


def source(name):
    return (PRESENTATION / name).read_text(encoding="utf-8")


def slide_metadata():
    text = source("slides.js")
    return re.findall(r"\{ id: '([^']+)', title: '([^']+)'[^}]+?(?:revealSteps: (\d+))? \}", text)


def test_presentation_mode_is_selected_before_app_bootstrap():
    main = (ROOT / "src" / "main.jsx").read_text(encoding="utf-8")
    assert "get('modo') === 'apresentacao'" in main
    assert "presentationMode ? <Presentation /> : <App />" in main


def test_deck_has_eighteen_unique_slides_and_demo_id():
    ids = [item[0] for item in slide_metadata()]
    assert len(ids) == 18
    assert len(ids) == len(set(ids))
    assert ids[15] == "demo"


def test_progressive_reveal_is_limited_to_three_opening_questions():
    slides_source = source("slides.js")
    assert slides_source.count("revealSteps: 1") == 3
    component = source("Presentation.jsx")
    assert "revealStep < maxReveal" in component
    assert "revealStep > 0" in component


def test_keyboard_navigation_implements_expected_keys_and_ignores_controls():
    component = source("Presentation.jsx")
    for key in ("ArrowRight", "ArrowLeft", "Home", "End", "Escape"):
        assert key in component
    assert "event.key === ' '" in component
    assert "event.target.closest?.(INTERACTIVE_SELECTOR)" in component


def test_counter_and_progress_are_structural_controls():
    component = source("Presentation.jsx")
    assert 'aria-label={`Slide ${currentIndex + 1} de ${slides.length}`}' in component
    assert 'role="progressbar"' in component
    assert "aria-valuenow={currentIndex + 1}" in component


def test_fullscreen_and_print_require_explicit_buttons():
    component = source("Presentation.jsx")
    assert "onClick={start}" in component
    assert "requestFullscreen" in component
    assert "document.exitFullscreen" in component
    assert "onClick={() => window.print()}" in component


def test_demo_round_trip_uses_named_demo_slide():
    main = (ROOT / "src" / "main.jsx").read_text(encoding="utf-8")
    data = source("presentationData.js")
    component = source("Presentation.jsx")
    assert "DEMO_SLIDE_ID = 'demo'" in data
    assert "origem', 'apresentacao'" in data
    assert "retorno', DEMO_SLIDE_ID" in data
    assert "return-to-presentation" in main
    assert "mvpUrl({ fromPresentation: true })" in component


def test_qr_code_is_rendered_by_shared_slide_footer_and_is_local():
    slide = source("Slide.jsx")
    qr = source("components/PresentationQRCode.jsx")
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    assert "<PresentationQRCode compact />" in slide
    assert "QRCodeSVG" in qr
    assert "qrcode.react" in package["dependencies"]
    assert "api.qrserver" not in qr.lower()


def test_external_context_links_open_safely():
    component = source("Presentation.jsx")
    assert component.count('target="_blank" rel="noopener noreferrer"') == 2
    assert "g1.globo.com" in component
    assert "veja.abril.com.br" in component


def test_presentation_data_matches_current_repository_scope():
    candidates = json.loads((ROOT / "data" / "candidates.json").read_text(encoding="utf-8"))
    questions = json.loads((ROOT / "data" / "questions.json").read_text(encoding="utf-8"))
    research = json.loads((ROOT / "data" / "research_evidence.json").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "data" / "generated" / "extraction_manifest.json").read_text(encoding="utf-8"))
    eligible_ids = {candidate["id"] for candidate in candidates}
    eligible_documents = [item for item in manifest["documents"] if item["candidate_id"] in eligible_ids]
    presentation_data = source("presentationData.js")
    expected = {
        "candidacies": len(candidates),
        "officialPlans": len(eligible_documents),
        "analyzedPages": sum(item["page_count"] for item in eligible_documents),
        "themes": len({question["theme"] for question in questions}),
        "publishedQuestions": len(questions),
        "researchParticipants": research["sample_size"],
        "ocrDocuments": sum(any(method.startswith("ocr") for method in item["methods"]) for item in eligible_documents),
    }
    for key, value in expected.items():
        assert re.search(rf"{key}: {value},", presentation_data)


def test_every_slide_gets_qr_code_through_slide_component():
    component = source("Presentation.jsx")
    assert "<Slide slide={current}" in component
    assert "slides.map((slide, index) => <Slide" in component
    assert "PresentationQRCode" in source("Slide.jsx")


def test_print_css_uses_one_widescreen_slide_per_page():
    css = source("Presentation.css")
    assert "@media print" in css
    assert "size: 13.333in 7.5in" in css
    assert "page-break-after: always" in css
    assert "print-color-adjust: exact" in css


def test_reduced_motion_and_visible_focus_are_supported():
    css = source("Presentation.css")
    assert "@media (prefers-reduced-motion: reduce)" in css
    assert ":focus-visible" in css


def test_presentation_avoids_prohibited_claims():
    content = "\n".join(path.read_text(encoding="utf-8") for path in PRESENTATION.rglob("*.*") if path.suffix in {".js", ".jsx"}).casefold()
    for expression in ("melhor candidato", "candidato ideal", "resultado certo", "ranking dos melhores", "a ia escolhe", "a ia recomenda"):
        assert expression not in content


def test_scoring_engine_hash_is_preserved():
    assert hashlib.sha256((ROOT / "scoring.py").read_bytes()).hexdigest() == "8d40d85428646c8f80dce63ffc8d7e244f5600cab4df8d93247449280a04c81d"
