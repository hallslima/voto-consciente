import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_candidate_assets_are_associated_and_exist():
    candidates = json.loads((ROOT / "data" / "candidates.json").read_text(encoding="utf-8"))

    assert len(candidates) == 7
    assert all(candidate["registration_status"] == "Deferido" for candidate in candidates)

    for candidate in candidates:
        photo = ROOT / "public" / candidate["photo_url"].lstrip("/")
        plan = ROOT / "public" / candidate["local_plan_url"].lstrip("/")
        assert photo.is_file()
        assert plan.is_file()
        assert candidate["official_data_url"] != candidate["local_plan_url"]
        assert candidate["plan_document"].endswith(".pdf")

    expected_photos = {Path(candidate["photo_url"]).name for candidate in candidates}
    expected_plans = {Path(candidate["local_plan_url"]).name for candidate in candidates}
    actual_photos = {path.name for path in (ROOT / "public" / "assets" / "candidates").glob("*.jpg")}
    actual_plans = {path.name for path in (ROOT / "public" / "documents" / "government-plans").glob("*.pdf")}
    assert actual_photos == expected_photos
    assert actual_plans == expected_plans
    assert len(actual_photos) == len(actual_plans) == 7
