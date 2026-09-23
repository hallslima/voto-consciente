from __future__ import annotations

from dataclasses import dataclass
from typing import Any


NO_OPINION = "NO_OPINION"


@dataclass(frozen=True)
class CandidateResult:
    candidate_id: str
    name: str
    party: str
    score: float
    coverage: float
    answered_with_evidence: int
    answered_questions: int
    priority_points: float
    numerator: float
    denominator: float
    details: list[dict[str, Any]]


def calculate_results(
    questions: list[dict[str, Any]],
    candidates: list[dict[str, Any]],
    answers: dict[str, str],
    weights: dict[str, int],
) -> list[CandidateResult]:
    """Calculate the ICT exactly as documented by the project.

    Questions answered with "No opinion" are ignored for everyone. For each
    candidate, questions without a classified position are excluded from that
    candidate's denominator and remain visible through the coverage indicator.
    """
    answered_ids = [
        question["id"]
        for question in questions
        if answers.get(question["id"]) not in (None, NO_OPINION)
    ]
    question_by_id = {question["id"]: question for question in questions}
    results: list[CandidateResult] = []

    for candidate in candidates:
        numerator = 0.0
        denominator = 0.0
        priority_points = 0.0
        evidence_count = 0
        details: list[dict[str, Any]] = []

        for question_id in answered_ids:
            chosen = answers[question_id]
            weight = int(weights.get(question_id, 1))
            position = candidate.get("positions", {}).get(question_id)
            question = question_by_id[question_id]

            if not position or not position.get("primary_option"):
                details.append(
                    {
                        "question_id": question_id,
                        "theme": question["theme"],
                        "chosen_option": chosen,
                        "candidate_option": None,
                        "similarity": None,
                        "weight": weight,
                        "status": "Sem classificação na matriz atual",
                    }
                )
                continue

            evidence_count += 1
            denominator += weight
            similarity = float(position.get("compatibility", {}).get(chosen, 0.0))
            points = similarity * weight
            numerator += points
            if weight == 3:
                priority_points += points

            details.append(
                {
                    "question_id": question_id,
                    "theme": question["theme"],
                    "chosen_option": chosen,
                    "candidate_option": position["primary_option"],
                    "similarity": similarity,
                    "weight": weight,
                    "points": points,
                    "max_points": weight,
                    "theme_score": similarity * 100.0,
                    "status": "Evidência classificada",
                    "summary": position.get("summary", ""),
                    "source": position.get("source", ""),
                    "page": position.get("page", ""),
                    "evidence_level": position.get("evidence_level"),
                }
            )

        score = (numerator / denominator * 100.0) if denominator else 0.0
        for detail in details:
            detail["contribution_percent"] = (
                detail.get("points", 0.0) / denominator * 100.0
                if denominator and detail.get("similarity") is not None
                else 0.0
            )
        coverage = (
            evidence_count / len(answered_ids) * 100.0 if answered_ids else 0.0
        )
        results.append(
            CandidateResult(
                candidate_id=candidate["id"],
                name=candidate["name"],
                party=candidate["party"],
                score=round(score, 1),
                coverage=round(coverage, 1),
                answered_with_evidence=evidence_count,
                answered_questions=len(answered_ids),
                priority_points=priority_points,
                numerator=round(numerator, 2),
                denominator=round(denominator, 2),
                details=details,
            )
        )

    return sorted(
        results,
        key=lambda item: (-item.score, -item.priority_points, item.name.casefold()),
    )
