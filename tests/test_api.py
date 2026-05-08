from __future__ import annotations

from fastapi.testclient import TestClient

from api.app.main import app
from api.app.schemas import ScanResponse

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


def test_upload_reads_form_options(monkeypatch) -> None:
    captured = {}

    def fake_analyze_file_bytes(*, file_bytes, filename, show_safe, max_display):
        captured["filename"] = filename
        captured["show_safe"] = show_safe
        captured["max_display"] = max_display

        return ScanResponse.model_validate(
            {
                "meta": {
                    "mode": "upload",
                    "filename": filename,
                    "rowCount": 1,
                    "returnedRowCount": 1,
                    "processingTimeMs": 1,
                },
                "summary": {
                    "total": 1,
                    "critical": 0,
                    "high": 0,
                    "medium": 0,
                    "low": 0,
                    "safe": 1,
                    "anomalyCount": 0,
                },
                "topThreats": [],
                "distribution": [{"level": "SAFE", "count": 1}],
                "rows": [],
                "exportToken": None,
                "warnings": [],
            }
        )

    monkeypatch.setattr("api.app.main._analyze_file_bytes", fake_analyze_file_bytes)

    response = client.post(
        "/api/v1/scans/upload",
        data={"showSafe": "true", "maxDisplay": "17"},
        files={"file": ("traffic.csv", b"src_port,dst_port\n1234,80\n", "text/csv")},
    )

    assert response.status_code == 200
    assert captured == {
        "filename": "traffic.csv",
        "show_safe": True,
        "max_display": 17,
    }
