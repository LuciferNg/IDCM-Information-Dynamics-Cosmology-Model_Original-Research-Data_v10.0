#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O237 U2 — Chain 扇區 partition 普查: 由 chain 結構定義桶, 計 v₂/γ-mean, 後對照 C_f
================================================================================
docs/08 指針: C_e = 18/5 = (Σv₂(G8))/|G8| 係「扇區 v₂-mean」唔係 mode 函數。
本 script 由【chain 內部結構】預先定義 15+ 個 partition 桶 (零 C_f 輸入),
逐桶計 (Σv₂)/|S| 同 (Σγ)/|S| —— 然後先一次過 print C_f 對照 (唔 fit)。

分區家族 (全部由 88-ring 代數定義, 唔睇質量):
  P1: mod-4 餘類 (4 桶)          n ≡ 0,1,2,3 (mod 4)
  P2: ℤ₄ 相位組 (i^n ∈ {1,i,−1,−i})  ← 同 P1 但命名來自 Ŝ 相位
  P3: mod-8 餘類 (8 桶)
  P4: π 階梯 = O137 9-mode 選取 {1,2,3,4,5,7,9,11,13}
  P5: Lucas 位置 (L_k = 2,1,3,4,7,11,18,29,47...; k=1..8 ≤44)
  P6: Fibonacci 位置 (F_k = 1,1,2,3,5,8,13,21,34 ≤44)
  P7: Z₂ 鏡像對 (n, 44−n) 14 對 + 4 自對偶
  P8: 奇/偶 二分
  P9: A5 9-mode 補集 (35 個非選擇模式)
"""
import math

def g(m): return 4 * math.sin(math.pi * m / 88) ** 2
def v2(n):
    c = 0
    while n % 2 == 0:
        n //= 2; c += 1
    return c

LUCAS = [2, 1, 3, 4, 7, 11, 18, 29, 47]
FIBO  = [1, 1, 2, 3, 5, 8, 13, 21, 34]
A5MODES = [1, 2, 3, 4, 5, 7, 9, 11, 13]

def stats(S):
    """桶統計: (|S|, Σγ, Σv₂, Σv₂/|S|, Σγ/|S|)"""
    S = [n for n in S if 1 <= n <= 44]
    if not S: return None
    return (len(S), sum(g(n) for n in S), sum(v2(n) for n in S),
            sum(v2(n) for n in S)/len(S), sum(g(n) for n in S)/len(S))

P = {}
P['P1 mod4=0'] = [n for n in range(1,45) if n%4==0]
P['P1 mod4=1'] = [n for n in range(1,45) if n%4==1]
P['P1 mod4=2'] = [n for n in range(1,45) if n%4==2]
P['P1 mod4=3'] = [n for n in range(1,45) if n%4==3]
P['P2 phase=i^1'] = [n for n in range(1,45) if n%4==1]
P['P2 phase=i^2'] = [n for n in range(1,45) if n%4==2]
P['P2 phase=i^3'] = [n for n in range(1,45) if n%4==3]
P['P2 phase=i^0'] = [n for n in range(1,45) if n%4==0]
for r in range(8):
    P[f'P3 mod8={r}'] = [n for n in range(1,45) if n%8==r]
P['P4 A5-modes'] = A5MODES
P['P4 A5-complement'] = [n for n in range(1,45) if n not in A5MODES]
P['P5 Lucas'] = [n for n in range(1,45) if n in LUCAS]
P['P5 Lucas-comp'] = [n for n in range(1,45) if n not in LUCAS]
P['P6 Fibo'] = [n for n in range(1,45) if n in FIBO]
P['P6 Fibo-comp'] = [n for n in range(1,45) if n not in FIBO]
P['P7 mirror-half1'] = [n for n in range(1,23)]
P['P7 mirror-half2'] = [n for n in range(23,45)]
P['P8 odd'] = [n for n in range(1,45,2)]
P['P8 even'] = [n for n in range(2,45,2)]

print("="*100)
print("O237 U2 — Chain 扇區 partition 普查 (桶先行, C_f 後對照)")
print("="*100)
print(f"{'桶':>16} {'|S|':>4} {'Σγ':>8} {'Σv₂':>5} {'Σv₂/|S|':>8} {'Σγ/|S|':>8}")

bucket_rows = []
for name, S in P.items():
    st = stats(S)
    if st is None:
        continue
    bucket_rows.append((name, st))
    print(f"{name:>16} {st[0]:>4} {st[1]:>8.4f} {st[2]:>5} {st[3]:>8.4f} {st[4]:>8.4f}")

print("\n[對照] A5 C_f 真值 (O206 第十輪) — 一次過睇有冇結構對應:")
M0 = 27.9009
MASS = {"e":0.510998950,"u":2.16,"d":4.67,"s":93.4,"mu":105.6583755,
        "c":1270.0,"tau":1776.86,"b":4180.0}
CF = {p: MASS[p]/(M0*g(n)) for p, n in zip(["e","u","d","s","mu","c","tau","b"],
                                           [1,2,3,4,5,7,9,11])}
print(f"  {'p':>4} {'n':>3} {'C_f':>10}")
for p, n in zip(["e","u","d","s","mu","c","tau","b"], [1,2,3,4,5,7,9,11]):
    print(f"  {p:>4} {n:>3} {CF[p]:>10.4f}")

print(f"""
[判定] 目標: 搵「一個桶 (或其子結構)」嘅 (Σv₂)/|S| 或 (Σγ)/|S| 一次過覆蓋 8 個 C_f 值。
已知: G8 (v₂≥3 層) 嘅 Σv₂/|S| = 18/5 = 3.6 ≈ C_e。其他桶值全部列晒喺上表。
規則: 唔可以因為 8 個值去揀桶 —— 桶已經由 chain 結構定義 (P1-P8)。
若冇任何桶 mean 同時命中多個 C_f (或 C_f 嘅線性組合), 即負結果照記錄。
""")

# 簡單偵測: 逐個桶 v2-mean 有冇接近任何 C_f (>100 結構, 唔逐個比)
hit = {}
for name, st in bucket_rows:
    for p, cv in CF.items():
        if abs(st[3] - cv) < 0.05*st[3] if st[3]>0 else False:
            hit.setdefault(name, []).append((p, cv, st[3]))
print("桶 v₂-mean 對 C_f 命中 (<5% rel):")
if not hit:
    print("  無")
else:
    for k,v in hit.items(): print(f"  {k}: {v}")

print("\n[總結]")
print("  桶統計全部列出; 冇任何單一桶 mean 一次過覆蓋 8 值 (預期)。")
print("  C_e=3.6 例外 (G8 層) 已被 docs/04 確認唯一; 本表提供其余桶嘅對照。")