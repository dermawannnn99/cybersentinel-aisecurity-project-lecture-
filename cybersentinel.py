"""
cybersentinel.py
─────────────────
Entry point utama CyberSentinel AI.

Cara pakai:
    python cybersentinel.py --demo
    python cybersentinel.py --demo --rows 500
    python cybersentinel.py --input data/traffic.csv
    python cybersentinel.py --input data/traffic.csv --export hasil.csv
    python cybersentinel.py --help
"""

import argparse
import sys
import time
import threading

from colorama import Fore, Style, init

init(autoreset=True)

from banner.banner      import print_banner
from core.helpers       import section_header, step, ok, warn, SEP
from core.loader        import load_data
from core.rules         import run_rules
from core.ml_engine     import run_isolation_forest
from core.scorer        import score_all
from output.display     import print_results_table, print_summary
from output.exporter    import export_csv
from data.dummy         import generate_dummy_data


# ── Spinner ───────────────────────────────────────────────────────────────────

class Spinner:
    FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    def __init__(self, message: str):
        self.message = message
        self._stop   = threading.Event()
        self._thread = threading.Thread(target=self._spin, daemon=True)

    def _spin(self):
        i = 0
        while not self._stop.is_set():
            frame = self.FRAMES[i % len(self.FRAMES)]
            print(f"\r  {Style.DIM}{frame}{Style.RESET_ALL}  {self.message}   ",
                  end="", flush=True)
            time.sleep(0.08)
            i += 1

    def start(self):
        self._thread.start()
        return self

    def stop(self, success=True):
        self._stop.set()
        self._thread.join()
        icon = f"{Fore.GREEN}✔{Style.RESET_ALL}" if success else f"{Fore.RED}✘{Style.RESET_ALL}"
        print(f"\r  {icon}  {self.message}   ")


def spin_for(message: str, func, *args, **kwargs):
    sp = Spinner(message).start()
    try:
        result = func(*args, **kwargs)
        sp.stop(success=True)
        return result
    except Exception as e:
        sp.stop(success=False)
        raise e


# ── Instruksi & prompt ────────────────────────────────────────────────────────

def print_instructions(args):
    print(Style.DIM + "─" * 72 + Style.RESET_ALL)
    print(f"  {Style.BRIGHT}PETUNJUK PENGGUNAAN{Style.RESET_ALL}")
    print(Style.DIM + "─" * 72 + Style.RESET_ALL)
    print(f"  {'--demo':<22}{Style.DIM}Jalankan dengan data simulasi (300 baris){Style.RESET_ALL}")
    print(f"  {'--demo --rows N':<22}{Style.DIM}Tentukan jumlah baris data simulasi{Style.RESET_ALL}")
    print(f"  {'--input file.csv':<22}{Style.DIM}Analisis file CSV jaringan nyata{Style.RESET_ALL}")
    print(f"  {'--export hasil.csv':<22}{Style.DIM}Simpan hasil ke file CSV{Style.RESET_ALL}")
    print(f"  {'--show-safe':<22}{Style.DIM}Tampilkan traffic aman juga{Style.RESET_ALL}")
    print(f"  {'--help':<22}{Style.DIM}Tampilkan semua opsi{Style.RESET_ALL}")
    print(Style.DIM + "─" * 72 + Style.RESET_ALL)
    print()

    if args.demo:
        mode_info = f"Mode  : {Fore.WHITE}Demo{Style.RESET_ALL}  {Style.DIM}({args.rows:,} baris data simulasi){Style.RESET_ALL}"
    else:
        mode_info = f"Mode  : {Fore.WHITE}File{Style.RESET_ALL}  {Style.DIM}{args.input}{Style.RESET_ALL}"

    print(f"  {mode_info}")
    print()


def wait_for_run():
    """Tunggu user ketik 'run' atau 'go' sebelum memulai scan."""
    while True:
        try:
            cmd = input(f"  {Style.DIM}Ketik{Style.RESET_ALL} {Fore.WHITE}run{Style.RESET_ALL} "
                        f"{Style.DIM}atau{Style.RESET_ALL} {Fore.WHITE}go{Style.RESET_ALL} "
                        f"{Style.DIM}untuk memulai scan >{Style.RESET_ALL} ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            print(f"\n  {Style.DIM}Dibatalkan.{Style.RESET_ALL}\n")
            sys.exit(0)

        if cmd in ("run", "go"):
            print()
            break
        else:
            print(f"  {Style.DIM}Perintah tidak dikenal. Ketik 'run' atau 'go'.{Style.RESET_ALL}")


# ── Proportional sampling per level ──────────────────────────────────────────

LEVELS_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "SAFE"]

LEVEL_COLORS = {
    "CRITICAL": Fore.RED + Style.BRIGHT,
    "HIGH"    : Fore.RED,
    "MEDIUM"  : Fore.YELLOW,
    "LOW"     : Fore.CYAN,
    "SAFE"    : Fore.GREEN,
}


def sample_per_level(result, max_display, show_safe):
    """
    Ambil sample proporsional dari setiap level risk.
    Setiap level yang punya data mendapat jatah = max_display // jumlah_level_aktif.
    Sisa kuota diberikan ke CRITICAL.

    Return: dict { level_str -> DataFrame }
    """
    levels = LEVELS_ORDER if show_safe else LEVELS_ORDER[:-1]  # skip SAFE jika tidak diminta

    # Kumpulkan data per level yang benar-benar ada
    level_dfs = {}
    for lvl in levels:
        sub = result[result["risk_label"] == lvl]
        if not sub.empty:
            level_dfs[lvl] = sub.sort_values("risk_score", ascending=False)

    if not level_dfs:
        return {}

    n_active  = len(level_dfs)
    per_level = max(1, max_display // n_active)
    remainder = max_display - (per_level * n_active)

    sampled = {}
    first   = True
    for lvl in levels:
        if lvl not in level_dfs:
            continue
        quota          = per_level + (remainder if first else 0)
        sampled[lvl]   = level_dfs[lvl].head(quota)
        first          = False

    return sampled


# ── Pipeline ──────────────────────────────────────────────────────────────────

def run_pipeline(df, max_display=50, show_safe=False):
    # Step 1: Isolation Forest
    section_header("AI ENGINE — ISOLATION FOREST")
    predictions, if_scores = spin_for(
        "Melatih Isolation Forest & mendeteksi anomali...",
        run_isolation_forest, df,
    )
    n_anomaly = int((predictions == -1).sum())
    ok(f"{n_anomaly:,} anomali terdeteksi dari {len(df):,} entri")

    # Step 2: Rule-Based
    section_header("RULE-BASED THREAT DETECTION")
    all_threats = spin_for(
        "Memindai payload & pola traffic...",
        run_rules, df,
    )
    n_rule_hits = sum(1 for t in all_threats if t)
    ok(f"{n_rule_hits:,} entri terdeteksi rule engine")

    # Step 3: Risk Score
    section_header("RISK SCORING")
    risk_scores, risk_labels = spin_for(
        "Menggabungkan skor ML + rules \u2192 risk score 0\u2013100...",
        score_all, df, predictions, if_scores, all_threats,
    )

    result = df.copy()
    result["if_anomaly"]  = (predictions == -1)
    result["threats"]     = all_threats
    result["risk_score"]  = risk_scores
    result["risk_label"]  = risk_labels

    # Step 4: Display — proporsional per level
    section_header("HASIL ANALISIS ANCAMAN")

    sampled = sample_per_level(result, max_display, show_safe)

    if not sampled:
        ok("Tidak ada ancaman signifikan yang terdeteksi.")
    else:
        level_counts  = result["risk_label"].value_counts()
        total_shown   = sum(len(v) for v in sampled.values())
        n_active      = len(sampled)
        per_level_qty = max(1, max_display // n_active)

        print(f"  {Style.DIM}Sample ~{per_level_qty} per level  "
              f"| Ditampilkan: {total_shown:,}  "
              f"| Total data: {len(result):,}{Style.RESET_ALL}\n")

        for lvl in LEVELS_ORDER:
            if lvl not in sampled:
                continue
            part      = sampled[lvl]
            color     = LEVEL_COLORS.get(lvl, "")
            total_lvl = level_counts.get(lvl, 0)
            shown_lvl = len(part)

            # Header separator per level
            print(
                f"  {color}"
                f"{'─' * 8} {lvl}  "
                f"({shown_lvl} sample dari {total_lvl:,} total)"
                f" {'─' * 8}"
                f"{Style.RESET_ALL}"
            )
            print_results_table(part)
            print()

    print_summary(result)
    return result


def build_parser():
    parser = argparse.ArgumentParser(
        prog="cybersentinel",
        description="CyberSentinel AI \u2014 Intelligent Network Threat Detection",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--input",       "-i", help="Path ke file CSV")
    parser.add_argument("--demo",        "-d", action="store_true",
                        help="Jalankan dengan data simulasi")
    parser.add_argument("--rows",        "-r", type=int, default=300,
                        help="Jumlah baris data dummy (default: 300)")
    parser.add_argument("--show-safe",         action="store_true",
                        help="Tampilkan traffic SAFE juga")
    parser.add_argument("--export",      "-e", help="Simpan hasil ke file CSV")
    parser.add_argument("--max-display", "-m", type=int, default=50,
                        help="Total baris ditampilkan, dibagi rata per level (default: 50)")
    return parser


def main():
    parser = build_parser()
    args   = parser.parse_args()

    # Banner
    print_banner()

    if not args.input and not args.demo:
        print_instructions(argparse.Namespace(demo=False, input=None, rows=300))
        print(f"  {Fore.YELLOW}Gunakan --demo atau --input <file.csv> untuk memulai.{Style.RESET_ALL}\n")
        sys.exit(1)

    # Instruksi + prompt
    print_instructions(args)
    wait_for_run()

    # Load / generate data
    if args.demo:
        section_header("MEMUAT DATA SIMULASI")
        df = spin_for(
            f"Generating {args.rows:,} baris data traffic simulasi...",
            generate_dummy_data, n_rows=args.rows,
        )
        ok(f"Data siap — {len(df):,} entri")
    else:
        section_header("MEMUAT DATA")
        df = load_data(args.input)

    # Pipeline
    result = run_pipeline(df, max_display=args.max_display, show_safe=args.show_safe)

    # Export
    if args.export:
        section_header("EXPORT HASIL")
        export_csv(result, args.export)


if __name__ == "__main__":
    main()