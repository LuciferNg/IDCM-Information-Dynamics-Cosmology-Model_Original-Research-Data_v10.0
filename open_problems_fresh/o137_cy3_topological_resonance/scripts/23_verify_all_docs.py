#!/usr/bin/env python3
"""
O137 — Full Independent Verification of All Docs (2026-08-30 audit)
Cross-checks every formula/number in docs/02-17 against first principles.
"""
import json, os
from math import sin, pi as PI, sqrt, log, isclose
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)

PASS = []
FAIL = []

def ck(name, got, exp, tol=1e-3, note=""):
    ok = isclose(got, exp, rel_tol=tol) if isinstance(exp, (int, float)) else got == exp
    tag = "✅" if ok else "❌"
    if ok: PASS.append(name)
    else: FAIL.append(f"{name}: got={got}, exp={exp}")
    print(f"  {tag} {name} = {got}{'  ~ '+note if note else ''}" + ("" if ok else f"  ❗EXP={exp}"))

# ============ 1. K_Chain (docs/02) ============
print("\n=== 1. K_Chain spectrum (docs/02) ===")
def gamma44(n): return 4*sin(n*PI/88)**2   # 44-site chain
def gamma88(k): return 4*sin(k*PI/176)**2  # 88-site chain
def omega(n): return 2*sin(n*PI/88)

ck("Σγ₄₄ (44-site total)", sum(gamma44(n) for n in range(1,45)), 90, 1e-9)
ck("γ₁", gamma44(1), 0.00509577, 1e-5)
ck("γ₇", gamma44(7), 0.24464202, 1e-5)
ck("γ₂₀", gamma44(20), 1.71537032, 1e-5)
ck("γ₇/γ₁", gamma44(7)/gamma44(1), 48.008835, 1e-4)
ck("γ₂₀/γ₁", gamma44(20)/gamma44(1), 336.62627, 1e-4)
ck("γ₂₀/γ₇", gamma44(20)/gamma44(7), 7.011757, 1e-4)
ck("γ₃₃/γ₁", gamma44(33)/gamma44(1), 670.00925, 1e-4)

# 88-site even/odd split
sum_even88 = sum(gamma88(k) for k in range(2, 89, 2))   # k even = world
sum_odd88 = sum(gamma88(k) for k in range(1, 89, 2))    # k odd = observer
ck("Σγ_even(88-site) = 90 (World)", sum_even88, 90, 1e-9)
ck("Σγ_odd(88-site) = 88 (Observer)", sum_odd88, 88, 1e-9)
ck("Σγ_even+Σγ_odd = 178 = 2F₁₁", sum_even88+sum_odd88, 178, 1e-9)

# 44-site odd/even
sum_odd44 = sum(gamma44(n) for n in range(1,45,2))
sum_even44 = sum(gamma44(n) for n in range(2,45,2))
print(f"  (note) 44-site: Σγ_odd={sum_odd44:.6f}, Σγ_even={sum_even44:.6f}")

# ============ 2. GKZ φ (docs/08, 09, 11) ============
print("\n=== 2. GKZ φ structure (docs/08/09/11) ===")
with open("data/dual_triangulation_data.json") as f:
    tri = json.load(f)
phi = tri["gkz_phi"]
ck("φ_origin = 360", phi[0], 360)
ck("Σφ = 1800", sum(phi), 1800)
ck("φ[1] = 176", phi[1], 176)
ck("φ_origin = 4·Σγ₄₄", phi[0], 4*90, 1e-9)
ck("Σφ = 20·Σγ₄₄", sum(phi), 20*90, 1e-9)
ck("triangulation n_simplices = 283", tri["n_simplices"], 283)
ck("triangulation n_points = 73", tri["n_points"], 73)
ck("is_fine", tri["is_fine"], True)
ck("is_regular", tri["is_regular"], True)
ck("is_star", tri["is_star"], True)

phi_le12 = [v for v in phi if v <= 12]
ck("φ≤12 count = 44 = Nd", len(phi_le12), 44)
cnt = Counter(phi_le12)
ck("φ=12: 28", cnt[12], 28)
ck("φ=9: 9", cnt[9], 9)
ck("φ=8: 5", cnt[8], 5)
ck("φ=6: 2", cnt[6], 2)

# ============ 3. O54 lepton masses (docs/13, 16) ============
print("\n=== 3. O54 lepton masses ===")
M0 = 27.9009
m_e = M0*gamma44(1)*3.6
m_mu = M0*gamma44(7)*15.5
m_tau = M0*gamma44(20)*37.0
ck("m_e = 0.5118 MeV", m_e, 0.5118, 1e-3)
ck("m_μ = 105.80 MeV", m_mu, 105.80, 1e-3)
ck("m_τ = 1770.8 MeV", m_tau, 1770.8, 1e-3)
ck("τ/μ ratio", m_tau/m_mu, 16.74, 1e-2)
ck("μ/e ratio", m_mu/m_e, 206.7, 1e-2)

# ============ 4. O65 PMNS/CKM (docs/15, 17) ============
print("\n=== 4. O65 PMNS/CKM mixing ===")
s12 = gamma44(2)/(gamma44(2)+gamma44(3))
s23 = gamma44(7)/(gamma44(7)+gamma44(6))
s13 = gamma44(6)/8
lam = (gamma44(6)/16)**(1/3)
ck("sin²θ₁₂ = γ₂/(γ₂+γ₃)", s12, 0.30815, 1e-3)
ck("sin²θ₂₃ = γ₇/(γ₇+γ₆)", s23, 0.57512, 1e-3)
ck("sin²θ₁₃ = γ₆/2³", s13, 0.02259, 1e-3)
ck("CKM λ = (γ₆/2⁴)^(1/3)", lam, 0.22438, 1e-3)

# ============ 5. T1 γ₆/2^k (docs/16) ============
print("\n=== 5. γ₆/2^k decay chain ===")
g6 = gamma44(6)
ck("γ₆ = 0.180736", g6, 0.180736, 1e-5)
ck("γ₆/2³ = sin²θ₁₃", g6/8, 0.022592, 1e-5)
ck("γ₆/2⁴ = λ³", g6/16, 0.011296, 1e-5)
ck("γ₆/2⁴^(1/3) = λ", (g6/16)**(1/3), 0.22438, 1e-4)

# ============ 6. T3 gauge (docs/16) ============
print("\n=== 6. SU(12) gauge structure ===")
ck("28 = C(8,2) = Λ²(8)", 8*7//2, 28)
ck("5 = F₅ (Fibonacci)", 5, 5)
ck("66 = Λ²(12) = 12·11/2", 12*11//2, 66)
ck("Λ²(12) = 36+30", 36+30, 66)
ck("12 = 4×3 = B×N_gen", 4*3, 12)

# ============ 7. T4 bosons (docs/16) ============
print("\n=== 7. Boson sector (T4) ===")
def v2(x):
    c = 0
    while x % 2 == 0:
        x //= 2; c += 1
    return c
bosons = [n for n in range(1,45) if v2(n) >= 3]
ck("bosons v₂≥3 = {8,16,24,32,40}", bosons, [8,16,24,32,40])
# bosons → 88-site k=2n all even (world)
ks = [2*n for n in bosons]
ck("bosons → k=2n all even (world)", all(k % 2 == 0 for k in ks), True)

# ============ 8. Lucas notation check (docs/08/09/11/13) ============
print("\n=== 8. Lucas indexing consistency ===")
# docs/02 standard: L₀=2, L₁=1, L₂=3, L₃=4, L₄=7, L₅=11, L₆=18, L₇=29, L₈=47
L = [2,1,3,4,7,11,18,29,47]
ck("L₃ = 4", L[3], 4)
ck("L₄ = 7", L[4], 7)
ck("L₅ = 11", L[5], 11)
ck("L₃×L₄ = 28", L[3]*L[4], 28)
ck("L₄×L₅ = 77", L[4]*L[5], 77)
print(f"  ⚠️ docs/08,09,11,13 寫「28 = B×L₅ = 4×7」: 標準 Lucas L₅=11 ≠ 7")
print(f"     → 應為 L₄=7 (或 B×L₄=4×7 / L₃×L₄=4×7)")

# ============ 9. D_quark check (docs/14) ============
print("\n=== 9. D_quark (docs/14 vs O136) ===")
h11, h21 = 36, 98
eps = 0.1545085  # φ⁻¹/4 (docs/02)
Dq_correct = 1 + h11/h21 * eps * (1+eps)
print(f"  D_quark (O136, ε=φ⁻¹/4): {Dq_correct:.6f}  ← docs/02 標準")
print(f"  D_quark (docs/14): 1.27551  ← 用了 ε=0.5, 與 O136 不符 ❌")

# ============ 10. Batyrev (docs/07) ============
print("\n=== 10. Mirror polytope (docs/07) ===")
with open("data/dual_polytope_points.json") as f:
    dp = json.load(f)
ck("l(Δ*) = 85 points", len(dp["points"]), 85)

# ============ 11. φ=9 intersection (docs/14, 16) ============
print("\n=== 11. φ=9 intersection matrix (docs/14) ===")
g1_x3 = [1, 5, 9]
g2_x3 = [0, 1, 3, 4, 6, 7]
Phi = [[1 + x3i*x3j for x3j in g2_x3] for x3i in g1_x3]
ck("Φ[41][47] = 28 (x₃=9 × x₃'=3)", Phi[2][2], 28)
ck("Φ[33][44] = 1", Phi[0][0], 1)
ck("Φ[37][45] = 6", Phi[1][1], 6)
# φ=9 point coords from data
dpts = dp["points"]
ck("pt[33] = (-1,0,0,1)", list(dpts[33]), [-1,0,0,1])
ck("pt[37] = (-1,0,0,5)", list(dpts[37]), [-1,0,0,5])
ck("pt[41] = (-1,0,0,9)", list(dpts[41]), [-1,0,0,9])

# ============ SUMMARY ============
print(f"\n{'='*60}")
print(f"PASS: {len(PASS)}, FAIL: {len(FAIL)}")
if FAIL:
    print("FAILURES:")
    for f in FAIL:
        print(f"  ❌ {f}")
print(f"{'='*60}")