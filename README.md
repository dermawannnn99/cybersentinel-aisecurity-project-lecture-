# CyberSentinel AI
**Intelligent Threat Detection & Response System**

> Created with ❤️ by @m4nray @geral @nugi — FASILKOM UNSIKA 2026
> Group 7 — Artificial Intelligence

---

## Struktur Folder

```
cybersentinel/
├── cybersentinel.py        ← Entry point utama (jalankan ini)
├── requirements.txt
├── README.md
│
├── banner/
│   └── banner.py           ← ASCII art header
│
├── core/
│   ├── helpers.py          ← Fungsi warna & output terminal
│   ├── loader.py           ← Load & validasi CSV (CICIDS / custom)
│   ├── rules.py            ← Rule-Based threat detection engine
│   ├── ml_engine.py        ← Isolation Forest anomaly detection
│   └── scorer.py           ← Risk score calculator (0–100)
│
├── output/
│   ├── display.py          ← Print tabel & summary ke terminal
│   └── exporter.py         ← Export hasil ke CSV
│
├── data/
│   └── dummy.py            ← Generator data simulasi (--demo)
│
└── wordlists/
    └── signatures.py       ← Semua keyword/signature & threshold rules
```

---

## Install & Jalankan

```bash
pip install -r requirements.txt

# Mode demo
python cybersentinel.py --demo
python cybersentinel.py --demo --rows 500

# Dataset real (CICIDS 2017)
python cybersentinel.py --input data/Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv

# Tampilkan semua traffic termasuk SAFE
python cybersentinel.py --demo --show-safe

# Export hasil ke CSV
python cybersentinel.py --demo --export hasil.csv
```

---

## Dataset Real

Download: https://www.unb.ca/cic/datasets/ids-2017.html
File: `Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv`
Taruh di folder `data/` lalu jalankan dengan `--input`.

---

## Teknik AI yang Diimplementasi

| Teknik | Modul | Keterangan |
|--------|-------|------------|
| Isolation Forest | `core/ml_engine.py` | Anomaly detection |
| StandardScaler | `core/ml_engine.py` | Normalisasi fitur |
| Feature Engineering | `core/ml_engine.py` | byte_per_packet, log transform |
| Rule-Based Engine | `core/rules.py` | Knowledge-Based System |
| Signature Matching | `wordlists/signatures.py` | Payload keyword rules |
| Risk Scoring | `core/scorer.py` | Gabungkan ML + Rules → 0–100 |