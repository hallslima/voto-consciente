from __future__ import annotations

import argparse
import json
from pathlib import Path


def approved(records: list[dict]) -> list[dict]:
    """Only reviewed evidence may feed a generated matrix candidate."""
    return [
        record
        for record in records
        if record.get("review_status") == "approved"
        and record.get("matrix_eligibility") not in {"no", "needs_adjustment"}
    ]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    records = json.loads(args.input.read_text(encoding="utf-8"))
    selected = approved(records if isinstance(records, list) else [records])
    args.output.write_text(json.dumps(selected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK: {len(selected)} registro(s) aprovado(s) consolidado(s).")


if __name__ == "__main__":
    main()
