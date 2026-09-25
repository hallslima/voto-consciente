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
    assert "DEMO_SLIDE_ID = 'demo'" in data
    assert "origem', 'apresentacao'" in data
    assert "retorno', DEMO_SLIDE_ID" in data
    assert "return-to-presentation" in main


def test_qr_code_is_not_rendered_by_shared_slide_footer():
    slide = source("Slide.jsx")
    qr = source("components/PresentationQRCode.jsx")
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    assert "PresentationQRCode" not in slide
    assert "Acesse o MVP" not in slide
    assert "QRCodeSVG" in qr
    assert "qrcode.react" in package["dependencies"]
    assert "api.qrserver" not in qr.lower()


def test_only_demo_slide_renders_the_large_public_qr_code():
    component = source("Presentation.jsx")
    demo_case = component.split("case 'demo':", 1)[1].split("case 'limitacoes':", 1)[0]
    conclusion_case = component.split("case 'conclusao':", 1)[1].split("default:", 1)[0]
    assert component.count("<PresentationQRCode") == 1
    assert "<PresentationQRCode" in demo_case
    assert "<PresentationQRCode" not in conclusion_case
    assert "https://voto-consciente.netlify.app/" in component


def test_demo_slide_is_qr_focused_and_removes_old_actions():
    component = source("Presentation.jsx")
    demo_case = component.split("case 'demo':", 1)[1].split("case 'limitacoes':", 1)[0]
    assert "Aponte a câmera do celular e responda ao questionário" in demo_case
    assert "Voto Consciente Pernambuco" in demo_case
    assert "Não é necessário fazer cadastro." in demo_case
    for removed in ("A demonstração abre", "Abrir demonstração", "mini-browser", "demo-preview"):
        assert removed not in demo_case


def test_demo_qr_has_prominent_responsive_size():
    css = source("Presentation.css")
    rule = re.search(r"\.demo-qr-code \{([^}]+)\}", css).group(1)
    assert "width: clamp(260px, 28vw, 380px)" in rule
    assert "aspect-ratio: 1" in rule


def test_external_context_links_open_safely():
    component = source("Presentation.jsx")
    evidence_card = source("components/EvidenceCard.jsx")
    assert 'target="_blank"' in evidence_card
    assert 'rel="noopener noreferrer"' in evidence_card
    assert "abre em nova aba" in evidence_card
    assert "g1.globo.com" in component
    assert "veja.abril.com.br" in component


def test_presentation_data_matches_current_repository_scope_except_team_validated_research():
    candidates = json.loads((ROOT / "data" / "candidates.json").read_text(encoding="utf-8"))
    questions = json.loads((ROOT / "data" / "questions.json").read_text(encoding="utf-8"))
    presentation_data = source("presentationData.js")
    expected = {
        "candidacies": len(candidates),
        "officialPlans": len(candidates),
        "themes": len({question["theme"] for question in questions}),
        "publishedQuestions": len(questions),
    }
    for key, value in expected.items():
        assert re.search(rf"{key}: {value},", presentation_data)
    assert "researchParticipants: 136" in presentation_data
    assert "Valores atualizados e validados pela equipe" in presentation_data
    assert "Conferir sincronização posterior com data/research_evidence.json" in presentation_data


def test_toolbar_stage_and_navigation_are_separate_structural_areas():
    component = source("Presentation.jsx")
    toolbar = component.index('<header className="presentation-toolbar"')
    stage = component.index('<div className="presentation-stage"', toolbar)
    navigation = component.index('<footer className="presentation-navigation">', stage)
    assert toolbar < stage < navigation
    stage_markup = component[stage:navigation]
    assert "Voltar ao MVP" not in stage_markup
    assert "Imprimir ou salvar em PDF" not in stage_markup
    assert 'className="presentation-slide-frame"' in stage_markup


def test_controls_are_in_flow_outside_the_slide():
    css = source("Presentation.css")
    assert "grid-template-rows: auto minmax(0, 1fr) auto" in css
    assert "grid-template-columns: 1fr auto 1fr" in css
    toolbar_rule = re.search(r"\.presentation-toolbar \{([^}]+)\}", css).group(1)
    controls_rule = re.search(r"\.presentation-controls \{([^}]+)\}", css).group(1)
    assert "position: fixed" not in toolbar_rule
    assert "position: absolute" not in toolbar_rule
    assert "position: fixed" not in controls_rule
    assert "position: absolute" not in controls_rule


def test_slide_seven_has_three_independent_evidence_cards_and_updated_values():
    component = source("Presentation.jsx")
    data = source("presentationData.js")
    evidence_case = component.split("case 'evidencias':", 1)[1].split("case 'objetivo':", 1)[0]
    assert evidence_case.count("<EvidenceCard") == 3
    for text in ("Pesquisa do grupo", "136 participantes", "69%", "88%", "59%"):
        assert text in component or text in data
    for old_value in ("80.7", "97.8", "80,7%", "97,8%"):
        assert old_value not in evidence_case
        assert old_value not in data
    assert "79.4" in data
    assert "40.4" in data


def test_slide_seven_states_context_and_limitations():
    component = source("Presentation.jsx")
    assert "amostra por conveniência" in component
    assert "não representam todo o eleitorado de Pernambuco" in component
    assert "Rio de Janeiro, não a Pernambuco" in component
    assert "Contexto histórico nacional de 2018" in component
    assert "Percentuais informados pela equipe" in component


def test_evidence_cards_are_responsive_without_internal_scroll():
    css = source("Presentation.css")
    assert "grid-template-columns: repeat(3, minmax(0, 1fr))" in css
    assert "grid-template-columns: repeat(2, minmax(0, 1fr))" in css
    mobile = css.split("@media (max-width: 700px)", 1)[1].split("@media (max-width: 380px)", 1)[0]
    assert ".evidence-grid { grid-template-columns: 1fr" in mobile
    evidence_rule = re.search(r"\.evidence-card \{([^}]+)\}", css).group(1)
    assert "overflow" not in evidence_rule


def test_print_hides_all_controls_and_keeps_only_slide_deck():
    css = source("Presentation.css")
    print_css = css.split("@media print", 1)[1]
    for selector in (".presentation-toolbar", ".presentation-navigation", ".presentation-notes-button", ".speaker-notes"):
        assert selector in print_css
    assert ".print-deck { display: block !important; }" in print_css


def test_slide_footer_keeps_no_qr_placeholder_or_qr_styles():
    component = source("Presentation.jsx")
    css = source("Presentation.css")
    slide = source("Slide.jsx")
    assert "<Slide slide={current}" in component
    assert "slides.map((slide, index) => <Slide" in component
    assert "justify-content: space-between" not in re.search(r"\.slide-footer \{([^}]+)\}", css).group(1)
    assert "presentation-qr" not in css
    assert "Acesse o MVP" not in slide


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
    normalized = (ROOT / "scoring.py").read_bytes().replace(b"\r\n", b"\n")
    assert hashlib.sha256(normalized).hexdigest() == "8d40d85428646c8f80dce63ffc8d7e244f5600cab4df8d93247449280a04c81d"
