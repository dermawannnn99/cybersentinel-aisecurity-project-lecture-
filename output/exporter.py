"""
output/exporter.py
───────────────────
Menyimpan hasil analisis ke file CSV.
"""

import pandas as pd
from core.helpers import ok


def export_csv(df, output_path: str):
    """
    Simpan DataFrame hasil analisis ke file CSV.
    Kolom 'threats' (list) dikonversi ke string dipisah ' | '.

    Parameter:
        df          (pd.DataFrame): Data hasil analisis
        output_path (str)         : Path file output
    """
    export_df = df.copy()
    export_df["threats"] = export_df["threats"].apply(
        lambda t: " | ".join(t) if t else "None"
    )
    export_df.to_csv(output_path, index=False)
    ok(f"Hasil disimpan ke: {output_path}")


def dataframe_to_csv_bytes(df) -> bytes:
    export_df = df.copy()
    export_df["threats"] = export_df["threats"].apply(
        lambda t: " | ".join(t) if t else "None"
    )
    return export_df.to_csv(index=False).encode("utf-8")
