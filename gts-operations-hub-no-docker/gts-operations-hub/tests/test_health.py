import os
import tempfile
from pathlib import Path

# Ensure tests do not use a developer's real database.
_temp = tempfile.TemporaryDirectory()
os.environ["DATABASE_URL"] = "sqlite:///" + str(Path(_temp.name) / "test.db").replace("\\", "/")
os.environ["AUTH_ENABLED"] = "false"

from fastapi.testclient import TestClient
from app.main import app


def test_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


def test_asset_and_incident_lifecycle():
    with TestClient(app) as client:
        a = client.post("/api/v1/assets", json={"name": "test-api", "asset_type": "application"})
        assert a.status_code == 201, a.text
        asset_id = a.json()["id"]
        assert client.get("/api/v1/overview").json()["total_assets"] == 1
        incident = client.post("/api/v1/incidents", json={"title": "Demo outage", "asset_id": asset_id})
        assert incident.status_code == 201
        incident_id = incident.json()["id"]
        assert client.get("/api/v1/overview").json()["open_incidents"] == 1
        assert client.post(f"/api/v1/incidents/{incident_id}/resolve").json()["status"] == "resolved"
        assert client.get("/api/v1/overview").json()["open_incidents"] == 0


def test_metrics_content_type():
    with TestClient(app) as client:
        r = client.get("/api/v1/metrics")
        assert r.status_code == 200
        assert "text/plain" in r.headers["content-type"]
        assert "gts_assets_total" in r.text
