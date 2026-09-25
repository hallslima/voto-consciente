from __future__ import annotations

from dataclasses import asdict

import pytest
from fastapi import HTTPException

import app
from scoring import NO_OPINION, calculate_results


def call_results(answers, weights=None):
    return app.results(app.QuestionnairePayload(answers=answers, weights=weights or {}))


def test_valid_alternative_preserves_scoring_result():
    answers = {"q1_saude": "A"}
    weights = {"q1_saude": 3}
    response = call_results(answers, weights)
    expected = calculate_results(app.QUESTIONS, app.CANDIDATES, answers, weights)
    assert response == {"results": [asdict(result) for result in expected]}


def test_no_opinion_is_valid_when_another_question_is_answered():
    response = call_results({"q1_saude": NO_OPINION, "q2_educacao": "B"})
    assert len(response["results"]) == 7


@pytest.mark.parametrize(
    "answers, expected_detail",
    [
        ({"q1_saude": "Z"}, "Alternativa inválida"),
        ({"q1_saude": "D"}, "Alternativa inválida"),
        ({"pergunta_inexistente": "A"}, "Pergunta desconhecida"),
    ],
)
def test_invalid_answers_are_rejected_before_scoring(answers, expected_detail):
    with pytest.raises(HTTPException) as captured:
        call_results(answers)
    assert captured.value.status_code == 400
    assert expected_detail in captured.value.detail


def test_invalid_weight_is_rejected():
    with pytest.raises(HTTPException) as captured:
        call_results({"q1_saude": "A"}, {"q1_saude": 4})
    assert captured.value.status_code == 400
    assert "pesos" in captured.value.detail


def test_all_answers_without_opinion_are_rejected():
    answers = {question["id"]: NO_OPINION for question in app.QUESTIONS}
    with pytest.raises(HTTPException) as captured:
        call_results(answers)
    assert captured.value.status_code == 400
    assert "pelo menos uma resposta" in captured.value.detail
