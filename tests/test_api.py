from __future__ import annotations

from fastapi.testclient import TestClient

from api.app.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_demo_scan_response_shape() -> None:
    response = client.post("/api/v1/scans/demo", json={"rows": 120, "showSafe": False, "maxDisplay": 40})

    assert response.status_code == 200
    payload = response.json()
    assert payload["meta"]["mode"] == "demo"
    assert payload["summary"]["total"] == 120
    assert "exportToken" in payload
    assert isinstance(payload["rows"], list)


def test_upload_rejects_invalid_file() -> None:
    response = client.post(
        "/api/v1/scans/upload",
        files={"file": ("invalid.csv", b"foo,bar\n1,2\n", "text/csv")},
    )

    assert response.status_code == 400
    assert "Kolom tidak ditemukan" in response.json()["detail"]
