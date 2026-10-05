#!/usr/bin/env python3
"""
Microcode 語法規則 II: d 行內部結構 — 交替/週期/對稱
=====================================================
發現:
  d=22 (half-node) 行: deg 40,20 交替, 中間 (11,33) deg=4, 尾 (22,44) deg=2
  d=33 (K_tree) 行: 全 40, 尾 (11,44) deg=4
問題: 全 43 行嘅內部 deg pattern 有冇統一規則?
"""
from math import gcd, lcm, pi, sin
from collections import Counter

def phi(n):
    r = n; p = 2
    while p*p <= n:
        if n % p == 0:
            while n % p == 0: n //= p
            r -= r // p
        p += 1
    if n > 1: r -= r // n
    return r

def sin_deg(k):
    k = abs(k) % 176
    if k == 88: return 1
    m = (88 - k) % 176
    g = gcd(352, m)
    return phi(352 // g) // 2

def beat_degree(d, s):
    k1 = abs(d+s) % 352; k2 = abs(d-s) % 352
    return lcm(sin_deg(k1), sin_deg(k2))

pairs = [(i,j) for i in range(1,44) for j in range(i+1,45)]

print("="*70)
print("1. 全 43 行嘅 deg pattern (壓縮顯示)")
print("="*70)
for d in range(1,44):
    members = [(i,j) for (i,j) in pairs if j-i==d]
    seq = [beat_degree(d, i+j) for (i,j) in members]
    # 壓縮: 連續相同合併
    comp = []
    prev = None; cnt = 0
    for x in seq:
        if x == prev: cnt += 1
        else:
            if prev is not None: comp.append(f"{prev}×{cnt}")
            prev = x; cnt = 1
    comp.append(f"{prev}×{cnt}")
    # 簡化顯示: 只顯示非40
    non40 = [(k+1, v) for k,v in enumerate(seq) if v != 40]
    print(f"d={d:2d} ({len(members):2d}): {' '.join(comp)}  非40: {non40}")

print("\n" + "="*70)
print("2. 每行嘅 '非40' 位置 — 有冇規則?")
print("="*70)
print("(位置 = 行內第 k 個成員, i = k 即第一成員 i=1)")
print()
# 收集每行非40成員嘅 (i, deg)
rows_info = {}
for d in range(1,44):
    members = [(i,j) for (i,j) in pairs if j-i==d]
    non40 = [(i, beat_degree(d, i+j)) for (i,j) in members if beat_degree(d,i+j) != 40]
    if non40:
        rows_info[d] = non40
        print(f"d={d:2d}: " + ", ".join(f"i={i}(deg={deg})" for i,deg in non40))
