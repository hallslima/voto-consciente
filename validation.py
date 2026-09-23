from __future__ import annotations


ALLOWED_COMPATIBILITY = {0.0, 0.5, 1.0}


def validate_matrix(questions, candidates) -> list[str]:
    errors: list[str] = []
    question_options = {
        question["id"]: {option["id"] for option in question["options"]}
        for question in questions
    }
    for candidate in candidates:
        for question_id, position in candidate.get("positions", {}).items():
            if question_id not in question_options:
                errors.append(f"{candidate['name']}: pergunta desconhecida {question_id}.")
                continue
            primary = position.get("primary_option")
            if primary not in question_options[question_id]:
                errors.append(f"{candidate['name']}: alternativa principal inválida em {question_id}.")
            compatibility = position.get("compatibility", {})
            if set(compatibility) != question_options[question_id]:
                errors.append(f"{candidate['name']}: alternativas incompletas em {question_id}.")
            invalid = {
                float(value) for value in compatibility.values()
                if float(value) not in ALLOWED_COMPATIBILITY
            }
            if invalid:
                errors.append(f"{candidate['name']}: compatibilidades inválidas {sorted(invalid)}.")
            if float(compatibility.get(primary, -1)) != 1.0:
                errors.append(f"{candidate['name']}: alternativa principal sem nota 1 em {question_id}.")
    return errors
