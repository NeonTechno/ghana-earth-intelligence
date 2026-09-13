"use client";

import { useEffect, useRef } from "react";
import maplibregl, { Map as MLMap, Marker } from "maplibre-gl";
import type { Alert, RiskBucket } from "@/lib/types";

// Free, no-API-key vector basemap (OpenFreeMap). No fabricated/paid
// credentials -- see PROJECT_AUDIT.md / DATA_SOURCES.md for the backend's
// data-sourcing discipline; the frontend follows the same rule.
const BASEMAP_STYLE_URL = "https://tiles.openfreemap.org/styles/liberty";

// Rough center of Ghana's mining belt, not the country centroid, so the
// four demo locations are all visible on load without extra panning.
const GHANA_CENTER: [number, number] = [-1.9, 5.9];
const INITIAL_ZOOM = 6.4;

const RISK_COLORS: Record<string, string> = {
  LOW: "#2e7d32",
  MODERATE: "#f9a825",
  ELEVATED: "#ef6c00",
  HIGH: "#d84315",
  CRITICAL: "#b71c1c",
};

function riskColor(bucket: string): string {
  return RISK_COLORS[bucket as RiskBucket] ?? "#616161";
}

interface GhanaMapProps {
  alerts: Alert[];
  selectedAlertId: string | null;
  onSelectAlert: (alert: Alert) => void;
}

export default function GhanaMap({ alerts, selectedAlertId, onSelectAlert }: GhanaMapProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const mapRef = useRef<MLMap | null>(null);
  const markersRef = useRef<Map<string, Marker>>(new Map());

  // Initialize the map once.
  useEffect(() => {
    if (!containerRef.current || mapRef.current) return;

    const map = new maplibregl.Map({
      container: containerRef.current,
      style: BASEMAP_STYLE_URL,
      center: GHANA_CENTER,
      zoom: INITIAL_ZOOM,
    });
    map.addControl(new maplibregl.NavigationControl(), "top-right");
    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  // Keep markers in sync with the alerts list.
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    const currentIds = new Set(alerts.map((a) => a.id));

    // Remove markers for alerts no longer present.
    for (const [id, marker] of markersRef.current.entries()) {
      if (!currentIds.has(id)) {
        marker.remove();
        markersRef.current.delete(id);
      }
    }

    // Add/update markers.
    for (const alert of alerts) {
      let marker = markersRef.current.get(alert.id);
      if (!marker) {
        const el = document.createElement("button");
        el.className = "gei-marker";
        el.type = "button";
        el.setAttribute("aria-label", `${alert.location.name}: ${alert.risk_bucket} risk`);
        el.addEventListener("click", () => onSelectAlert(alert));

        marker = new maplibregl.Marker({ element: el })
          .setLngLat([alert.location.lon, alert.location.lat])
          .addTo(map);
        markersRef.current.set(alert.id, marker);
      }

      const el = marker.getElement();
      el.style.backgroundColor = riskColor(alert.risk_bucket);
      el.classList.toggle("gei-marker--selected", alert.id === selectedAlertId);
      el.title = `${alert.location.name} \u2014 ${alert.risk_bucket} (${alert.risk_score})`;
    }
  }, [alerts, selectedAlertId, onSelectAlert]);

  return <div ref={containerRef} className="gei-map" />;
}
