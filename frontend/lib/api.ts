import type { Alert, Location, Verdict, VerificationRecord } from "./types";

// Defaults to the local MVP backend from ghana-earth-intelligence.
// Set NEXT_PUBLIC_API_BASE_URL to point at a deployed backend instead.
const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL?.replace(/\/$/, "") || "http://localhost:8000";

async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, { cache: "no-store" });
  if (!res.ok) {
    throw new Error(`GEI API GET ${path} failed: ${res.status} ${res.statusText}`);
  }
  return (await res.json()) as T;
}

async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const detail = await res.text().catch(() => "");
    throw new Error(`GEI API POST ${path} failed: ${res.status} ${detail}`);
  }
  return (await res.json()) as T;
}

export function fetchLocations(): Promise<Location[]> {
  return apiGet<Location[]>("/api/locations");
}

export function fetchAlerts(): Promise<Alert[]> {
  return apiGet<Alert[]>("/api/alerts");
}

export function fetchAlert(id: string): Promise<Alert> {
  return apiGet<Alert>(`/api/alerts/${encodeURIComponent(id)}`);
}

export function fetchVerifications(alertId: string): Promise<VerificationRecord[]> {
  return apiGet<VerificationRecord[]>(`/api/verification/${encodeURIComponent(alertId)}`);
}

export function submitVerification(input: {
  alert_id: string;
  verdict: Verdict;
  notes?: string;
  verified_by: string;
}): Promise<VerificationRecord> {
  return apiPost<VerificationRecord>("/api/verification", input);
}

export { API_BASE_URL };
