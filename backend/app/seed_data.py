"""
Seed script: generates realistic treaties + policies for the CedeIQ demo,
including deliberate 'mainstream scenarios' so the dashboard has something
meaningful to show (see chat discussion — this isn't random test data).

Run with:  python -m app.seed_data   (from the backend/ folder, venv active)

Scenarios baked in on purpose:
  - Property QS treaty: most Property policies cede cleanly at 30%.
  - Marine XoL treaty: most Marine policies attach cleanly above 500K.
  - 2 policies with NO matching treaty at all (wrong line of business) -> blind spot.
  - 1 Marine policy below the XoL attachment point -> blind spot.
  - 1 Marine policy whose exposure exceeds the XoL limit -> partially ceded +
    flagged remainder (steering rule 3 in action).
"""

from datetime import date
from decimal import Decimal

from app.db import Base, engine, SessionLocal
from app.models.treaty import Treaty, TreatyType
from app.models.policy import Policy

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# --- Treaties -----------------------------------------------------------

property_qs = Treaty(
    name="Property Quota Share 2026",
    type=TreatyType.QUOTA_SHARE,
    line_of_business="Property",
    peril=None,  # applies to all perils within Property
    cession_pct=30.00,
    capacity=Decimal("50000000"),
    effective_from=date(2026, 1, 1),
    effective_to=date(2026, 12, 31),
)

marine_xol = Treaty(
    name="Marine Cargo XoL Layer 1",
    type=TreatyType.EXCESS_OF_LOSS,
    line_of_business="Marine",
    peril="Cargo",
    attachment_point=Decimal("500000"),
    limit=Decimal("2000000"),
    capacity=Decimal("20000000"),
    effective_from=date(2026, 1, 1),
    effective_to=date(2026, 12, 31),
)

db.add_all([property_qs, marine_xol])
db.commit()

# --- Policies -------------------------------------------------------------
# 15 clean Property policies (will cede via Quota Share)
property_policies = [
    Policy(
        policy_number=f"PROP-{1000+i}",
        line_of_business="Property",
        peril="Fire" if i % 2 == 0 else "Flood",
        geography="US-CA" if i % 3 == 0 else "US-TX",
        sum_insured=Decimal(str(500_000 + i * 75_000)),
        premium=Decimal(str(8_000 + i * 900)),
        effective_date=date(2026, 3, 1),
    )
    for i in range(15)
]

# 10 clean Marine Cargo policies (will cede via XoL, above 500K attachment)
marine_policies_clean = [
    Policy(
        policy_number=f"MAR-{2000+i}",
        line_of_business="Marine",
        peril="Cargo",
        geography="US-Gulf",
        sum_insured=Decimal(str(800_000 + i * 150_000)),
        premium=Decimal(str(15_000 + i * 1_200)),
        effective_date=date(2026, 4, 1),
    )
    for i in range(10)
]

# Scenario: below attachment point -> blind spot (doesn't reach 500K)
marine_below_attachment = Policy(
    policy_number="MAR-3001",
    line_of_business="Marine",
    peril="Cargo",
    geography="US-Gulf",
    sum_insured=Decimal("350000"),
    premium=Decimal("6000"),
    effective_date=date(2026, 4, 15),
)

# Scenario: exceeds XoL limit -> partially ceded + flagged remainder
marine_exceeds_limit = Policy(
    policy_number="MAR-3002",
    line_of_business="Marine",
    peril="Cargo",
    geography="US-Gulf",
    sum_insured=Decimal("4000000"),  # attachment 500K + limit 2M = covers up to 2.5M; 1.5M uncovered
    premium=Decimal("60000"),
    effective_date=date(2026, 5, 1),
)

# Scenario: wrong line of business entirely -> no treaty matches -> blind spot
no_treaty_policies = [
    Policy(
        policy_number="CASU-4001",
        line_of_business="Casualty",
        peril="Liability",
        geography="US-NY",
        sum_insured=Decimal("1000000"),
        premium=Decimal("20000"),
        effective_date=date(2026, 2, 1),
    ),
    Policy(
        policy_number="AVIA-4002",
        line_of_business="Aviation",
        peril="Hull",
        geography="US-FL",
        sum_insured=Decimal("5000000"),
        premium=Decimal("90000"),
        effective_date=date(2026, 6, 1),
    ),
]

all_policies = (
    property_policies
    + marine_policies_clean
    + [marine_below_attachment, marine_exceeds_limit]
    + no_treaty_policies
)

db.add_all(all_policies)
db.commit()

print(f"Seeded 2 treaties and {len(all_policies)} policies.")
print("Expected outcomes when you run POST /cessions/run:")
print(f"  - {len(property_policies)} Property policies -> ceded via Quota Share")
print(f"  - {len(marine_policies_clean)} Marine policies -> ceded via XoL cleanly")
print("  - MAR-3001 -> blind spot (below attachment point)")
print("  - MAR-3002 -> ceded 2M, remainder flagged (exceeds treaty limit)")
print("  - CASU-4001, AVIA-4002 -> blind spots (no matching treaty)")

db.close()