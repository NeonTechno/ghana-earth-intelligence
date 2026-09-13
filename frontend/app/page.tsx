"use client";

import { useCallback, useEffect, useState } from "react";
import GhanaMap from "@/components/GhanaMap";
import AlertDetailPanel from "@/components/AlertDetailPanel";
import { fetchAlerts } from "@/lib/api";
import type { Alert } from "@/lib/types";

export default function Page() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchAlerts();
      const sorted = [...data].sort((a, b) => b.risk_score - a.risk_score);
      setAlerts(sorted);
      if (!selectedAlert && sorted.length > 0) {
        setSelectedAlert(sorted[0]);
      }
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Failed to reach the Ghana Earth Intelligence API."
      );
    } finally {
      setLoading(false);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <main className="gei-app">
      <header className="gei-topbar">
        <div>
          <h1>Ghana Earth Intelligence</h1>
          <p className="gei-tagline">Galamsey satellite monitor \u2014 MVP dashboard</p>
        </div>
        <button className="gei-refresh" onClick={load} disabled={loading}>
          {loading ? "Loading\u2026" : "Refresh"}
        </button>
      </header>

      {error && (
        <div className="gei-error-banner">
          Could not load alerts from the backend ({error}). Is the API running at the
          configured NEXT_PUBLIC_API_BASE_URL?
        </div>
      )}

      <div className="gei-disclaimer-banner">
        All data shown is <strong>synthetic</strong> (procedurally generated for MVP
        demonstration) and every alert requires human verification. See LIMITATIONS.md
        in the backend repo. Nothing here is evidence of real activity at these
        locations.
      </div>

      <div className="gei-layout">
        <aside className="gei-alert-list">
          <h2>Alerts ({alerts.length})</h2>
          <ul>
            {alerts.map((alert) => (
              <li key={alert.id}>
                <button
                  className={`gei-alert-item ${
                    selectedAlert?.id === alert.id ? "gei-alert-item--active" : ""
                  }`}
                  onClick={() => setSelectedAlert(alert)}
                >
                  <span
                    className={`gei-dot gei-dot--${alert.risk_bucket.toLowerCase()}`}
                    aria-hidden
                  />
                  <span className="gei-alert-item__name">{alert.location.name}</span>
                  <span className="gei-alert-item__score">{alert.risk_score}</span>
                </button>
              </li>
            ))}
          </ul>
        </aside>

        <div className="gei-map-wrap">
          <GhanaMap
            alerts={alerts}
            selectedAlertId={selectedAlert?.id ?? null}
            onSelectAlert={setSelectedAlert}
          />
        </div>

        <AlertDetailPanel alert={selectedAlert} />
      </div>
    </main>
  );
}
