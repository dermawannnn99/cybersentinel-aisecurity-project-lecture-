"""
core/scorer.py
───────────────
Risk Score Calculator.
Menggabungkan hasil Isolation Forest (ML) + Rule-Based Engine
menjadi satu angka risk score 0–100 per baris traffic.

Formula:
    score = kontribusi_IF (0–50) + kontribusi_rules (0–50) + bonus_keduanya (10)
    score = min(100, score)

Label:
    80–100 → CRITICAL
    60–79  → HIGH
    40–59  → MEDIUM
    20–39  → LOW
    0–19   → SAFE
"""

from wordlists.signatures import THREAT_WEIGHTS


def calculate_risk_score(if_score: float, threats: list, is_anomaly: bool) -> int:
    """
    Hitung risk score 0–100 untuk satu baris traffic.

    Parameter:
        if_score   (float)    : Anomaly score dari Isolation Forest
                                (negatif = lebih anomali, range ~-0.5 s/d 0.5)
        threats    (list[str]): Ancaman dari rule-based engine
        is_anomaly (bool)     : True jika IF menandai sebagai anomali

    Return:
        int: Risk score 0–100
    """
    score = 0.0

    # Kontribusi ML — normalisasi ke 0–50
    if_normalized = max(0.0, min(1.0, (-if_score + 0.5)))
    score += if_normalized * 50

    # Kontribusi rule-based — tambah bobot per threat
    for threat in threats:
        score += THREAT_WEIGHTS.get(threat, 20)

    # Bonus jika ML + rules sama-sama setuju ada ancaman
    if is_anomaly and threats:
        score += 10

    return min(100, int(score))


def get_risk_label(score: int) -> tuple[str, str]:
    """
    Konversi angka score ke label kategori dan kode warna ANSI.

    Parameter:
        score (int): Risk score 0–100

    Return:
        tuple: (label_string, ansi_color_code)
    """
    from colorama import Fore, Style
    if score >= 80:
        return "CRITICAL", Fore.RED + Style.BRIGHT
    elif score >= 60:
        return "HIGH",     Fore.RED
    elif score >= 40:
        return "MEDIUM",   Fore.YELLOW
    elif score >= 20:
        return "LOW",      Fore.CYAN
    else:
        return "SAFE",     Fore.GREEN


def score_all(df, predictions, if_scores, all_threats) -> tuple:
    """
    Hitung risk score untuk seluruh DataFrame sekaligus.

    Parameter:
        df          (pd.DataFrame)    : Data traffic
        predictions (np.ndarray)      : Output IF (-1 atau 1)
        if_scores   (np.ndarray)      : Anomaly score dari IF
        all_threats (list[list[str]]) : Threats per baris dari rules

    Return:
        tuple:
            risk_scores (list[int])  : Score per baris
            risk_labels (list[str])  : Label per baris
    """
    is_anomalies = (predictions == -1)
    risk_scores  = []
    risk_labels  = []

    for i in range(len(df)):
        score        = calculate_risk_score(if_scores[i], all_threats[i], is_anomalies[i])
        label, _     = get_risk_label(score)
        risk_scores.append(score)
        risk_labels.append(label)

    return risk_scores, risk_labels