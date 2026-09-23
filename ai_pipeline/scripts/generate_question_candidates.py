from __future__ import annotations

import argparse
import json
from pathlib import Path


def generate_candidates(records: list[dict]) -> list[dict]:
    """Create review drafts; this never publishes questions automatically."""
    themes = sorted({record["theme"] for record in records if record.get("review_status") == "approved"})
    return [{"theme": theme, "generation_mode": "general", "source_evidence_ids": [], "review_status": "pending", "reviewer": "", "review_notes": "Rascunho para revisão humana."} for theme in themes]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    records = json.loads(args.input.read_text(encoding="utf-8"))
    drafts = generate_candidates(records if isinstance(records, list) else [records])
    args.output.write_text(json.dumps(drafts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"OK: {len(drafts)} pergunta(s) candidata(s) para revisão.")


if __name__ == "__main__":
    main()
