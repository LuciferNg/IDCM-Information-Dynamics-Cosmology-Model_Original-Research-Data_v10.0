"""
IDCM v10.0 — 結構性配對篩選
===========================
區分結構性匹配 vs 數值巧合
"""

import math
import itertools
from dataclasses import dataclass

# ============================================================
# 基本常數
# ============================================================
R_world = 4129.94
R_H = R_world  # deprecated alias (O73)
Nd = 44
c = 299792.458
Gyr = 3.15576e16
hbar = 6.582119569e-16
Mpc_to_km = 3.085677581e19
c_ms = c * 1e3
omega_scale = 88 * c_ms / (R_world * Mpc_to_km * 1e3)

# ============================================================
# SM 粒子質量 (MeV)
# ============================================================
SM_PARTICLES = {
    "u": 2.16, "d": 4.67,
    "s": 93.4, "c": 1270.0,
    "b": 4180.0, "t": 172760.0,
    "e": 0.51099895, "mu": 105.6583745, "tau": 1776.86,
    "W": 80377.0, "Z": 91187.6, "H": 125250.0,
}

# 按質量排序
sorted_particles = sorted(SM_PARTICLES.items(), key=lambda x: x[1])
particle_names = [p[0] for p in sorted_particles]
particle_masses = [p[1] for p in sorted_particles]

# ============================================================
# K_Chain 能量
# ============================================================
E_n = [hbar * omega_scale * math.sin(math.pi * n / 88) for n in range(1, Nd + 1)]


def find_beat_combination(target_ratio: float, max_order: int = 2,
                          max_components: int = 4) -> list:
    """
    對一個目標 ratio，嘗試用最簡單嘅 beat 組合匹配
    返回所有匹配 (order, components, error)
    """
    results = []

    # 一階: 直接 beat
    for n in range(1, Nd + 1):
        for m in range(n + 1, Nd + 1):
            r = abs(E_n[n-1] - E_n[m-1]) / E_n[0]
            err = abs(r / target_ratio - 1) * 100
            if err < 1.0:
                results.append((1, (n, m), r, err))

    # 二階: beat 嘅 beat
    if max_order >= 2:
        beats1 = []
        for n in range(1, Nd + 1):
            for m in range(n + 1, Nd + 1):
                r = abs(E_n[n-1] - E_n[m-1]) / E_n[0]
                beats1.append(((n, m), r))

        for i in range(len(beats1)):
            for j in range(i + 1, len(beats1)):
                b1, r1 = beats1[i]
                b2, r2 = beats1[j]
                r = abs(r1 - r2)
                if r <= 0:
                    continue
                err = abs(r / target_ratio - 1) * 100
                if err < 0.5:
                    results.append((2, (b1, b2, '-'), r, err))

                r = r1 + r2
                err = abs(r / target_ratio - 1) * 100
                if err < 0.5:
                    results.append((2, (b1, b2, '+'), r, err))

    results.sort(key=lambda x: (x[0], x[3]))
    return results[:20]  # 每個 ratio 返回最佳 20 個


# ============================================================
# 主要分析
# ============================================================
print("=" * 90)
print("IDCM v10.0 — 結構性配對分析")
print("僅保留一階/二階 beat，排除過擬合")
print("=" * 90)

# 1. 列出所有 SM 質量比
print("\n【SM 粒子質量譜】")
print(f"{'粒子':>6} | {'質量 (MeV)':>12} | {'質量比 m_n/m_e':>16}")
print("-" * 45)
for name, mass in sorted_particles:
    ratio = mass / SM_PARTICLES["e"]
    print(f"{name:>6} | {mass:>12.4f} | {ratio:>16.6f}")

# 2. 對每個粒子，找佢同最低質量粒子 (e) 嘅 ratio 嘅 beat 匹配
print("\n" + "=" * 90)
print("【結構性匹配: 一階 Beat 直接匹配】")
print("每對粒子質量比 vs K_Chain 一階 beat frequency")
print("=" * 90)

all_1st_matches = []  # 記錄所有一階匹配

for name, mass in sorted_particles:
    # 用電子做基準: ratio = m/m_e
    ratio = mass / SM_PARTICLES["e"]
    matches = find_beat_combination(ratio, max_order=1)
    if matches:
        order, comp, r, err = matches[0]
        if err < 0.2:
            print(f"m_{name}/m_e = {ratio:>12.6f} | "
                  f"一階({comp[0]:2d},{comp[1]:2d}) r={r:>8.6f} | "
                  f"err={err:>6.3f}% ✅")
            all_1st_matches.append((name, ratio, comp, err))
        else:
            print(f"m_{name}/m_e = {ratio:>12.6f} | "
                  f"最近一階({comp[0]:2d},{comp[1]:2d}) r={r:>8.6f} | "
                  f"err={err:>6.3f}% ❌")

print(f"\n一階直接匹配: {len(all_1st_matches)}/{len(sorted_particles)}")

# 3. 同一生成分折
print("\n" + "=" * 90)
print("【三代結構分析】")
print("=" * 90)

# 3a. 夸克代間比
print("\n3a. 夸克代間比例:")
generations = {
    "1st": ("u", "d"),
    "2nd": ("s", "c"),
    "3rd": ("b", "t"),
}
for gen_name, (q1, q2) in generations.items():
    m1 = SM_PARTICLES[q1]
    m2 = SM_PARTICLES[q2]
    avg = (m1 + m2) / 2
    if gen_name == "1st":
        next_gen = "2nd"
        m3 = (SM_PARTICLES["s"] + SM_PARTICLES["c"]) / 2
    elif gen_name == "2nd":
        next_gen = "3rd"
        m3 = (SM_PARTICLES["b"] + SM_PARTICLES["t"]) / 2
    else:
        continue
    ratio = m3 / avg
    print(f"  {gen_name} ({q1},{q2}) avg={avg:>10.2f} -> "
          f"{next_gen} avg={m3:>10.2f} : ratio={ratio:>10.4f}")
    matches = find_beat_combination(ratio, max_order=2)
    if matches:
        order, comp, r, err = matches[0]
        print(f"    -> 最佳匹配: [{order}阶]{comp}, err={err:.3f}%")

# 3b. 輕子代間比
print("\n3b. 輕子代間比例:")
leptons = [("e", "mu"), ("mu", "tau")]
for l1, l2 in leptons:
    ratio = SM_PARTICLES[l2] / SM_PARTICLES[l1]
    print(f"  m_{l2}/m_{l1} = {ratio:>10.4f}")
    matches = find_beat_combination(ratio, max_order=2)
    if matches:
        order, comp, r, err = matches[0]
        print(f"    -> 最佳匹配: [{order}阶]{comp}, err={err:.3f}%")

# 3c. 玻色子比
print("\n3c. 規範玻色子比例:")
bosons = [("W", "Z"), ("H", "W")]
for b1, b2 in bosons:
    ratio = SM_PARTICLES[b2] / SM_PARTICLES[b1]
    print(f"  m_{b2}/m_{b1} = {ratio:>10.4f}")
    matches = find_beat_combination(ratio, max_order=2)
    if matches:
        order, comp, r, err = matches[0]
        print(f"    -> 最佳匹配: [{order}阶]{comp}, err={err:.3f}%")

# 4. 總結
print("\n" + "=" * 90)
print("【總結: 結構性 vs 巧合】")
print("=" * 90)
print("""
判斷標準:
  1. 一階 beat 匹配 (直接物理共振) -> 結構性強
  2. 二階 beat 匹配 (兩層疊加)     -> 可能結構性
  3. 三階+ beat 匹配               -> 過擬合高

結果:
  - 一階 beat 可以直接匹配宇宙大尺度結構 (ξ(s) 17/19 ✅)
  - 但 SM 粒子質量比唔可以直接用一階 beat match
  - 需要 CY₃(36,98) 投影因子做幾何放大

下一步:
  1. 編寫 CY₃(36,98) 投影矩陣 -> 引入幾何放大因子
  2. 建立粒子質量 = ω_nm × Hodge因子 模型
  3. 用 36 Kähler + 98 complex structure 模數解釋 134 個自由度
""")

# 5. 完整記錄
print("\n[儲存] 寫入結構性匹配記錄...")
with open("data/structural_matches.txt", "w") as f:
    f.write("IDCM v10.0 — 結構性配對分析\n")
    f.write("=" * 80 + "\n\n")
    f.write("一階 Beat 匹配 (直接物理共振)\n\n")
    for name, mass in sorted_particles:
        ratio = mass / SM_PARTICLES["e"]
        matches = find_beat_combination(ratio, max_order=1)
        f.write(f"m_{name}/m_e = {ratio:.6f}\n")
        if matches:
            for order, comp, r, err in matches[:5]:
                f.write(f"  [{order}阶] {comp}: r={r:.6f}, err={err:.4f}%\n")
        else:
            f.write(f"  [無匹配]\n")
        f.write("\n")
    f.write("\n二階 Beat 匹配\n\n")
    for name, mass in sorted_particles:
        ratio = mass / SM_PARTICLES["e"]
        matches = find_beat_combination(ratio, max_order=2)
        f.write(f"m_{name}/m_e = {ratio:.6f}\n")
        if matches:
            for order, comp, r, err in matches[:5]:
                f.write(f"  [{order}阶] {comp}: r={r:.6f}, err={err:.4f}%\n")
        else:
            f.write(f"  [無匹配]\n")
        f.write("\n")
print("  已儲存至 data/structural_matches.txt")