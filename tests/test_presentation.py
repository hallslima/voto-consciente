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


def test_deck_has_fourteen_unique_slides_and_removed_sections_are_absent():
    ids = [item[0] for item in slide_metadata()]
    assert len(ids) == 14
    assert len(ids) == len(set(ids))
    assert ids[-1] == "conclusao"
    assert {"questionario", "motor", "cobertura", "demo"}.isdisjoint(ids)
    titles = {item[1] for item in slide_metadata()}
    assert {"Questionário e importância", "Motor matemático", "Correspondência e cobertura", "Demonstração do MVP"}.isdisjoint(titles)


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


def test_round_trip_uses_named_conclusion_slide():
    main = (ROOT / "src" / "main.jsx").read_text(encoding="utf-8")
    data = source("presentationData.js")
    assert "PRESENTATION_RETURN_SLIDE_ID = 'conclusao'" in data
    assert "origem', 'apresentacao'" in data
    assert "retorno', PRESENTATION_RETURN_SLIDE_ID" in data
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


def test_only_conclusion_slide_renders_the_large_public_qr_code():
    component = source("Presentation.jsx")
    data = source("presentationData.js")
    conclusion_case = component.split("case 'conclusao':", 1)[1].split("default:", 1)[0]
    assert component.count("<PresentationQRCode") == 1
    assert "<PresentationQRCode url={PUBLIC_SITE_URL}" in conclusion_case
    assert "{PUBLIC_SITE_URL}/" in conclusion_case
    assert "import.meta.env.VITE_PUBLIC_SITE_URL" in data
    assert "https://voto-consciente.netlify.app/" in data
    assert "https://voto-consciente.netlify.app/" not in component


def test_conclusion_combines_message_call_to_action_and_qr():
    component = source("Presentation.jsx")
    conclusion_case = component.split("case 'conclusao':", 1)[1].split("default:", 1)[0]
    assert "O projeto não diz em quem o eleitor deve votar" in conclusion_case
    assert "Aponte a câmera ou acesse o endereço" in conclusion_case
    assert "Não é necessário fazer cadastro." in conclusion_case
    assert "Abrir o MVP" in conclusion_case
    assert "case 'demo':" not in component


def test_conclusion_qr_has_prominent_responsive_size():
    css = source("Presentation.css")
    rule = re.search(r"\.presentation-qr-code \{([^}]+)\}", css).group(1)
    assert "width: clamp(250px, 26vw, 390px)" in rule
    assert "aspect-ratio: 1" in rule


def test_external_context_links_open_safely():
    component = source("Presentation.jsx")
    evidence_card = source("components/EvidenceCard.jsx")
    assert 'target="_blank"' in evidence_card
    assert 'rel="noopener noreferrer"' in evidence_card
    assert "abre em nova aba" in evidence_card
    assert "g1.globo.com" in component
    assert "veja.abril.com.br" in component


def test_presentation_data_matches_current_repository_scope_and_imports_official_research():
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
    assert "import researchEvidence from '../../data/research_evidence.json'" in presentation_data
    assert "researchParticipants: researchEvidence.sample_size" in presentation_data
    assert "researchResult('candidate_awareness')" in presentation_data
    assert "researchResult('proposal_awareness')" in presentation_data
    assert "researchParticipants: 136" not in presentation_data


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
    research = json.loads((ROOT / "data" / "research_evidence.json").read_text(encoding="utf-8"))
    results = {item.get("id"): item for item in research["results"]}
    evidence_case = component.split("case 'evidencias':", 1)[1].split("case 'objetivo':", 1)[0]
    assert evidence_case.count("<EvidenceCard") == 3
    for text in ("Pesquisa do grupo", "69%", "88%", "59%"):
        assert text in component or text in data
    assert research["sample_size"] == 136
    assert results["candidate_awareness"]["percentage"] == 79.4
    assert results["proposal_awareness"]["percentage"] == 40.4
    assert "metrics.researchParticipants" in evidence_case
    assert "RESEARCH_RESULTS.map" in evidence_case
    for duplicated_value in ("136 participantes", "79.4", "40.4", "79,4%", "40,4%"):
        assert duplicated_value not in data
        assert duplicated_value not in evidence_case


def test_slide_seven_states_context_and_limitations():
    component = source("Presentation.jsx")
    evidence_case = component.split("case 'evidencias':", 1)[1].split("case 'objetivo':", 1)[0]
    expected = (
        "Conhecem pouco ou apenas algumas candidaturas",
        "Dizem conhecer poucas propostas dos candidatos",
        "amostra por conveniência",
        "se dizem indecisos sobre o voto para governador",
        "se dizem indecisos sobre o voto para o Senado",
        "Fonte externa referente ao Rio de Janeiro",
        "dos brasileiros não sabiam em quem votar ou declaravam intenção de votar em branco ou nulo",
        "Dado nacional usado como contexto histórico de 2018",
        "Não representa Pernambuco em 2026",
    )
    research = json.loads((ROOT / "data" / "research_evidence.json").read_text(encoding="utf-8"))
    combined = evidence_case + json.dumps(research, ensure_ascii=False)
    assert all(text in combined for text in expected)


def test_slide_seven_uses_projectable_type_hierarchy():
    css = source("Presentation.css")
    metric_value = re.search(r"\.evidence-metric strong \{([^}]+)\}", css).group(1)
    metric_label = re.search(r"\.evidence-metric span \{([^}]+)\}", css).group(1)
    disclaimer = re.search(r"\.evidence-card__source \{([^}]+)\}", css).group(1)
    assert "clamp(2rem, 3.2vw, 3.5rem)" in metric_value
    assert "clamp(1.05rem, 1.35vw, 1.45rem)" in metric_label
    assert "font-size: var(--slide-small-size)" in disclaimer


def test_slides_eight_ten_eleven_twelve_and_thirteen_are_top_aligned_by_semantic_id():
    css = source("Presentation.css")
    expected_ids = ("objetivo", "preparacao", "perguntas", "arquitetura", "limitacoes")
    for slide_id in expected_ids:
        assert f".presentation-slide--{slide_id} .slide-content" in css
    alignment_rule = css.split(".presentation-slide--evidencias .slide-content", 1)[1].split("}", 1)[0]
    assert "justify-content: flex-start" in alignment_rule
    assert "padding-top: clamp(" in alignment_rule


def test_slide_eleven_has_five_cards_in_two_then_three_structure():
    component = source("Presentation.jsx")
    css = source("Presentation.css")
    questions_case = component.split("case 'perguntas':", 1)[1].split("case 'arquitetura':", 1)[0]
    for title in ("Fonte dos dados", "Organização temática", "Identificação dos contrastes", "Formulação", "Limite metodológico"):
        assert questions_case.count(title) == 1
    assert "grid-template-columns: repeat(6, minmax(0, 1fr))" in css
    assert ".method-steps > :nth-child(-n + 2) { grid-column: span 3; }" in css
    assert ".method-steps > :nth-child(n + 3) { grid-column: span 2; }" in css


def test_slide_thirteen_has_eight_numbered_limitations():
    component = source("Presentation.jsx")
    limitations_case = component.split("case 'limitacoes':", 1)[1].split("case 'conclusao':", 1)[0]
    expected = (
        "Compara somente conteúdo documentado",
        "Não avalia viabilidade jurídica, técnica ou financeira",
        "Não prevê cumprimento das propostas",
        "Planos têm níveis diferentes de detalhamento",
        "A classificação parcial exige julgamento metodológico",
        "Pesquisa própria por conveniência",
        "Recorte exclusivo do Governo de Pernambuco",
        "A preparação inicial ocorreu fora do código e ainda possui limitação de rastreabilidade técnica",
    )
    assert all(limitations_case.count(text) == 1 for text in expected)
    assert "map((item, index)" in limitations_case
    assert "String(index + 1).padStart(2, '0')" in limitations_case


def test_method_and_limitations_grids_have_responsive_and_print_layouts():
    css = source("Presentation.css")
    tablet = css.split("@media (max-width: 900px)", 1)[1].split("@media (max-width: 700px)", 1)[0]
    mobile = css.split("@media (max-width: 700px)", 1)[1].split("@media (max-width: 380px)", 1)[0]
    print_css = css.split("@media print", 1)[1]
    assert ".method-steps { grid-template-columns: repeat(2, minmax(0, 1fr))" in tablet
    assert ".method-steps > :last-child { grid-column: 1 / -1; }" in tablet
    assert ".method-steps { grid-template-columns: 1fr" in mobile
    assert ".limitations-grid { grid-template-columns: 1fr" in mobile
    assert ".print-deck .method-steps" in print_css
    assert ".print-deck .limitations-grid" in print_css


def test_removed_question_example_is_not_left_in_presentation():
    component = source("Presentation.jsx")
    assert "HEALTH_QUESTION" not in component
    assert "case 'questionario':" not in component


def test_current_scope_and_pipeline_boundaries_are_explicit():
    component = source("Presentation.jsx")
    data = source("presentationData.js")
    assert "candidacies: 7" in data
    assert "officialPlans: 7" in data
    assert "analyzedPages: 311" in data
    assert "themes: 7" in data
    assert "publishedQuestions: 7" in data
    assert "Agente de IA generativa supervisionado" in component
    assert "Baseado no Gemini e supervisionado pela equipe" in component
    assert "O questionário e o cálculo não utilizam IA" in component
    assert "Gemini em ambiente de notebook, utilizado na preparação offline dos dados" in component
    for step in (
        "Planos oficiais do TSE",
        "Agente de IA generativa supervisionado",
        "Organização dos temas e propostas",
        "Perguntas e matriz em JSON",
        "Questionário",
        "Cálculo determinístico",
        "Resultados e fontes",
    ):
        assert step in component
    assert "não possui rastreabilidade técnica completa" in component
    for obsolete in ("OCR", "PyPDF", "Tesseract", "manifesto", "revisão humana"):
        assert obsolete.casefold() not in component.casefold()


def test_evidence_cards_are_responsive_without_internal_scroll():
    css = source("Presentation.css")
    grid_rule = re.search(r"\.evidence-grid \{([^}]+)\}", css).group(1)
    evidence_rule = re.search(r"\.evidence-card \{([^}]+)\}", css).group(1)
    assert "grid-template-columns: repeat(3, minmax(0, 1fr))" in grid_rule
    assert "flex-direction: column" in evidence_rule
    assert "min-height: 0" in evidence_rule
    assert "overflow" not in evidence_rule


def test_slide_frame_uses_one_bounded_sixteen_by_nine_viewport():
    css = source("Presentation.css")
    frame = re.search(r"\.presentation-slide-frame \{([^}]+)\}", css, re.S).group(1)
    slide = re.search(r"\.presentation-slide \{([^}]+)\}", css, re.S).group(1)
    assert "aspect-ratio: 16 / 9" in frame
    assert "calc(100cqh * 16 / 9)" in frame
    assert "max-width: 100%" in frame
    assert "max-height: 100%" in frame
    assert "container-type: size" in frame
    assert "width: 1600px" in slide
    assert "height: 900px" in slide
    assert "transform: scale(calc(100cqw / 1600px))" in slide
    assert "transform-origin: top left" in slide
    assert "min-height: 0" in slide
    assert "box-sizing: border-box" in slide
    assert "grid-template-rows: auto minmax(0, 1fr) auto" in slide


def test_slide_footer_has_dedicated_grid_row_and_content_can_shrink():
    css = source("Presentation.css")
    content = re.search(r"\.slide-content \{([^}]+)\}", css).group(1)
    footer = re.search(r"\.slide-footer \{([^}]+)\}", css).group(1)
    assert "min-height: 0" in content
    assert "position: absolute" not in footer
    assert "position: relative" in footer


def test_problem_slide_uses_two_columns_three_rows_without_fixed_card_height():
    component = source("Presentation.jsx")
    css = source("Presentation.css")
    problem_case = component.split("case 'problema':", 1)[1].split("case 'evidencias':", 1)[0]
    for item in ("Planos extensos", "Documentos pouco padronizados", "Comparação difícil", "Candidaturas pouco conhecidas", "Propostas difíceis de localizar no TSE"):
        assert problem_case.count(item) == 1
    grid = re.search(r"\.problem-grid \{([^}]+)\}", css).group(1)
    card = re.search(r"\.problem-grid > div \{([^}]+)\}", css).group(1)
    assert "repeat(2, minmax(0, 1fr))" in grid
    assert "repeat(3, minmax(0, 1fr))" in grid
    assert "min-height: 0" in card
    assert not re.search(r"(?<!min-)height\s*:", card)


def test_print_uses_same_grid_frame_and_exact_sixteen_by_nine_page():
    css = source("Presentation.css")
    print_css = css.split("@media print", 1)[1]
    assert "size: 13.333in 7.5in" in print_css
    assert "width: 13.333in !important" in print_css
    assert "height: 7.5in !important" in print_css
    assert "max-height: 7.5in !important" in print_css
    assert "display: grid !important" in print_css
    assert "grid-template-rows: auto minmax(0, 1fr) auto !important" in print_css
    assert ".print-deck .evidence-grid { grid-template-columns: repeat(3" in print_css


def test_presentation_uses_centralized_type_spacing_and_card_tokens():
    css = source("Presentation.css")
    shell = re.search(r"\.presentation-shell \{([^}]+)\}", css, re.S).group(1)
    expected_tokens = (
        "--slide-title-size",
        "--slide-question-size",
        "--slide-subtitle-size",
        "--slide-highlight-size",
        "--slide-body-size",
        "--slide-small-size",
        "--slide-gap-xs",
        "--slide-gap-sm",
        "--slide-gap-md",
        "--slide-gap-lg",
        "--slide-gap-xl",
        "--slide-padding-inline",
        "--slide-padding-block",
        "--slide-card-padding",
        "--slide-card-radius",
        "--slide-border",
    )
    assert all(token in shell for token in expected_tokens)
    assert "--slide-body-size: clamp(1.125rem" in shell
    assert "--slide-small-size: clamp(1.125rem" in shell


def test_informational_text_uses_minimum_eighteen_pixel_tokens_and_strong_contrast():
    css = source("Presentation.css")
    for selector in (
        ".slide-kicker",
        ".slide-eyebrow",
        ".slide-footer",
        ".method-steps small",
        ".tech-diagram span",
        ".closing-qr__url",
    ):
        rule = re.search(rf"{re.escape(selector)} \{{([^}}]+)\}}", css).group(1)
        assert "var(--slide-small-size)" in rule
    for color in ("#0d554d", "#263d38", "#42544f", "#a33f32"):
        assert color in css


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
    footer_rule = re.search(r"\.slide-footer \{([^}]+)\}", css).group(1)
    assert "presentation-qr" not in footer_rule
    assert "Acesse o MVP" not in slide


def test_team_name_and_order_are_consistent():
    component = source("Presentation.jsx")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    expected = ["Ben-hur Queiroz", "Hallisson Lima", "Lucas Kamel", "Rodrigo Monteiro", "Thamyres Costa"]
    assert "Ben-Hur Cavalcanti" not in component
    assert "Ben-Hur Cavalcanti" not in readme
    assert "const TEAM = ['" + "', '".join(expected) + "'];" in component
    positions = [readme.index(f"- {name}") for name in expected]
    assert positions == sorted(positions)


def test_flow_has_no_arrow_after_last_step_and_snakes_without_empty_target():
    flow = source("components/SlideFlow.jsx")
    css = source("Presentation.css")
    assert "index < steps.length - 1" in flow
    assert ".slide-flow li:nth-child(5) { grid-column: 4; grid-row: 2; }" in css
    assert ".slide-flow li:nth-child(7) { grid-column: 2; grid-row: 2; }" in css
    mobile = css.split("@media (max-width: 700px)", 1)[1].split("@media (max-width: 380px)", 1)[0]
    assert ".slide-flow { grid-template-columns: 1fr" in mobile


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
    for expression in ("melhor candidato", "candidato ideal", "resultado certo", "ranking dos melhores", "a ia escolhe", "a ia recomenda", "agente autônomo", "agentes de ia"):
        assert expression not in content


def test_scoring_engine_hash_is_preserved():
    normalized = (ROOT / "scoring.py").read_bytes().replace(b"\r\n", b"\n")
    assert hashlib.sha256(normalized).hexdigest() == "8d40d85428646c8f80dce63ffc8d7e244f5600cab4df8d93247449280a04c81d"
