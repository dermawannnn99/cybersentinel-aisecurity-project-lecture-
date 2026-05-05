"""
core/rules.py
──────────────
Rule-Based Threat Detection Engine.
"""

from wordlists.signatures import (
    PAYLOAD_RULES,
    PORT_SCAN,
    DOS_DDOS,
    BRUTE_FORCE,
)


def check_payload(payload: str) -> list:
    threats = []
    payload_lower = payload.lower()
    for threat_name, keywords in PAYLOAD_RULES.items():
        for kw in keywords:
            if kw.lower() in payload_lower:
                threats.append(threat_name)
                break
    return threats


def check_traffic_pattern(row) -> list:
    threats  = []
    pkt      = float(row.get("packet_count", 0))
    byt      = float(row.get("byte_count",   0))
    flag     = str(row.get("flag", "")).upper()
    dst_port = int(row.get("dst_port", 0))

    if pkt > PORT_SCAN["packet_count_min"]:
        bpp = byt / pkt if pkt > 0 else 0
        if bpp < PORT_SCAN["byte_per_packet_max"] or "SYN" in flag:
            threats.append("Port Scan")

    if pkt > DOS_DDOS["packet_count_min"]:
        threats.append("DoS / DDoS Attack")

    if dst_port in BRUTE_FORCE["ports"] and pkt > BRUTE_FORCE["packet_count_min"]:
        threats.append("Brute Force")

    return threats


def analyze_row(row) -> list:
    payload  = str(row.get("payload", ""))
    threats  = check_payload(payload)
    threats += check_traffic_pattern(row)
    return list(set(threats))


def run_rules(df) -> list:
    return [analyze_row(row) for _, row in df.iterrows()]
