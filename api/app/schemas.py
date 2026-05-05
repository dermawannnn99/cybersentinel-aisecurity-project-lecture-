"""
api/app/schemas.py
──────────────────
Pydantic models for the FastAPI API.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class DemoScanRequest(BaseModel):
    rows: int = Field(default=300, ge=50, le=5000)
    showSafe: bool = False
    maxDisplay: int = Field(default=50, ge=10, le=500)


class ScanMeta(BaseModel):
    mode: str
    filename: str | None = None
    rowCount: int
    returnedRowCount: int
    processingTimeMs: int


class ScanSummary(BaseModel):
    total: int
    critical: int
    high: int
    medium: int
    low: int
    safe: int
    anomalyCount: int


class ThreatCount(BaseModel):
    name: str
    count: int


class DistributionItem(BaseModel):
    level: str
    count: int


class ResultRow(BaseModel):
    src_ip: str
    dst_ip: str
    protocol: str
    dst_port: int
    if_anomaly: bool
    threats: list[str]
    risk_score: int
    risk_label: str


class ScanResponse(BaseModel):
    meta: ScanMeta
    summary: ScanSummary
    topThreats: list[ThreatCount]
    distribution: list[DistributionItem]
    rows: list[ResultRow]
    exportToken: str | None = None
    warnings: list[str] = Field(default_factory=list)


class HealthResponse(BaseModel):
    status: str
    version: str
