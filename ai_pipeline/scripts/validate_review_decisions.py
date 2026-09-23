from __future__ import annotations

from datetime import datetime


DOCUMENTARY_DECISIONS = {"approved", "needs_correction", "rejected"}
COMPETENCES = {"state", "federal", "municipal", "shared", "uncertain"}
ELIGIBILITY_DECISIONS = {"yes", "no", "needs_adjustment"}


def promotion_errors(decision: dict) -> list[str]:
    """Return blockers that prevent a human review decision from being promoted."""
    errors = []
    if decision.get("documentary_decision") != "approved":
        errors.append("decisão documental deve ser approved")
    if not str(decision.get("reviewer_name") or "").strip():
        errors.append("nome do revisor ausente")
    reviewed_at = decision.get("reviewed_at")
    if not reviewed_at:
        errors.append("data da revisão ausente")
    else:
        try:
            datetime.fromisoformat(str(reviewed_at).replace("Z", "+00:00"))
        except ValueError:
            errors.append("data da revisão não está em ISO 8601")
    eligibility = decision.get("matrix_eligibility")
    if eligibility not in ELIGIBILITY_DECISIONS:
        errors.append("decisão de elegibilidade ausente ou inválida")
    if eligibility in {"no", "needs_adjustment"} and not str(decision.get("eligibility_justification") or "").strip():
        errors.append("justificativa de elegibilidade obrigatória")
    if decision.get("predominant_competence") not in COMPETENCES:
        errors.append("competência predominante ausente ou inválida")
    return errors


def is_promotable(decision: dict) -> bool:
    return not promotion_errors(decision)
