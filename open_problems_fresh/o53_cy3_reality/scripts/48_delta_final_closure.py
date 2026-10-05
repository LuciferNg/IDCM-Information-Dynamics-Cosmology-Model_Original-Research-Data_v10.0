#!/usr/bin/env python3
"""
O53 攻堅目標二 (閉合): Δδ = c·lnφ + CKM φ^(-n/3) 最終驗證
==============================================================
發現:
  - Δδ/lnφ: b=+1, e=+1, s=-2/3, d=-2/3, τ=-2/3, c=+2/3, μ=-1/3, t=+1/3, u=0
  - 質量預測誤差 29.7% → 2.8%
  - Vtd = φ^(-10) (0.1%), Vcb = φ^(-20/3) (1.4%)

閉合驗證:
  1. c 分數集結構: {+1, +2/3, +1/3, 0, -1/3, -2/3}
  2. CKM φ^(-n/3) 全檢驗
  3. 完整質量公式 m = m₄₄·φ^(3δ_int/2 + 3c/2)? (lnφ 形式轉換)
"""
import os, json, math, sys
import numpy as np
from collections import Counter

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
print("O53 攻堅 2c: Δδ 閉合鏈")
print("=" * 70)

M_Pl = 1.22e19
m44 = M_Pl * math.exp(-44)
lnphi = math.log(phi)
SM = {'t': 172.69, 'b': 4.18, 'c': 1.27, 'tau': 1.777, 's': 0.093,
      'mu': 0.10566, 'd': 0.0047, 'u': 0.0022, 'e': 0.000511}
Vs = {k: math.log(M_Pl/m) for k, m in SM.items()}
delta = {k: 44 - v for k, v in Vs.items()}

# c 值 (最近 1/3)
cvals = {}
for k, d in delta.items():
    n = round(d)
    r = (d - n)/lnphi
    cvals[k] = round(r*3)/3
print(f"\n[1] c 值 (Δδ/lnφ, 最近 1/3):")
for k, c in cvals.items():
    print(f"    {k:4s}: c = {c:+5.2f}")
cc = Counter(cvals.values())
print(f"    c 分佈: {dict(sorted(cc.items()))}")

# 三代
print(f"\n    Gen1 (t,b,τ): {[cvals[k] for k in ['t','b','tau']]}")
print(f"    Gen2 (c,s,μ): {[cvals[k] for k in ['c','s','mu']]}")
print(f"    Gen3 (u,d,e): {[cvals[k] for k in ['u','d','e']]}")

# --- [1] c 同 charge 結構? ---
print("\n[2] c 同電荷:")
print(f"    Up (Q=+2/3): t=+1/3, c=+2/3, u=0")
print(f"    Down (Q=-1/3): b=+1, s=-2/3, d=-2/3")
print(f"    Lep (Q=-1): τ=-2/3, μ=-1/3, e=+1")
print(f"    → Up 冇共通, Down 唔一致, Lep 唔一致")

# 代間 pattern
print(f"\n    c 依代:")
print(f"    Gen1: t=+1/3, b=+1, τ=-2/3")
print(f"    Gen2: c=+2/3, s=-2/3, μ=-1/3")
print(f"    Gen3: u=0, d=-2/3, e=+1")

# --- [2] 質量預測最終 ---
print("\n[3] 最終模型 m = m₄₄·e^(n + c·lnφ):")
errs = []
for k, m in SM.items():
    n = round(delta[k])
    c = cvals[k]
    m_pred = m44 * math.exp(n + c*lnphi)
    err = abs(m_pred - m)/m*100
    errs.append(err)
    print(f"    {k:4s}: {m_pred:10.5f} vs {m:10.5f} GeV ({err:5.1f}%)")
print(f"    平均誤差: {np.mean(errs):.1f}%")
print(f"    最大誤差: {np.max(errs):.1f}%")
check("平均誤差 < 5%", np.mean(errs) < 5, f"({np.mean(errs):.1f}%)")
check("≤4 粒子 < 2%", np.sum(np.array(errs) < 2) >= 4, f"({np.sum(np.array(errs)<2)})")

# --- [3] CKM 全 φ 檢驗 ---
print("\n[4] CKM φ^(-n/3):")
CKM = {'Vus': 0.2243, 'Vcb': 0.0422, 'Vub': 0.00394, 'Vtd': 0.00809,
       'Vts': 0.0394, 'Vcd': 0.221}
for name, val in CKM.items():
    exp = math.log(val)/math.log(phi)
    n3 = round(exp*3)/3
    err = abs(exp - n3)/abs(exp)*100
    print(f"    {name} = {val:.5f}: φ^({exp:+.3f}) ≈ φ^(-{abs(n3):.3f}) ({err:.1f}%)")

# --- [4] 轉換成 φ 冪形式 ---
print("\n[5] 質量公式 φ 形式:")
print(f"    m = m₄₄·e^(n + c·lnφ) = m₄₄·φ^(c)·e^(n)")
print(f"    e^(n) = φ^(n/lnφ) 唔係 φ 冪")
print(f"    但 m = m₄₄·φ^(c)·e^(n)")
print(f"    → 每粒子: m = m₄₄·φ^(c)·e^(δ_int)")
print(f"    e^(δ_int): δ=+5→148.4, δ=0→1, δ=-2→0.135, δ=-5→0.0067, δ=-6→0.0025")
print(f"    φ^c: c=+1→1.618, c=+2/3→1.383, c=+1/3→1.183, c=0→1, c=-1/3→0.846, c=-2/3→0.723")

# --- [5] 最終閉合鏈 ---
print("\n[6] 攻堅目標二閉合鏈:")
print(f"    m_f = M_Pl·e^(-44)·e^(δ_f + Δδ_f)")
print(f"    δ_f ∈ {{+5, +1, 0, -2, -5, -6, -8}} (整數階梯)")
print(f"    Δδ_f = c_f·ln(φ), c_f ∈ {{+1, +2/3, +1/3, 0, -1/3, -2/3}}")
print(f"    → 質量誤差 29.7% → 2.8%")
print(f"    → CKM: Vtd = φ^(-10) (0.1%), Vcb = φ^(-20/3) (1.4%)")
print(f"    → sin(π/14) ≈ Vus (0.79%)")

print("\n" + "=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 70)
sys.exit(0 if FAIL == 0 else 1)
