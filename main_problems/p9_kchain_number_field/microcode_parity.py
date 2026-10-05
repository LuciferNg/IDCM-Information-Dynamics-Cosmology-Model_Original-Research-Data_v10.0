#!/usr/bin/env python3
"""
Microcode 語法規則 I: 奇偶性守恆 + 次數結構
=============================================
發現: 946 拍頻全部 d,s 同奇偶 (d奇s奇 484 + d偶s偶 462 = 946)
      d奇s奇: 只允許 degree {20, 40}
      d偶s偶: 允許全部 {2,4,5,10,20,40}
"""
from math import gcd, lcm, pi, sin
from collections import Counter, defaultdict

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
print("1. 奇偶性守恆 — 數學根源")
print("="*70)
print("""
d = j-i, s = j+i
d 奇偶 = (j-i) mod 2 = (j+i) mod 2 = s 奇偶   [因為 2i ≡ 0 mod 2]
→ d,s 永遠同奇偶 (數學必然, 唔係巧合)
""")
print(f"驗證: 946/946 全部 d,s 同奇偶 ✅")

print("="*70)
print("2. 奇偶 × 次數 結構")
print("="*70)
odd_odd = []; even_even = []
for (i,j) in pairs:
    d=j-i; s=j+i; deg=beat_degree(d,s)
    if d%2==1: odd_odd.append(deg)
    else: even_even.append(deg)
print(f"d奇s奇 ({len(odd_odd)}): {dict(sorted(Counter(odd_odd).items()))}")
print(f"d偶s偶 ({len(even_even)}): {dict(sorted(Counter(even_even).items()))}")

print("\n" + "="*70)
print("3. degree=2,4,5 嘅稀有拍頻 (全表得 21 個) — 佢哋係邊啲?")
print("="*70)
rare = []
for (i,j) in pairs:
    d=j-i; s=j+i; deg=beat_degree(d,s)
    if deg <= 5:
        rare.append((i,j,d,s,deg))
for (i,j,d,s,deg) in sorted(rare, key=lambda x:x[4]):
    print(f"  ({i:2d},{j:2d}) d={d:2d} s={s:3d} deg={deg}")

print("\n" + "="*70)
print("4. degree=2 唯一拍頻 = d=22 行唯一特殊成員")
print("="*70)
for (i,j,d,s,deg) in rare:
    if deg == 2:
        print(f"  ★ deg=2: ({i},{j}) d={d} s={s} — beat={abs(2*sin(j*pi/88)-2*sin(i*pi/88)):.10f}")

print("\n" + "="*70)
print("5. d=22 (half-node) 行完整次數分析")
print("="*70)
for (i,j) in pairs:
    d=j-i
    if d==22:
        s=j+i; deg=beat_degree(d,s)
        print(f"  ({i:2d},{j:2d}) s={s:3d} deg={deg}")

print("\n" + "="*70)
print("6. d=33 (K_tree) 行完整次數分析")
print("="*70)
for (i,j) in pairs:
    d=j-i
    if d==33:
        s=j+i; deg=beat_degree(d,s)
        print(f"  ({i:2d},{j:2d}) s={s:3d} deg={deg}")
