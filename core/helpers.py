"""
core/helpers.py
────────────────
Fungsi warna dan output terminal yang dipakai di seluruh modul.
"""

import sys
from colorama import Fore, Style, init

init(autoreset=True)

SEP = Style.DIM + "─" * 72 + Style.RESET_ALL


def step(msg):
    print(f"  {Style.DIM}•{Style.RESET_ALL}  {msg}")

def ok(msg):
    print(f"  {Fore.GREEN}✔{Style.RESET_ALL}  {msg}")

def warn(msg):
    print(f"  {Fore.YELLOW}!{Style.RESET_ALL}  {Fore.YELLOW}{msg}{Style.RESET_ALL}")

def err(msg):
    print(f"  {Fore.RED}✘{Style.RESET_ALL}  {Fore.RED}{msg}{Style.RESET_ALL}")
    sys.exit(1)

def section_header(title):
    print(f"\n{SEP}")
    print(f"  {Style.BRIGHT}{title}{Style.RESET_ALL}")
    print(f"{SEP}\n")


# ── Color wrappers ─────────────────────────────────────────────────────────────

def c_critical(text): return Fore.RED + Style.BRIGHT + str(text) + Style.RESET_ALL
def c_high(text):     return Fore.RED + str(text) + Style.RESET_ALL
def c_medium(text):   return Fore.YELLOW + str(text) + Style.RESET_ALL
def c_low(text):      return Style.DIM + str(text) + Style.RESET_ALL
def c_safe(text):     return Fore.GREEN + str(text) + Style.RESET_ALL
def c_info(text):     return Style.BRIGHT + str(text) + Style.RESET_ALL
def c_dim(text):      return Style.DIM + str(text) + Style.RESET_ALL
def c_white(text):    return str(text)
