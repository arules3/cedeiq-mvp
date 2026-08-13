"""
Tests for the treaty rules engine (app/services/rules_engine.py).

These instantiate Treaty/Policy objects directly in memory — no database
needed, because the rules engine is deliberately pure (see module docstring
in rules_engine.py). That design choice is exactly what makes it this easy
to test.

Run with:  pytest -q   (from backend/, venv active)
"""

from datetime import date
from decimal import Decimal

import pytest

from app.models.treaty import Treaty, TreatyType
from app.models.policy import Policy
from app.services.rules_engine import (
    find_matching_treaties,
    apply_quota_share,
    apply_excess_of_loss,
    process_policy,
    CessionResult,
    BlindSpot,
)


# --- Fixtures -------------------------------------------------------------

@pytest.fixture
def property_qs_treaty():
    return Treaty(
        id=1,
        name="Property QS",
        type=TreatyType.QUOTA_SHARE,
        line_of_business="Property",
        peril=None,
        cession_pct=Decimal("30.00"),
        capacity=Decimal("50000000"),
        effective_from=date(2026, 1, 1),
        effective_to=date(2026, 12, 31),
    )


@pytest.fixture
def marine_xol_treaty():
    return Treaty(
        id=2,
        name="Marine XoL",
        type=TreatyType.EXCESS_OF_LOSS,
        line_of_business="Marine",
        peril="Cargo",
        attachment_point=Decimal("500000"),
        limit=Decimal("2000000"),
        capacity=Decimal("20000000"),
        effective_from=date(2026, 1, 1),
        effective_to=date(2026, 12, 31),
    )


def make_policy(**overrides):
    defaults = dict(
        id=1,
        policy_number="TEST-1",
        line_of_business="Property",
        peril="Fire",
        geography="US-CA",
        sum_insured=Decimal("1000000"),
        premium=Decimal("10000"),
        effective_date=date(2026, 6, 1),
    )
    defaults.update(overrides)
    return Policy(**defaults)


# --- find_matching_treaties -------------------------------------------------

def test_matches_on_line_of_business(property_qs_treaty):
    policy = make_policy(line_of_business="Property")
    matches = find_matching_treaties(policy, [property_qs_treaty])
    assert matches == [property_qs_treaty]


def test_no_match_for_different_line_of_business(property_qs_treaty):
    policy = make_policy(line_of_business="Casualty")
    matches = find_matching_treaties(policy, [property_qs_treaty])
    assert matches == []


def test_no_match_outside_effective_window(property_qs_treaty):
    policy = make_policy(effective_date=date(2027, 1, 15))  # after treaty's 2026 window
    matches = find_matching_treaties(policy, [property_qs_treaty])
    assert matches == []


def test_peril_specific_treaty_requires_matching_peril(marine_xol_treaty):
    matching = make_policy(line_of_business="Marine", peril="Cargo", sum_insured=Decimal("1000000"))
    non_matching = make_policy(line_of_business="Marine", peril="Hull", sum_insured=Decimal("1000000"))

    assert find_matching_treaties(matching, [marine_xol_treaty]) == [marine_xol_treaty]
    assert find_matching_treaties(non_matching, [marine_xol_treaty]) == []


# --- Quota Share ------------------------------------------------------------

def test_quota_share_cedes_correct_percentage(property_qs_treaty):
    policy = make_policy(sum_insured=Decimal("1000000"), premium=Decimal("10000"))
    result = apply_quota_share(policy, property_qs_treaty)

    assert isinstance(result, CessionResult)
    assert result.ceded_premium == Decimal("3000.00")   # 30% of 10,000
    assert result.ceded_exposure == Decimal("300000.00")  # 30% of 1,000,000
    assert "30.00%" in result.rule_applied or "30.00" in result.rule_applied


# --- Excess of Loss ----------------------------------------------------------

def test_xol_cedes_layer_above_attachment(marine_xol_treaty):
    # sum insured 1.5M, attachment 500K -> exposure above attachment = 1M, within 2M limit
    policy = make_policy(line_of_business="Marine", peril="Cargo", sum_insured=Decimal("1500000"))
    result = apply_excess_of_loss(policy, marine_xol_treaty)

    assert isinstance(result, CessionResult)
    assert result.ceded_exposure == Decimal("1000000")


def test_xol_below_attachment_is_blind_spot(marine_xol_treaty):
    # sum insured below the 500K attachment point never reaches the treaty at all
    policy = make_policy(line_of_business="Marine", peril="Cargo", sum_insured=Decimal("350000"))
    result = apply_excess_of_loss(policy, marine_xol_treaty)

    assert isinstance(result, BlindSpot)
    assert "attachment" in result.reason.lower()


def test_xol_exceeding_limit_flags_remainder_not_silent_cap(marine_xol_treaty):
    # sum insured 4M: attachment 500K + limit 2M covers up to 2.5M -> 1.5M uncovered.
    # Steering rule 3 (CLAUDE.md): must flag, not silently cap.
    policy = make_policy(line_of_business="Marine", peril="Cargo", sum_insured=Decimal("4000000"))
    result = apply_excess_of_loss(policy, marine_xol_treaty)

    assert isinstance(result, CessionResult)  # still cedes what the treaty covers...
    assert result.ceded_exposure == Decimal("2000000")  # exactly the treaty limit
    assert "exceeds treaty limit" in result.rule_applied  # ...but the rule text flags the breach


# --- process_policy (full pipeline) -----------------------------------------

def test_process_policy_no_treaty_is_blind_spot(property_qs_treaty):
    policy = make_policy(line_of_business="Aviation")
    result = process_policy(policy, [property_qs_treaty])
    assert isinstance(result, BlindSpot)
    assert "No treaty matches" in result.reason


def test_process_policy_prefers_xol_when_both_match(property_qs_treaty, marine_xol_treaty):
    # Construct a treaty pool where a policy could theoretically match two
    # treaties on the same line of business, to confirm the documented
    # precedence rule (XoL preferred over QS) in process_policy().
    xol_property = Treaty(
        id=3,
        name="Property XoL Backstop",
        type=TreatyType.EXCESS_OF_LOSS,
        line_of_business="Property",
        peril=None,
        attachment_point=Decimal("100000"),
        limit=Decimal("5000000"),
        capacity=Decimal("10000000"),
        effective_from=date(2026, 1, 1),
        effective_to=date(2026, 12, 31),
    )
    policy = make_policy(line_of_business="Property", sum_insured=Decimal("1000000"))
    result = process_policy(policy, [property_qs_treaty, xol_property])

    assert isinstance(result, CessionResult)
    assert result.treaty_id == xol_property.id  # XoL won precedence over QS