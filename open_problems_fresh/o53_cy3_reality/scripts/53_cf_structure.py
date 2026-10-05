#!/usr/bin/env python3
"""
O53 A1: c_f n/3 機制 — 結構搜索
====================================
c_f ∈ {+1, +2/3, +1/3, 0, -1/3, -2/3} 已確認 (p=7.9e-5)
但 Z₃ 已排除 → 真正機制開放

搜索 c_f 結構:
  1. c_f vs δ_int (整數階梯)
  2. c_f vs 電荷/代數
  3. c_f 有冇「對稱」pattern
  4. 3×12D sector 相關? (c_f = f(sector)?)
"""
import os, json, math
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 70)
print("O53 A1: c_f 結構搜索")
print("=" * 70)

M_Pl = 1.22e19
m44 = M_Pl * math.exp(-44)
lnphi = math.log(phi)
SM = {'t': 172.69, 'b': 4.18, 'c': 1.27, 'tau': 1.777, 's': 0.093,
      'mu': 0.10566, 'd': 0.0047, 'u': 0.0022, 'e': 0.000511}
charges = {'t': 2/3, 'b': -1/3, 'c': 2/3, 'tau': -1, 's': -1/3,
           'mu': -1, 'd': -1/3, 'u': 2/3, 'e': -1}

data = {}
for k, m in SM.items():
    d = 44 - math.log(M_Pl/m)
    n = round(d)
    c = round((d-n)/lnphi*3)/3
    data[k] = {'m': m, 'delta': d, 'n_int': n, 'c': c, 'Q': charges[k]}

print(f"\n[1] 完整表:")
print(f"    {'粒子':5s} {'δ':>8s} {'n':>4s} {'c':>7s} {'3c':>4s} {'Q':>6s}")
for k, v in data.items():
    print(f"    {k:5s} {v['delta']:+8.4f} {v['n_int']:+4d} {v['c']:+7.3f} {v['c']*3:+4.0f} {v['Q']:+6.3f}")

# --- [1] c vs n_int ---
print("\n[2] c vs δ_int (n):")
for n in sorted(set(v['n_int'] for v in data.values())):
    cs = [v['c'] for v in data.values() if v['n_int'] == n]
    ks = [k for k, v in data.items() if v['n_int'] == n]
    print(f"    n={n:+3d}: c={cs} ({ks})")

# --- [2] c vs Q ---
print("\n[3] c vs 電荷:")
for Q in [2/3, -1/3, -1]:
    cs = [(k, v['c']) for k, v in data.items() if v['Q'] == Q]
    print(f"    Q={Q:+5.2f}: {cs}")

# --- [3] 3c 值 (整數) ---
print("\n[4] 3c (整數) 結構:")
c3 = {k: int(round(v['c']*3)) for k, v in data.items()}
print(f"    3c = {c3}")
# 3c = n? 有冇 pattern
print(f"    n_int: { {k: v['n_int'] for k, v in data.items()} }")
print(f"    3c+n? { {k: c3[k]+data[k]['n_int'] for k in data} }")

# --- [4] 3c 矩陣 pattern ---
print("\n[5] 3c 按 (代, 電荷) 排列:")
gens = {'t': 1, 'c': 2, 'u': 3, 'b': 1, 's': 2, 'd': 3, 'tau': 1, 'mu': 2, 'e': 3}
for qname, Q in [('U(+2/3)', 2/3), ('D(−1/3)', -1/3), ('L(−1)', -1)]:
    row = []
    for g in [1, 2, 3]:
        k = [k for k, v in data.items() if gens[k] == g and v['Q'] == Q][0]
        row.append(f"{c3[k]:+d}")
    print(f"    {qname}: {row}")

# --- [5] c 同 φ 指數? ---
print("\n[6] c 有冇 φ 結構?")
# 3c ∈ {-2,-1,0,1,2,3}: 呢啲數字有冇意義?
print(f"    3c 值域: {-2,-1,0,1,2,3}")
print(f"    -2, -1, 0, +1, +2, +3 — 連續整數帶!")
print(f"    3c = −2 至 +3 (6 個連續值)")
print(f"    → c = n/3, n ∈ [−2, +3]")

# --- [6] 3c 同 3×12D sector 相關? ---
print("\n[7] 3c 分佈 (3 代 × 3 電荷):")
matrix = np.zeros((3, 3))
for k, v in data.items():
    g = gens[k] - 1
    q = [2/3, -1/3, -1].index(v['Q'])
    matrix[g, q] = c3[k]
print(f"    列=代 (1-3), 行=U/D/L:")
print(f"    {np.array2string(matrix.astype(int), precision=0)}")
print(f"    代和: {matrix.sum(axis=1)}")
print(f"    電荷和: {matrix.sum(axis=0)}")
print(f"    總和: {matrix.sum():.0f}")
print(f"    → 3c 總和 = {matrix.sum():.0f} = 0? {'✅' if matrix.sum()==0 else '❌'}")

print("\n" + "=" * 70)
print("搜索完成")
print("=" * 70)
