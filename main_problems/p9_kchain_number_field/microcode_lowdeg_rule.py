#!/usr/bin/env python3
"""
Microcode 語法規則 III: 「低次數位置規則」驗證
===============================================
假說: 全 946 拍頻, deg<40 只出現喺:
  A) i ≡ 0 mod 4 (即 i=4,8,12,...,40)
  B) i = 11 (對稱中心)
  C) 特別例外: d=22 行嘅 i=22 (deg=2), d=2 行嘅 i=20,22 (deg=10)?
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

# 收集所有 deg<40 嘅拍頻
low = []
for (i,j) in pairs:
    d = j-i; s = j+i
    deg = beat_degree(d,s)
    if deg < 40:
        low.append((i,j,d,s,deg))

print(f"deg<40 拍頻總數: {len(low)}")
print()
# 分類: i≡0 mod 4? i=11? 其他?
catA = [x for x in low if x[0] % 4 == 0]
catB = [x for x in low if x[0] == 11]
other = [x for x in low if x[0] % 4 != 0 and x[0] != 11]
print(f"分類 A (i≡0 mod 4): {len(catA)}")
print(f"分類 B (i=11): {len(catB)}")
print(f"其他 (例外): {len(other)}")
print()
if other:
    print("⚠️ 例外 (唔符合 A 或 B):")
    for (i,j,d,s,deg) in sorted(other, key=lambda x:(x[4],x[0])):
        print(f"  ({i:2d},{j:2d}) d={d:2d} s={s:3d} deg={deg}")
else:
    print("✅ 全部 deg<40 符合 A (i≡0 mod 4) 或 B (i=11)!")

# 深入: deg<40 嘅 d 分布
print()
print("deg<40 嘅 i 值完整統計:")
ic = Counter(x[0] for x in low)
for i in sorted(ic):
    degs = sorted(set(deg for (ii,jj,d,s,deg) in low if ii==i))
    print(f"  i={i:2d}: {ic[i]:2d} 個, deg={degs}")
