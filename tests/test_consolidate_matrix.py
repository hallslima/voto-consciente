from ai_pipeline.scripts.consolidate_matrix import approved


def record(evidence_id="evidence-001", status="approved", **extra):
    return {"evidence_id": evidence_id, "review_status": status, **extra}


def decision(evidence_id="evidence-001", eligibility="yes"):
    return {"evidence_id": evidence_id, "matrix_eligibility": eligibility}


def test_approved_with_yes_is_consolidated():
    item = record()
    assert approved([item], [decision()]) == [item]


def test_approved_with_no_is_not_consolidated():
    assert approved([record()], [decision(eligibility="no")]) == []


def test_approved_with_needs_adjustment_is_not_consolidated():
    assert approved([record()], [decision(eligibility="needs_adjustment")]) == []


def test_approved_without_matching_decision_is_not_consolidated():
    assert approved([record()], [decision(evidence_id="different-id")]) == []


def test_pending_with_yes_is_not_consolidated():
    assert approved([record(status="pending")], [decision()]) == []


def test_rejected_with_yes_is_not_consolidated():
    assert approved([record(status="rejected")], [decision()]) == []


def test_unknown_decision_does_not_release_another_record():
    records = [record("known-id")]
    decisions = [decision("unknown-id", "yes")]
    assert approved(records, decisions) == []


def test_legacy_format_remains_compatible_but_explicit_eligibility_is_strict():
    legacy = record("legacy-without-field")
    eligible = record("legacy-yes", matrix_eligibility="yes")
    ineligible = record("legacy-no", matrix_eligibility="no")
    unknown = record("legacy-unknown", matrix_eligibility="unknown")
    assert approved([legacy, eligible, ineligible, unknown]) == [legacy, eligible]


def test_empty_review_decisions_publishes_nothing():
    assert approved([record()], []) == []
