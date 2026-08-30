"""
These tests intentionally run WITHOUT SUPABASE_URL set, to verify the
no-op fallback path works (so the app/tests never require a live DB).
"""
import pytest

from app import db


@pytest.fixture(autouse=True)
def _clear_supabase_env(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    monkeypatch.delenv("SUPABASE_ANON_KEY", raising=False)
    db.get_client.cache_clear()
    db.get_default_model_version_id.cache_clear()
    yield
    db.get_client.cache_clear()
    db.get_default_model_version_id.cache_clear()


def test_not_configured_without_env():
    assert db.is_configured() is False
    assert db.get_client() is None


def test_writes_are_noops_when_not_configured():
    assert db.upsert_location("obuasi", "Obuasi", 6.2, -1.6) is None
    assert (
        db.persist_alert(
            location_id=None,
            ndvi_drop=0.1,
            disturbed_fraction=0.1,
            disturbance_class="no_significant_change",
            risk_score=10.0,
            risk_bucket="LOW",
            evidence=[],
        )
        is None
    )
    assert db.persist_verification("some-id", "confirmed", None, "tester") is False
    assert db.fetch_verifications("some-id") == []
