"""
output/display.py
──────────────────
Semua fungsi untuk menampilkan hasil analisis ke terminal.
"""

from tabulate import tabulate
from colorama import Fore, Style

from core.helpers  import section_header, c_critical, c_high, c_medium, c_low, c_safe, c_info, c_dim, c_white
from core.scorer   import get_risk_label
from wordlists.signatures import THREAT_WEIGHTS


def print_results_table(display_df):
    rows = []
    for _, row in display_df.iterrows():
        score        = row["risk_score"]
        label, color = get_risk_label(score)

        threats_str = ", ".join(row["threats"]) if row["threats"] else "-"
        if len(threats_str) > 42:
            threats_str = threats_str[:39] + "..."

        anomaly_flag = (
            Fore.RED + "✗ ANOMALI" if row["if_anomaly"]
            else Style.DIM + "✓ Normal"
        ) + Style.RESET_ALL

        rows.append([
            color + f"{score:>3}/100" + Style.RESET_ALL,
            color + f"{label:<8}"    + Style.RESET_ALL,
            str(row.get("src_ip",   "-"))[:16],
            Style.DIM + str(row.get("dst_ip",   "-"))[:16] + Style.RESET_ALL,
            Style.DIM + str(row.get("protocol", "-"))[:5]  + Style.RESET_ALL,
            Style.DIM + str(int(row.get("dst_port", 0)))   + Style.RESET_ALL,
            anomaly_flag,
            Style.DIM + threats_str + Style.RESET_ALL,
        ])

    headers = [
        c_info("SCORE"),  c_info("LEVEL"),
        c_info("SRC IP"), c_info("DST IP"),
        c_info("PROTO"),  c_info("PORT"),
        c_info("ML"),     c_info("THREATS DETECTED"),
    ]
    print(tabulate(rows, headers=headers, tablefmt="simple"))


def print_summary(df):
    section_header("RINGKASAN EKSEKUTIF")

    total      = len(df)
    n_critical = len(df[df["risk_label"] == "CRITICAL"])
    n_high     = len(df[df["risk_label"] == "HIGH"])
    n_medium   = len(df[df["risk_label"] == "MEDIUM"])
    n_low      = len(df[df["risk_label"] == "LOW"])
    n_safe     = len(df[df["risk_label"] == "SAFE"])
    n_anomaly  = int(df["if_anomaly"].sum())

    stats = [
        [c_dim("Total Traffic Dianalisis"),        c_white(f"{total:,}")],
        [c_critical("▸ CRITICAL"),                 c_critical(f"{n_critical:,}")],
        [c_high("▸ HIGH"),                         c_high(f"{n_high:,}")],
        [c_medium("▸ MEDIUM"),                     c_medium(f"{n_medium:,}")],
        [c_low("▸ LOW"),                           c_low(f"{n_low:,}")],
        [c_safe("▸ SAFE"),                         c_safe(f"{n_safe:,}")],
        [c_dim("ML Anomali (Isolation Forest)"),   f"{n_anomaly:,}"],
    ]
    print(tabulate(stats, tablefmt="plain"))

    # Top threats
    threat_counter = {}
    for threats in df["threats"]:
        for t in threats:
            threat_counter[t] = threat_counter.get(t, 0) + 1

    if threat_counter:
        print(f"\n  {Style.BRIGHT}Top Ancaman Terdeteksi:{Style.RESET_ALL}")
        for threat, count in sorted(threat_counter.items(), key=lambda x: x[1], reverse=True):
            bar      = "█" * min(count, 30)
            _, color = get_risk_label(THREAT_WEIGHTS.get(threat, 20) + 20)
            print(f"    {color}{threat:<40}{Style.RESET_ALL}"
                  f"{count:>4}x  {Style.DIM}{bar}{Style.RESET_ALL}")

    # Overall threat level
    print()
    if n_critical > 0:
        status = c_critical("⚠  THREAT LEVEL: CRITICAL — Segera investigasi!")
    elif n_high > 0:
        status = c_high("⚠  THREAT LEVEL: HIGH — Perlu perhatian segera")
    elif n_medium > 0:
        status = c_medium("⚠  THREAT LEVEL: MEDIUM — Monitor dengan seksama")
    else:
        status = c_safe("✓  THREAT LEVEL: LOW — Jaringan relatif aman")

    print(f"  {status}\n")

    # Footer
    print(Style.DIM + "─" * 72 + Style.RESET_ALL)
    print(f"\n  {Fore.GREEN}✔  Scan selesai.{Style.RESET_ALL}  "
          f"{Style.DIM}{total:,} entri dianalisis, "
          f"{n_critical + n_high} ancaman kritis ditemukan.{Style.RESET_ALL}\n")
