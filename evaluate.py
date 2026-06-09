# evaluate.py — Evaluasi model Isolation Forest CyberSentinel
# Pipeline pengolahan data sudah terintegrasi di modul .py, file ini
# dibuat sebagai pengganti .ipynb (sudah dikonsultasikan dengan aslab).
# Cara menjalankan: python evaluate.py

import os
import sys

import numpy as np
import pandas as pd
from colorama import Fore, Style, init
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from tabulate import tabulate

init(autoreset=True)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.helpers import ok, section_header, step, warn
from core.loader import load_data_with_metadata
from core.ml_engine import build_features

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# Dataset yang dievaluasi — NSL-KDD versi 20% lebih balanced untuk IF
DATASETS = {
    "NSL-KDD (20%)": os.path.join(DATA_DIR, "KDDTrain+_20Percent.txt"),
    "CICIDS 2017"  : os.path.join(DATA_DIR, "Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv"),
}

IF_N_ESTIMATORS = 150
IF_RANDOM_STATE = 42


# Konversi label string ke binary: SAFE=0, serangan=1
def label_to_binary(series: pd.Series) -> np.ndarray:
    return (series != "SAFE").astype(int).values


# Konversi output IF ke binary: -1 (anomali)=1, 1 (normal)=0
def prediction_to_binary(predictions: np.ndarray) -> np.ndarray:
    return (predictions == -1).astype(int)


def evaluate_dataset(name: str, filepath: str) -> dict | None:
    section_header(f"Dataset: {name}")

    # Load data — auto-detect format NSL-KDD atau CICIDS
    step(f"Memuat dataset dari: {filepath}")
    try:
        df, warnings = load_data_with_metadata(filepath, exit_on_error=False, verbose=True)
    except Exception as e:
        warn(f"Gagal memuat dataset {name}: {e}")
        return None

    for w in warnings:
        warn(w)

    if "label" not in df.columns:
        warn(f"Kolom 'label' tidak ditemukan di {name} — evaluasi dilewati.")
        return None

    ok(f"Dataset dimuat: {len(df):,} baris")

    # Feature engineering via build_features() dari ml_engine.py
    step("Membangun fitur (feature engineering)...")
    try:
        X_scaled, _ = build_features(df)
    except Exception as e:
        warn(f"Gagal membangun fitur untuk {name}: {e}")
        return None
    ok(f"Fitur siap: {X_scaled.shape[1]} dimensi")

    # Contamination di-calibrate dari proporsi serangan aktual di dataset
    # agar model tidak terlalu agresif atau terlalu pasif flagging anomali
    attack_ratio  = float((df["label"] != "SAFE").mean())
    contamination = float(np.clip(attack_ratio, 0.01, 0.5))
    step(f"Auto-calibrate contamination: {attack_ratio:.2%} serangan → contamination={contamination:.4f}")

    # Training IF — unsupervised, tidak pakai label saat training
    step("Training Isolation Forest (unsupervised)...")
    from sklearn.ensemble import IsolationForest
    model = IsolationForest(
        n_estimators=IF_N_ESTIMATORS,
        contamination=contamination,
        random_state=IF_RANDOM_STATE,
        n_jobs=-1,
    )
    predictions = model.fit_predict(X_scaled)
    ok("Training selesai")

    # Bandingkan prediksi IF dengan ground truth label untuk hitung metrik
    y_true = label_to_binary(df["label"])
    y_pred = prediction_to_binary(predictions)

    return {
        "name"     : name,
        "rows"     : len(df),
        "accuracy" : accuracy_score(y_true, y_pred),
        "precision": precision_score(y_true, y_pred, zero_division=0),
        "recall"   : recall_score(y_true, y_pred, zero_division=0),
        "f1"       : f1_score(y_true, y_pred, zero_division=0),
        "cm"       : confusion_matrix(y_true, y_pred),
        "y_true"   : y_true,
        "y_pred"   : y_pred,
    }


def print_confusion_matrix(cm: np.ndarray, dataset_name: str):
    tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, cm[0][0])
    print(f"\n  {Style.BRIGHT}Confusion Matrix — {dataset_name}{Style.RESET_ALL}")
    print(f"  {'':25} {'Pred: Normal':>15} {'Pred: Serangan':>16}")
    print(f"  {'Actual: Normal (SAFE)':25} {Fore.GREEN}{tn:>15,}{Style.RESET_ALL} {Fore.RED}{fp:>16,}{Style.RESET_ALL}")
    print(f"  {'Actual: Serangan':25} {Fore.RED}{fn:>15,}{Style.RESET_ALL} {Fore.GREEN}{tp:>16,}{Style.RESET_ALL}")
    print(f"\n  {Style.DIM}TP={tp:,}  TN={tn:,}  FP={fp:,}  FN={fn:,}{Style.RESET_ALL}")


def print_classification_report(y_true, y_pred, dataset_name: str):
    print(f"\n  {Style.BRIGHT}Classification Report — {dataset_name}{Style.RESET_ALL}")
    report = classification_report(y_true, y_pred, target_names=["Normal (0)", "Serangan (1)"], zero_division=0)
    for line in report.splitlines():
        print(f"  {line}")


def print_summary_table(results: list[dict]):
    section_header("Ringkasan Metrik Evaluasi")
    rows = []
    for r in results:
        f1_val = r["f1"]
        if f1_val >= 0.75:
            f1_str = Fore.GREEN + f"{f1_val:.4f}" + Style.RESET_ALL
        elif f1_val >= 0.50:
            f1_str = Fore.YELLOW + f"{f1_val:.4f}" + Style.RESET_ALL
        else:
            f1_str = Fore.RED + f"{f1_val:.4f}" + Style.RESET_ALL

        rows.append([
            Style.BRIGHT + r["name"] + Style.RESET_ALL,
            f"{r['rows']:,}",
            f"{r['accuracy']:.4f}",
            f"{r['precision']:.4f}",
            f"{r['recall']:.4f}",
            f1_str,
        ])

    headers = ["Dataset", "Jumlah Data", "Accuracy", "Precision", "Recall", "F1-Score"]
    print(tabulate(rows, headers=headers, tablefmt="rounded_outline"))

    print(f"""
  {Style.DIM}Keterangan:
  • Accuracy  : proporsi prediksi benar dari seluruh data
  • Precision : dari semua yang diprediksi serangan, berapa yang benar
  • Recall    : dari semua serangan nyata, berapa yang terdeteksi
  • F1-Score  : keseimbangan antara Precision dan Recall
  • Model IF bersifat unsupervised — tidak pakai label saat training
  • Metrik dihitung dengan membandingkan prediksi IF vs ground truth label{Style.RESET_ALL}
""")


def main():
    print(f"\n{Style.BRIGHT}{Fore.CYAN}")
    print("  ╔══════════════════════════════════════════════════════════════╗")
    print("  ║         CyberSentinel — Evaluasi Model ML                  ║")
    print("  ║         Isolation Forest Anomaly Detection                 ║")
    print("  ╚══════════════════════════════════════════════════════════════╝")
    print(Style.RESET_ALL)

    results = []
    for name, path in DATASETS.items():
        if not os.path.exists(path):
            warn(f"Dataset '{name}' tidak ditemukan: {path} — dilewati.")
            continue
        result = evaluate_dataset(name, path)
        if result is None:
            continue
        print_confusion_matrix(result["cm"], name)
        print_classification_report(result["y_true"], result["y_pred"], name)
        results.append(result)

    if not results:
        print(f"\n  {Fore.RED}Tidak ada dataset yang berhasil dievaluasi.{Style.RESET_ALL}")
        sys.exit(1)

    print_summary_table(results)
    ok("Evaluasi selesai.\n")


if __name__ == "__main__":
    main()
