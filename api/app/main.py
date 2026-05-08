"""
api/app/main.py
───────────────
FastAPI application exposing the CyberSentinel analysis engine.
"""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response

from api.app.config import get_settings
from api.app.schemas import DemoScanRequest, HealthResponse, ScanResponse
from api.app.session_store import ExportSessionStore
from core.analysis import run_scan
from core.loader import load_data_with_metadata
from data.dummy import generate_dummy_data
from output.exporter import dataframe_to_csv_bytes

settings = get_settings()
app = FastAPI(title=settings.api_title, version=settings.api_version)
store = ExportSessionStore(ttl_seconds=settings.export_ttl_seconds)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(settings.cors_origins),
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _create_export(result_df, filename: str) -> str:
    content = dataframe_to_csv_bytes(result_df)
    return store.create(filename=filename, content=content)


def _analyze_file_bytes(
    *,
    file_bytes: bytes,
    filename: str,
    show_safe: bool,
    max_display: int,
) -> ScanResponse:
    suffix = Path(filename).suffix or ".csv"
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
            temp_file.write(file_bytes)
            temp_path = temp_file.name

        df, warnings = load_data_with_metadata(temp_path, exit_on_error=False, verbose=False)
        artifacts = run_scan(
            df,
            mode="upload",
            filename=filename,
            show_safe=show_safe,
            max_display=max_display,
            warnings=warnings,
        )
        export_token = _create_export(artifacts.result, f"{Path(filename).stem}-scan.csv")
        artifacts.response["exportToken"] = export_token
        return ScanResponse.model_validate(artifacts.response)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)


@app.get("/api/v1/health", response_model=HealthResponse)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok", version=settings.api_version)


@app.post("/api/v1/scans/demo", response_model=ScanResponse)
def create_demo_scan(payload: DemoScanRequest) -> ScanResponse:
    df = generate_dummy_data(n_rows=payload.rows)
    artifacts = run_scan(
        df,
        mode="demo",
        filename=None,
        show_safe=payload.showSafe,
        max_display=payload.maxDisplay,
    )
    export_token = _create_export(artifacts.result, "demo-scan.csv")
    artifacts.response["exportToken"] = export_token
    return ScanResponse.model_validate(artifacts.response)


@app.post("/api/v1/scans/upload", response_model=ScanResponse)
async def create_upload_scan(
    file: UploadFile = File(...),
    showSafe: bool = Form(False),
    maxDisplay: int = Form(50, ge=10, le=500),
) -> ScanResponse:
    file_bytes = await file.read()

    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must include a filename.")

    if len(file_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    if len(file_bytes) > settings.max_upload_bytes:
        limit_mb = settings.max_upload_bytes // (1024 * 1024)
        raise HTTPException(
            status_code=413,
            detail=f"Uploaded file exceeds the {limit_mb} MB limit for interactive scans.",
        )

    return _analyze_file_bytes(
        file_bytes=file_bytes,
        filename=file.filename,
        show_safe=showSafe,
        max_display=maxDisplay,
    )


@app.get("/api/v1/exports/{token}")
def download_export(token: str) -> Response:
    session = store.get(token)
    if session is None:
        raise HTTPException(status_code=404, detail="Export session not found or has expired.")

    headers = {
        "Content-Disposition": f'attachment; filename="{session.filename}"',
    }
    return Response(content=session.content, media_type="text/csv", headers=headers)
