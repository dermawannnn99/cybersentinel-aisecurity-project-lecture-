```
                @@                  
             @@@@@@@@               
     @ @@@@@@@@@@   @@@@@@@         
     @     @@@@        @@@@         
       @@@@             @@@         
       @@@@@@@@     @@@@@@@               ░█▀▀░█░█░█▀▄░█▀▀░█▀▄░█▀▀░█▀▀░█▀█░▀█▀░▀█▀░█▀█░█▀▀░█░░
         @@@@@@@@@  @@@@@@@               ░█░░░░█░░█▀▄░█▀▀░█▀▄░▀▀█░█▀▀░█░█░░█░░░█░░█░█░█▀▀░█░░
       @@    @@@@@@  @@@@@@               ░▀▀▀░░▀░░▀▀░░▀▀▀░▀░▀░▀▀▀░▀▀▀░▀░▀░░▀░░▀▀▀░▀░▀░▀▀▀░▀▀▀
       @@@@@@   @@@@  @@@@@               ░█▀█░▀█▀░░░█▀▀░█▀▀░█▀▀░█░█░█▀▄░▀█▀░▀█▀░█░█
        @@@@@@@@   @  @@@@@               ░█▀█░░█░░░░▀▀█░█▀▀░█░░░█░█░█▀▄░░█░░░█░░░█░
            @@@@@@    @@@@                ░▀░▀░▀▀▀░░░▀▀▀░▀▀░░▀▀▀░▀▀▀░▀░▀░▀▀▀░░▀░░░▀░
         @@     @@  @@@@@                
           @@@@@@   @@@@@                     Intelligent Threat Detection & Response System
                   @@@                      
                @@@                         
           @@  @@@                          
```

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![ML](https://img.shields.io/badge/ML-Isolation%20Forest-green?style=flat-square&logo=scikit-learn)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)

</div>

---

## Tentang Project

**CyberSentinel AI** adalah tools deteksi ancaman jaringan berbasis kecerdasan buatan yang menggabungkan _machine learning_ (Isolation Forest) dengan _rule-based engine_ untuk menganalisis traffic jaringan secara otomatis.

Sistem ini mampu mendeteksi berbagai jenis serangan siber seperti SQL Injection, XSS, Port Scan, DoS/DDoS, Brute Force, dan Command Injection dari file log atau dataset jaringan tanpa memerlukan koneksi internet apapun saat analisis.

---

## Identitas Kelompok

| | |
|---|---|
| **Kelompok** | 7 |
| **Mata Kuliah** | Artificial Intelligence |
| **Kelas** | 4B Informatika |
| **Universitas** | Universitas Singaperbangsa Karawang |
| **Tahun** | 2026 |
| **Dosen Pengampu** | Yuyun Umaidah, M.Kom |

### Anggota

| Nama | NIM |
|---|---|
| Muhammad Rizky Dermawan | 2410631170038 |
| Nugraha Adani | 2410631170098 |
| Geral Tritama Wahyuady | 2410631170070 |

---

## Fitur

| Fitur | Keterangan |
|---|---|
| **Isolation Forest** | Deteksi anomali traffic menggunakan unsupervised machine learning |
| **Rule-Based Engine** | Signature matching untuk 7+ jenis serangan siber |
| **Risk Scoring** | Setiap entri diberi skor 0–100 dengan 5 level risiko |
| **Auto-detect Format** | Mendukung NSL-KDD, KDD Cup 99, CICIDS 2017 tanpa konversi manual |
| **Demo Mode** | Jalankan langsung tanpa dataset menggunakan data simulasi |
| **Export CSV** | Simpan hasil analisis ke file |
| **Spinner Animasi** | Visualisasi proses analisis real-time di terminal |

---

## Struktur Project

```
cyber-sentinel-ai/
│
├── cybersentinel.py          # Entry point utama
│
├── banner/
│   └── banner.py             # ASCII art & tampilan header
│
├── core/
│   ├── helpers.py            # Fungsi warna & output terminal
│   ├── loader.py             # Load & auto-detect format dataset
│   ├── ml_engine.py          # Isolation Forest engine
│   ├── rules.py              # Rule-based threat detection
│   └── scorer.py             # Risk score calculator
│
├── data/
│   └── dummy.py              # Generator data simulasi
│
├── output/
│   ├── display.py            # Tampilan tabel & ringkasan hasil
│   └── exporter.py           # Export hasil ke CSV
│
├── wordlists/
│   └── signatures.py         # Signature & keyword serangan
│
├── requirements.txt
└── README.md
```

---

## Instalasi

### 1. Clone repository

```bash
git clone https://github.com/username/cyber-sentinel-ai.git
cd cyber-sentinel-ai
```

### 2. Buat virtual environment (disarankan)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Cara Menjalankan

### Perintah Dasar

| Perintah | Keterangan |
|---|---|
| `python cybersentinel.py --demo` | Jalankan dengan data simulasi (300 baris) |
| `python cybersentinel.py --demo --rows 500` | Data simulasi dengan jumlah baris custom |
| `python cybersentinel.py --input data/file.txt` | Analisis file NSL-KDD atau KDD Cup |
| `python cybersentinel.py --input data/file.csv` | Analisis file CICIDS 2017 atau CSV lainnya |

### Semua Opsi

| Opsi | Singkatan | Keterangan | Default |
|---|---|---|---|
| `--demo` | `-d` | Jalankan mode demo dengan data simulasi | — |
| `--input FILE` | `-i` | Path ke file dataset (`.txt` / `.csv`) | — |
| `--rows N` | `-r` | Jumlah baris data simulasi | `300` |
| `--export FILE` | `-e` | Simpan hasil analisis ke file CSV | — |
| `--show-safe` | — | Tampilkan traffic aman (SAFE) di tabel hasil | — |
| `--max-display N` | `-m` | Batas maksimal baris yang ditampilkan | `50` |
| `--help` | `-h` | Tampilkan semua opsi | — |

### Contoh Penggunaan

```bash
# Demo cepat
python cybersentinel.py --demo

# Demo dengan 1000 baris dan simpan hasilnya
python cybersentinel.py --demo --rows 1000 --export hasil.csv

# Analisis dataset NSL-KDD
python cybersentinel.py --input data/KDDTrain+_20Percent.txt

# Analisis CICIDS 2017 + tampilkan semua traffic termasuk yang aman
python cybersentinel.py --input data/Thursday-WorkingHours.pcap_ISCX.csv --show-safe

# Analisis + export + batasi tampilan 20 baris
python cybersentinel.py --input data/KDDTrain+.txt --export output.csv --max-display 20
```

---

## Dataset yang Didukung

| Dataset | Format | Ukuran | Link Download |
|---|---|---|---|
| NSL-KDD (20%) | `.txt` | ~4 MB | [Kaggle](https://www.kaggle.com/datasets/hassan06/nslkdd) |
| NSL-KDD (Full) | `.txt` | ~18 MB | [Kaggle](https://www.kaggle.com/datasets/hassan06/nslkdd) |
| KDD Cup 99 (10%) | tanpa ekstensi | ~2 MB | [Kaggle](https://www.kaggle.com/datasets/galaxyh/kdd-cup-1999-data) |
| CICIDS 2017 | `.csv` | ~50–500 MB | [UNB](https://www.unb.ca/cic/datasets/ids-2017.html) |

> Semua format dideteksi otomatis — tidak perlu konversi manual.

---

## Cara Kerja

```
Input Data (CSV / TXT)
        │
        ▼
  [ Loader ] ── auto-detect format ──▶ DataFrame
        │
        ├──▶ [ Isolation Forest ]  ── deteksi anomali (ML)
        │
        ├──▶ [ Rule-Based Engine ] ── signature matching
        │
        └──▶ [ Risk Scorer ]       ── gabung hasil → skor 0–100
                    │
                    ▼
            [ Display & Export ]
```

### Level Risiko

| Label | Skor | Keterangan |
|---|---|---|
| 🔴 CRITICAL | 80 – 100 | Ancaman aktif, investigasi segera |
| 🟠 HIGH | 60 – 79 | Indikasi serangan kuat |
| 🟡 MEDIUM | 40 – 59 | Perlu dimonitor |
| 🟢 LOW | 20 – 39 | Anomali ringan |
| ⚪ SAFE | 0 – 19 | Traffic normal |

### Jenis Serangan yang Dideteksi

| Serangan | Metode Deteksi |
|---|---|
| SQL Injection | Rule-Based (payload signature) |
| XSS (Cross-Site Scripting) | Rule-Based (payload signature) |
| Path Traversal | Rule-Based (payload signature) |
| Command Injection | Rule-Based (payload signature) |
| DoS / DDoS Attack | Rule-Based (traffic pattern) + ML |
| Port Scan | Rule-Based (traffic pattern) + ML |
| Brute Force | Rule-Based (traffic pattern) + ML |
| Anomali Umum | Isolation Forest (ML) |

---

## Lisensi

Didistribusikan di bawah lisensi MIT. Lihat `LICENSE` untuk informasi lebih lanjut.
