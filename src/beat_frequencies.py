"""
K_Chain 44 個模式之間嘅 Beat Frequency 分析
=============================================
共震點：物質 = 44 個頻率之間嘅 beat frequency 經 CY3(36,98) 幾何投影激化
"""

import math
from dataclasses import dataclass
from itertools import combinations

# ============================================================
# 基本常數
# ============================================================
R_H = 4129.94        # Mpc, K_Chain 環周長
Nd = 44              # site 數
c = 299792.458       # km/s, 光速
Gyr = 3.15576e16     # s/Gyr
hbar = 6.582119569e-16  # eV·s

Mpc_to_km = 3.085677581e19
c_ms = c * 1e3
omega_scale = 88 * c_ms / (R_H * Mpc_to_km * 1e3)


@dataclass
class BeatFrequency:
    """兩個 K_Chain 模式之間嘅 beat frequency"""
    n: int                    # 模式 1
    m: int                    # 模式 2
    omega_nm: float           # rad/s, beat frequency = |omega_n - omega_m|
    energy_nm: float          # eV, 能量 = hbar * omega_nm
    ratio_to_omega1: float    # omega_nm / omega_1
    ratio_to_omega22: float   # omega_nm / omega_22
    type: str                 # 'difference' | 'sum'

    def __repr__(self) -> str:
        return (f"({self.n:2d},{self.m:2d}) | "
                f"w/w1={self.ratio_to_omega1:8.4f} | "
                f"E={self.energy_nm:8.2e} eV | {self.type}")


def compute_omega(n: int) -> float:
    """計算 mode n 嘅角頻率 (rad/s)"""
    return omega_scale * math.sin(math.pi * n / 88)


def compute_beat_frequencies() -> tuple[list[BeatFrequency], list[BeatFrequency]]:
    """
    計算所有 beat frequency（差頻同和頻）
    返回 (difference_beats, sum_beats)
    """
    omegas = [compute_omega(n) for n in range(1, Nd + 1)]
    w1 = omegas[0]   # omega_1
    w22 = omegas[21]  # omega_22（光速模式）

    diff_beats = []
    sum_beats = []

    for n in range(1, Nd + 1):
        for m in range(n + 1, Nd + 1):
            w_n = omegas[n - 1]
            w_m = omegas[m - 1]

            # 差頻
            w_diff = w_m - w_n  # m > n, 所以 w_m > w_n
            E_diff = hbar * w_diff

            diff_beats.append(BeatFrequency(
                n=n, m=m,
                omega_nm=w_diff,
                energy_nm=E_diff,
                ratio_to_omega1=w_diff / w1,
                ratio_to_omega22=w_diff / w22,
                type='difference'
            ))

            # 和頻
            w_sum = w_n + w_m
            E_sum = hbar * w_sum

            sum_beats.append(BeatFrequency(
                n=n, m=m,
                omega_nm=w_sum,
                energy_nm=E_sum,
                ratio_to_omega1=w_sum / w1,
                ratio_to_omega22=w_sum / w22,
                type='sum'
            ))

    # 按 ratio 排序
    diff_beats.sort(key=lambda b: b.ratio_to_omega1)
    sum_beats.sort(key=lambda b: b.ratio_to_omega1)

    return diff_beats, sum_beats


def find_closest_beat(beats: list[BeatFrequency], target: float,
                      min_n: int = 1, max_n: int = 44
                      ) -> tuple[BeatFrequency, float]:
    """搵最接近 target ratio 嘅 beat"""
    filtered = [b for b in beats if min_n <= b.n <= max_n and min_n <= b.m <= max_n]
    if not filtered:
        filtered = beats
    closest = min(filtered, key=lambda b: abs(b.ratio_to_omega1 - target))
    err = abs(closest.ratio_to_omega1 / target - 1) * 100
    return closest, err


def check_important_ratios(diff_beats: list[BeatFrequency]):
    """檢查重要數學常數係咪可以從 beat frequency 產生"""
    targets = {
        "phi (黄金比)": (1.618033989, 1, 44),
        "1/phi      ": (0.618033989, 1, 44),
        "phi^2      ": (2.618033989, 1, 44),
        "sqrt(2)    ": (1.414213562, 1, 44),
        "pi         ": (3.141592654, 1, 44),
        "e          ": (2.718281828, 1, 44),
        "2          ": (2.0, 1, 44),
        "3          ": (3.0, 1, 44),
        "4          ": (4.0, 1, 44),
        "1/2        ": (0.5, 1, 44),
        "1/3        ": (0.333333, 1, 44),
        "eps=phi^-1/4": (0.154508, 1, 44),
        "kappa=1/16 ": (0.0625, 1, 44),
        "beta=phi^-1/2": (0.309017, 1, 44),
    }

    print(f"{'常數':<14} | {'目標值':>10} | {'Beat (n,m)':>12} | {'中標值':>10} | {'誤差%':>7}")
    print("-" * 65)
    for name, (target, nmin, nmax) in targets.items():
        closest, err = find_closest_beat(diff_beats, target, nmin, nmax)
        marker = "V" if err < 0.1 else ("-" if err < 1.0 else "X")
        print(f"{name:<14} | {target:10.6f} | ({closest.n:2d},{closest.m:2d})     | "
              f"{closest.ratio_to_omega1:10.6f} | {err:6.2f}% {marker}")


def check_sm_mass_ratios(diff_beats: list[BeatFrequency]):
    """嘗試對應 SM 粒子質量比"""
    # SM 粒子質量比 (PDG 2024)
    sm_ratios = {
        "m_e/m_mu  ": 0.511 / 105.658,        # 0.004836
        "m_e/m_tau ": 0.511 / 1776.93,        # 0.000288
        "m_mu/m_tau": 105.658 / 1776.93,      # 0.05946
        "m_u/m_d   ": 2.16 / 4.67,            # 0.4625
        "m_s/m_d   ": 93.4 / 4.67,            # 20.0
        "m_c/m_b   ": 1.27 / 4.18,            # 0.3038
        "m_t/m_b   ": 172.76 / 4.18,          # 41.33
        "m_W/m_Z   ": 80.377 / 91.1876,       # 0.8814
        "m_H/m_W   ": 125.25 / 80.377,        # 1.558
        "m_e/m_H   ": 0.511e-3 / 125.25,      # 4.08e-6
        "m_e/m_W   ": 0.511e-3 / 80.377,      # 6.36e-6
        "m_nu/m_e  ": 0.001 / 0.511,          # 0.00196 (假設)
    }

    print(f"\n{'粒子質量比':<14} | {'目標值':>12} | {'Beat (n,m)':>12} | {'中標值':>12} | {'誤差%':>8}")
    print("-" * 65)
    for name, target in sm_ratios.items():
        closest, err = find_closest_beat(diff_beats, target)
        marker = "V" if err < 1.0 else ("-" if err < 10.0 else "X")
        print(f"{name:<14} | {target:12.6e} | ({closest.n:2d},{closest.m:2d})     | "
              f"{closest.ratio_to_omega1:12.6f} | {err:8.2f}% {marker}")


if __name__ == "__main__":
    diff_beats, sum_beats = compute_beat_frequencies()

    print("=" * 65)
    print("K_CHAIN BEAT FREQUENCY 分析")
    print("=" * 65)
    print(f"\n差頻 (difference beats): {len(diff_beats)} 個")
    print(f"和頻 (sum beats):       {len(sum_beats)} 個")
    print(f"總共:                   {len(diff_beats) + len(sum_beats)} 個")
    print(f"w1 能量: {hbar * compute_omega(1):.4e} eV")
    print(f"w22 能量: {hbar * compute_omega(22):.4e} eV")

    print("\n" + "=" * 65)
    print("重要數學常數對應")
    print("=" * 65)
    check_important_ratios(diff_beats)

    print("\n" + "=" * 65)
    print("SM 粒子質量比對應（初步探索）")
    print("=" * 65)
    check_sm_mass_ratios(diff_beats)

    print("\n" + "=" * 65)
    print("三階 Beat (beat of beats)")
    print("=" * 65)
    # 三階 beat: 取兩個 beat frequency 嘅差
    top_beats = diff_beats[:50]  # 取最小嘅 50 個 beat
    third_order = []
    for i in range(len(top_beats)):
        for j in range(i + 1, len(top_beats)):
            b1 = top_beats[i]
            b2 = top_beats[j]
            w_3rd = abs(b1.omega_nm - b2.omega_nm)
            r = w_3rd / compute_omega(1)
            if r < 50:
                third_order.append(r)
    third_order.sort()
    print(f"一階 beat 密度 (0-50 w1): {len(diff_beats)} 個")
    print(f"三階 beat 密度 (0-50 w1): {len(third_order)} 個")
    print(f"密度增加: {len(third_order)/len(diff_beats):.1f} 倍")
    print(f"最小三階 beat: {third_order[0]:.6f} w1")