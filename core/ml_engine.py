"""
core/ml_engine.py
──────────────────
Machine Learning Engine — Isolation Forest untuk deteksi anomali traffic.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from core.helpers import step, ok, warn

BASE_COLS = ["src_port", "dst_port", "packet_count", "byte_count", "duration"]


def build_features(df):
    features = df[BASE_COLS].copy()

    # Pastikan semua kolom numerik dan bersih dari inf/nan
    for col in BASE_COLS:
        features[col] = pd.to_numeric(features[col], errors="coerce").fillna(0)
        features[col] = features[col].replace([np.inf, -np.inf], 0)

    features["byte_per_packet"] = np.where(
        features["packet_count"] > 0,
        features["byte_count"] / features["packet_count"], 0
    )

    # log1p hanya aman untuk nilai >= 0, clip dulu untuk antisipasi nilai negatif
    features["log_packet_count"] = np.log1p(features["packet_count"].clip(lower=0))
    features["log_byte_count"]   = np.log1p(features["byte_count"].clip(lower=0))
    features["log_duration"]     = np.log1p(features["duration"].clip(lower=0))

    # Bersihkan hasil akhir dari inf/nan yang mungkin masih tersisa
    features = features.replace([np.inf, -np.inf], 0).fillna(0)

    scaler   = StandardScaler()
    X_scaled = scaler.fit_transform(features)
    return X_scaled, scaler


def run_isolation_forest(df, contamination=0.15, n_estimators=150, n_jobs=1):
    X_scaled, _ = build_features(df)

    model = IsolationForest(
        n_estimators=n_estimators,
        contamination=contamination,
        random_state=42,
        n_jobs=n_jobs,
    )
    predictions = model.fit_predict(X_scaled)
    scores      = model.decision_function(X_scaled)
    return predictions, scores
