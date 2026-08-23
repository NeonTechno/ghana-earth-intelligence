from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_list_locations():
    resp = client.get("/api/locations")
    assert resp.status_code == 200
    assert len(resp.json()) == 4


def test_list_alerts_returns_risk_scores():
    resp = client.get("/api/alerts")
    assert resp.status_code == 200
    alerts = resp.json()
    assert len(alerts) == 4
    for a in alerts:
        assert 0 <= a["risk_score"] <= 100
        assert a["data_source"] == "synthetic"
        assert a["status"] == "REQUIRES_HUMAN_VERIFICATION"


def test_get_risk_custom_location():
    resp = client.get("/api/risk", params={"lat": 6.5, "lon": -1.5, "name": "test-site"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["location"]["lat"] == 6.5


def test_verification_flow():
    alerts = client.get("/api/alerts").json()
    alert_id = alerts[0]["id"]
    resp = client.post(
        "/api/verification",
        json={"alert_id": alert_id, "verdict": "requires_investigation", "verified_by": "test-user"},
    )
    assert resp.status_code == 200
    assert resp.json()["verdict"] == "requires_investigation"


def test_unknown_alert_404():
    resp = client.get("/api/alerts/does-not-exist")
    assert resp.status_code == 404
