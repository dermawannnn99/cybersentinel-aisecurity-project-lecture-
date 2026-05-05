from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from core.loader import load_data_with_metadata

TEMP_ROOT = Path("C:/tmp")


def test_load_custom_csv_with_defaults() -> None:
    TEMP_ROOT.mkdir(parents=True, exist_ok=True)
    temp_dir = Path(tempfile.mkdtemp(dir=TEMP_ROOT))
    filepath = temp_dir / "traffic.csv"

    try:
        filepath.write_text(
            "src_port,dst_port,packet_count,byte_count,duration\n"
            "1234,80,10,512,1.5\n",
            encoding="utf-8",
        )

        df, warnings = load_data_with_metadata(str(filepath), exit_on_error=False, verbose=False)

        assert len(df) == 1
        assert df.loc[0, "src_ip"] == "0.0.0.0"
        assert any("Filled missing standard columns" in warning for warning in warnings)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_load_cicids_variant_maps_labels() -> None:
    filepath = Path("data/Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv")
    df, warnings = load_data_with_metadata(str(filepath), exit_on_error=False, verbose=False)

    assert not df.empty
    assert "risk_label" not in df.columns
    assert "label" in df.columns
    assert "Brute Force" in set(df["label"]) or "SQL Injection" in set(df["label"])
    assert isinstance(warnings, list)


def test_load_nslkdd_dataset() -> None:
    filepath = Path("data/KDDTrain+_20Percent.txt")
    df, warnings = load_data_with_metadata(str(filepath), exit_on_error=False, verbose=False)

    assert not df.empty
    assert "payload" in df.columns
    assert "label" in df.columns
    assert warnings == []
