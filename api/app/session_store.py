"""
api/app/session_store.py
────────────────────────
Ephemeral in-memory export storage for scan CSV files.
"""

from __future__ import annotations

import secrets
import threading
import time
from dataclasses import dataclass


@dataclass
class ExportSession:
    filename: str
    content: bytes
    expires_at: float


class ExportSessionStore:
    def __init__(self, ttl_seconds: int):
        self.ttl_seconds = ttl_seconds
        self._lock = threading.Lock()
        self._sessions: dict[str, ExportSession] = {}

    def _purge_expired(self) -> None:
        now = time.time()
        expired = [token for token, session in self._sessions.items() if session.expires_at <= now]
        for token in expired:
            self._sessions.pop(token, None)

    def create(self, *, filename: str, content: bytes) -> str:
        token = secrets.token_urlsafe(18)
        with self._lock:
            self._purge_expired()
            self._sessions[token] = ExportSession(
                filename=filename,
                content=content,
                expires_at=time.time() + self.ttl_seconds,
            )
        return token

    def get(self, token: str) -> ExportSession | None:
        with self._lock:
            self._purge_expired()
            return self._sessions.get(token)
