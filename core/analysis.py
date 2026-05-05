"""
core/analysis.py
────────────────
Reusable analysis pipeline shared by the CLI and FastAPI service.
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import pandas as pd

from core.ml_engine import run_isolation_forest
from core.rules import run_rules
from core.scorer import score_all

LEVELS_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "SAFE"]


@dataclass
class AnalysisArtifacts:
    result: pd.DataFrame
    response: dict


def build_result_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    predictions, if_scores = run_isolation_forest(df)
    all_threats = run_rules(df)
    risk_scores, risk_labels = score_all(df, predictions, if_scores, all_threats)

    result = df.copy()
    result["if_anomaly"] = predictions == -1
    result["threats"] = all_threats
    result["risk_score"] = risk_scores
    result["risk_label"] = risk_labels
    return result


def sample_per_level(result: pd.DataFrame, max_display: int, show_safe: bool) -> dict[str, pd.DataFrame]:
    levels = LEVELS_ORDER if show_safe else LEVELS_ORDER[:-1]

    level_dfs: dict[str, pd.DataFrame] = {}
    for level in levels:
        subset = result[result["risk_label"] == level]
        if not subset.empty:
            level_dfs[level] = subset.sort_values("risk_score", ascending=False)

    if not level_dfs:
        return {}

    n_active = len(level_dfs)
    per_level = max(1, max_display // n_active)
    remainder = max_display - (per_level * n_active)

    sampled: dict[str, pd.DataFrame] = {}
    first = True
    for level in levels:
        if level not in level_dfs:
            continue
        quota = per_level + (remainder if first else 0)
        sampled[level] = level_dfs[level].head(quota)
        first = False

    return sampled


def _build_summary(result: pd.DataFrame) -> dict:
    counts = result["risk_label"].value_counts()
    return {
        "total": int(len(result)),
        "critical": int(counts.get("CRITICAL", 0)),
        "high": int(counts.get("HIGH", 0)),
        "medium": int(counts.get("MEDIUM", 0)),
        "low": int(counts.get("LOW", 0)),
        "safe": int(counts.get("SAFE", 0)),
        "anomalyCount": int(result["if_anomaly"].sum()),
    }


def _build_distribution(result: pd.DataFrame) -> list[dict]:
    counts = result["risk_label"].value_counts()
    return [
        {"level": level, "count": int(counts.get(level, 0))}
        for level in LEVELS_ORDER
    ]


def _build_top_threats(result: pd.DataFrame) -> list[dict]:
    threat_counter: dict[str, int] = {}
    for threats in result["threats"]:
        for threat in threats:
            threat_counter[threat] = threat_counter.get(threat, 0) + 1

    ordered = sorted(threat_counter.items(), key=lambda item: (-item[1], item[0]))
    return [{"name": name, "count": count} for name, count in ordered[:8]]


def _rows_for_response(result: pd.DataFrame, show_safe: bool, max_display: int | None) -> list[dict]:
    visible = result if show_safe else result[result["risk_label"] != "SAFE"]

    if max_display is not None:
        sampled = sample_per_level(visible, max_display, show_safe)
        if sampled:
            visible = pd.concat(sampled.values(), ignore_index=True)
        else:
            visible = visible.head(max_display)

    visible = visible.sort_values(["risk_score", "dst_port"], ascending=[False, True])

    rows: list[dict] = []
    for _, row in visible.iterrows():
        rows.append(
            {
                "src_ip": str(row.get("src_ip", "0.0.0.0")),
                "dst_ip": str(row.get("dst_ip", "0.0.0.0")),
                "protocol": str(row.get("protocol", "TCP")),
                "dst_port": int(row.get("dst_port", 0)),
                "if_anomaly": bool(row.get("if_anomaly", False)),
                "threats": [str(item) for item in row.get("threats", [])],
                "risk_score": int(row.get("risk_score", 0)),
                "risk_label": str(row.get("risk_label", "SAFE")),
            }
        )
    return rows


def build_scan_response(
    result: pd.DataFrame,
    *,
    mode: str,
    filename: str | None,
    processing_time_ms: int,
    show_safe: bool,
    max_display: int | None,
    warnings: list[str] | None = None,
    export_token: str | None = None,
) -> dict:
    rows = _rows_for_response(result, show_safe, max_display)
    response_warnings = list(warnings or [])
    visible_total = int(len(result if show_safe else result[result["risk_label"] != "SAFE"]))

    if max_display is not None and len(rows) < visible_total:
        response_warnings.append(
            f"Response rows were limited to {len(rows)} items using proportional per-level sampling."
        )

    return {
        "meta": {
            "mode": mode,
            "filename": filename,
            "rowCount": int(len(result)),
            "returnedRowCount": int(len(rows)),
            "processingTimeMs": int(processing_time_ms),
        },
        "summary": _build_summary(result),
        "topThreats": _build_top_threats(result),
        "distribution": _build_distribution(result),
        "rows": rows,
        "exportToken": export_token,
        "warnings": response_warnings,
    }


def run_scan(
    df: pd.DataFrame,
    *,
    mode: str,
    filename: str | None = None,
    show_safe: bool = False,
    max_display: int | None = None,
    warnings: list[str] | None = None,
    export_token: str | None = None,
) -> AnalysisArtifacts:
    started_at = time.perf_counter()
    result = build_result_dataframe(df)
    elapsed_ms = int((time.perf_counter() - started_at) * 1000)
    response = build_scan_response(
        result,
        mode=mode,
        filename=filename,
        processing_time_ms=elapsed_ms,
        show_safe=show_safe,
        max_display=max_display,
        warnings=warnings,
        export_token=export_token,
    )
    return AnalysisArtifacts(result=result, response=response)
