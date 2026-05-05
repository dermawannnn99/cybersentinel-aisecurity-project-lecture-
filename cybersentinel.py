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
from core.analysis      import build_result_dataframe, sample_per_level
from core.helpers       import section_header, step, ok, warn, SEP
from core.loader        import load_data
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

LEVEL_COLORS = {
    "CRITICAL": Fore.RED + Style.BRIGHT,
    "HIGH"    : Fore.RED,
    "MEDIUM"  : Fore.YELLOW,
    "LOW"     : Fore.CYAN,
    "SAFE"    : Fore.GREEN,
}


# ── Pipeline ──────────────────────────────────────────────────────────────────

def run_pipeline(df, max_display=50, show_safe=False):
    section_header("ANALISIS TRAFFIC")
    result = spin_for(
        "Menjalankan pipeline analisis ML + rules + scoring...",
        build_result_dataframe, df,
    )
    n_anomaly = int(result["if_anomaly"].sum())
    n_rule_hits = sum(1 for threats in result["threats"] if threats)
    ok(f"{n_anomaly:,} anomali terdeteksi dari {len(df):,} entri")
    ok(f"{n_rule_hits:,} entri terdeteksi rule engine")

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

        for lvl in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "SAFE"]:
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
