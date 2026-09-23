import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scoring import NO_OPINION, calculate_results
from validation import validate_matrix


def load(name):
    with (ROOT / "data" / name).open(encoding="utf-8") as file:
        return json.load(file)


def test_no_opinion_is_ignored():
    questions = load("questions.json")
    candidates = load("candidates.json")
    answers = {question["id"]: NO_OPINION for question in questions}
    weights = {question["id"]: 3 for question in questions}
    results = calculate_results(questions, candidates, answers, weights)
    assert all(result.score == 0 for result in results)
    assert all(result.answered_questions == 0 for result in results)


def test_exact_match_reaches_one_hundred_on_answered_classified_theme():
    questions = load("questions.json")
    candidates = load("candidates.json")
    answers = {question["id"]: NO_OPINION for question in questions}
    answers["q1_saude"] = "A"
    weights = {question["id"]: 1 for question in questions}
    results = calculate_results(questions, candidates, answers, weights)
    guilherme = next(item for item in results if item.candidate_id == "guilherme_fonseca")
    assert guilherme.score == 100
    assert guilherme.coverage == 100


def test_missing_classification_reduces_coverage():
    questions = load("questions.json")
    candidates = load("candidates.json")
    answers = {question["id"]: "A" for question in questions}
    weights = {question["id"]: 1 for question in questions}
    results = calculate_results(questions, candidates, answers, weights)
    victor = next(item for item in results if item.candidate_id == "victor_assis")
    assert victor.coverage < 100


def test_matrix_uses_only_allowed_compatibility_values():
    assert validate_matrix(load("questions.json"), load("candidates.json")) == []


def test_weighted_formula_and_memory():
    questions = load("questions.json")
    candidates = load("candidates.json")
    answers = {question["id"]: NO_OPINION for question in questions}
    answers["q1_saude"] = "A"
    answers["q2_educacao"] = "B"
    weights = {question["id"]: 1 for question in questions}
    weights["q1_saude"] = 3
    weights["q2_educacao"] = 2
    results = calculate_results(questions, candidates, answers, weights)
    joao = next(item for item in results if item.candidate_id == "joao_campos")
    assert joao.numerator == 2
    assert joao.denominator == 5
    assert joao.score == 40


def test_multiple_response_profiles_stay_bounded_and_sorted():
    questions = load("questions.json")
    candidates = load("candidates.json")
    scenarios = [
        ({question["id"]: question["options"][0]["id"] for question in questions}, 1),
        ({question["id"]: question["options"][-1]["id"] for question in questions}, 3),
        (
            {
                question["id"]: (
                    NO_OPINION if index % 2 else question["options"][index % len(question["options"])]["id"]
                )
                for index, question in enumerate(questions)
            },
            2,
        ),
    ]
    for answers, weight in scenarios:
        weights = {question["id"]: weight for question in questions}
        results = calculate_results(questions, candidates, answers, weights)
        assert all(0 <= result.score <= 100 for result in results)
        assert all(0 <= result.coverage <= 100 for result in results)
        assert [result.score for result in results] == sorted(
            [result.score for result in results], reverse=True
        )
