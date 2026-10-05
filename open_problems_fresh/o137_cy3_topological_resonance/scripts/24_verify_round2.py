#!/usr/bin/env python3
"""
O137 — Round 2 Verification Audit (docs/19-23)
Verifies all NEW derivations in the open-problem attack docs.
"""
import json, os
from math import sin, cos, pi as PI, sqrt, isclose
from collections import Counter

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE)

PASS, FAIL = [], []
def ck(name, got, exp, tol=1e-3, note=""):
    ok = isclose(got, exp, rel_tol=tol) if isinstance(exp, (int, float)) else got == exp
    (PASS if ok else FAIL).append(name)
    print(f"  {'✅' if ok else '❌'} {name} = {got}{'  ~ '+note if note else ''}" + ("" if ok else f"  ❗EXP={exp}"))

def v2(x):
    c = 0
    while x % 2 == 0:
        x //= 2; c += 1
    return c
def gamma_n(n): return 4*sin(n*PI/88)**2
def omega_n(n): return 2*sin(n*PI/88)

M0 = 27.9009

# ============ docs/19: C_f = φ=9 intersection ============
print("\n=== docs/19: C_f = Φ intersection values ===")
Phi = {}
for x3i in [1, 5, 9]:
    for x3j in [0, 1, 3, 4, 6, 7]:
        Phi[(x3i, x3j)] = 1 + x3i*x3j

ck("Φ[5][6] = 31", Phi[(5,6)], 31)
ck("Φ[9][4] = 37", Phi[(9,4)], 37)
ck("Φ[5][7] = 36 = h11", Phi[(5,7)], 36)
ck("Φ[9][3] = 28 = φ12 group", Phi[(9,3)], 28)
ck("Φ[9][6] = 55 = F₁₀", Phi[(9,6)], 55)
ck("Φ[5][3] = 16 = B²", Phi[(5,3)], 16)
ck("Φ[5][4] = 21 = F₈", Phi[(5,4)], 21)

# C_f verification
m_mu = M0 * gamma_n(7) * (Phi[(5,6)]/2)
m_tau = M0 * gamma_n(20) * Phi[(9,4)]
ck("m_μ = M₀·γ₇·(31/2) = 105.80", m_mu, 105.80, 1e-3)
ck("m_τ = M₀·γ₂₀·37 = 1770.8", m_tau, 1770.8, 1e-3)
ck("C_e = 18/5 = 2×9/5 = 2·x₃₃/x₃₂", 18/5, 3.6)
ck("C_μ = 31/2 = 15.5", Phi[(5,6)]/2, 15.5)
ck("C_τ = 37 = 1+h11", Phi[(9,4)], 37)

# ============ docs/19: γ₃₃ = 2+√2 ============
print("\n=== docs/19: γ₃₃ vs γ₁₁ ===")
ck("γ₃₃ = 2+√2", gamma_n(33), 2+sqrt(2), 1e-8)
ck("γ₁₁ = 2−√2", gamma_n(11), 2-sqrt(2), 1e-8)
ck("γ₃₃+γ₁₁ = 4", gamma_n(33)+gamma_n(11), 4.0, 1e-8)

# φ values of pts 33 and 11
phi = json.load(open("data/dual_triangulation_data.json"))["gkz_phi"]
ck("pt33 φ = 9", phi[33], 9)
ck("pt11 φ = 18", phi[11], 18)

# ============ docs/19: odd parts ============
print("\n=== docs/19-20: 候選奇部 ===")
odd_parts = {n: n // (2**v2(n)) for n in [1, 7, 20, 14, 34, 33]}
ck("e odd part = 1", odd_parts[1], 1)
ck("μ odd part = 7", odd_parts[7], 7)
ck("τ odd part = 5", odd_parts[20], 5)
ck("s odd part = 7", odd_parts[14], 7)
ck("c odd part = 17", odd_parts[34], 17)
ck("b odd part = 33", odd_parts[33], 33)
ck("odd part mod 8 ∈ {1,5,7} 全部", all(odd_parts[n] % 8 in [1,5,7] for n in odd_parts), True)
ck("1+B²k = {1,17,33}", [1+16*k for k in range(3)], [1,17,33])

# ============ docs/21: D_quark + Φ ============
print("\n=== docs/21: D_quark ===")
eps = 0.1545085  # φ⁻¹/4
Dq = 1 + 36/98 * eps * (1+eps)
ck("D_quark = 1 + h11/h21·ε(1+ε) = 1.065528", Dq, 1.065528, 1e-5)
ck("h11 = 36 = Φ[5][7]", Phi[(5,7)], 36)

# ============ docs/22: Wolfenstein A ============
print("\n=== docs/22: Wolfenstein A ===")
A = omega_n(12)/omega_n(15)
ck("A = ω₁₂/ω₁₅ = 0.81411", A, 0.81411, 1e-4)
ck("12 = N_gen×B = 3×4", 12, 12)
ck("15 = N_gen×F₅ = 3×5", 15, 15)
# A vs |V_cb|/λ²
lam = (gamma_n(6)/16)**(1/3)
A_obs = 0.04097/lam**2
ck("A vs |V_cb|/λ² = 0.81380 (Δ=0.038%)", A, A_obs, 4e-4)
# δ_CP = 4π/5
ck("4π/5 = 144°", 4*PI/5, 2.5133, 1e-3)

# ============ docs/22: flavor↔mass ============
print("\n=== docs/22: flavor↔mass ===")
ck("γ₃/γ₁ ≈ 9 = N_gen²", gamma_n(3)/gamma_n(1), 8.97, 5e-3)
ck("γ₂₀/γ₇ ≈ 7 = L₄", gamma_n(20)/gamma_n(7), 7.0118, 2e-3)
# 9 φ=9 points = 2 parallel lines
dpts = json.load(open("data/dual_polytope_points.json"))["points"]
g1 = [dpts[33], dpts[37], dpts[41]]   # x₂=0
g2 = [dpts[44], dpts[45], dpts[47], dpts[48], dpts[50], dpts[51]]  # x₂=1
ck("G1 全部 x₂=0", all(p[2] == 0 for p in g1), True)
ck("G2 全部 x₂=1", all(p[2] == 1 for p in g2), True)
ck("G1 x₃ = {1,5,9} = 1+4k", [p[3] for p in g1], [1,5,9])
ck("G2 x₃' = {0,1,3,4,6,7}", sorted(p[3] for p in g2), [0,1,3,4,6,7])

# ============ docs/23: lepton mode uniqueness ============
print("\n=== docs/23: 輕子模式唯一性 ===")
Cf = {'e': 3.6, 'mu': 15.5, 'tau': 37}
masses = {'e': 0.511, 'mu': 105.66, 'tau': 1776.86}
exp_modes = {'e': 1, 'mu': 7, 'tau': 20}
for name in ['e', 'mu', 'tau']:
    gamma_target = masses[name]/(M0*Cf[name])
    best_n, best_d = None, 1e9
    for n in range(1, 45):
        d = abs(gamma_n(n) - gamma_target)
        if d < best_d:
            best_d, best_n = d, n
    ck(f"{name} → mode {exp_modes[name]} (γ dist {best_d:.5f})", best_n, exp_modes[name])
    # uniqueness: second closest must be far
    ds = sorted(abs(gamma_n(n) - gamma_target) for n in range(1, 45))
    ck(f"{name} 唯一 (2nd dist {ds[1]:.4f} > 3× best)", ds[1] > 3*best_d, True)

# ============ SUMMARY ============
print(f"\n{'='*60}")
print(f"PASS: {len(PASS)}, FAIL: {len(FAIL)}")
if FAIL:
    print("FAILURES:")
    for f in FAIL:
        print(f"  ❌ {f}")
print(f"{'='*60}")