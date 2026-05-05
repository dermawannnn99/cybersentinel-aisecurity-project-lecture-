"""
data/dummy.py
──────────────
Generator data traffic jaringan simulasi untuk mode --demo.
Menghasilkan mix traffic normal dan berbagai jenis serangan.

Cara pakai:
    from data.dummy import generate_dummy_data
    df = generate_dummy_data(n_rows=300)
"""

import numpy as np
import pandas as pd


# Pool IP yang digunakan dalam simulasi
NORMAL_IPS  = [f"192.168.1.{i}" for i in range(1, 30)]
SUSPECT_IPS = [
    "10.0.0.99", "172.16.0.5", "192.168.1.200",
    "45.33.32.156", "198.51.100.1"
]

# Payload contoh per jenis serangan
PAYLOADS = {
    "sql_injection": [
        "GET /login?user=' OR '1'='1 HTTP/1.1",
        "GET /search?q=1 UNION SELECT * FROM users-- HTTP/1.1",
        "POST /api?id=1; DROP TABLE users;-- HTTP/1.1",
        "GET /item?id=1' AND SLEEP(5)-- HTTP/1.1",
        "GET /page?cat=1 HAVING 1=1-- HTTP/1.1",
    ],
    "xss": [
        "GET /search?q=<script>alert('XSS')</script> HTTP/1.1",
        "POST /comment body=<img src=x onerror=alert(1)>",
        "GET /page?name=<svg onload=alert(document.cookie)>",
        "GET /input?val=javascript:alert('hacked')",
        "GET /view?x=<iframe src=javascript:alert(1)>",
    ],
    "path_traversal": [
        "GET /files?path=../../etc/passwd HTTP/1.1",
        "GET /download?file=../../../windows/system32/config/sam",
        "GET /view?doc=....//....//etc/shadow",
        "GET /img?src=../../../../.env",
    ],
    "command_injection": [
        "GET /ping?host=127.0.0.1;cat /etc/passwd HTTP/1.1",
        "POST /exec body=cmd=ls | whoami",
        "GET /tool?q=test`id`",
        "GET /run?cmd=$(id) HTTP/1.1",
    ],
    "normal": [
        "GET / HTTP/1.1",
        "GET /index.html HTTP/1.1",
        "POST /api/login HTTP/1.1",
        "GET /favicon.ico HTTP/1.1",
        "GET /assets/style.css HTTP/1.1",
        "DNS_QUERY",
    ],
}


def _make_attack_row(src_ip, dst_ip, attack_type):
    """Buat satu baris data traffic serangan."""
    base = {"src_ip": src_ip, "dst_ip": dst_ip, "protocol": "TCP", "flag": "ACK"}

    if attack_type == "port_scan":
        return {**base,
            "src_port"    : np.random.randint(40000, 65535),
            "dst_port"    : np.random.randint(1, 1024),
            "packet_count": np.random.randint(500, 2000),
            "byte_count"  : np.random.randint(100, 500),
            "duration"    : np.random.uniform(0.001, 0.1),
            "flag"        : "SYN",
            "payload"     : "SYN_SCAN",
        }
    elif attack_type == "dos":
        return {**base,
            "src_port"    : np.random.randint(1024, 65535),
            "dst_port"    : 80,
            "packet_count": np.random.randint(5000, 20000),
            "byte_count"  : np.random.randint(500000, 2000000),
            "duration"    : np.random.uniform(0.1, 2.0),
            "flag"        : "SYN",
            "payload"     : "GET / HTTP/1.1",
        }
    elif attack_type == "brute_force":
        return {**base,
            "src_port"    : np.random.randint(1024, 65535),
            "dst_port"    : np.random.choice([22, 3389, 21]),
            "packet_count": np.random.randint(300, 1500),
            "byte_count"  : np.random.randint(10000, 80000),
            "duration"    : np.random.uniform(10, 120),
            "payload"     : "AUTH_ATTEMPT",
        }
    else:
        # sql_injection, xss, path_traversal, command_injection
        return {**base,
            "src_port"    : np.random.randint(1024, 65535),
            "dst_port"    : 80,
            "packet_count": np.random.randint(1, 20),
            "byte_count"  : np.random.randint(100, 2000),
            "duration"    : np.random.uniform(0.05, 2.0),
            "payload"     : np.random.choice(PAYLOADS.get(attack_type, PAYLOADS["normal"])),
        }


def _make_normal_row(src_ip, dst_ip):
    """Buat satu baris data traffic normal."""
    return {
        "src_ip"      : src_ip,
        "dst_ip"      : dst_ip,
        "src_port"    : np.random.randint(1024, 65535),
        "dst_port"    : np.random.choice([80, 443, 53, 8080], p=[0.4, 0.4, 0.1, 0.1]),
        "protocol"    : np.random.choice(["TCP", "UDP"], p=[0.8, 0.2]),
        "packet_count": np.random.randint(1, 150),
        "byte_count"  : np.random.randint(64, 50000),
        "duration"    : np.random.uniform(0.01, 30.0),
        "flag"        : np.random.choice(["SYN", "ACK", "FIN", "PSH"]),
        "payload"     : np.random.choice(PAYLOADS["normal"]),
    }


def generate_dummy_data(n_rows=300, attack_ratio=0.18):
    """
    Generate dataset traffic jaringan simulasi.

    Parameter:
        n_rows       (int)  : Jumlah total baris (default 300)
        attack_ratio (float): Proporsi traffic serangan (default 18%)

    Return:
        pd.DataFrame: Dataset siap pakai untuk dianalisis
    """
    np.random.seed(42)

    attack_types = [
        "sql_injection", "xss", "path_traversal",
        "command_injection", "port_scan", "dos", "brute_force"
    ]

    rows = []
    for _ in range(n_rows):
        src_ip = np.random.choice(SUSPECT_IPS if np.random.random() < attack_ratio else NORMAL_IPS)
        dst_ip = np.random.choice(NORMAL_IPS)

        if src_ip in SUSPECT_IPS and np.random.random() < 0.75:
            attack = np.random.choice(attack_types)
            rows.append(_make_attack_row(src_ip, dst_ip, attack))
        else:
            rows.append(_make_normal_row(src_ip, dst_ip))

    return pd.DataFrame(rows)