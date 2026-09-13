// Mirrors app/models.py in the ghana-earth-intelligence backend repo.
// Keep these two in sync by hand until an OpenAPI-to-TS codegen step
// is added (tracked as a Phase 3 follow-up, not done yet).

export type RiskBucket = "LOW" | "MODERATE" | "ELEVATED" | "HIGH" | "CRITICAL";

export type DisturbanceClass =
  | "mining_disturbance_candidate"
  | "vegetation_loss_ambiguous"
  | "natural_variation_candidate"
  | "no_significant_change";

export type Verdict =
  | "confirmed"
  | "false_positive"
  | "requires_investigation"
  | "insufficient_evidence";

export interface Location {
  id: string;
  name: string;
  lat: number;
  lon: number;
}

export interface EvidenceItem {
  signal: string;
  value: number;
  contribution_points: number;
}

export interface Alert {
  id: string;
  location: Location;
  disturbance_class: DisturbanceClass | string;
  ndvi_drop: number;
  disturbed_fraction: number;
  risk_score: number;
  risk_bucket: RiskBucket | string;
  evidence: EvidenceItem[];
  status: string;
  data_source: "synthetic" | "sentinel-2" | "sentinel-1" | "landsat" | string;
  model_version: string;
  persisted: boolean;
  generated_at: string;
}

export interface VerificationRecord {
  alert_id: string;
  verdict: Verdict;
  notes?: string | null;
  verified_by: string;
  verified_at: string;
}
