"""
core/loader.py
───────────────
Membaca dan memvalidasi file input (CSV atau TXT).
Mendukung tiga format:
    1. Format CyberSentinel (output dari dummy.py atau buatan sendiri)
    2. Format CICIDS 2017  (dataset publik UNB) — termasuk varian tanpa kolom IP
    3. Format NSL-KDD      (KDDTrain+.txt / KDDTest+.txt)
"""

import os
import sys
import pandas as pd
import numpy as np
from colorama import Fore, Style

from core.helpers import step, ok, err

NUMERIC_COLS = ["src_port", "dst_port", "packet_count", "byte_count", "duration"]

# ── CICIDS 2017 column mapping ────────────────────────────────────────────────
# Mendukung dua varian:
#   - Lengkap : ada Source IP, Destination IP, Source Port
#   - Stripped : tidak ada kolom IP & Source Port (misal Thursday-WebAttacks.csv)
CICIDS_COL_MAP = {
    # Varian lengkap
    " Source IP"                   : "src_ip",
    "Source IP"                    : "src_ip",
    " Destination IP"              : "dst_ip",
    "Destination IP"               : "dst_ip",
    " Source Port"                 : "src_port",
    "Source Port"                  : "src_port",
    # Kolom yang selalu ada di semua varian CICIDS
    " Destination Port"            : "dst_port",
    "Destination Port"             : "dst_port",
    " Protocol"                    : "protocol",
    "Protocol"                     : "protocol",
    " Total Fwd Packets"           : "packet_count",
    "Total Fwd Packets"            : "packet_count",
    " Total Length of Fwd Packets" : "byte_count",
    "Total Length of Fwd Packets"  : "byte_count",
    " Flow Duration"               : "duration",
    "Flow Duration"                : "duration",
    " Flow Packets/s"              : "flag",
    "Flow Packets/s"               : "flag",
    " Label"                       : "label",
    "Label"                        : "label",
}

# Kolom-kolom yang cukup untuk mendeteksi bahwa file ini adalah CICIDS 2017
# (tidak harus semua ada — cukup salah satu indikator kuat)
CICIDS_INDICATORS = [
    " Source IP", "Source IP",
    " Destination Port", "Destination Port",
    " Flow Duration", "Flow Duration",
    " Label", "Label",
    " Total Fwd Packets", "Total Fwd Packets",
]

CICIDS_PROTO_MAP = {6: "TCP", 17: "UDP", 1: "ICMP"}

# Label CICIDS 2017 → label internal CyberSentinel
CICIDS_LABEL_MAP = {
    "BENIGN"                        : "SAFE",
    "benign"                        : "SAFE",
    # DoS / DDoS
    "DoS Hulk"                      : "DoS / DDoS Attack",
    "DoS GoldenEye"                 : "DoS / DDoS Attack",
    "DoS slowloris"                 : "DoS / DDoS Attack",
    "DoS Slowhttptest"              : "DoS / DDoS Attack",
    "DDoS"                          : "DoS / DDoS Attack",
    "Heartbleed"                    : "DoS / DDoS Attack",
    # Port Scan
    "PortScan"                      : "Port Scan",
    # Brute Force
    "FTP-Patator"                   : "Brute Force",
    "SSH-Patator"                   : "Brute Force",
    "Web Attack \x96 Brute Force"      : "Brute Force",
    "Web Attack \u2013 Brute Force"    : "Brute Force",
    "Web Attack  Brute Force"          : "Brute Force",
    # Injection
    "Web Attack \x96 Sql Injection"    : "SQL Injection",
    "Web Attack \u2013 Sql Injection"  : "SQL Injection",
    "Web Attack  Sql Injection"        : "SQL Injection",
    # XSS
    "Web Attack \x96 XSS"              : "XSS (Cross-Site Scripting)",
    "Web Attack \u2013 XSS"            : "XSS (Cross-Site Scripting)",
    "Web Attack  XSS"                  : "XSS (Cross-Site Scripting)",
    # Infiltration / Botnet
    "Infiltration"                  : "Data Exfiltration",
    "Bot"                           : "Data Exfiltration",
}

# ── NSL-KDD column names (42 kolom) ──────────────────────────────────────────
KDD_COLUMNS = [
    "duration", "protocol_type", "service", "flag",
    "src_bytes", "dst_bytes", "land", "wrong_fragment", "urgent",
    "hot", "num_failed_logins", "logged_in", "num_compromised",
    "root_shell", "su_attempted", "num_root", "num_file_creations",
    "num_shells", "num_access_files", "num_outbound_cmds",
    "is_host_login", "is_guest_login", "count", "srv_count",
    "serror_rate", "srv_serror_rate", "rerror_rate", "srv_rerror_rate",
    "same_srv_rate", "diff_srv_rate", "srv_diff_host_rate",
    "dst_host_count", "dst_host_srv_count", "dst_host_same_srv_rate",
    "dst_host_diff_srv_rate", "dst_host_same_src_port_rate",
    "dst_host_srv_diff_host_rate", "dst_host_serror_rate",
    "dst_host_srv_serror_rate", "dst_host_rerror_rate",
    "dst_host_srv_rerror_rate", "label", "difficulty"
]

KDD_SERVICE_PORT = {
    "http": 80, "https": 443, "ftp": 21, "ftp_data": 20,
    "smtp": 25, "ssh": 22, "telnet": 23, "dns": 53,
    "pop3": 110, "imap4": 143, "ldap": 389, "kerberos": 88,
    "irc": 6667, "nntp": 119, "ntp_u": 123, "sunrpc": 111,
    "X11": 6000, "Z39_50": 210, "http_443": 443, "sql_net": 1521,
    "other": 0, "private": 0,
}

KDD_LABEL_MAP = {
    "normal"          : "SAFE",
    "neptune"         : "DoS / DDoS Attack",
    "smurf"           : "DoS / DDoS Attack",
    "pod"             : "DoS / DDoS Attack",
    "teardrop"        : "DoS / DDoS Attack",
    "back"            : "DoS / DDoS Attack",
    "land"            : "DoS / DDoS Attack",
    "apache2"         : "DoS / DDoS Attack",
    "mailbomb"        : "DoS / DDoS Attack",
    "processtable"    : "DoS / DDoS Attack",
    "udpstorm"        : "DoS / DDoS Attack",
    "worm"            : "DoS / DDoS Attack",
    "ipsweep"         : "Port Scan",
    "portsweep"       : "Port Scan",
    "nmap"            : "Port Scan",
    "satan"           : "Port Scan",
    "snmpgetattack"   : "Port Scan",
    "xsnoop"          : "Port Scan",
    "guess_passwd"    : "Brute Force",
    "ftp_write"       : "Brute Force",
    "multihop"        : "Brute Force",
    "imap"            : "Brute Force",
    "snmpguess"       : "Brute Force",
    "sendmail"        : "Brute Force",
    "named"           : "Brute Force",
    "rootkit"         : "Command Injection",
    "buffer_overflow" : "Command Injection",
    "loadmodule"      : "Command Injection",
    "perl"            : "Command Injection",
    "ps"              : "Command Injection",
    "xterm"           : "Command Injection",
    "sqlattack"       : "SQL Injection",
    "phf"             : "Path Traversal",
    "warezclient"     : "Data Exfiltration",
    "warezmaster"     : "Data Exfiltration",
    "spy"             : "Data Exfiltration",
    "httptunnel"      : "Data Exfiltration",
}


def _load_nslkdd(filepath):
    """Parse NSL-KDD .txt langsung tanpa konversi manual."""
    step("Format NSL-KDD terdeteksi — parsing otomatis...")

    df = pd.read_csv(filepath, header=None, names=KDD_COLUMNS)

    out = pd.DataFrame()
    out["src_ip"]       = [f"10.0.{i//256}.{i%256}" for i in range(len(df))]
    out["dst_ip"]       = "192.168.1.1"
    out["src_port"]     = df["src_bytes"].apply(lambda x: min(int(x) % 64512 + 1024, 65535))
    out["dst_port"]     = df["service"].map(KDD_SERVICE_PORT).fillna(0).astype(int)
    out["protocol"]     = df["protocol_type"].str.upper()
    out["packet_count"] = df["count"]
    out["byte_count"]   = df["src_bytes"] + df["dst_bytes"]
    out["duration"]     = df["duration"].apply(lambda x: max(float(x), 0.001))
    out["flag"]         = df["flag"]
    out["payload"]      = ""
    out["label"]        = df["label"].map(lambda l: KDD_LABEL_MAP.get(l, "Unknown Attack"))

    ok(f"NSL-KDD parsed — {len(out):,} baris, {out['label'].nunique()} kategori label")
    return out


def _is_cicids(df):
    """
    Deteksi apakah DataFrame adalah format CICIDS 2017.
    Cukup 2 indikator kuat yang cocok untuk dikonfirmasi.
    """
    matched = sum(1 for col in CICIDS_INDICATORS if col in df.columns)
    return matched >= 2


def _map_cicids_label(raw_label: str) -> str:
    """
    Konversi label CICIDS 2017 ke label internal CyberSentinel.
    Menangani encoding rusak (karakter en-dash yang terbaca sebagai \x96).
    """
    if not isinstance(raw_label, str):
        return "Unknown Attack"

    label = raw_label.strip()

    # Coba exact match dulu
    if label in CICIDS_LABEL_MAP:
        return CICIDS_LABEL_MAP[label]

    # Fallback: normalisasi karakter aneh lalu coba lagi
    label_norm = label.replace("\x96", "\u2013").replace("\xe2\x80\x93", "\u2013")
    if label_norm in CICIDS_LABEL_MAP:
        return CICIDS_LABEL_MAP[label_norm]

    # Fallback substring matching untuk label tak dikenal
    label_lower = label_norm.lower()
    if "brute" in label_lower:
        return "Brute Force"
    if "sql" in label_lower:
        return "SQL Injection"
    if "xss" in label_lower:
        return "XSS (Cross-Site Scripting)"
    if "dos" in label_lower or "ddos" in label_lower:
        return "DoS / DDoS Attack"
    if "portscan" in label_lower or "port scan" in label_lower:
        return "Port Scan"
    if "infiltration" in label_lower or "bot" in label_lower:
        return "Data Exfiltration"
    if "web attack" in label_lower:
        return "Unknown Web Attack"

    return "Unknown Attack"


def _load_cicids(df):
    """
    Proses DataFrame CICIDS 2017 — rename kolom, isi kolom yang hilang,
    dan konversi label ke format internal CyberSentinel.
    """
    step("Format CICIDS 2017 terdeteksi — mapping kolom...")

    # Rename kolom yang ada sesuai peta
    df = df.rename(columns={k: v for k, v in CICIDS_COL_MAP.items() if k in df.columns})

    # Konversi protocol angka → string (jika ada)
    if "protocol" in df.columns:
        df["protocol"] = df["protocol"].map(
            lambda x: CICIDS_PROTO_MAP.get(x, str(x)) if isinstance(x, int) else str(x)
        ).fillna("OTHER")

    # ── Isi kolom yang hilang di varian stripped (tanpa IP / Source Port) ──
    if "src_ip" not in df.columns:
        df["src_ip"] = "0.0.0.0"

    if "dst_ip" not in df.columns:
        df["dst_ip"] = "0.0.0.0"

    if "src_port" not in df.columns:
        # Tidak ada di CSV ini — isi 0 sebagai placeholder
        df["src_port"] = 0

    if "payload" not in df.columns:
        df["payload"] = ""

    # Konversi label CICIDS → label internal
    if "label" in df.columns:
        df["label"] = df["label"].map(_map_cicids_label)
    else:
        df["label"] = "Unknown Attack"

    n_labels = df["label"].nunique()
    ok(f"Mapping kolom CICIDS selesai — {n_labels} kategori label ditemukan")
    return df


def load_data(filepath):
    step(f"Membaca file: {Fore.WHITE}{filepath}{Style.RESET_ALL}")

    if not os.path.exists(filepath):
        err(f"File tidak ditemukan: {filepath}")

    try:
        # ── Deteksi NSL-KDD dari ekstensi dan isi baris pertama ──────────────
        ext = os.path.splitext(filepath)[1].lower()
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            first_line = f.readline().strip()

        is_nslkdd = (
            ext == ".txt" and
            len(first_line.split(",")) >= 41 and
            first_line.split(",")[1] in ("tcp", "udp", "icmp")
        )

        if is_nslkdd:
            df = _load_nslkdd(filepath)

        else:
            df = pd.read_csv(filepath, low_memory=False, encoding="utf-8", encoding_errors="replace")
            ok(f"Loaded {Fore.WHITE}{len(df):,}{Style.RESET_ALL} {Fore.GREEN}baris, "
               f"{Fore.WHITE}{len(df.columns)}{Style.RESET_ALL} {Fore.GREEN}kolom{Style.RESET_ALL}")

            # ── Auto-detect CICIDS 2017 (lengkap maupun varian stripped) ─────
            if _is_cicids(df):
                df = _load_cicids(df)

            else:
                # ── Format CyberSentinel / custom ─────────────────────────────
                missing = [c for c in NUMERIC_COLS if c not in df.columns]
                if missing:
                    err(
                        f"Kolom tidak ditemukan: {missing}\n"
                        f"  Kolom wajib: {NUMERIC_COLS}\n"
                        f"  Tip: Pastikan file adalah format CyberSentinel, CICIDS 2017, "
                        f"atau NSL-KDD (.txt)"
                    )

    except SystemExit:
        raise
    except Exception as e:
        err(f"Gagal membaca file: {e}")

    # ── Paksa tipe numerik untuk semua kolom angka ───────────────────────────
    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    # ── Kolom default jika masih belum ada ───────────────────────────────────
    defaults = {
        "src_ip"  : "0.0.0.0",
        "dst_ip"  : "0.0.0.0",
        "flag"    : "-",
        "payload" : "",
        "protocol": "TCP",
    }
    for col, val in defaults.items():
        if col not in df.columns:
            df[col] = val

    return df