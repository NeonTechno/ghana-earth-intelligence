from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


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
    generated_at: datetime = Field(default_factory=datetime.utcnow)


class VerificationRecord(BaseModel):
    alert_id: str
    verdict: Literal["confirmed", "false_positive", "requires_investigation", "insufficient_evidence"]
    notes: Optional[str] = None
    verified_by: str
    verified_at: datetime = Field(default_factory=datetime.utcnow)
