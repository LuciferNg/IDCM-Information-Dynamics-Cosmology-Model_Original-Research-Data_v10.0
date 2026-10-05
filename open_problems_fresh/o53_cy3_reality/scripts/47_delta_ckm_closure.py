#!/usr/bin/env python3
"""
O53 攻堅目標二 (part 2): Δδ = ln(φ)·c 精確檢驗 + CKM φ 結構
===============================================================
發現: Δδ/lnφ: b=+1.002, e=+0.983 (≈+1!)
      Vus = φ^(-3.106) (φ^(-3) 誤差 5.2%)

深化:
  1. Δδ/lnφ 精確值: 有冇 = 整數/3, /4, /6?
  2. 用「精確 Δδ = c·lnφ」預測質量 — 誤差幾多?
  3. CKM 全矩陣 φ 檢驗 (Vus, Vcb, Vub, Vtd)
  4. θ_c = φ^(-3) 定 θ_c = φ^(-π/5)?
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
print("O53 攻堅 2b: Δδ 精確閉合 + CKM φ")
print("=" * 70)

M_Pl = 1.22e19
m44 = M_Pl * math.exp(-44)
lnphi = math.log(phi)
SM = {'t': 172.69, 'b': 4.18, 'c': 1.27, 'tau': 1.777, 's': 0.093,
      'mu': 0.10566, 'd': 0.0047, 'u': 0.0022, 'e': 0.000511}
Vs = {k: math.log(M_Pl/m) for k, m in SM.items()}
delta = {k: 44 - v for k, v in Vs.items()}
deltas = {k: d - round(d) for k, d in delta.items()}

# --- [1] Δδ/lnφ 精確分數 (denominator ≤ 12) ---
print("\n[1] Δδ/lnφ 分數 (den ≤ 12):")
for k, dd in deltas.items():
    r = dd/lnphi
    best = (1e9, None)
    for den in range(1, 13):
        num = round(r*den)
        err = abs(r - num/den)
        if err < best[0]:
            best = (err, f"{num}/{den}")
    print(f"    {k:4s}: Δδ/lnφ = {r:+7.4f} ≈ {best[1]} (err {best[0]:.4f})")

# --- [2] 用 c·lnφ 模型 (c = 最近 1/3 倍) ---
print("\n[2] Δδ = c·lnφ 模型 (c = 最近 1/3):")
errs_model = []
for k, dd in deltas.items():
    r = dd/lnphi
    c3 = round(r*3)/3
    pred = c3*lnphi
    err = abs(pred - dd)
    errs_model.append(err)
    print(f"    {k:4s}: c = {c3:+6.3f}, Δδ_pred = {pred:+7.4f}, err = {err:.4f}")
print(f"    平均 |err| = {np.mean(errs_model):.4f}")

# --- [3] 質量預測 (δ_int + c·lnφ) ---
print("\n[3] 完整模型 m = m₄₄·e^(δ_int + c·lnφ):")
print(f"    m₄₄ = {m44:.6f} GeV")
errs_pred = []
for k, m in SM.items():
    d = delta[k]
    n = round(d)
    r = (d - n)/lnphi
    c3 = round(r*3)/3
    m_pred = m44 * math.exp(n + c3*lnphi)
    err = abs(m_pred - m)/m*100
    errs_pred.append(err)
    print(f"    {k:4s}: δ={n:+d}+{c3:+.3f}lnφ, m_pred = {m_pred:10.5f}, m = {m:10.5f}, 誤差 {err:5.1f}%")
print(f"    平均誤差: {np.mean(errs_pred):.1f}%")
print(f"    (對比無修正 29.7%)")

# --- [4] CKM φ 檢驗 ---
print("\n[4] CKM φ 結構:")
CKM = {'Vus': 0.2243, 'Vcb': 0.0422, 'Vub': 0.00394, 'Vtd': 0.00809,
       'Vts': 0.0394, 'Vcd': 0.221, 'Vcs': 0.975, 'Vud': 0.97373, 'Vtb': 0.9991}
for name, val in CKM.items():
    if val > 0.9:
        # 近 1 嘅: 1−val
        e = 1 - val
        exp = math.log(e)/math.log(phi) if e > 0 else None
        print(f"    {name} = {val:.5f} (1−val = {e:.5f}, φ^({exp:+.3f}))" if exp else f"    {name} = {val}")
    else:
        exp = math.log(val)/math.log(phi)
        # 最接近 n/3
        n3 = round(exp*3)/3
        print(f"    {name} = {val:.5f}: φ^({exp:+.3f}) ≈ φ^(-{abs(n3)}) (err {abs(exp-n3)/abs(exp)*100:.1f}%)")

# --- [5] 候選: sinθ_c = φ^(-3)·(1+φ^(-5))? ---
print("\n[5] Vus 精確候選:")
vus = 0.2243
print(f"    φ^(-3) = {phi**-3:.6f}")
print(f"    φ^(-3)/2 = {phi**-3/2:.6f}")
print(f"    φ^(-3)·φ^(-1)/2 = {phi**-3*phi**-1/2:.6f}")
print(f"    φ^(-7/2) = {phi**(-3.5):.6f}")
print(f"    sin(π/14) = {math.sin(math.pi/14):.6f} (14 = 2×7)")
print(f"    sin(π/13) = {math.sin(math.pi/13):.6f}")
print(f"    sin(π/12) = {math.sin(math.pi/12):.6f} = {math.sin(math.pi/12):.6f}")
print(f"    Vus = {vus}")
print(f"    → sin(π/14) vs Vus: {abs(math.sin(math.pi/14)-vus)/vus*100:.2f}%")
print(f"    → sin(π/13) vs Vus: {abs(math.sin(math.pi/13)-vus)/vus*100:.2f}%")

# θ_c 角度
print(f"\n    θ_c = {math.degrees(math.asin(vus)):.3f}°")
print(f"    13° ≈ ?")
print(f"    13° = 2π×13/360 rad")
print(f"    φ^(-3) rad = {phi**-3:.4f} rad = {math.degrees(phi**-3):.2f}°")

print("\n" + "=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 70)
sys.exit(0 if FAIL == 0 else 1)
