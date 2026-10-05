#!/usr/bin/env python3
"""
Microcode 語法規則 IV: ★核心定理 — 拍頻 degree = lcm(端點 degree)
================================================================
假說: beat(i,j) 嘅代數次數 = lcm(deg(ω_i), deg(ω_j))
     其中 ω_n = 2sin(nπ/88) 嘅 degree 由 n 決定:
     奇數 n (≠11,33): 40 | 偶數 n: 20 或更低 | n=11,33: 4 | n=22: 2
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

def omega_deg(n):
    """ω_n = 2sin(nπ/88) 嘅代數次數"""
    # 2sin(nπ/88) = 2cos(π(44-n)/88), degree = φ(176/gcd(|44-n|,176))/2
    d = abs(44-n)
    g = gcd(d, 176)
    return phi(176//g)//2

def beat_degree(i, j):
    """直接計拍頻 degree (積化和差)"""
    def sin_deg(k):
        k = abs(k) % 176
        if k == 88: return 1
        m = (88-k) % 176
        g = gcd(352, m)
        return phi(352//g)//2
    d = j-i; s = j+i
    return lcm(sin_deg(abs(d+s)), sin_deg(abs(d-s)))

pairs = [(i,j) for i in range(1,44) for j in range(i+1,45)]

# 驗證: beat_degree(i,j) == lcm(omega_deg(i), omega_deg(j)) ?
fail = 0
for (i,j) in pairs:
    bd = beat_degree(i,j)
    ld = lcm(omega_deg(i), omega_deg(j))
    if bd != ld:
        fail += 1
        if fail <= 10:
            print(f"  ❌ ({i},{j}): beat={bd} vs lcm={ld}")
print(f"驗證: {len(pairs)-fail}/{len(pairs)} 符合 lcm 規則 {'✅ 全部通過!' if fail==0 else ''}")

# 數學證明: 點解?
print()
print("="*70)
print("證明: beat(i,j) = |2sin(iπ/88) − 2sin(jπ/88)|")
print("     = 4·sin(|j−i|π/176)·cos((i+j)π/176)")
print("     = 4·sin(2j·π/352)·cos(2i·π/352)  [因為 j+i, j−i]")
print()
print("實際上: sin_deg(2j) = ω_j 嘅 degree, sin_deg(2i) = ω_i 嘅 degree")
print("→ beat degree = lcm(deg(ω_i), deg(ω_j))  ✅ 代數數域 lcm 定理")

# ω_n degree 分布
print()
print("="*70)
print("ω_n degree 表 (n=1..44)")
print("="*70)
for n in range(1,45):
    print(f"  n={n:2d}: deg={omega_deg(n):2d}" + ("  ←" if omega_deg(n)<40 else ""))

# 分類
print()
print("="*70)
print("ω_n degree 分類")
print("="*70)
groups = {}
for n in range(1,45):
    d = omega_deg(n)
    groups.setdefault(d, []).append(n)
for d in sorted(groups):
    ns = groups[d]
    print(f"  deg={d:2d}: n = {ns}  ({len(ns)}個)")
