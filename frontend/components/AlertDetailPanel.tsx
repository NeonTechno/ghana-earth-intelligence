"use client";

import { useState } from "react";
import { submitVerification } from "@/lib/api";
import type { Alert, Verdict } from "@/lib/types";

const VERDICT_OPTIONS: { value: Verdict; label: string }[] = [
  { value: "confirmed", label: "Confirmed" },
  { value: "false_positive", label: "False positive" },
  { value: "requires_investigation", label: "Requires investigation" },
  { value: "insufficient_evidence", label: "Insufficient evidence" },
];

interface AlertDetailPanelProps {
  alert: Alert | null;
}

export default function AlertDetailPanel({ alert }: AlertDetailPanelProps) {
  const [verdict, setVerdict] = useState<Verdict>("requires_investigation");
  const [notes, setNotes] = useState("");
  const [verifiedBy, setVerifiedBy] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);

  if (!alert) {
    return (
      <aside className="gei-panel gei-panel--empty">
        <p>Select a marker on the map to inspect its evidence and risk breakdown.</p>
      </aside>
    );
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!alert || !verifiedBy.trim()) return;
    setSubmitting(true);
    setSubmitError(null);
    try {
      await submitVerification({
        alert_id: alert.id,
        verdict,
        notes: notes.trim() || undefined,
        verified_by: verifiedBy.trim(),
      });
      setSubmitted(true);
    } catch (err) {
      setSubmitError(err instanceof Error ? err.message : "Failed to submit verification.");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <aside className="gei-panel">
      <header className="gei-panel__header">
        <h2>{alert.location.name}</h2>
        <span className={`gei-badge gei-badge--${alert.risk_bucket.toLowerCase()}`}>
          {alert.risk_bucket} &middot; {alert.risk_score}
        </span>
      </header>

      <dl className="gei-facts">
        <dt>Coordinates</dt>
        <dd>
          {alert.location.lat.toFixed(4)}, {alert.location.lon.toFixed(4)}
        </dd>

        <dt>Disturbance class</dt>
        <dd>{alert.disturbance_class.replaceAll("_", " ")}</dd>

        <dt>NDVI drop</dt>
        <dd>{alert.ndvi_drop.toFixed(3)}</dd>

        <dt>Disturbed fraction</dt>
        <dd>{(alert.disturbed_fraction * 100).toFixed(1)}%</dd>

        <dt>Data source</dt>
        <dd>
          <span className="gei-tag">{alert.data_source}</span>
          {alert.data_source === "synthetic" && (
            <span className="gei-disclaimer"> \u2014 not a real observation, see LIMITATIONS.md</span>
          )}
        </dd>

        <dt>Persisted to database</dt>
        <dd>{alert.persisted ? "yes" : "no (in-memory only)"}</dd>

        <dt>Model version</dt>
        <dd>{alert.model_version}</dd>

        <dt>Status</dt>
        <dd className="gei-status">{alert.status.replaceAll("_", " ")}</dd>
      </dl>

      <h3>Evidence breakdown</h3>
      <ul className="gei-evidence">
        {alert.evidence.map((item) => (
          <li key={item.signal}>
            <span className="gei-evidence__signal">{item.signal.replaceAll("_", " ")}</span>
            <span className="gei-evidence__bar">
              <span
                className="gei-evidence__bar-fill"
                style={{ width: `${Math.round(item.value * 100)}%` }}
              />
            </span>
            <span className="gei-evidence__points">+{item.contribution_points.toFixed(1)}</span>
          </li>
        ))}
      </ul>

      <h3>Record a verification decision</h3>
      {submitted ? (
        <p className="gei-success">Verification recorded. Thank you.</p>
      ) : (
        <form className="gei-form" onSubmit={handleSubmit}>
          <label>
            Verdict
            <select value={verdict} onChange={(e) => setVerdict(e.target.value as Verdict)}>
              {VERDICT_OPTIONS.map((opt) => (
                <option key={opt.value} value={opt.value}>
                  {opt.label}
                </option>
              ))}
            </select>
          </label>

          <label>
            Verified by
            <input
              type="text"
              value={verifiedBy}
              onChange={(e) => setVerifiedBy(e.target.value)}
              placeholder="your name"
              required
            />
          </label>

          <label>
            Notes (optional)
            <textarea value={notes} onChange={(e) => setNotes(e.target.value)} rows={3} />
          </label>

          {submitError && <p className="gei-error">{submitError}</p>}

          <button type="submit" disabled={submitting || !verifiedBy.trim()}>
            {submitting ? "Submitting\u2026" : "Submit verification"}
          </button>
        </form>
      )}
    </aside>
  );
}
