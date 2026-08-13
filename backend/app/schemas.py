from datetime import date, datetime
from pydantic import BaseModel, ConfigDict
from app.models.treaty import TreatyType


class TreatyCreate(BaseModel):
    name: str
    type: TreatyType
    line_of_business: str
    peril: str | None = None
    cession_pct: float | None = None       # required if type == quota_share
    attachment_point: float | None = None  # required if type == excess_of_loss
    limit: float | None = None             # required if type == excess_of_loss
    capacity: float
    effective_from: date
    effective_to: date


class TreatyOut(TreatyCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class PolicyCreate(BaseModel):
    policy_number: str
    line_of_business: str
    peril: str
    geography: str
    sum_insured: float
    premium: float
    effective_date: date


class PolicyOut(PolicyCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    created_at: datetime


class CessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    policy_id: int
    treaty_id: int
    ceded_premium: float
    ceded_exposure: float
    rule_applied: str
    created_at: datetime


class BlindSpotOut(BaseModel):
    policy_id: int
    reason: str


class AuditLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    policy_id: int | None
    cession_id: int | None
    action: str
    rule_fired: str
    input_snapshot: dict
    output_snapshot: dict
    created_at: datetime


class DashboardSummary(BaseModel):
    total_policies: int
    total_treaties: int
    total_cessions: int
    total_ceded_premium: float
    total_ceded_exposure: float
    ceded_ratio: float  # total_ceded_premium / total_gross_premium
    blind_spot_count: int
    outstanding_recoverables: float
