#!/usr/bin/env python3
"""
O10 68: 質數峰 K_Chain 對稱性 — γ(m2)=γ(m7)
============================================
γ(m2) = γ(m7) = 2.2846 (完全相同!)

K_Chain 對稱: γ_n = γ_{88-n} (sin² 對稱)
m2: n=24, m7: n=64
24 + 64 = 88 ✓!

質數峰 n 對:
  m2 (24) + m7 (64) = 88
  m3 (36) + m5 (50) = 86?
  m1 (10) + ? = ?
"""
import numpy as np, math

phi = (1 + 5**0.5) / 2
eps = phi**-1/4

print("=" * 72)
print("質數峰 K_Chain 對稱性")
print("=" * 72)

N = {1: 5, 2: 12, 3: 18, 5: 25, 7: 32}
n_modes = {1: 10, 2: 24, 3: 36, 5: 50, 7: 64}

# n 對稱
print("n 值: 10, 24, 36, 50, 64")
print("n 對 (sum = 88):")
pairs = [(24, 64), (36, 50)]
for a, b in pairs:
    print(f"  {a} + {b} = {a+b} {'✅' if a+b==88 else '❌'}")

print()
print("24+64 = 88 ✓ (m2+m7)")
print("36+50 = 86 ✗ (m3+m5)")
print()

# γ 對稱
print("γ_n = 4sin²(πn/88) 對稱性:")
for n in [10, 24, 36, 50, 64]:
    g = 4*math.sin(math.pi*n/88)**2
    g_mirror = 4*math.sin(math.pi*(88-n)/88)**2
    print(f"  n={n}: γ={g:.4f}, γ(88-n)={g_mirror:.4f}")

print()
print("γ(24) = γ(64) = 2.2846 ✓ (對稱)")
print("γ(36) = γ(52)? 52 唔係質數峰")
print()

# 質數峰同 88-n 對稱
print("質數峰 n ↔ 88-n:")
for m in [1, 2, 3, 5, 7]:
    n = n_modes[m]
    mirror = 88 - n
    # mirror 係咪另一個質數峰?
    if mirror in n_modes.values():
        m2 = [k for k, v in n_modes.items() if v == mirror][0]
        print(f"  m={m} (n={n}) ↔ m={m2} (n={mirror}) ✅")
    else:
        print(f"  m={m} (n={n}) ↔ n={mirror} (唔係質數峰)")

print()
print("只有 m2 (24) ↔ m7 (64) 對稱")
print("m1 (10) ↔ n=78, m3 (36) ↔ n=52, m5 (50) ↔ n=38")
print()

# 檢查 88-n 對質數峰
print("88 - n 值: 78, 64, 52, 38, 24")
print("只有 64 同 24 係質數峰模式")
print()

# 更重要: 質數峰位置同 K_Chain 格點
print("=" * 72)
print("質數峰 ℓ = 44N±1 → K_Chain 相位")
print("=" * 72)
print("ℓ/44 = N ± 1/44")
print("相位: sin(πℓ/88) = sin(π(N±1/44)/2)")
print()
for m in [1, 2, 3, 5, 7]:
    l = {1: 221, 2: 527, 3: 815, 5: 1121, 7: 1409}[m]
    N = {1: 5, 2: 12, 3: 18, 5: 25, 7: 32}[m]
    frac = l - 44*N
    s = math.sin(math.pi*l/88)
    print(f"  m={m}: ℓ=44×{N}{frac:+d}, sin(πℓ/88)={s:+.4f}")

print()
print("sin 值: +0.9994, -0.0357, -0.7319, +0.7319, +0.0357")
print()
print("sin 值模式:")
print("  m1: +1.0 (sin 峰頂)")
print("  m2: 0.0 (sin 零點)")
print("  m3: -0.73")
print("  m5: +0.73 (m3 反相)")
print("  m7: 0.0 (m2 反相)")
print()
print("sin 值 = cos(π×2N/44)?")
for m in [1, 2, 3, 5, 7]:
    N = {1: 5, 2: 12, 3: 18, 5: 25, 7: 32}[m]
    c = math.cos(math.pi*N/22)
    print(f"  m={m}: cos(π×{N}/22) = {c:+.4f}")
