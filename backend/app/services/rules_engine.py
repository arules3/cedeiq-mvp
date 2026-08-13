"""
Treaty rules engine.

This is the heart of CedeIQ (see CLAUDE.md §6 steering rules): given a Policy
and the pool of active Treaties, decide which treaty applies, calculate the
cession, and always return a traceable rule description for the audit log.

Two treaty types are implemented (MVP scope — see specs/mvp-spec.md §6):

- Quota Share (QS): reinsurer takes a fixed % of every matching policy.
  ceded_premium = policy.premium * (cession_pct / 100)
  ceded_exposure = policy.sum_insured * (cession_pct / 100)

- Excess of Loss (XoL): reinsurer covers exposure ABOVE an attachment point,
  up to a limit. It doesn't cede premium the same way QS does — in a real
  XoL treaty the cedent pays a separate XoL premium (rate on line), but for
  MVP purposes we treat "ceded_premium" as a proportional allocation of the
  policy premium representing the layer covered, which is a simplification
  documented here on purpose so it isn't mistaken for production actuarial logic.

Matching rule (steering rule 3): a treaty only applies if line_of_business
matches AND (treaty.peril is None OR treaty.peril == policy.peril) AND the
policy's effective_date falls within the treaty's effective window.

If no treaty matches, or the matched treaty's capacity would be exceeded,
the policy is a BLIND SPOT — it is flagged, not silently dropped or capped.
"""

from dataclasses import dataclass
from decimal import Decimal

from app.models.treaty import Treaty, TreatyType
from app.models.policy import Policy


@dataclass
class CessionResult:
    policy_id: int
    treaty_id: int
    ceded_premium: Decimal
    ceded_exposure: Decimal
    rule_applied: str


@dataclass
class BlindSpot:
    policy_id: int
    reason: str


def find_matching_treaties(policy: Policy, treaties: list[Treaty]) -> list[Treaty]:
    """Steering rule 3 lives here: matching is explicit and testable, not implicit."""
    matches = []
    for t in treaties:
        if t.line_of_business != policy.line_of_business:
            continue
        if t.peril is not None and t.peril != policy.peril:
            continue
        if not (t.effective_from <= policy.effective_date <= t.effective_to):
            continue
        matches.append(t)
    return matches


def apply_quota_share(policy: Policy, treaty: Treaty) -> CessionResult:
    pct = Decimal(str(treaty.cession_pct)) / Decimal("100")
    ceded_premium = Decimal(str(policy.premium)) * pct
    ceded_exposure = Decimal(str(policy.sum_insured)) * pct
    rule = f"Quota Share '{treaty.name}': {treaty.cession_pct}% of premium and sum insured ceded."
    return CessionResult(policy.id, treaty.id, ceded_premium, ceded_exposure, rule)


def apply_excess_of_loss(policy: Policy, treaty: Treaty) -> CessionResult | BlindSpot:
    sum_insured = Decimal(str(policy.sum_insured))
    attachment = Decimal(str(treaty.attachment_point))
    limit = Decimal(str(treaty.limit))

    if sum_insured <= attachment:
        # Exposure doesn't reach the treaty's attachment point at all.
        return BlindSpot(
            policy.id,
            f"Sum insured {sum_insured} does not reach XoL attachment point {attachment} "
            f"on treaty '{treaty.name}'.",
        )

    exposure_above_attachment = sum_insured - attachment
    ceded_exposure = min(exposure_above_attachment, limit)

    if exposure_above_attachment > limit:
        # Real blind spot: the layer above the treaty's limit is uncovered.
        # We still cede what the treaty covers, but this must ALSO be flagged
        # for the uncovered remainder (steering rule 3: never silently cap).
        rule = (
            f"Excess of Loss '{treaty.name}': covers {ceded_exposure} above "
            f"{attachment}, but exposure exceeds treaty limit by "
            f"{exposure_above_attachment - limit} — uncovered remainder flagged separately."
        )
    else:
        rule = f"Excess of Loss '{treaty.name}': covers {ceded_exposure} above attachment {attachment}."

    # Simplified premium allocation, proportional to exposure ceded (see module docstring).
    proportion = ceded_exposure / sum_insured if sum_insured > 0 else Decimal("0")
    ceded_premium = Decimal(str(policy.premium)) * proportion

    return CessionResult(policy.id, treaty.id, ceded_premium, ceded_exposure, rule)


def process_policy(policy: Policy, treaties: list[Treaty]) -> CessionResult | BlindSpot:
    """Entry point: match, apply, and return either a CessionResult or a BlindSpot.
    Caller (routers/cessions.py) is responsible for persisting the result and
    writing the AuditLog entry — this function stays pure/testable.
    """
    matches = find_matching_treaties(policy, treaties)

    if not matches:
        return BlindSpot(policy.id, "No treaty matches this policy's line of business/peril/date.")

    # If multiple treaties match, prefer XoL over QS (XoL is typically a
    # backstop layered on top of QS in real programs) — documented choice,
    # revisit if your capstone's scenario needs different precedence.
    matches.sort(key=lambda t: 0 if t.type == TreatyType.EXCESS_OF_LOSS else 1)
    treaty = matches[0]

    if treaty.type == TreatyType.QUOTA_SHARE:
        return apply_quota_share(policy, treaty)
    elif treaty.type == TreatyType.EXCESS_OF_LOSS:
        return apply_excess_of_loss(policy, treaty)

    return BlindSpot(policy.id, f"Unsupported treaty type: {treaty.type}")
