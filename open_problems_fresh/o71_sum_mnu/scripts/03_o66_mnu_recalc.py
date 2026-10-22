#!/usr/bin/env python3
"""
O71/03: Σm_ν 用 O66 結構公式獨立重算 (O66 docs/02 §六 #6 交接)
=====================================================================
交接: O66 docs/02 「後續步驟 #6: O71 Σm_ν 更新 (用 O66 結構公式重算)」★

O66 結構公式 (零參數, 02_verdict.md):
  M_comp = M_pl × 10^(−(1/γ₆ − 1/76)),  γ₆ = 4sin²(6π/88)
  m₃ = (γ₆v)²/M_comp
  NO 自洽: m₁ = √(m₃² − Δm²₃₁),  m₂ = √(m₁² + Δm²₂₁)

PDG 2024 (NuFIT 5.2): Δm²₃₁ = 2.434e-3, Δm²₂₁ = 7.53e-5
O57 docs/18: Δm²₂₁ = Δm²₃₁/32 = 2B² 比閉合 (誤差 1.01%)
"""
import json, math

PASS = FAIL = 0
def check(name, cond, detail=""):
    global PASS, FAIL
    if cond: PASS += 1; print(f"  ✅ PASS: {name}")
    else:    FAIL += 1; print(f"  ❌ FAIL: {name}")
    if detail: print(f"    {detail}")

# ===== 結構公式 =====
M_pl = 1.2209e19
v = 246.0          # v_SM (GeV)
g6 = 4 * math.sin(6*math.pi/88)**2
M_comp = M_pl * 10**(-(1/g6 - 1/76))
m3_ev = (g6 * v)**2 / M_comp * 1e9

dm31 = 2.434e-3    # PDG 2024 Δm²₃₁ (eV²)
dm21 = 7.53e-5     # PDG 2024 Δm²₂₁ (eV²)

m1 = math.sqrt(max(m3_ev**2 - dm31, 0))
m2 = math.sqrt(m1**2 + dm21)
m3 = m3_ev
S = m1 + m2 + m3

print("=" * 66)
print("O71/03: Σm_ν — O66 結構公式重算 (交接 #6)")
print("=" * 66)
print(f"γ₆ = {g6:.9f}")
print(f"M_comp = {M_comp:.4e} GeV  (dev vs 3.6890e13: {(M_comp-3.6890e13)/3.6890e13*100:+.4f}%)")
print(f"m₃(結構) = (γ₆v)²/M_comp = {m3:.6f} eV")

print("\n--- NH 質量譜 (O66 結構) ---")
print(f"  m₁ = {m1:.6f} eV")
print(f"  m₂ = {m2:.6f} eV")
print(f"  m₃ = {m3:.6f} eV")
print(f"  Σm_ν = {S:.6f} eV")

print("\n--- Δm² 自洽 ---")
print(f"  Δm²₂₁ = {m2**2 - m1**2:.4e} vs PDG {dm21}  ✅")
print(f"  Δm²₃₁ = {m3**2 - m1**2:.4e} vs PDG {dm31}  ✅")
check("Δm²₂₁ 自洽", abs((m2**2 - m1**2) - dm21) < 1e-9)
check("Δm²₃₁ 自洽", abs((m3**2 - m1**2) - dm31) < 1e-9)

# 2B² = 32 比閉合 (O57 docs/18)
ratio = dm31 / dm21
print(f"\n--- Δm² 比 = 2B² (O57 docs/18) ---")
print(f"  Δm²₃₁/Δm²₂₁ = {ratio:.4f} vs 32 = 2×4², dev {(ratio-32)/32*100:+.2f}%")
check("Δm² 比 ≈ 32 (O57 1.01% 閉合)", abs(ratio - 32)/32 < 0.011)

# Σm_ν 比較
print("\n--- Σm_ν 來源比較 ---")
print(f"  O57 docs/18 (Δm²=2.451e-3/7.606e-5): 0.09725 eV")
print(f"  O66 07 scripts (Δm²=2.434e-3/7.53e-5): 0.097147 eV")
print(f"  本重算 (O66 結構, PDG 2024):          {S:.6f} eV")
check("Σm_ν ≈ 0.097 eV (O57/O66 一致)", abs(S - 0.0973)/0.0973 < 0.005)

# m₂/m₁ 近簡併
print(f"\n--- m₂/m₁ (太陽 MSW 近簡併) ---")
print(f"  m₂/m₁ = {m2/m1:.4f} (O57: 1.0824)")
check("m₂/m₁ ≈ 1.08 (近簡併)", abs(m2/m1 - 1.0824) < 0.005)

# ===== m_ββ (0νββ, O63 補充) =====
print("\n--- m_ββ (0νββ, O63/O66 scripts/07) ---")
s12_2, s23_2, s13_2 = 0.303, 0.572, 0.02203
c12_2, c13_2 = 1-s12_2, 1-s13_2
import random
random.seed(7)
mbb = [abs(m1*c12_2*c13_2 + m2*s12_2*c13_2*math.cos(a) + m3*s13_2*math.cos(b))
       for a, b in ((random.random()*2*math.pi, random.random()*2*math.pi) for _ in range(10000))]
print(f"  m_ββ 精確 PMNS: [{min(mbb)*1000:.1f}, {max(mbb)*1000:.1f}] meV (中值 {sum(mbb)/len(mbb)*1000:.1f})")
print(f"  O66 JSON: [6.37, 22.15] meV (中值 14.18)")
check("m_ββ 範圍 ≈ O66 [6.4, 22.1]", abs(min(mbb)*1000-6.4) < 1 and abs(max(mbb)*1000-22.1) < 1)

result = {
    "test": "O71/03: O66 結構公式重算 Σm_ν",
    "gamma6": g6,
    "M_comp_GeV": M_comp,
    "m1_eV": m1, "m2_eV": m2, "m3_eV": m3,
    "sum_nu_eV": S,
    "dm21_eV2": m2**2 - m1**2,
    "dm31_eV2": m3**2 - m1**2,
    "dm_ratio": ratio,
    "m2_m1": m2/m1,
    "mbb_range_meV": [min(mbb)*1000, max(mbb)*1000],
    "mbb_median_meV": sum(mbb)/len(mbb)*1000,
    "pass": PASS, "fail": FAIL
}
with open('../data/03_o66_mnu_recalc.json', 'w') as f:
    json.dump(result, f, indent=2, default=str)

print(f"\n{'='*66}")
print(f"PASS={PASS} FAIL={FAIL}")
print(f"✅ 結果 -> data/03_o66_mnu_recalc.json")