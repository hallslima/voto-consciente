from __future__ import annotations

import argparse
import json
from pathlib import Path


def approved(records: list[dict], decisions: list[dict] | None = None) -> list[dict]:
    """Select records eligible for consolidation.

    Payloads with ``review_decisions`` are strict: an approved record needs a
    matching decision whose ``matrix_eligibility`` is exactly ``yes``.

    Temporary legacy compatibility applies only when ``review_decisions`` is
    absent (``decisions is None``). Old reviewed files, such as the Guilherme
    Fonseca pilot, predate matrix eligibility and remain publishable when
    approved. If a legacy record already has ``matrix_eligibility``, however,
    its value must also be exactly ``yes``.
    """
    if decisions is not None:
        eligibility = {
            decision.get("evidence_id"): decision.get("matrix_eligibility")
            for decision in decisions
            if decision.get("evidence_id")
        }
        return [
            record
            for record in records
            if record.get("review_status") == "approved"
            and eligibility.get(record.get("evidence_id")) == "yes"
        ]

    return [
        record
        for record in records
        if record.get("review_status") == "approved"
        and (
            "matrix_eligibility" not in record
            or record.get("matrix_eligibility") == "yes"
        )
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        selected = approved(payload)
    elif "records" in payload:
        selected = approved(payload["records"], payload.get("review_decisions"))
    else:
        selected = approved([payload])
    args.output.write_text(json.dumps(selected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK: {len(selected)} registro(s) aprovado(s) consolidado(s).")


if __name__ == "__main__":
    main()
