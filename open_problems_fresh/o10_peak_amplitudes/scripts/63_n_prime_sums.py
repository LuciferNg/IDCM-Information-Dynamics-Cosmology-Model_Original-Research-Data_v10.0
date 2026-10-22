#!/usr/bin/env python3
"""
O10 63: N_m = 質數對和 — 完整結構
==================================
發現: N₁=5=2+3, N₂=12=5+7, N₃=18=7+11, N₇=32=13+19
但 N₅=25 唔匹配簡單質數對

真正結構?
"""
import numpy as np, math

print("=" * 72)
print("N_m 質數對結構")
print("=" * 72)

N = {1: 5, 2: 12, 3: 18, 5: 25, 7: 32}
primes = [2, 3, 5, 7, 11, 13, 17, 19, 23]

# 質數對和
print("質數對和 (p, p+next):")
for i in range(len(primes)-1):
    print(f"  {primes[i]}+{primes[i+1]} = {primes[i]+primes[i+1]}")

print()
print("N_m: 5, 12, 18, 25, 32")
print("質數對和: 5, 8, 12, 18, 24, 30, 36, 42")
print()

# 孿生質數對 (差 2)
print("孿生質數對 (差 2):")
twin_pairs = [(3,5), (5,7), (11,13), (17,19)]
for a, b in twin_pairs:
    print(f"  ({a},{b}): 和 = {a+b}, 差 = {b-a}")

print()
print("孿生質數對和: 8, 12, 24, 36")
print("N₂ = 12 = 5+7 ✓ (孿生質數對)")
print()

# 質數和 (質數 pair 唔一定孿生)
print("所有質數對和:")
all_sums = []
for i in range(len(primes)):
    for j in range(i+1, len(primes)):
        s = primes[i] + primes[j]
        if s in N.values():
            all_sums.append((primes[i], primes[j], s))
print(all_sums)
print()

# N_m 分解
print("N_m 所有質數對分解:")
for m, nm in N.items():
    decomps = [(a, b) for a in primes for b in primes if a < b and a+b == nm]
    print(f"  N_{m} = {nm}: {decomps}")

print()
print("哥德巴赫: 所有偶數 = 質數對和 (25 奇數用 2+23)")
print("N₅ = 25 = 2+23 (唯一質數對)")
print()

# 更重要: 峰位 ℓ 同質數嘅直接關係
print("=" * 72)
print("峰位 ℓ 同質數")
print("=" * 72)
ells = {1: 221, 2: 527, 3: 815, 5: 1121, 7: 1409}
for m in [1, 2, 3, 5, 7]:
    print(f"  m={m}: ℓ={ells[m]}, ℓ/44 = {ells[m]/44:.3f}, ℓ/88 = {ells[m]/88:.3f}")

print()
print("ℓ/88: 2.511, 5.989, 9.261, 12.739, 16.011")
print("接近半整數? 2.5, 6.0, 9.25, 12.75, 16.0")
print()
print("ℓ = 44×N + frac:")
for m in [1, 2, 3, 5, 7]:
    frac = ells[m] - 44*N[m]
    print(f"  m={m}: ℓ = 44×{N[m]} + {frac}")
print()

# 質數乘積?
print("質數乘積:")
print("  2×3 = 6, 5×7 = 35")
print("  6 同 35 有咩用?")
print()

# 關鍵測試: 峰位整數 N_m 係咪質數序列嘅累積差?
print("質數累積差 (1,1,2,2):")
print("  N: 5, 12, 18, 25, 32")
print("  差: 7, 6, 7, 7")
print("  7+6+7+7 = 27")
print()

# 檢查 N_m 是否 = Σ質數到某點
print("質數累積和:")
s = 0
for i, p in enumerate(primes):
    s += p
    print(f"  Σ到 p_{i+1}={p}: {s}")
print()
print("累積: 2, 5, 10, 17, 28, 41, 58, 77, 100")
print("N_m:  5, 12, 18, 25, 32")
print()
print("N₁ = 5 = Σp₂ ✓")
print("N₂ = 12 = ? (Σp₃=10, Σp₄=17)")
print("N₃ = 18 = Σp₄+1")
print("N₅ = 25 = ?")
print("N₇ = 32 = ?")
