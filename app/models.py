from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Location(BaseModel):
    id: str
    name: str
    lat: float
    lon: float


class EvidenceItem(BaseModel):
    signal: str
    value: float = Field(ge=0, le=1)
    contribution_points: float


class Alert(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    id: str
    location: Location
    disturbance_class: str
    ndvi_drop: float
    disturbed_fraction: float
    risk_score: float
    risk_bucket: str
    evidence: List[EvidenceItem]
    status: str = "REQUIRES_HUMAN_VERIFICATION"
    data_source: Literal["synthetic", "sentinel-2", "sentinel-1", "landsat"] = "synthetic"
    model_version: str = "gei-mvp-0.1.0"
    persisted: bool = False
    generated_at: datetime = Field(default_factory=_utc_now)


class VerificationRecord(BaseModel):
    alert_id: str
    verdict: Literal["confirmed", "false_positive", "requires_investigation", "insufficient_evidence"]
    notes: Optional[str] = None
    verified_by: str
    verified_at: datetime = Field(default_factory=_utc_now)
