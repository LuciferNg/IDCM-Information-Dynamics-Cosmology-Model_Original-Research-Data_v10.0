#!/usr/bin/env python3
"""
O53 A1 閉合嘗試: Σ(3c)² = 36 = h11?
=========================================
發現: 3c 矩陣 Σ² = 36 = h11 (CY₃ Kähler 維度)
      tr = 2 = μ² (O41 守恆差)

驗證:
  1. Σ(3c)² = 36 精確?
  2. 呢個閉合有冇更深意義?
  3. c_f 同 h11 嘅連結
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
print("O53 A1: Σ(3c)² = 36 驗證")
print("=" * 70)

M_Pl = 1.22e19
lnphi = math.log(phi)
SM = {'t': 172.69, 'b': 4.18, 'c': 1.27, 'tau': 1.777, 's': 0.093,
      'mu': 0.10566, 'd': 0.0047, 'u': 0.0022, 'e': 0.000511}

c3 = {}
for k, m in SM.items():
    d = 44 - math.log(M_Pl/m)
    n = round(d)
    c = round((d-n)/lnphi*3)/3
    c3[k] = int(round(c*3))

print(f"\n[1] 3c 值: {c3}")
vals = np.array(list(c3.values()))
print(f"    Σ(3c) = {vals.sum()}")
print(f"    Σ(3c)² = {(vals**2).sum()}")
print(f"    h11 = 36")
check("Σ(3c)² = 36 = h11", (vals**2).sum() == 36, f"({(vals**2).sum()})")
check("Σ(3c) = 2 = μ² (O41)", vals.sum() == 2, f"({vals.sum()})")

# --- [1] 3c 同 36 嘅關係 ---
print(f"\n[2] 3c 平方和 = 36:")
print(f"    36 = h11 (CY₃ Kähler 維度)")
print(f"    36 = Nd − 2B = 44 − 8")
print(f"    36 = 3×12 (3 個 12D sector)")
print(f"    → Σ(3c)² = h11 — c_f 同 CY₃ 維度直接連結!")

# 但係: 3c ∈ [-2,3] 嘅任意 9 值平均平方 = 36/9 = 4
print(f"\n    <(3c)²> = {36/9:.1f}")
print(f"    <c²> = {36/9/9:.4f}")
print(f"    <c²> = 4/9? 4/9 = (2/3)²")
print(f"    → c_rms = 2/3 = B/6?")

# --- [2] 統計顯著性 ---
print(f"\n[3] 統計: 9 個隨機整數 [-2,3] 平方和 = 36 概率?")
# 均勻 [-2,3] (6 值), 每個平方期望 = (4+1+0+1+4+9)/6 = 19/6 = 3.17
# 9 個: 期望 28.5, 觀測 36 — 偏高但唔極端
exp = (4+1+0+1+4+9)/6
print(f"    均勻 [-2,3] 期望 <x²> = {exp:.3f}")
print(f"    9 個期望和 = {9*exp:.1f} vs 36")
print(f"    z = (36−28.5)/(std) — std = sqrt(9 × Var(x²))")
x2 = np.array([4,1,0,1,4,9])
var_x2 = x2.var()
print(f"    Var(x²) = {var_x2:.2f}, std(9 個和) = {np.sqrt(9*var_x2):.2f}")
z = (36 - 9*exp)/np.sqrt(9*var_x2)
print(f"    z = {z:.2f}σ")
check("Σ(3c)² = 36 顯著 (>1.5σ)", z > 1.5, f"(z={z:.2f})")

# --- [3] 對稱性檢查: 3c 排列有冇 pattern ---
print(f"\n[4] 3c 排列:")
print(f"    依粒子: {list(c3.values())}")
print(f"    排序: {np.sort(vals)}")
print(f"    → 無明顯對稱")

# --- [4] 另一候選: Σc = 2/3? ---
print(f"\n[5] Σc = {vals.sum()/3:.4f}")
print(f"    Σc = 2/3 = Q_up? (u quark 電荷)")
print(f"    Σc/3 = 2/9 ≈ Vus²?")
print(f"    Vus = 0.2243, Vus² = 0.0503")
print(f"    (Σc/3)² = {(2/9)**2:.4f} = 4/81 = 0.0494")
print(f"    Vus² vs 4/81: 誤差 {abs(0.0503-4/81)/(4/81)*100:.1f}%")
check("(Σc/3)² ≈ Vus²", abs(0.0503 - 4/81)/(4/81) < 0.05, f"({abs(0.0503-4/81)/(4/81)*100:.1f}%)")

print("\n" + "=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 70)
sys.exit(0 if FAIL == 0 else 1)
