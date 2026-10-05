#!/usr/bin/env python3
"""
O53 第一性原理推導: (36,98) 由 K_Chain 結構唯一確定
====================================================
推導鏈:
  x²+x−1=0 → φ → B=4, L₅=11, L₆=18, F₆=8
  Nd = B×L₅ = 44
  Σγ = 90
  h¹¹+h²¹ = Nd+Σγ = 134
  h²¹−h¹¹ = Nd+L₆ = 62
  → h¹¹=36, h²¹=98 (唯一解)
"""
import math
import numpy as np
import os

phi = (1 + math.sqrt(5)) / 2

print("=" * 64)
print("O53 第一性原理: (36,98) 由 K_Chain 結構推導")
print("=" * 64)

# 基本結構
B = phi**3 - phi**-3
L5 = phi**5 + (-phi)**-5
L6 = phi**6 + (-phi)**-6
F6 = 8
Nd = int(round(B * L5))
S_gamma = sum(4 * math.sin(math.pi * n / 88)**2 for n in range(1, 45))

print(f"\n[1] 基本結構 (全部由 x²+x−1=0 → φ 派生)")
print(f"    B  = φ³−φ⁻³ = {B:.6f} → 4 (MERA branching)")
print(f"    L₅ = φ⁵+(−φ)⁻⁵ = {L5:.6f} → 11 (Lucas)")
print(f"    L₆ = φ⁶+(−φ)⁻⁶ = {L6:.6f} → 18 (Lucas)")
print(f"    F₆ = 8 (Fibonacci)")
print(f"    Nd = B×L₅ = {Nd}")
print(f"    Σγ = Σ 4sin²(πn/88) = {S_gamma:.6f} → 90")

print(f"\n[2] 兩個結構約束 (第一性原理)")
print(f"    h¹¹+h²¹ = Nd + Σγ = {Nd} + {round(S_gamma)} = {Nd+round(S_gamma)}")
print(f"    h²¹−h¹¹ = Nd + L₆ = {Nd} + {round(L6)} = {Nd+round(L6)}")
print(f"    (物理詮釋: 總 moduli = 鏈 site + 鏈能量; 半差 = 鏈 site + 觀察者維度)")

print(f"\n[3] 解")
S = Nd + round(S_gamma)
D = Nd + round(L6)
h11 = (S - D) // 2
h21 = (S + D) // 2
print(f"    h¹¹ = (S−D)/2 = ({S}−{D})/2 = {h11}")
print(f"    h²¹ = (S+D)/2 = ({S}+{D})/2 = {h21}")
print(f"    → (h¹¹, h²¹) = ({h11}, {h21})")
print(f"    χ = 2(h¹¹−h²¹) = 2×({h11}−{h21}) = {2*(h11-h21)}")

# 驗證 36/98 各自
assert h11 == 36 and h21 == 98, "推導失敗!"
print(f"\n[4] 交叉驗證")
print(f"    h¹¹ = 36 = Nd−F₆ = 44−8")
print(f"    h²¹ = 98 = Σγ+F₆ = 90+8")
assert Nd - F6 == 36
assert round(S_gamma) + F6 == 98
print(f"    ✅ 全部命中")

# KS 唯一性
print(f"\n[5] KS 景觀唯一性 (30,108 pairs)")
data = os.path.join(os.path.dirname(__file__), '..', 'data', 'alltoric.spec')
pairs = []
with open(data) as f:
    for line in f:
        p = line.split()
        if len(p) >= 3:
            try:
                pairs.append((int(p[0]), int(p[1]), int(p[2])))
            except ValueError:
                pass
arr = np.array(pairs)
mask = (arr[:, 0] + arr[:, 1] == 134) & (arr[:, 1] - arr[:, 0] == 62)
print(f"    KS 中同時滿足兩約束: {np.sum(mask)} 個")
for b in arr[mask]:
    print(f"      ({b[0]}, {b[1]}) χ={b[2]}")
assert np.sum(mask) == 1

print("\n" + "=" * 64)
print("✅ 第一性原理閉合:")
print("   (36,98) 由 x²+x−1=0 → φ → B,L₅,L₆,F₆ → Nd,Σγ")
print("   兩個約束 h¹¹+h²¹=Nd+Σγ, h²¹−h¹¹=Nd+L₆ 唯一確定")
print("   χ = −124 = 2(Nd−F₆−Σγ−F₆) = 2(36−98)")
print("=" * 64)
