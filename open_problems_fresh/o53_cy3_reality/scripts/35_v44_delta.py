#!/usr/bin/env python3
"""
O53 開放 3 閉合: V = 44 + δ 嘅結構分析
==========================================
發現: SM 質量對應 V ∈ [38.8, 51.5], 中心 ≈ 44 = Nd

分析:
  1. 44−V 有冇精確結構 (整數/半整數/φ)?
  2. δ = 44−V: t=+5.2, b=+1.5, c=+0.3, τ=+0.6, s=-2.3, μ=-2.2, d=-5.3, u=-6.1, e=-7.5
  3. δ 同 K_Chain 結構 (γ_n, mode 數) 有冇對應?
  4. 三代分組: δ 嘅三代結構?
"""
import os, json, math, sys
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2
PASS = 0
FAIL = 0

def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name} {detail}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")

print("=" * 70)
print("O53 開放 3: V = 44 + δ 結構")
print("=" * 70)

M_Pl = 1.22e19  # GeV
SM = {'t': 172.69, 'b': 4.18, 'c': 1.27, 'tau': 1.777, 's': 0.093,
      'mu': 0.10566, 'd': 0.0047, 'u': 0.0022, 'e': 0.000511}
Vs = {k: math.log(M_Pl/m) for k, m in SM.items()}

print("\n[1] 44−V (δ) 結構:")
delta = {k: 44 - v for k, v in Vs.items()}
for k, d in delta.items():
    # 最近整數
    n = round(d)
    print(f"    {k:4s}: δ = {d:+7.3f}  最近整數 {n:+3d} (差 {abs(d-n):.3f})  φ^? {d/math.log(phi):+6.2f}")

# 有冇 δ ≈ 整數?
print(f"\n    δ 最近整數誤差:")
for k, d in delta.items():
    n = round(d)
    print(f"      {k}: |δ−{n}| = {abs(d-n):.3f}")
near_int = [k for k, d in delta.items() if abs(d - round(d)) < 0.35]
print(f"    近整數: {near_int}")

# --- [2] δ 同 γ 譜 ---
print("\n[2] δ vs K_Chain γ:")
# γ_n = 4sin²(nπ/88) 前幾個: 0.005, 0.02, 0.046, 0.08, 0.13, 0.18, 0.24, 0.31, 0.38, 0.46...
gammas = [4*math.sin(math.pi*n/88)**2 for n in range(1, 45)]
# δ 值: 5.2, 1.5, 0.3, 0.6, -2.3, -2.2, -5.3, -6.1, -7.5
# γ 冇負 → δ 唔係 γ 直接
print(f"    γ 全部正 [0.005, 4.0], δ 有負 → 唔係 γ 直接")
# δ 絕對值?
print(f"    |δ|: " + "  ".join(f"{abs(delta[k]):.2f}" for k in SM))
print(f"    |δ| 排序: {sorted([abs(delta[k]) for k in SM])}")
# 有冇對應 mode?
print(f"    γ_n 值: {[round(g,2) for g in gammas[:20]]}")

# --- [3] 三代 δ 分組 ---
print("\n[3] 三代 δ:")
# 3 代: (t,c,u) (b,s,d) (τ,μ,e)? 或 (t,b,τ) (c,s,μ) (u,d,e)
gen_sets = [
    ("(t,c,u) 上型", ['t', 'c', 'u']),
    ("(b,s,d) 下型", ['b', 's', 'd']),
    ("(τ,μ,e) 輕子", ['tau', 'mu', 'e']),
]
for name, members in gen_sets:
    ds = [delta[m] for m in members]
    print(f"    {name}: δ = {[f'{d:+.2f}' for d in ds]}")

# (t,b,τ) (c,s,μ) (u,d,e) 代間
print(f"\n    代間分組 (t,b,τ / c,s,μ / u,d,e):")
gen_sets2 = [
    ("Gen1 (t,b,τ)", ['t', 'b', 'tau']),
    ("Gen2 (c,s,μ)", ['c', 's', 'mu']),
    ("Gen3 (u,d,e)", ['u', 'd', 'e']),
]
for name, members in gen_sets2:
    ds = [delta[m] for m in members]
    print(f"    {name}: δ = {[f'{d:+.2f}' for d in ds]}  mean={np.mean(ds):+.2f}")

# --- [4] δ 同 Lucas/Fibonacci ---
print("\n[4] δ 候選結構:")
print(f"    δ_t = +5.20 ≈ 5 = F₅?")
print(f"    δ_b = +1.48 ≈ 1.5 = 3/2?")
print(f"    δ_c = +0.29 ≈ 0.3?")
print(f"    δ_τ = +0.63 ≈ 0.6?")
print(f"    δ_s = -2.32 ≈ -2.3?")
print(f"    δ_d = -5.31 ≈ -5.3?")
print(f"    δ_u = -6.07 ≈ -6.1?")
print(f"    δ_e = -7.53 ≈ -7.5?")
print(f"    → 候選: 5, 1.5, 0.3, 0.6, -2.3, -2.2, -5.3, -6.1, -7.5")
print(f"    → 5 同 -5.3 成對! 1.5 同 ? 0.6 同 -2.3?")

# --- [5] e^(-44) 基準 ---
print("\n[5] e^(-44) 基準:")
m44 = M_Pl * math.exp(-44)
print(f"    M_Pl × e^(-44) = {m44:.4f} GeV")
print(f"    m_t/m_44 = {SM['t']/m44:.2f}")
print(f"    m_e/m_44 = {SM['e']/m44:.4f}")
print(f"    → e^(-44) 基準介乎 t 同 e 之間 (中間質量)")
print(f"    → 44 = Nd 係中心! δ = 44−V = ln(m/m_44)")

# δ = ln(m/m_44)
print(f"\n    δ = ln(m/m_44):")
for k, m in SM.items():
    print(f"      {k:4s}: δ = {math.log(m/m44):+7.3f}")

print("\n" + "=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 70)
sys.exit(0 if FAIL == 0 else 1)
