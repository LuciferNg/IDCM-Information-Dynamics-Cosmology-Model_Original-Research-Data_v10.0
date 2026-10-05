#!/usr/bin/env python3
"""
O49-2: M_comp Exact Ratio Decomposition
=========================================
M_Pl / M_comp_target = 330,789  (approximately, vs [A] calibrated)
Find the exact structural decomposition of this ratio.

⚠️ REFERENCE 聲明: 本 script 用 [A] M_comp_calib = 3.6909e13 (舊校準值)
作目標. 物理反演值 [C] = 3.7030e13 (ratio 329,708). 最終結構閉合
用 [B] M_comp_struct = M_Pl/(2×h11×h21×Nd) = 3.9325e13 (ratio 310,464 EXACT),
配合 φ^(1/8) 修正 (script 04). 三者區分詳見 script 01 header.
"""
import math, os, json
import itertools

phi = (1 + math.sqrt(5)) / 2

M_Pl = 1.220910e19
# [A] legacy calibrated target (main_problems/p15_early_derivations/docs/neutrino_p6_mode.md)
M_comp_target = 3.6909e13
ratio = M_Pl / M_comp_target

# IDCM structural primitives
PRIMITIVES = {
    "Nd": 44, "B": 4, "N_gen": 3,
    "h11": 36, "h21": 98, "CY3": 134,
    "L3": 4, "L4": 7, "L5": 11, "L6": 18, "L7": 29, "L8": 47, "L9": 76, "L10": 123,
    "F5": 5, "F6": 8, "F7": 13, "F8": 21, "F9": 34, "F10": 55, "F11": 89,
    "phi": phi, "phi2": phi**2, "phi3": phi**3,
    "phi_m1": phi**-1, "phi_m2": phi**-2, "phi_m3": phi**-3,
    "Nd_phi": 44*phi, "Nd_phi2": 44*phi**2,
    "B2": 16, "B3": 64, "B4": 256,
    "Nd2": 1936, "Nd3": 85184, "Nd4": 3748096,
    "h11_h21": 36*98, "h11_2": 1296, "h21_2": 9604,
}

gamma6 = 4 * math.sin(6 * math.pi / 88) ** 2

print("=" * 80)
print("O49-2: M_comp Exact Ratio Decomposition")
print("=" * 80)
print(f"\n  M_Pl / M_comp = {ratio:.4f}")
print(f"  Nearest integer: {round(ratio)}")
print(f"  Error: {abs(round(ratio) - ratio) / ratio * 100:.4f}%")

# 1. Find all 2-factor and 3-factor products of primitives that match
print("\n" + "─" * 80)
print("2-FACTOR DECOMPOSITIONS")
print("─" * 80)

target = round(ratio)
best = []

for (k1, v1), (k2, v2) in itertools.combinations(PRIMITIVES.items(), 2):
    prod = v1 * v2
    err = abs(prod - target) / target * 100
    if err < 2:
        status = "🟢" if err < 0.5 else "🟡"
        best.append((err, status, f"{k1}×{k2}", prod, v1, v2))
        print(f"  {status} {k1}×{k2} = {v1}×{v2} = {prod:.0f}  (error: {err:.4f}%)")

print("\n" + "─" * 80)
print("3-FACTOR DECOMPOSITIONS")
print("─" * 80)

for (k1, v1), (k2, v2), (k3, v3) in itertools.combinations(PRIMITIVES.items(), 3):
    prod = v1 * v2 * v3
    err = abs(prod - target) / target * 100
    if err < 1:
        status = "🟢" if err < 0.3 else "🟡"
        best.append((err, status, f"{k1}×{k2}×{k3}", prod, v1, v2, v3))
        print(f"  {status} {k1}×{k2}×{k3} = {v1}×{v2}×{v3} = {prod:.0f}  (error: {err:.4f}%)")

# 2. Also check 2×h11×h21×Nd (the existing candidate)
print("\n" + "─" * 80)
print("EXISTING CANDIDATE RE-EXAMINATION")
print("─" * 80)

existing = 2 * 36 * 98 * 44
print(f"  2×h¹¹×h²¹×Nd = 2×36×98×44 = {existing}")
print(f"  Target ratio = {target}")
print(f"  Error: {abs(existing - target)/target*100:.4f}%")

# What's the missing factor?
missing = target / existing
print(f"  Missing factor (target/existing) = {missing:.6f}")
print(f"  φ⁻¹ = {phi**-1:.6f} (diff: {abs(missing - phi**-1)/phi**-1*100:.4f}%)")
print(f"  φ⁻² = {phi**-2:.6f} (diff: {abs(missing - phi**-2)/phi**-2*100:.4f}%)")
print(f"  F₅/L₅ = {5/11:.6f} (diff: {abs(missing - 5/11)/(5/11)*100:.4f}%)")
print(f"  L₄/L₅ = {7/11:.6f} (diff: {abs(missing - 7/11)/(7/11)*100:.4f}%)")
print(f"  F₆/L₆ = {8/18:.6f} (diff: {abs(missing - 8/18)/(8/18)*100:.4f}%)")
print(f"  B/Nd = {4/44:.6f} (diff: {abs(missing - 4/44)/(4/44)*100:.4f}%)")

# 3. Search for exact match
print("\n" + "─" * 80)
print("EXACT RATIO SEARCH (within 0.1%)")
print("─" * 80)

# Try combinations with division
items = list(PRIMITIVES.items())
exact_matches = []
for (k1, v1), (k2, v2) in itertools.combinations(items, 2):
    for (k3, v3) in items:
        if v3 == 0:
            continue
        val = v1 * v2 / v3
        err = abs(val - target) / target * 100
        if err < 0.1:
            exact_matches.append((err, f"{k1}×{k2}/{k3}", val, v1, v2, v3))

exact_matches.sort()
for err, formula, val, *_ in exact_matches[:10]:
    print(f"  🟢 {formula} = {val:.0f}  (error: {err:.4f}%)")

# 4. Check if M_comp can be expressed as M_Pl / (Nd × 2 × h11 × h21 × φ^(something))
print("\n" + "─" * 80)
print("M_comp = M_Pl / (2 × h¹¹ × h²¹ × Nd × φ^p)")
print("─" * 80)

base = 2 * 36 * 98 * 44
for p_int in range(-5, 6):
    p = float(p_int)
    denom = base * phi**p
    m = M_Pl / denom
    err = abs(m - M_comp_target) / M_comp_target * 100
    print(f"  φ^{p_int:+d}: M_comp = {m:.4e} GeV, error = {err:.4f}%")

# 5. Check M_comp = M_Pl / (CY3 × Nd × something)
print("\n" + "─" * 80)
print("M_comp = M_Pl / (CY₃ × Nd × factor)")
print("─" * 80)

base2 = 134 * 44
for factor_label, factor_val in [("L₅=11", 11), ("L₆=18", 18), ("L₇=29", 29),
                                  ("L₅×B=44", 44), ("L₅×L₄=77", 77),
                                  ("F₉=34", 34), ("F₈=21", 21)]:
    denom = base2 * factor_val
    m = M_Pl / denom
    err = abs(m - M_comp_target) / M_comp_target * 100
    print(f"  CY₃×Nd×{factor_label}: M_comp = {m:.4e} GeV, error = {err:.4f}%")

# 6. Exact ratio factorization
print("\n" + "─" * 80)
print("RATIO = 330788: PRIME FACTORIZATION")
print("─" * 80)
n = 330788
factors = []
d = 2
while d * d <= n:
    while n % d == 0:
        factors.append(d)
        n //= d
    d += 1
if n > 1:
    factors.append(n)
print(f"  330788 = {' × '.join(map(str, factors))}")
print(f"          = 2² × 41 × 2017")

# 41 = Nd - 3 = 44 - 3 = L₄ × L₃ + 1?  No, 41 is prime.
# Let's check: 41 = ?
print(f"\n  41 = ?")
print(f"    Nd - 3 = 44 - 3 = {44-3}")
print(f"    L₇ + L₅ = 29 + 11 = {29+11}")
print(f"    L₆ + L₄ = 18 + 7 = {18+7}")
print(f"    F₈ + F₇ = 21 + 13 = {21+13}")
print(f"    F₉ + F₆ = 34 + 8 = {34+8}")
print(f"    h¹¹ + 5 = 36 + 5 = {36+5}")
print(f"    h²¹/2 - 8 = 49 - 8 = {49-8}")

# 2017 = ?
print(f"\n  2017 = ?")
print(f"    44×44 + 81 = {44*44} + 81 = {44*44+81}")
print(f"    44×44 + 9² = 1936 + 81 = 2017 ✓")
print(f"    36×56 + 1 = 2016 + 1 = {36*56+1}")
print(f"    44×46 - 7 = {44*46-7}")

# 7. Check if the exact ratio relates to 2×36×98×44 = 310464
# 310464 = 2² × 2³ × 3² × 7² × 11
# Let's factor 310464
print("\n" + "─" * 80)
print("EXISTING: 2×h¹¹×h²¹×Nd = 310464")
print("─" * 80)
n2 = 310464
factors2 = []
d = 2
while d * d <= n2:
    while n2 % d == 0:
        factors2.append(d)
        n2 //= d
    d += 1
if n2 > 1:
    factors2.append(n2)
print(f"  310464 = {' × '.join(map(str, factors2))}")
print(f"          = 2⁶ × 3² × 7² × 11")

# 330788 / 310464 = ?
ratio2 = 330788 / 310464
print(f"\n  330788 / 310464 = {ratio2:.6f}")
print(f"  = 2017 / (2³ × 3² × 7) = 2017 / (8×9×7) = 2017 / 504")
print(f"  2017 / 504 = {2017/504:.6f}")

# 8. Check: 330788 - 310464 = ?
diff = 330788 - 310464
print(f"\n  330788 - 310464 = {diff}")
print(f"  = 2 × 89 × 134 = 2 × F₁₁ × CY₃?  2×89×134 = {2*89*134}")
print(f"  = 2 × 89 = {2*89}")
print(f"  = F₁₀ = 55? {55}")
print(f"  = L₇ = 29? {29}")
print(f"  diff = {diff}")

# 9. Check if the exact ratio is 2×h11×h21×Nd × (1 + 1/L₇)
print(f"\n  2×h11×h21×Nd × (1 + 1/L₇) = {310464 * (1 + 1/29):.0f}")
print(f"  error = {abs(310464*(1+1/29) - 330788)/330788*100:.4f}%")

# 10. Check structural: M_comp = M_Pl / (Nd × (h¹¹ + h²¹) × L₅ × L₆)
print(f"\n  Nd × CY₃ × L₅ = 44 × 134 × 11 = {44*134*11}")
print(f"  error = {abs(M_Pl/(44*134*11) - M_comp_target)/M_comp_target*100:.4f}%")

# 11. Check: gamma6 × M_Pl / M_comp = ?
print(f"\n  γ₆ × M_Pl / M_comp = {gamma6 * M_Pl / M_comp_target:.4f}")
print(f"  γ₆ × M_Pl / M_comp / Nd = {gamma6 * M_Pl / M_comp_target / 44:.4f}")

results = {
    "ratio": ratio,
    "ratio_rounded": round(ratio),
    "prime_factors": [2, 2, 41, 2017],
    "existing_candidate": {"denom": 2*36*98*44, "error_pct": abs(2*36*98*44 - round(ratio)) / round(ratio) * 100},
    "best_2factor": best[:5] if best else [],
}
os.makedirs(os.path.join(os.path.dirname(__file__), "..", "data"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "..", "data", "02_ratio_decomposition.json"), "w") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

print(f"\n{'='*80}")
print("Analysis complete. Results saved.")
print("=" * 80)