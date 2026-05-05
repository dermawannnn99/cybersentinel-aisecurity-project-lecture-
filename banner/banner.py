from colorama import Fore, Style, init

init(autoreset=True)

FACE_ART = [
    "                @@               ",
    "             @@@@@@@@            ",
    "     @ @@@@@@@@@@   @@@@@@@      ",
    "     @     @@@@        @@@@      ",
    "       @@@@             @@@      ",
    "       @@@@@@@@     @@@@@@@      ",
    "         @@@@@@@@@  @@@@@@@      ",
    "       @@    @@@@@@  @@@@@@      ",
    "       @@@@@@   @@@@  @@@@@      ",
    "        @@@@@@@@   @  @@@@       ",
    "            @@@@@@    @@@@       ",
    "         @@     @@  @@@@         ",
    "           @@@@@@   @@@@         ",
    "                   @@@           ",
    "                @@@              ",
    "           @@  @@@               "
]

TEXT_ART = [
    "░█▀▀░█░█░█▀▄░█▀▀░█▀▄░█▀▀░█▀▀░█▀█░▀█▀░▀█▀░█▀█░█▀▀░█░░",
    "░█░░░░█░░█▀▄░█▀▀░█▀▄░▀▀█░█▀▀░█░█░░█░░░█░░█░█░█▀▀░█░░",
    "░▀▀▀░░▀░░▀▀░░▀▀▀░▀░▀░▀▀▀░▀▀▀░▀░▀░░▀░░▀▀▀░▀░▀░▀▀▀░▀▀▀",
    "░█▀█░▀█▀░░░█▀▀░█▀▀░█▀▀░█░█░█▀▄░▀█▀░▀█▀░█░█          ",
    "░█▀█░░█░░░░▀▀█░█▀▀░█░░░█░█░█▀▄░░█░░░█░░░█░          ",
    "░▀░▀░▀▀▀░░░▀▀▀░▀▀░░▀▀▀░▀▀▀░▀░▀░▀▀▀░░▀░░░▀░          "
]

def print_banner():
    max_l = len(FACE_ART)
    # Mencari lebar logo asli tanpa spasi kanan berlebih agar bisa mepet
    max_w = max(len(line.rstrip()) for line in FACE_ART)
    gap = "  "  # Jarak dipersempit jadi 2 spasi agar nempel

    # start_text diubah ke 4 agar teks turun lebih ke tengah logo
    start_text = 4 
    start_footer = start_text + len(TEXT_ART) + 1

    for i in range(max_l):
        # 1. WARNA LOGO (Grayscale)
        if i < 5: f_color = Style.BRIGHT + Fore.WHITE
        elif i < 11: f_color = Fore.WHITE
        else: f_color = Style.DIM + Fore.WHITE
        
        # ljust menggunakan max_w yang sudah di-rstrip agar gap benar-benar mepet
        line_output = f_color + FACE_ART[i].rstrip().ljust(max_w) + Style.RESET_ALL + gap

        # 2. BAGIAN KANAN (Teks ASCII atau Footer)
        if start_text <= i < (start_text + len(TEXT_ART)):
            idx = i - start_text
            t_color = Fore.MAGENTA if idx < 3 else Fore.CYAN
            line_output += t_color + TEXT_ART[idx]
        
        elif i == start_footer:
            line_output += Style.DIM + "─" * 65
        elif i == start_footer + 1:
            line_output += Style.BRIGHT + Fore.WHITE + "Intelligent Threat Detection & Response System"
        elif i == start_footer + 2:
            line_output += Style.DIM + "─" * 65
        elif i == start_footer + 3:
            line_output += f"{Style.BRIGHT}Created with ❤️  by {Fore.MAGENTA}@m4nray {Fore.CYAN}@geral {Fore.GREEN}@nugi {Style.RESET_ALL}{Style.DIM}│ Group 7 - AI | FASILKOM UNSIKA 2026"

        print(line_output)

if __name__ == "__main__":
    print_banner()