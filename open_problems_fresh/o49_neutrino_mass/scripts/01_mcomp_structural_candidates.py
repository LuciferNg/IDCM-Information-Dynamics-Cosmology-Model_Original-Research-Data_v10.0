#!/usr/bin/env python3
"""
O49-1: M_comp Structural Candidates — Systematic Exploration
=============================================================
從 CY₃(36,98) 幾何結構推導 M_comp，唔係數值反推。

M_comp 係 Z₅ orbifold 嘅幾何緊化能標，控制中微子質量：
  m_ν = (γ₆ × v)² / M_comp

⚠️ 參考基準 (REFERENCE) 聲明 — 三個 M_comp 值必須區分:
  [A] M_comp_calib = 3.6909e13 GeV  — 舊文檔 (neutrino_p6_mode.md) 數值校準值
  [B] M_comp_struct = M_Pl/(2×h11×h21×Nd) = 3.9325e13 GeV — 本 O49 結構推導值
  [C] M_comp_inv    = (γ₆v)²/√(Δm²₃₁/(1-φ⁻⁴)) = 3.7030e13 GeV — 由 PDG Δm²₃₁ 物理反演
  本 script 搜索用 [A] (歷史校準) 作目標, [C] 嘅結構閉合由 script 03/04 完成。
  最終閉合邏輯: [B] × φ^(1/8) 修正 → Δm²₃₁ 0.0024% ✅ (script 04)

已知:
  - M_Pl = 1.220910 × 10¹⁹ GeV
  - h¹¹ = 36, h²¹ = 98, CY₃ = 134
  - Nd = 44, B = 4
  - Lucas: L₃=4, L₄=7, L₅=11, L₆=18, L₇=29, L₈=47
  - Fibonacci: F₅=5, F₆=8, F₇=13, F₈=21, F₉=34
  - φ = (1+√5)/2
"""

import math, sys, os
import json
import itertools

phi = (1 + math.sqrt(5)) / 2

# Constants
M_Pl = 1.220910e19   # GeV
# [A] legacy calibrated value (from main_problems/p15_early_derivations/docs/neutrino_p6_mode.md)
M_comp_target = 3.6909e13  # GeV
# [C] physical inversion from PDG Δm²₃₁ (for reference)
M_comp_inv = 3.7030e13     # GeV
v = 246.0  # GeV
gamma6 = 4 * math.sin(6 * math.pi / 88) ** 2

# Lucas numbers
L = [2, 1, 3, 4, 7, 11, 18, 29, 47, 76, 123]
# Fibonacci
F = [0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89]

# CY₃ parameters
h11, h21 = 36, 98
Nd = 44
B = 4
N_gen = 3

print("=" * 80)
print("O49-1: M_comp Structural Candidates")
print("=" * 80)

# ============ RATIO ANALYSIS ============
print("\n" + "─" * 80)
print("RATIO: M_Pl / M_comp_target")
print("─" * 80)

ratio = M_Pl / M_comp_target
print(f"  M_Pl / M_comp = {ratio:.4f}")
print(f"  log10(ratio) = {math.log10(ratio):.4f}")

# Factor decomposition
print(f"\n  Prime factorization:")
n = round(ratio)
factors = []
d = 2
while d * d <= n:
    while n % d == 0:
        factors.append(d)
        n //= d
    d += 1
if n > 1:
    factors.append(n)
print(f"  {round(M_Pl/M_comp_target)} = {' × '.join(map(str, factors))}")

# ============ CANDIDATE FORMULAS ============
print("\n" + "─" * 80)
print("STRUCTURAL CANDIDATES FOR M_comp = M_Pl / denominator")
print("─" * 80)

candidates = []

def test(name, denom, note=""):
    m = M_Pl / denom
    err = abs(m - M_comp_target) / M_comp_target * 100
    status = "🟢" if err < 0.5 else ("🟡" if err < 5 else "🔴")
    candidates.append((status, name, m, err, note))
    return status, err

# === Group 1: CY₃ Volume Factors ===
test("h¹¹ × h²¹ × Nd", h11 * h21 * Nd,
     "CY₃ Hodge numbers × chain length")
test("2 × h¹¹ × h²¹ × Nd", 2 * h11 * h21 * Nd,
     "(existing session candidate)")
test("h¹¹ × h²¹ × Nd × B", h11 * h21 * Nd * B,
     "× B=4 (K_Tree)")
test("h¹¹ × h²¹ × Nd × L₅", h11 * h21 * Nd * L[5],
     "× L₅=11")
test("h¹¹ × h²¹ × L₇ × L₅", h11 * h21 * L[7] * L[5],
     "× L₇×L₅ = 29×11")
test("h¹¹ × h²¹ × Nd × L₇/L₃", h11 * h21 * Nd * L[7] / L[3],
     "× L₇/L₃ = 29/4")
test("h¹¹ × h²¹ × Nd × F₉/F₅", h11 * h21 * Nd * F[9] / F[5],
     "× F₉/F₅ = 34/5")
test("h¹¹ × h²¹ × Nd × φ²", h11 * h21 * Nd * phi**2,
     "× φ²")

# === Group 2: Nd multiples ===
test("Nd⁴", Nd**4, "Nd⁴ = 44⁴")
test("Nd³ × B", Nd**3 * B, "Nd³ × 4")
test("Nd² × h¹¹ × h²¹", Nd**2 * h11 * h21, "Nd² × CY₃ Hodge")
test("Nd × h¹¹² × h²¹", Nd * h11**2 * h21, "Nd × 36² × 98")
test("Nd × h¹¹ × h²¹²", Nd * h11 * h21**2, "Nd × 36 × 98²")

# === Group 3: Lucas/Fibonacci combinations ===
test("L₅ × L₆ × L₇ × L₈", L[5]*L[6]*L[7]*L[8],
     "11×18×29×47")
test("L₅ × L₇ × F₈ × F₉", L[5]*L[7]*F[8]*F[9],
     "11×29×21×34")
test("F₇ × F₈ × F₉ × L₅", F[7]*F[8]*F[9]*L[5],
     "13×21×34×11")
test("L₆ × L₇ × Nd × B", L[6]*L[7]*Nd*B,
     "18×29×44×4")
test("L₅ × L₇ × Nd × F₈", L[5]*L[7]*Nd*F[8],
     "11×29×44×21")
test("F₆ × F₇ × F₈ × L₆", F[6]*F[7]*F[8]*L[6],
     "8×13×21×18")

# === Group 4: φ-based candidates ===
# M_comp = M_Pl × φ^p
for p_int in range(-20, 1):
    p = float(p_int)
    m = M_Pl * phi**p
    err = abs(m - M_comp_target) / M_comp_target * 100
    if err < 5:
        test(f"M_Pl × φ^{p_int}", phi**(-p_int),
             f"φ-power: exact {p_int}")

# === Group 5: γ₆-based candidates ===
for p in [1, 2, 3, 4, 5, 6, 7, 8]:
    denom = gamma6**(-p)
    m = M_Pl / denom
    err = abs(m - M_comp_target) / M_comp_target * 100
    if err < 10:
        test(f"M_Pl × γ₆^{p}", denom,
             f"γ₆^{p} = {gamma6**p:.6e}")

# === Group 6: SUSY/GUT scale relations ===
M_GUT = 2e16  # GeV
test("M_GUT × L₇ × L₅ / B", M_GUT / (L[7]*L[5]/B),
     f"M_GUT × {L[7]}×{L[5]}/{B} from GUT scale (M_GUT=2e16)")
test("M_GUT × Nd × B", M_GUT / (Nd*B),
     "M_GUT × Nd×B (M_GUT=2e16)")

# === Group 7: String-inspired exponentials ===
# M_comp = M_Pl × exp(-V_cycle) where V_cycle is a structural number
V_cycle_candidates = {
    "V=ln(330788)": math.log(330788),
    "V=L₇+L₅": L[7]+L[5],
    "V=L₆+L₅": L[6]+L[5],
    "V=Nd/2": Nd/2,
    "V=h¹¹": h11,
    "V=h²¹/2": h21/2,
    "V=CY₃": h11+h21,
}
for name, V in V_cycle_candidates.items():
    m = M_Pl * math.exp(-V)
    err = abs(m - M_comp_target) / M_comp_target * 100
    if err < 10:
        test(f"M_Pl × e^(-{name})", math.exp(V),
             f"e^-V={math.exp(-V):.4e}")

# === Group 8: Transfer matrix approach (O142) ===
# T̂ = [[1,1],[1,0]], L_n = Tr(T̂ⁿ), F_n = (T̂ⁿ)₁₂
# M_comp might be M_Pl / (L_a × L_b × F_c × ...)
for a in range(1, 10):
    for b in range(1, 10):
        for c in range(1, 8):
            denom = L[a] * L[b] * F[c]
            if denom == 0:
                continue
            m = M_Pl / denom
            err = abs(m - M_comp_target) / M_comp_target * 100
            if err < 1:
                test(f"L_{a}×L_{b}×F_{c}", denom,
                     f"L{a}={L[a]}, L{b}={L[b]}, F{c}={F[c]}")

# ============ SORT AND DISPLAY ============
print(f"\n{'Status':<6} {'Error%':<8} {'M_comp (GeV)':<20} {'Candidate':<40} Note")
print("─" * 80)

candidates.sort(key=lambda x: x[3])  # sort by error
for status, name, m_val, err, note in candidates:
    print(f"{status:<6} {err:<8.4f} {m_val:<20.4e} {name:<40} {note}")

# ============ FOCUSED ANALYSIS: BEST CANDIDATE ============
print("\n" + "─" * 80)
print("FOCUSED ANALYSIS: Top Candidates")
print("─" * 80)

# Best structural candidates
top = candidates[:5]
for status, name, m_val, err, note in top:
    print(f"\n  {status} {name} (error: {err:.4f}%)")
    print(f"     M_comp = {m_val:.4e} GeV")
    print(f"     Target = {M_comp_target:.4e} GeV")
    print(f"     Note: {note}")

# ============ DERIVATION PATH: M_comp composition ============
print("\n" + "─" * 80)
print("STRUCTURAL DECOMPOSITION OF M_comp")
print("─" * 80)

# M_comp = 3.6909e13 GeV
# What is this number in terms of IDCM primitives?
print(f"\n  M_comp = {M_comp_target:.4e} GeV")
print(f"  M_comp in natural units: M_comp/M_Pl = {M_comp_target/M_Pl:.6e}")
print(f"  log10(M_comp/GeV) = {math.log10(M_comp_target):.4f}")

# M_comp in terms of M₀
M0 = 27.900915e-3  # GeV
print(f"  M_comp / M₀ = {M_comp_target/M0:.4e}")

# What about the γ₆ × v product?
print(f"  γ₆ × v = {gamma6 * v:.4f} GeV")
print(f"  (γ₆ × v)² = {(gamma6 * v)**2:.4f} GeV²")

# ============ VERIFICATION ============
print("\n" + "─" * 80)
print("VERIFICATION: m_ν from best candidate")
print("─" * 80)

for status, name, m_val, err, note in top[:3]:
    m_nu = (gamma6 * v) ** 2 / m_val
    m_nu_eV = m_nu * 1e9  # GeV → eV
    print(f"\n  {status} {name}")
    print(f"    M_comp = {m_val:.4e} GeV")
    print(f"    m_ν_τ = {m_nu_eV:.4f} eV")
    print(f"    m_ν_μ = {m_nu_eV/phi:.4f} eV (φ⁻¹)")
    print(f"    m_ν_e = {m_nu_eV/phi**2:.4f} eV (φ⁻²)")
    dm31 = m_nu_eV**2 - (m_nu_eV/phi**2)**2
    dm21 = (m_nu_eV/phi)**2 - (m_nu_eV/phi**2)**2
    print(f"    Δm²₃₁ = {dm31:.4e} eV² (PDG: 2.434e-3)")
    print(f"    Δm²₂₁ = {dm21:.4e} eV² (PDG: 7.53e-5)")

# ============ SAVE RESULTS ============
results = {
    "title": "O49-1: M_comp Structural Candidates",
    "M_comp_target": M_comp_target,
    "M_Pl": M_Pl,
    "ratio": M_Pl / M_comp_target,
    "top_candidates": [
        {"name": name, "M_comp": m_val, "error_pct": round(err, 4),
         "status": status}
        for status, name, m_val, err, note in top[:5]
    ],
    "gamma6": gamma6,
    "m_nu_inferred": (gamma6 * v) ** 2 / M_comp_target * 1e9,
}

outdir = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(outdir, exist_ok=True)
with open(os.path.join(outdir, "01_mcomp_candidates.json"), "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\n{'='*80}")
print("Results saved to data/01_mcomp_candidates.json")
print("=" * 80)