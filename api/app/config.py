"""
api/app/config.py
─────────────────
Application settings for the FastAPI service.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    api_title: str = "CyberSentinel AI API"
    api_version: str = "1.0.0"
    max_upload_bytes: int = 25 * 1024 * 1024
    export_ttl_seconds: int = 60 * 30
    cors_origins: tuple[str, ...] = ("http://localhost:3000",)


def get_settings() -> Settings:
    raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    origins = tuple(origin.strip() for origin in raw_origins.split(",") if origin.strip())

    return Settings(
        max_upload_bytes=int(os.getenv("MAX_UPLOAD_BYTES", str(25 * 1024 * 1024))),
        export_ttl_seconds=int(os.getenv("EXPORT_TTL_SECONDS", str(60 * 30))),
        cors_origins=origins or ("http://localhost:3000",),
    )
