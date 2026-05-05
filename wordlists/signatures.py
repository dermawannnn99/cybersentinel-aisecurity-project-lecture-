"""
wordlists/signatures.py
────────────────────────
Berisi semua keyword dan signature yang digunakan oleh rule-based engine.
Dipisah dari logic agar mudah di-update tanpa menyentuh kode utama.

Cara tambah rule baru:
    Cukup tambahkan key baru di PAYLOAD_RULES beserta list keyword-nya.
"""

# ── Signature payload per jenis serangan ──────────────────────────────────────
# Setiap key = nama ancaman, value = list keyword yang dicari di payload (lowercase)

PAYLOAD_RULES = {
    "SQL Injection": [
        "' or '", "' or 1=1", "union select", "drop table",
        "insert into", "sleep(", "benchmark(", "xp_cmdshell",
        "1=1", "' and ", "or 1=1--", "char(", "exec(",
        "waitfor delay", "cast(", "convert(", "information_schema",
        "select * from", "having 1=1", "group by",
    ],
    "XSS (Cross-Site Scripting)": [
        "<script>", "</script>", "onerror=", "onload=",
        "javascript:", "alert(", "document.cookie",
        "<img src=x", "<svg ", "eval(", "expression(",
        "vbscript:", "data:text/html", "onmouseover=",
        "onfocus=", "<iframe", "src=javascript",
    ],
    "Path Traversal": [
        "../", "..\\", "....//", "%2e%2e", "/etc/passwd",
        "/etc/shadow", "win.ini", "system32", "boot.ini",
        "/proc/self", "../../../../", "%252e%252e",
        "/var/www", "/root/.ssh", "/.env",
    ],
    "Command Injection": [
        "; ls", "; cat", "| whoami", "| id", "`id`",
        "$(id)", "&& cat", "|| ls", "; rm -rf",
        "| nc ", "bash -i", "/bin/sh", "/bin/bash",
        "wget http", "curl http", "python -c", "perl -e",
    ],
    "LDAP Injection": [
        ")(cn=", "*))(", "objectclass=", "|(&", "!(uid=",
        ")(objectclass=*)", "*()|", ")(|(cn=",
    ],
    "XXE Injection": [
        "<!entity", "<!doctype", "system \"http",
        "system 'file", "<!element", "dtd\"",
    ],
}

# ── Threshold untuk deteksi berbasis traffic pattern ──────────────────────────

PORT_SCAN = {
    "packet_count_min"   : 200,   # minimal paket agar dicurigai scan
    "byte_per_packet_max": 5.0,   # byte/paket rendah = kemungkinan SYN scan
}

DOS_DDOS = {
    "packet_count_min": 3000,     # traffic banjir
}

BRUTE_FORCE = {
    # Port umum yang jadi target brute force
    "ports"           : [22, 21, 23, 25, 110, 143, 3389, 5900, 8080],
    "packet_count_min": 200,
}

# ── Bobot risiko per jenis ancaman (dipakai scorer.py) ────────────────────────
# Semakin tinggi angka = kontribusi lebih besar ke risk score

THREAT_WEIGHTS = {
    "SQL Injection"              : 40,
    "XSS (Cross-Site Scripting)" : 35,
    "Command Injection"          : 45,
    "Path Traversal"             : 30,
    "LDAP Injection"             : 30,
    "XXE Injection"              : 35,
    "Port Scan"                  : 25,
    "DoS / DDoS Attack"          : 50,
    "Brute Force"                : 35,
}