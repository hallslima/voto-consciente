import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load(name):
    return json.loads((ROOT / "data" / name).read_text(encoding="utf-8"))


def test_public_copy_has_correct_non_storage_message():
    public_text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in [ROOT / "src" / "main.jsx", ROOT / "data" / "questions.json"]
    )
    assert "Suas respostas ficam neste dispositivo" not in public_text
    assert "Suas escolhas não saem deste dispositivo" not in public_text
    assert "As respostas são usadas apenas para calcular o resultado e não são armazenadas pelo sistema." in public_text


def test_readme_explains_application_level_privacy_without_infrastructure_promise():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    source = (ROOT / "src" / "main.jsx").read_text(encoding="utf-8")
    for statement in (
        "Não existe banco de dados de respostas, login ou perfil do eleitor.",
        "estado temporário da interface",
        "enviadas à API somente para o cálculo",
        "não são gravadas pela aplicação",
        "`localStorage`, `sessionStorage` ou cookies",
        "logs operacionais da infraestrutura",
    ):
        assert statement in readme
    for storage_api in ("localStorage", "sessionStorage", "document.cookie", "indexedDB"):
        assert storage_api not in source


def test_research_form_and_spreadsheet_urls_are_not_consumed_by_frontend_components():
    main = (ROOT / "src" / "main.jsx").read_text(encoding="utf-8")
    presentation = (ROOT / "src" / "presentation" / "Presentation.jsx").read_text(encoding="utf-8")
    assert "research_evidence" not in main
    assert "form_url" not in main + presentation
    assert "spreadsheet_url" not in main + presentation


def test_result_help_actions_and_accessible_weights_are_present():
    source = (ROOT / "src" / "main.jsx").read_text(encoding="utf-8")
    assert source.count('className="result-help"') == 1
    assert "O que significa % de correspondência?" in source
    assert "O que significa % de cobertura?" in source
    assert "Como ler os dois indicadores juntos?" in source
    assert "← Rever respostas" in source
    assert "Refazer questionário" in source
    assert "[1, 2, 3].map" in source
    assert "shouldRevealResults.current = false" in source
    assert "shouldRevealResults.current = true" in source
    assert "scrollIntoView" in source


def test_question_and_option_ids_are_the_expected_contract():
    questions = load("questions.json")
    assert [question["id"] for question in questions] == [
        "q1_saude", "q2_educacao", "q3_seguranca", "q4_transporte",
        "q5_saneamento", "q6_emprego", "q7_assistencia",
    ]
    assert {question["id"]: [option["id"] for option in question["options"]] for question in questions} == {
        "q1_saude": ["A", "B", "C"], "q2_educacao": ["A", "B", "C"],
        "q3_seguranca": ["A", "B", "C", "D"], "q4_transporte": ["A", "B", "C"],
        "q5_saneamento": ["A", "B", "C"], "q6_emprego": ["A", "B", "C"],
        "q7_assistencia": ["A", "B", "C"],
    }


def test_social_links_are_unique_safe_http_urls_and_invalid_whatsapp_is_absent():
    candidates = load("candidates.json")
    serialized = json.dumps(candidates, ensure_ascii=False)
    assert "08199272-4739" not in serialized
    assert "081992723398" not in serialized
    for candidate in candidates:
        urls = [link["url"] for link in candidate.get("social_links", [])]
        assert len(urls) == len(set(urls))
        assert all(re.match(r"^https?://[^\s]+$", url) for url in urls)
    without_links = {candidate["id"] for candidate in candidates if not candidate.get("social_links")}
    assert {"guilherme_fonseca"} <= without_links


def test_result_photos_and_external_link_protection_are_structural():
    source = (ROOT / "src" / "main.jsx").read_text(encoding="utf-8")
    styles = (ROOT / "src" / "styles.css").read_text(encoding="utf-8")
    assert 'className="candidate-photo"' in source
    assert "aspect-ratio: 3 / 4" in styles
    assert 'className={`theme-candidate' in source
    assert 'alt="" aria-hidden="true"' in source
    assert 'rel="noopener noreferrer"' in source


def test_theme_comparison_reserves_plot_and_label_space_per_theme():
    source = (ROOT / "src" / "main.jsx").read_text(encoding="utf-8")
    styles = (ROOT / "src" / "styles.css").read_text(encoding="utf-8")
    assert 'className="theme-list"' in source
    assert 'className="theme-plot"' in source
    assert "grid-template-rows: 118px 36px" in styles
    assert "min-height: 206px" in styles
    assert "border-bottom: 1px solid var(--line)" in styles
    assert "theme-bar-stage" in source
    assert "theme_score.toFixed(0)" in source
    assert "'--theme-score': detail.theme_score" in source


def test_theme_comparison_distinguishes_scores_missing_evidence_and_ignored_themes():
    source = (ROOT / "src" / "main.jsx").read_text(encoding="utf-8")
    styles = (ROOT / "src" / "styles.css").read_text(encoding="utf-8")
    assert "detail?.similarity === null" in source
    assert "Sem evidência" in source
    assert "Não considerado" in source
    assert "sem evidência localizada" in source
    assert "`${detail.theme_score.toFixed(0)}% de correspondência`" in source
    assert "role=\"img\"" in source
    assert "border-bottom: 2px dashed" in styles
    assert "bottom: min(calc(var(--theme-score)" in styles


def test_theme_comparison_explains_that_missing_evidence_is_not_opposition():
    source = (ROOT / "src" / "main.jsx").read_text(encoding="utf-8")
    assert "Os valores mostram a correspondência em cada tema. Ausência de evidência não significa posição contrária." in source


def test_calculation_explainer_uses_full_width_and_responsive_columns():
    styles = (ROOT / "src" / "styles.css").read_text(encoding="utf-8")
    assert ".calculation-explainer { width: 100%; max-width: none" in styles
    assert "grid-template-columns: repeat(4, 1fr)" in styles
    assert "grid-template-columns: repeat(2, minmax(0, 1fr))" in styles
    assert "@media (max-width: 600px)" in styles
