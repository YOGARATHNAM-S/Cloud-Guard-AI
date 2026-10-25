from fastapi.testclient import TestClient

from app.main import app


def test_investigation_workflow():
    with TestClient(app) as client:
        response = client.post("/api/investigate", json={"description": "Payments API is timing out"})
        audit = client.get("/api/audit")
    assert response.status_code == 200
    body = response.json()
    assert body["data_mode"] == "mock"
    assert body["status"] == "approval_required"
    assert body["diagnosis"]["confidence"] > 0.9
    assert audit.status_code == 200
    assert len(audit.json()["events"]) >= len(body["policy_decisions"])
