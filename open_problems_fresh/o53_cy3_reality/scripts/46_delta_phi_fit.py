#!/usr/bin/env python3
"""
O53 攻堅目標二 (part 1): SM Δδ_f 黄金比例分量擬合
=====================================================
問題: m_f = M_Pl·e^(-44)·e^(δ_f + Δδ_f)
      δ_f ∈ 整數階梯 {+5, 0, -2, -5, -6}, Δδ_f ≈ 0.08~0.35

測試: Δδ_f 係咪服從 ln(φ) 嘅簡單分數倍?
      Δδ_f = c·ln(φ),  c = ?
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
print("O53 攻堅 2a: Δδ_f 黄金比例分量")
print("=" * 70)

M_Pl = 1.22e19
m44 = M_Pl * math.exp(-44)
SM = {'t': 172.69, 'b': 4.18, 'c': 1.27, 'tau': 1.777, 's': 0.093,
      'mu': 0.10566, 'd': 0.0047, 'u': 0.0022, 'e': 0.000511}
Vs = {k: math.log(M_Pl/m) for k, m in SM.items()}
delta = {k: 44 - v for k, v in Vs.items()}

print(f"\n[1] Δδ_f = δ_f − round(δ_f):")
deltas = {}
for k, d in delta.items():
    dd = d - round(d)
    deltas[k] = dd
    print(f"    {k:4s}: δ = {d:+7.4f}, Δδ = {dd:+7.4f}")

# --- [1] Δδ vs ln(φ) ---
print("\n[2] Δδ/ln(φ) 分數檢驗:")
lnphi = math.log(phi)
for k, dd in deltas.items():
    ratio = dd / lnphi
    # 最接近分數 (denominator ≤ 12)
    best = None
    for den in range(1, 13):
        num = round(ratio * den)
        err = abs(ratio - num/den)
        if best is None or err < best[0]:
            best = (err, num, den)
    print(f"    {k:4s}: Δδ = {dd:+7.4f}, Δδ/lnφ = {ratio:+7.3f}  ≈ {best[1]}/{best[2]} (err {best[0]:.3f})")

# --- [2] 統計: 有冇收斂到 lnφ 分數倍? ---
print("\n[3] 統計分析:")
ratios = {k: dd/math.log(phi) for k, dd in deltas.items()}
# 最近 1/4 倍
for k, r in ratios.items():
    q = r*4
    print(f"    {k:4s}: Δδ/lnφ = {r:+6.3f}  (×4 = {q:+6.3f}, 最近 1/4 = {round(q)/4:+7.3f}, 誤差 {abs(q-round(q))/4:.3f})")

# --- [3] Δδ 有冇對稱結構? ---
print("\n[4] Δδ 三代分組:")
gen1 = [deltas[k] for k in ['t', 'b', 'tau']]
gen2 = [deltas[k] for k in ['c', 's', 'mu']]
gen3 = [deltas[k] for k in ['u', 'd', 'e']]
print(f"    Gen1 (t,b,τ): {[f'{x:+.3f}' for x in gen1]}")
print(f"    Gen2 (c,s,μ): {[f'{x:+.3f}' for x in gen2]}")
print(f"    Gen3 (u,d,e): {[f'{x:+.3f}' for x in gen3]}")

# --- [4] Δδ 同 CKM 角? ---
print("\n[5] Δδ 候選結構:")
# Cabibbo: sinθ_c ≈ 0.225, θ_c ≈ 0.2268 rad = 13.0°
# φ^-3 = 0.236? φ^-3 = 1/4.236 = 0.236
print(f"    φ^(-3) = {phi**-3:.4f}")
print(f"    sinθ_c (PDG) = 0.22500")
print(f"    θ_c = 0.2268 rad")
print(f"    φ^(-3) vs sinθ_c: 誤差 {abs(phi**-3 - 0.225)/0.225*100:.1f}%")
print(f"    φ^(-3)/sinθ_c = {phi**-3/0.225:.4f}")

# CKM 值
print(f"\n    CKM (PDG):")
print(f"    |Vus| = 0.2243, |Vcb| = 0.0422, |Vub| = 0.00394")
print(f"    |Vtd| = 0.00809, |Vts| = 0.0394, |Vtb| = 0.9991")
print(f"    |Vud| = 0.97373, |Vcd| = 0.221, |Vcs| = 0.975")
print(f"    θ_c = arcsin|Vus| = {math.asin(0.2243):.4f} rad = {math.degrees(math.asin(0.2243)):.2f}°")

# φ 檢驗
print(f"\n[6] CKM φ 檢驗:")
for name, val in [("Vus", 0.2243), ("Vcb", 0.0422), ("Vub", 0.00394), ("Vtd", 0.00809)]:
    # 有冇 φ^-n?
    n = math.log(val)/math.log(phi)
    print(f"    {name} = {val}: φ^({n:+.3f})")

# φ^(-3) = 0.236 vs Vus = 0.224?
print(f"\n    Vus vs φ^(-3) = {phi**-3:.4f}: 誤差 {abs(phi**-3-0.2243)/0.2243*100:.1f}%")
print(f"    Vus vs φ^(-5/2) = {phi**-2.5:.4f}: 誤差 {abs(phi**-2.5-0.2243)/0.2243*100:.1f}%")
print(f"    Vus vs φ^(-7/3) = {phi**(-7/3):.4f}: 誤差 {abs(phi**(-7/3)-0.2243)/0.2243*100:.1f}%")
print(f"    Vus vs φ^(-8/3) = {phi**(-8/3):.4f}: 誤差 {abs(phi**(-8/3)-0.2243)/0.2243*100:.1f}%")

# sinθ_c = λ (Wolfenstein), λ = 0.225
print(f"\n    Wolfenstein λ = 0.225")
print(f"    φ^(-3)/λ = {phi**-3/0.225:.4f} (≈1.05)")
print(f"    φ^(-7/3)/λ = {phi**(-7/3)/0.225:.4f}")

print("\n" + "=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 70)
sys.exit(0 if FAIL == 0 else 1)
