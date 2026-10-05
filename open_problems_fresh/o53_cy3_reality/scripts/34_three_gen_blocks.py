#!/usr/bin/env python3
"""
O53 開放 3 深化: 3×3 三代塊本徵值 + e^(-V) 閉合
==================================================
發現:
  - Y 有 3×12 塊結構 (對角主導 12.05 vs 4.65)
  - SM 質量 φ 指數: t/b=7.73, t/c=10.2, t/τ=9.5
  - e^(-V) 模型: top 需要 V ≈ 38.8

深化:
  1. 3×12 塊嘅 3×3 有效矩陣本徵值 (3 代!)
  2. e^(-V) 壓抑模型閉合: V 有冇結構?
  3. φ 指數 (SM) 有冇 IDCM 結構?
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
print("O53 開放 3: 三代塊 + e^(-V)")
print("=" * 70)

with open(os.path.join(BASE, "kappa_36d_raw.json")) as f:
    kappa = json.load(f)
with open(os.path.join(BASE, "Jstar_36D.json")) as f:
    jstar = json.load(f)

K = np.zeros(tuple(kappa['shape']))
for key, val in kappa['kappa'].items():
    i, j, k = map(int, key.split(','))
    K[i, j, k] = val
    K[i, k, j] = val
    K[j, i, k] = val
    K[j, k, i] = val
    K[k, i, j] = val
    K[k, j, i] = val

J0 = np.array(jstar['Jstar_36D'])
Y = np.einsum('ijk,k->ij', K, J0)
Y = (Y + Y.T) / 2

# --- [1] 3×12 塊有效 3×3 矩陣 ---
print("\n[1] 3×12 塊 (每塊 12×12):")
Yeff = np.zeros((3, 3))
for bi in range(3):
    for bj in range(3):
        block = Y[bi*12:(bi+1)*12, bj*12:(bj+1)*12]
        Yeff[bi, bj] = np.linalg.svd(block, compute_uv=False)[0]  # 主奇異值
print(f"    有效 3×3 (主奇異值):")
print(f"      {Yeff[0,0]:.4f} {Yeff[0,1]:.4f} {Yeff[0,2]:.4f}")
print(f"      {Yeff[1,0]:.4f} {Yeff[1,1]:.4f} {Yeff[1,2]:.4f}")
print(f"      {Yeff[2,0]:.4f} {Yeff[2,1]:.4f} {Yeff[2,2]:.4f}")
ev_eff = np.linalg.eigvalsh(Yeff)
print(f"    本徵值: {np.array2string(np.sort(ev_eff)[::-1], precision=4)}")
print(f"    三代比: {ev_eff[0]/ev_eff[2]:.2f} (SM t/e 需要 ~3e5)")

# --- [2] 每塊嘅完整譜 ---
print("\n[2] 每塊 12×12 譜:")
for g in range(3):
    block = Y[g*12:(g+1)*12, g*12:(g+1)*12]
    evb = np.linalg.eigvalsh(block)
    evb_nz = np.sort(np.abs(evb))[::-1][:5]
    print(f"    Block {g} 前 5 |λ|: {np.array2string(evb_nz, precision=4)}")

# --- [3] e^(-V) 閉合 ---
print("\n[3] e^(-V) 壓抑模型:")
M_Pl = 1.22e19  # GeV
masses_GeV = {'t': 172.69, 'b': 4.18, 'c': 1.27, 'tau': 1.777, 's': 0.093,
              'mu': 0.10566, 'd': 0.0047, 'u': 0.0022, 'e': 0.000511}
print(f"    m = M_Pl × e^(-V) → V = ln(M_Pl/m):")
for k, m in masses_GeV.items():
    V = math.log(M_Pl / m)
    print(f"      {k:4s}: V = {V:7.3f}   (44−V = {44-V:+7.3f}, 22−V = {22-V:+7.3f})")

# 找結構: V 有冇接近整數/半整數?
print(f"\n    V 值與 44 嘅差:")
vs = {k: math.log(M_Pl/m) for k, m in masses_GeV.items()}
diffs = {k: 44 - v for k, v in vs.items()}
for k, d in diffs.items():
    print(f"      {k:4s}: 44−V = {d:7.3f}")

# --- [4] V 同 γ 譜? ---
print("\n[4] V 同 K_Chain γ 譜:")
# γ_n = 4sin²(nπ/88) — 睇有冇 γ 值 ≈ V_top = 38.8
import numpy as np
gammas = [4*math.sin(math.pi*n/88)**2 for n in range(1, 45)]
print(f"    γ 範圍: [{min(gammas):.3f}, {max(gammas):.3f}]")
print(f"    V_top = 38.8 喺 γ 範圍? {'✅' if min(gammas) < 38.8 < max(gammas) else '❌'}")
# 最接近 V 嘅 γ
for name, V in vs.items():
    dif = [(abs(g - V), g) for g in gammas]
    dif.sort()
    print(f"    {name}: V={V:.2f}, 最接近 γ = {dif[0][1]:.3f} (差 {dif[0][0]:.3f})")

# --- [5] 三代分塊嘅 φ 結構 ---
print("\n[5] 三代塊 φ 結構:")
for g in range(3):
    block = Y[g*12:(g+1)*12, g*12:(g+1)*12]
    evb = np.linalg.eigvalsh(block)
    l1b = max(np.abs(evb))
    if l1b > 0:
        exp = math.log(1/l1b)/math.log(phi)
        print(f"    Block {g} 主 λ = {l1b:.4f}, 1/λ = φ^({exp:+.3f})")

print("\n" + "=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 70)
sys.exit(0 if FAIL == 0 else 1)
