"""
Supabase/PostGIS persistence layer (project spec section 15).

Falls back to no-op (`get_client() -> None`) when SUPABASE_URL isn't set,
so the app -- and the test suite -- keep working without a live database
(e.g. fresh clone, CI, or before .env is configured). When configured,
this is the real Phase 1 persistence layer backing environmental_alerts,
land_change_events, locations, and verification_records.

Writes require the Supabase **service_role** key (not the anon key),
since every table's RLS policy only grants SELECT to anon/authenticated
(see the `gei_rls_policies` migration). Get the service_role key from
Supabase dashboard -> Settings -> API -> service_role and set it as
SUPABASE_SERVICE_ROLE_KEY. Never commit it -- it bypasses RLS entirely.
"""
from __future__ import annotations

import logging
import os
from functools import lru_cache
from typing import Any, Dict, List, Optional

logger = logging.getLogger("gei.db")

try:
    from supabase import Client, create_client
except ImportError:  # pragma: no cover - supabase-py optional at import time
    Client = None  # type: ignore
    create_client = None  # type: ignore


@lru_cache(maxsize=1)
def get_client() -> Optional["Client"]:
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or os.getenv("SUPABASE_ANON_KEY")
    if not url or not key or create_client is None:
        return None
    return create_client(url, key)


def is_configured() -> bool:
    return get_client() is not None


def upsert_location(region_hint: str, name: str, lat: float, lon: float) -> Optional[str]:
    """
    Get-or-create a `locations` row by name. Returns its id, or None if
    the DB isn't configured OR the write failed (e.g. only the anon key
    is set, and RLS correctly rejects the insert) -- callers must treat
    None as "not persisted", never crash on it.
    """
    client = get_client()
    if client is None:
        return None
    try:
        existing = client.table("locations").select("id").eq("name", name).limit(1).execute()
        if existing.data:
            return existing.data[0]["id"]
        point_wkt = f"SRID=4326;POINT({lon} {lat})"
        result = client.table("locations").insert(
            {"name": name, "region": region_hint, "geom": point_wkt}
        ).execute()
        return result.data[0]["id"] if result.data else None
    except Exception:  # noqa: BLE001 - degrade gracefully, never crash the API on a DB hiccup
        logger.warning("upsert_location failed; continuing without persistence", exc_info=True)
        return None


@lru_cache(maxsize=1)
def get_default_model_version_id() -> Optional[str]:
    client = get_client()
    if client is None:
        return None
    try:
        result = (
            client.table("model_versions")
            .select("id")
            .eq("name", "gei-mvp-change-detector")
            .eq("version", "0.1.0")
            .limit(1)
            .execute()
        )
        return result.data[0]["id"] if result.data else None
    except Exception:  # noqa: BLE001
        logger.warning("get_default_model_version_id failed", exc_info=True)
        return None


def persist_alert(
    location_id: Optional[str],
    ndvi_drop: float,
    disturbed_fraction: float,
    disturbance_class: str,
    risk_score: float,
    risk_bucket: str,
    evidence: List[Dict[str, Any]],
) -> Optional[str]:
    """
    Writes a `land_change_events` row + an `environmental_alerts` row.
    Returns the environmental_alerts.id (used as the API-facing alert id
    when persistence is active), or None if persistence isn't configured
    or the write failed.
    """
    client = get_client()
    if client is None:
        return None

    try:
        model_version_id = get_default_model_version_id()

        event = client.table("land_change_events").insert(
            {
                "location_id": location_id,
                "model_version_id": model_version_id,
                "ndvi_drop": ndvi_drop,
                "disturbed_fraction": disturbed_fraction,
                "disturbance_class": disturbance_class,
            }
        ).execute()
        if not event.data:
            return None
        event_id = event.data[0]["id"]

        alert = client.table("environmental_alerts").insert(
            {
                "land_change_event_id": event_id,
                "model_version_id": model_version_id,
                "risk_score": risk_score,
                "risk_bucket": risk_bucket,
                "evidence": evidence,
                "status": "REQUIRES_HUMAN_VERIFICATION",
                "data_source": "synthetic",
            }
        ).execute()
        return alert.data[0]["id"] if alert.data else None
    except Exception:  # noqa: BLE001 - e.g. only the anon key is set and RLS rejects the insert
        logger.warning("persist_alert failed; continuing without persistence", exc_info=True)
        return None


def persist_verification(alert_id: str, verdict: str, notes: Optional[str], verified_by: str) -> bool:
    client = get_client()
    if client is None:
        return False
    try:
        client.table("verification_records").insert(
            {"alert_id": alert_id, "verdict": verdict, "notes": notes, "verified_by": verified_by}
        ).execute()
        return True
    except Exception:  # noqa: BLE001
        logger.warning("persist_verification failed; continuing without persistence", exc_info=True)
        return False


def fetch_verifications(alert_id: str) -> List[Dict[str, Any]]:
    client = get_client()
    if client is None:
        return []
    try:
        result = (
            client.table("verification_records")
            .select("*")
            .eq("alert_id", alert_id)
            .order("verified_at")
            .execute()
        )
        return result.data or []
    except Exception:  # noqa: BLE001
        logger.warning("fetch_verifications failed", exc_info=True)
        return []
