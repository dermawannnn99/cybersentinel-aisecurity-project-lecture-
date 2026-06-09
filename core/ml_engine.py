"""
core/ml_engine.py
──────────────────
Machine Learning Engine — Isolation Forest untuk deteksi anomali traffic.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import LabelEncoder, StandardScaler

from core.helpers import step, ok, warn

BASE_COLS = ["src_port", "dst_port", "packet_count", "byte_count", "duration"]

# Nilai flag TCP yang paling sering muncul pada traffic serangan di NSL-KDD.
# S0 = SYN tanpa balasan (DoS/scan), REJ = koneksi ditolak, RSTO/RSTR = reset paksa.
# Dengan encoding ordinal ini, IF bisa membedakan pola koneksi normal (SF)
# dari pola serangan berdasarkan urutan kategorisasi.
_FLAG_ORDER = ["SF", "S0", "REJ", "RSTO", "RSTR", "SH", "S1", "S2", "S3", "OTH", "-"]
_PROTO_ORDER = ["TCP", "UDP", "ICMP", "OTHER"]


def _encode_categorical(series: pd.Series, known_order: list) -> pd.Series:
    """
    Encode kolom kategorikal ke integer berdasarkan urutan yang sudah ditentukan.
    Nilai yang tidak dikenal di-map ke indeks terakhir (unknown).
    Ini lebih stabil daripada LabelEncoder karena urutan konsisten antar dataset.
    """
    mapping = {v: i for i, v in enumerate(known_order)}
    return series.str.upper().map(mapping).fillna(len(known_order)).astype(int)


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

    # ── Fitur kategorikal: flag dan protocol ──────────────────────────────────
    # flag (TCP connection state) sangat diskriminatif untuk deteksi serangan:
    #   - Traffic normal mayoritas SF (established & closed normal)
    #   - DoS/scan cenderung S0 (SYN tanpa SYN-ACK) atau REJ
    # protocol juga informatif: serangan ICMP flood, UDP sweep berbeda dari TCP normal.
    if "flag" in df.columns:
        features["flag_enc"] = _encode_categorical(
            df["flag"].astype(str).fillna("-"), _FLAG_ORDER
        )
    else:
        features["flag_enc"] = 0

    if "protocol" in df.columns:
        features["protocol_enc"] = _encode_categorical(
            df["protocol"].astype(str).fillna("TCP"), _PROTO_ORDER
        )
    else:
        features["protocol_enc"] = 0

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
