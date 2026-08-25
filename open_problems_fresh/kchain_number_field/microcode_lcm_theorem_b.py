#!/usr/bin/env python3
"""
Microcode 語法規則 IVb: lcm 定理完整驗證 (含 n=44 邊界)
========================================================
修正: ω_44 = 2sin(44π/88) = 2sin(π/2) = 2 ∈ ℚ (有理, deg=0)
      lcm(deg, 0) = 0 係錯 — 應該用 lcm(deg, 1) 或者直接 handle
      實際: beat(i,44) degree = deg(ω_i) (因為 ω_44 有理, 唔影響數域)
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
    if n == 44: return 1   # 有理數 → 用 1 (中性元)
    d = abs(44-n)
    g = gcd(d, 176)
    return phi(176//g)//2

def beat_degree(i, j):
    def sin_deg(k):
        k = abs(k) % 176
        if k == 88: return 1
        m = (88-k) % 176
        g = gcd(352, m)
        return phi(352//g)//2
    d = j-i; s = j+i
    return lcm(sin_deg(abs(d+s)), sin_deg(abs(d-s)))

pairs = [(i,j) for i in range(1,44) for j in range(i+1,45)]
fail = []
for (i,j) in pairs:
    bd = beat_degree(i,j)
    ld = lcm(omega_deg(i), omega_deg(j))
    if bd != ld:
        fail.append((i,j,bd,ld))
print(f"驗證: {len(pairs)-len(fail)}/{len(pairs)} 符合 lcm 規則")
if fail:
    for f in fail[:10]: print(f"  ❌ {f}")
else:
    print("✅ 946/946 全部通過 — ★ lcm 定理成立!")

print()
print("="*70)
print("★ 核心定理: 拍頻 degree = lcm(deg(ω_i), deg(ω_j))")
print("="*70)
print("""
  beat(i,j) = |ω_i − ω_j| = 4·sin(|j−i|π/176)·cos((i+j)π/176)
  sin(2j·π/352) 嘅 degree = ω_j 嘅 degree (端點代數性質完全決定拍頻次數!)
  → 拍頻嘅「代數複雜度」= 兩個端點模式嘅 lcm
  
  ⚠️ 即係話: 946 個拍頻嘅 degree 並冇「新資訊」
  — 完全由 44 個 ω_n 嘅 degree 決定 (2,4,5,10,20,40)
""")

# 由 lcm 定理推導: 拍頻 degree 全表 = 端點 degree 嘅 lcm 表
print("="*70)
print("ω_n degree 分組 → lcm 表")
print("="*70)
groups = {}
for n in range(1,45):
    groups.setdefault(omega_deg(n), []).append(n)
for d in sorted(groups):
    print(f"  deg={d:2d}: n∈{groups[d]}  ({len(groups[d])}個)")

print()
print("  lcm(2,20)=20, lcm(5,10)=10, lcm(4,40)=40, lcm(20,40)=40...")
print("  → 只有 lcm 出 40 先係 degree-40 拍頻")
print("  → 高對稱端點 (11,33,22) 產生低次數拍頻")

# 對稱端點嘅低次數拍頻清單
print()
print("="*70)
print("對稱端點 (n=11,22,33) 產生嘅低次數拍頻")
print("="*70)
low = [(i,j,beat_degree(i,j)) for (i,j) in pairs
       if beat_degree(i,j) < 40 and (i in (11,22,33) or j in (11,22,33))]
for (i,j,d) in sorted(low, key=lambda x:x[2]):
    print(f"  ({i:2d},{j:2d}) deg={d}")
