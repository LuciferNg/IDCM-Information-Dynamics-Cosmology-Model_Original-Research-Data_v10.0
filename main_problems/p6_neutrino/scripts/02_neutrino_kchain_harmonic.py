"""
IDCM v10.0 — 中微子：K_Chain 44 模式 harmonic 結構推導
========================================================
從 K_Chain 44 模式嘅 harmonic 結構直接推導中微子質量。

核心假設:
1. 中微子 = W-field 嘅 p6 模式 (K_Chain n=6)
2. 質量 = 來自 K_Chain harmonic, 非 12D WDVV eigenvalue
3. 可能機制: beat frequency, harmonic product, 或 self-coupling
"""

import math
import numpy as np

φ = (1 + math.sqrt(5)) / 2

# K_Chain 44 模式
γ_n = [4 * math.sin(math.pi * n / 88)**2 for n in range(1, 45)]

# 已知質量
masses = {
    "Top": 172760e3, "Bottom": 4180e3, "Tau": 1777e3,
    "Charm": 1270e3, "Strange": 93.4, "Muon": 105.658,
    "Up": 2.16, "Down": 4.67, "Electron": 0.511,
}

print("=" * 80)
print("IDCM v10.0 — K_Chain 44 模式 harmonic 推導 🎯")
print("=" * 80)

# ══════════════════════════════════════════════════════════════
# 1. K_Chain 44 模式結構
# ══════════════════════════════════════════════════════════════
print("\n1. K_Chain 44 模式結構")
print(f"  γ_n = 4sin²(πn/88), n = 1, ..., 44")
print(f"  粒子-n 對應: Top(1), Bottom(2), Tau(3), Charm(4), Strange(5), Muon(6), Up(7), Down(8), Electron(9)")

# 質量同 γ_n 嘅關係
print(f"\n  {'Particle':>10} | {'n':>3} | {'γ_n':>10} | {'mass(MeV)':>12} | {'mass/γ_n':>12}")
print("-" * 55)
for name, m in masses.items():
    n = list(masses.keys()).index(name) + 1
    γ = γ_n[n-1]
    print(f"  {name:>10} | {n:>3} | {γ:>10.6f} | {m:>12.4f} | {m/γ:>12.4f}")

# ══════════════════════════════════════════════════════════════
# 2. Beat frequency 分析
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("2. Beat frequency 分析 (中微子質量機制)")
print("─" * 80)

# 中微子 = p6 模式 (n=6)
# 可能係 beat frequency 之間嘅差
# beat = γ_n - γ_m 或 |γ_n - γ_m|

# 對於 n=6, 最接近嘅 mode 係 n=5 同 n=7
beat_65 = abs(γ_n[5] - γ_n[4])  # |γ_6 - γ_5|
beat_76 = abs(γ_n[6] - γ_n[5])  # |γ_7 - γ_6|
beat_64 = abs(γ_n[5] - γ_n[3])  # |γ_6 - γ_4|

print(f"  Beat frequencies involving n=6:")
print(f"    |γ_6 - γ_5| = {beat_65:.6f}")
print(f"    |γ_7 - γ_6| = {beat_76:.6f}")
print(f"    |γ_6 - γ_4| = {beat_64:.6f}")

# 如果中微子質量 ∝ beat frequency
# 比例常數從已知粒子推導
# 例如 Top (n=1): beat = γ_1 - γ_0, 但 γ_0 = 0 (無定義)
# 實際對應係 m_top = γ_1 × M_eff
# M_eff = m_top / γ_1 = 172760e3 / 0.005096 = 3.39e10 MeV

M_eff_1 = masses["Top"] / γ_n[0]  # n=1
M_eff_9 = masses["Electron"] / γ_n[8]  # n=9

print(f"  M_eff (from Top): {M_eff_1:.2e} MeV")
print(f"  M_eff (from Electron): {M_eff_9:.2e} MeV")

# M_eff 似乎同 n 有關
# M_eff(n) = m_n / γ_n

print(f"\n  M_eff 分析:")
print(f"  {'Particle':>10} | {'n':>3} | {'γ_n':>10} | {'mass(MeV)':>12} | {'M_eff':>15}")
print("-" * 55)
for name, m in masses.items():
    n = list(masses.keys()).index(name) + 1
    γ = γ_n[n-1]
    M_eff = m / γ
    print(f"  {name:>10} | {n:>3} | {γ:>10.6f} | {m:>12.4f} | {M_eff:>15.2f}")

# ══════════════════════════════════════════════════════════════
# 3. γ_n 嘅冪次關係
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("3. γ_n 嘅冪次關係")
print("─" * 80)

# 可能質量同 γ_n 嘅某個冪次成正比
# m ∝ γ_n^p

# 從 Top 同 Electron 推導 p
# m_T / m_E = (γ_1 / γ_9)^p
# p = log(m_T/m_E) / log(γ_1/γ_9)

p = math.log(masses["Top"] / masses["Electron"]) / math.log(γ_n[0] / γ_n[8])
print(f"  p = log(m_T/m_E) / log(γ_1/γ_9) = {p:.4f}")
print(f"  (p ≈ 1 if linear, p ≈ 2 if quadratic)")

# 如果 p ≈ 3.6, 質量同 γ_n^(3.6) 成正比
# 但呢個可能係巧合

# ══════════════════════════════════════════════════════════════
# 4. 中微子質量估算 (從 K_Chain harmonic)
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("4. 中微子質量估算 (從 K_Chain harmonic)")
print("─" * 80)

# 中微子 = p6 模式 (n=6)
# 方法 1: M_eff 外推
# M_eff(n) 似乎同 n 有關係
# 從 Electron (n=9, M_eff=1.28) 到 Top (n=1, M_eff=3.39e10)
# 中微子 n=6 嘅 M_eff 應該係?

# 如果 M_eff 同 γ_n 成反比 (即係 m = 常數 × γ_n²)
# m ∝ γ_n² → m_ν = γ_6² × K
# K = m_e / γ_9² = 0.511 / 0.3989²

K_sq = masses["Electron"] / γ_n[8]**2
m_nu_sq = γ_n[5]**2 * K_sq

print(f"  方法 1: m ∝ γ_n²")
print(f"    K = m_e / γ_9² = {K_sq:.4f} MeV")
print(f"    m_ν = γ_6² × K = {m_nu_sq:.6f} MeV = {m_nu_sq*1e6:.2f} eV")

# 方法 2: 用 beat frequency
# m_ν = |γ_6 - γ_5| × M_eff_6
# M_eff_6 從插值得出
# M_eff 隨 n 變化: n=1: 3.39e10, n=5: 740.8, n=9: 1.28
# 呢個係近似指數衰減

# 方法 3: 中微子 = W-field 自耦合
# 中微子質量可能來自 W-field 嘅自耦合項
# m_ν = g_ν × M_W × exp(-S_inst)
# 其中 g_ν 係自耦合常數, S_inst 係 instanton action

# 用 muon (n=6) 同 electron (n=9) 嘅比例
# 如果中微子 = muon 嘅 p6 模式 (同一 n)
# 咁中微子質量可能同 muon 有關
# m_ν = m_μ × exp(-ΔV) 其中 ΔV 係 V_cycle 差

# 從 muon: m_μ = 105.658 MeV, V_cycle ≈ 47.05
# 如果中微子 V_cycle 更大
# 需要 V_cycle_ν ≈ 47.05 + ln(m_μ / m_ν)
# 對於 m_ν ≈ 0.1 eV: ΔV = ln(105.658e6 / 0.1) = 20.8
# V_cycle_ν = 47.05 + 20.8 = 67.85

ΔV = math.log(105.658e6 / 0.1)
V_nu_est = 47.05 + ΔV

print(f"\n  方法 3: 從 muon V_cycle 外推")
print(f"    m_μ = 105.658 MeV, V_μ = 47.05")
print(f"    如果 m_ν ≈ 0.1 eV:")
print(f"    ΔV = ln(105.658e6 / 0.1) = {ΔV:.2f}")
print(f"    V_ν = 47.05 + {ΔV:.2f} = {V_nu_est:.2f}")

# 方法 4: 從 K_Chain 44 模式嘅 beat
# K_Chain 嘅 44 個模式嘅 difference 形成 beat
# 中微子可能係 n=6 同 n=0 嘅 beat
# 但 n=0 對應 γ_0 = 0 (零模)
# m_ν = γ_6 × M_base

# 如果 m_ν ∝ 1/γ_n (反比)
# 咁高 n 嘅粒子質量更輕
# 中微子 n=6 嘅質量比 electron (n=9) 重
# 但實驗顯示中微子比 electron 輕得多
# 所以反比關係唔成立

# 方法 5: 中微子 = W-field 嘅 topological 質量
# 來自 W-field 嘅 instanton 或 vortex 修正
# m_ν = M_W × exp(-S_inst)
# 其中 S_inst = 2π/α_W ≈ 2π/(1/30) ≈ 188
# m_ν ≈ 246 GeV × exp(-188) ≈ 10^-80 eV (太細)

# 最佳估算: 中微子質量來自 K_Chain 嘅 harmonic 乘積
# m_ν = γ_6 × γ_9 × M_eff
# 用 electron 做校準

m_nu_product = γ_n[5] * γ_n[8] * K_sq
print(f"\n  方法 5: ∝ γ_6 × γ_9")
print(f"    m_ν = γ_6 × γ_9 × K = {m_nu_product:.6f} MeV = {m_nu_product*1e6:.2f} eV")

# ══════════════════════════════════════════════════════════════
# 5. 中微子嘅 W-field 非對角混合
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("5. 中微子嘅 W-field 非對角混合 (PMNS)")
print("─" * 80)

# 中微子混合來自 W-field 嘅非對角項
# 類似 CKM, 但中微子混合係 lepton sector
# PMNS 矩陣 = U_ν^† · U_l

# 從 12D eigenvalue 結構:
# ν_τ, ν_μ, ν_e 對應 eigenvalue 9, 10, 11
# 但佢哋嘅 W-field 模式係 n=6

# 混合角:
# θ_12(PMNS) ≈ 33.4° (solar)
# θ_23(PMNS) ≈ 49.0° (atmospheric)
# θ_13(PMNS) ≈ 8.6° (reactor)

# 從 Z₅ analysis:
# ν_τ (Z₅=4), ν_μ (Z₅=0), ν_e (Z₅=3)
# 同 CKM 唔同, PMNS 角更大
# 可能因為右旋中微子唔存在 (無 seesaw)

print(f"  PMNS 混合角 (PDG):")
print(f"    θ₁₂ = 33.4° (solar)")
print(f"    θ₂₃ = 49.0° (atmospheric)")
print(f"    θ₁₃ = 8.6° (reactor)")
print(f"")
print(f"  Z₅ charges for neutrinos:")
print(f"    ν_τ: Z₅=4 (index 9)")
print(f"    ν_μ: Z₅=0 (index 10)")
print(f"    ν_e: Z₅=3 (index 11)")

# Z₅ phase differences
print(f"\n  Z₅ phase differences for PMNS:")
ν_z5 = {"ν_τ": 4, "ν_μ": 0, "ν_e": 3}
for ni in ν_z5:
    for nj in ν_z5:
        if ni != nj:
            diff = (ν_z5[ni] - ν_z5[nj]) % 5
            phase = 2 * math.pi * diff / 5
            print(f"    {ni} ↔ {nj}: ΔZ₅={diff}, phase={math.degrees(phase):.1f}°")

# ══════════════════════════════════════════════════════════════
# 6. 總結
# ══════════════════════════════════════════════════════════════
print("\n" + "─" * 80)
print("6. 總結")
print("─" * 80)

print(f"""
  🎯 中微子 K_Chain harmonic 推導:

  γ_n = 4sin²(πn/88), n=1,...,44
  p6 mode: n=6, γ_6 = {γ_n[5]:.6f}

  質量估算方法:
  ────────────────
  1. ∝ γ_n²: m_ν = {m_nu_sq:.4f} MeV = {m_nu_sq*1e6:.2f} eV ❌
  2. ∝ γ_6 × γ_9: m_ν = {m_nu_product:.6f} MeV = {m_nu_product*1e6:.2f} eV ❌
  3. V_cycle 外推: V_ν ≈ {V_nu_est:.2f} (需要獨立推導)
  4. Beat frequency: |γ_6-γ_5| = {beat_65:.6f} (待定)
  5. W-field topological: exp(-S_inst) (太細)

  結論:
  ──────
  中微子質量唔係簡單嘅 γ_n 比例或 beat frequency。
  需要更深入嘅 W-field 動力學分析。

  可能方向:
  ────────
  1. W-field 嘅非線性自耦合項
  2. K_Chain 嘅 instanton 修正
  3. CY₃ projection 嘅中微子 sector
  4. PMNS 混合同 Z₅ phase 嘅關係
""")

with open("data/neutrino_p6_results.txt", "w") as f:
    f.write("中微子 K_Chain harmonic 推導\n")
    f.write(f"γ_6 = {γ_n[5]:.6f}\n")
    f.write(f"m_ν(γ²) = {m_nu_sq*1e6:.2f} eV\n")
    f.write(f"m_ν(product) = {m_nu_product*1e6:.2f} eV\n")
    f.write("需要更深層嘅 W-field 動力學分析\n")

print("已儲存 ✅")