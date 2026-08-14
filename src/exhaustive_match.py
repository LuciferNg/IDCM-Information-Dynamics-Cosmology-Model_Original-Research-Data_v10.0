"""
IDCM v10.0 — 窮舉法 + 疊加法
==============================
窮舉所有 K_Chain beat 組合，配對所有 SM 粒子質量比
"""

import math
import itertools
from dataclasses import dataclass, field

# ============================================================
# 基本常數
# ============================================================
R_H = 4129.94        # Mpc
Nd = 44
c = 299792.458       # km/s
Gyr = 3.15576e16     # s/Gyr
hbar = 6.582119569e-16  # eV·s
Mpc_to_km = 3.085677581e19
c_ms = c * 1e3
omega_scale = 88 * c_ms / (R_H * Mpc_to_km * 1e3)

# ============================================================
# SM 粒子質量 (PDG 2024, MeV)
# ============================================================
SM_PARTICLES = {
    # 第一代夸克
    "u": 2.16,      # up quark
    "d": 4.67,      # down quark
    # 第二代夸克
    "s": 93.4,      # strange quark
    "c": 1270,      # charm quark
    # 第三代夸克
    "b": 4180,      # bottom quark
    "t": 172760,    # top quark
    # 帶電輕子
    "e": 0.51099895,  # electron
    "mu": 105.6583745,  # muon
    "tau": 1776.86,  # tau
    # 規範玻色子
    "W": 80377,     # W boson
    "Z": 91187.6,   # Z boson
    # 希格斯
    "H": 125250,    # Higgs boson
    # 光子 (質量為 0, 唔做 ratio)
    # "gamma": 0.0,
    # "gluon": 0.0,
}

# ============================================================
# K_Chain 頻率
# ============================================================
def omega_n(n: int) -> float:
    """Mode n 嘅角頻率 (rad/s)"""
    return omega_scale * math.sin(math.pi * n / 88)

def energy_n(n: int) -> float:
    """Mode n 嘅能量 (eV)"""
    return hbar * omega_n(n)

# 預計算所有 mode 能量
E_n = [energy_n(n) for n in range(1, Nd + 1)]


# ============================================================
# 一階 Beat Frequency
# ============================================================
@dataclass
class Beat:
    """一個 beat frequency 記錄"""
    order: int          # 階數: 1=一階差頻, 2=二階, 3=三階
    components: tuple   # 組成 (n,m) 或 (n,m,p,q)
    omega: float        # rad/s
    energy: float       # eV
    ratio_to_w1: float  # ω / ω₁

    def __repr__(self) -> str:
        return f"[{self.order}阶] {self.components} | E={self.energy:.4e} eV | r={self.ratio_to_w1:.6f}"


def generate_first_order_beats() -> list[Beat]:
    """生成全部一階 beat frequency（差頻）"""
    beats = []
    for n in range(1, Nd + 1):
        for m in range(n + 1, Nd + 1):
            w = abs(E_n[n-1] - E_n[m-1])
            beats.append(Beat(
                order=1, components=(n, m),
                omega=w / hbar, energy=w,
                ratio_to_w1=w / E_n[0]
            ))
    return beats


def generate_second_order_beats(beats1: list[Beat]) -> list[Beat]:
    """生成二階 beat（beat 之間嘅差頻）"""
    beats2 = []
    # 取一階 beat 中最小嘅 500 個做疊加
    pool = beats1[:500]  # 工程限制: 500^2 = 250k 組合已夠
    for i in range(len(pool)):
        for j in range(i + 1, len(pool)):
            b1 = pool[i]
            b2 = pool[j]
            w = abs(b1.energy - b2.energy)
            if w / E_n[0] < 100:  # 只保留合理範圍
                beats2.append(Beat(
                    order=2, components=(b1.components, b2.components),
                    omega=w / hbar, energy=w,
                    ratio_to_w1=w / E_n[0]
                ))
    return beats2


def generate_third_order_beats(beats1: list[Beat]) -> list[Beat]:
    """生成三階 beat（三層 beat 嘅差頻）"""
    beats3 = []
    pool = beats1[:100]  # 100^3 = 1M, 工程限制
    for i in range(len(pool)):
        for j in range(i + 1, len(pool)):
            for k in range(j + 1, len(pool)):
                b1 = pool[i]
                b2 = pool[j]
                b3 = pool[k]
                # 疊加: beat1 + beat2 - beat3
                w = abs(b1.energy + b2.energy - b3.energy)
                if w / E_n[0] < 100 and w > 0:
                    beats3.append(Beat(
                        order=3, components=(b1.components, b2.components, b3.components),
                        omega=w / hbar, energy=w,
                        ratio_to_w1=w / E_n[0]
                    ))
    return beats3


# ============================================================
# 窮舉配對
# ============================================================
@dataclass
class Match:
    """一個配對結果"""
    ratio_name: str      # e.g. "m_u/m_d"
    ratio_value: float   # 目標比值
    beat: Beat           # 匹配嘅 beat
    error_pct: float     # 誤差百分比
    score: float         # 綜合評分 (越低越好)

    def __repr__(self) -> str:
        return (f"{self.ratio_name:>12} = {self.ratio_value:>12.6f} | "
                f"{self.beat} | "
                f"err={self.error_pct:7.3f}% | score={self.score:.2f}")


def exhaustive_match(beats: list[Beat], threshold: float = 10.0) -> list[Match]:
    """
    窮舉法: 所有 SM 質量比匹配所有 beat
    threshold: 只保留誤差 < threshold% 嘅匹配
    """
    # 生成所有 SM 質量比
    particles = list(SM_PARTICLES.items())
    matches = []

    for (name1, mass1) in particles:
        for (name2, mass2) in particles:
            if name1 == name2:
                continue
            # 質量比: 永遠大於 1 嘅方向
            ratio = max(mass1, mass2) / min(mass1, mass2)
            ratio_name = f"m_{name1}/m_{name2}" if mass1 > mass2 else f"m_{name2}/m_{name1}"

            # 對每個 beat 計算誤差
            for beat in beats:
                if beat.ratio_to_w1 <= 0:
                    continue
                # 直接比對: ratio = beat.ratio_to_w1
                err = abs(beat.ratio_to_w1 / ratio - 1) * 100
                if err < threshold:
                    # 評分: 誤差優先, 再考慮階數
                    score = err * (1 + beat.order * 0.1)
                    matches.append(Match(
                        ratio_name=ratio_name,
                        ratio_value=ratio,
                        beat=beat,
                        error_pct=err,
                        score=score
                    ))

    matches.sort(key=lambda m: m.score)
    return matches


def print_best_matches(matches: list[Match], top_n: int = 50):
    """打印最佳匹配"""
    print(f"{'質量比':>14} | {'目標值':>12} | {'Beat(order,comp)':>25} | {'Beat r':>8} | {'誤差%':>8} | {'評分':>6}")
    print("-" * 85)
    for m in matches[:top_n]:
        comp_str = str(m.beat.components)[:20]
        print(f"{m.ratio_name:>14} | {m.ratio_value:>12.6f} | "
              f"[{m.beat.order}阶]{comp_str:>20} | {m.beat.ratio_to_w1:>8.6f} | "
              f"{m.error_pct:>7.3f}% | {m.score:>5.1f}")


def print_summary(matches: list[Match]):
    """打印摘要"""
    print("\n" + "=" * 80)
    print("窮舉法 + 疊加法 摘要")
    print("=" * 80)

    # 按粒子分組
    particle_groups = {}
    for m in matches:
        key = m.ratio_name.split("/")[0]  # e.g. "m_u" from "m_u/m_d"
        if key not in particle_groups:
            particle_groups[key] = []
        particle_groups[key].append(m)

    for key in sorted(particle_groups.keys()):
        best = particle_groups[key][0]
        print(f"  {key}: 最佳匹配 {best.ratio_name} = {best.ratio_value:.6f}, "
              f"beat[{best.beat.order}阶]{best.beat.components}, "
              f"err={best.error_pct:.3f}%")

    # 統計
    err_bins = {"<0.1%": 0, "0.1-1%": 0, "1-5%": 0, "5-10%": 0}
    for m in matches:
        if m.error_pct < 0.1:
            err_bins["<0.1%"] += 1
        elif m.error_pct < 1.0:
            err_bins["0.1-1%"] += 1
        elif m.error_pct < 5.0:
            err_bins["1-5%"] += 1
        else:
            err_bins["5-10%"] += 1

    print(f"\n匹配分布 (誤差 < 10%):")
    for k, v in err_bins.items():
        print(f"  {k}: {v} 個")


# ============================================================
# 疊加法: Beat 嘅線性組合
# ============================================================
def superposition_match(beats: list[Beat], threshold: float = 5.0) -> list[Match]:
    """
    疊加法: 質量比 = a * beat1 + b * beat2
    其中 a, b = ±1
    """
    particles = list(SM_PARTICLES.items())
    matches = []
    pool = beats[:200]  # 工程限制

    for (name1, mass1) in particles:
        for (name2, mass2) in particles:
            if name1 == name2:
                continue
            ratio = max(mass1, mass2) / min(mass1, mass2)
            ratio_name = f"m_{name1}/m_{name2}" if mass1 > mass2 else f"m_{name2}/m_{name1}"

            # 疊加: beat_i ± beat_j
            for i in range(len(pool)):
                for j in range(i + 1, len(pool)):
                    b1 = pool[i]
                    b2 = pool[j]
                    for sign1, sign2 in [(1, 1), (1, -1), (-1, 1)]:
                        w = sign1 * b1.ratio_to_w1 + sign2 * b2.ratio_to_w1
                        if w <= 0:
                            continue
                        err = abs(w / ratio - 1) * 100
                        if err < threshold:
                            comp = (b1.components, b2.components, sign1, sign2)
                            beat = Beat(
                                order=4, components=comp,
                                omega=0, energy=0,
                                ratio_to_w1=w
                            )
                            score = err * 1.5  # 疊加 penalty
                            matches.append(Match(
                                ratio_name=ratio_name,
                                ratio_value=ratio,
                                beat=beat,
                                error_pct=err,
                                score=score
                            ))

    matches.sort(key=lambda m: m.score)
    return matches


# ============================================================
# 主程式
# ============================================================
if __name__ == "__main__":
    print("=" * 80)
    print("IDCM v10.0 — 窮舉法 + 疊加法")
    print("=" * 80)

    # 1. 生成一階 beat
    print("\n[1/4] 生成一階 beat...")
    beats1 = generate_first_order_beats()
    print(f"  一階 beat: {len(beats1)} 個")
    print(f"  能量範圍: {beats1[0].energy:.4e} ~ {beats1[-1].energy:.4e} eV")
    print(f"  ratio 範圍: {beats1[0].ratio_to_w1:.6f} ~ {beats1[-1].ratio_to_w1:.6f}")

    # 2. 生成二階 beat
    print("\n[2/4] 生成二階 beat (疊加)...")
    beats2 = generate_second_order_beats(beats1)
    print(f"  二階 beat: {len(beats2)} 個")

    # 3. 生成三階 beat
    print("\n[3/4] 生成三階 beat (疊加)...")
    beats3 = generate_third_order_beats(beats1)
    print(f"  三階 beat: {len(beats3)} 個")

    # 合併所有 beat
    all_beats = beats1 + beats2 + beats3
    all_beats.sort(key=lambda b: b.ratio_to_w1)
    print(f"\n  總 beat 數: {len(all_beats)} 個")
    print(f"  ratio 範圍: {all_beats[0].ratio_to_w1:.6f} ~ {all_beats[-1].ratio_to_w1:.6f}")

    # 4. 窮舉配對
    print("\n[4/4] 窮舉配對 SM 質量比...")
    matches = exhaustive_match(all_beats, threshold=5.0)
    print(f"  匹配總數 (<5% 誤差): {len(matches)} 個")

    print("\n" + "=" * 80)
    print("最佳匹配 (Top 50)")
    print("=" * 80)
    print_best_matches(matches, 50)

    # 5. 疊加法
    print("\n" + "=" * 80)
    print("疊加法匹配 (Top 20)")
    print("=" * 80)
    super_matches = superposition_match(all_beats, threshold=5.0)
    print_best_matches(super_matches, 20)

    # 6. 摘要
    print_summary(matches)

    # 7. 將結果寫入檔案
    print("\n[儲存] 寫入結果...")
    output_path = "data/exhaustive_match_results.txt"
    with open(output_path, "w") as f:
        f.write("IDCM v10.0 — 窮舉法 + 疊加法結果\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"SM 粒子數: {len(SM_PARTICLES)}\n")
        f.write(f"SM 質量比數: {len(SM_PARTICLES) * (len(SM_PARTICLES) - 1)}\n")
        f.write(f"一階 beat: {len(beats1)}\n")
        f.write(f"二階 beat: {len(beats2)}\n")
        f.write(f"三階 beat: {len(beats3)}\n")
        f.write(f"總 beat: {len(all_beats)}\n")
        f.write(f"匹配總數 (<5%): {len(matches)}\n\n")
        f.write("Top 50 匹配:\n")
        for m in matches[:50]:
            f.write(f"  {m}\n")
        f.write(f"\nTop 20 疊加匹配:\n")
        for m in super_matches[:20]:
            f.write(f"  {m}\n")
    print(f"  已儲存至 {output_path}")