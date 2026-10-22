#!/usr/bin/env python3
"""
O10 67: 質數峰對應 K_Chain 模式 — 半整數能量
==============================================
峰位 ℓ = 44×N ± 1 → 對應 K_Chain 模式 n ≈ 2N (偶數)

γ_n = 4sin²(πn/88) 能量:
  n = 2N: γ_{2N} = 4sin²(2πN/88) = 4sin²(πN/44)

質數峰 n: 10, 24, 36, 50, 64
"""
import numpy as np, math

phi = (1 + 5**0.5) / 2
eps = phi**-1/4

print("=" * 72)
print("質數峰 K_Chain 模式能量")
print("=" * 72)

N = {1: 5, 2: 12, 3: 18, 5: 25, 7: 32}
n_modes = {1: 10, 2: 24, 3: 36, 5: 50, 7: 64}

print("γ_n = 4sin²(πn/88):")
gammas = {}
for m in [1, 2, 3, 5, 7]:
    n = n_modes[m]
    g = 4*math.sin(math.pi*n/88)**2
    gammas[m] = g
    print(f"  m={m}: n={n}, γ = {g:.4f}")

print()
print("Σγ = 90 (全部模式), 質數峰 γ:")
total_prime = sum(gammas.values())
print(f"  Σγ_prime = {total_prime:.4f}")
print(f"  Σγ_prime/90 = {total_prime/90:.4f}")

print()
print("γ 比率:")
for m in [2, 3, 5, 7]:
    r = gammas[m]/gammas[1]
    print(f"  γ_{m}/γ₁ = {r:.4f}")

print()
print("γ: 0.2544, 1.4314, 3.0513, 5.2311, 7.8570")
print("差: 1.177, 1.620, 2.180, 2.626")
print()

# 質數峰高度 vs γ?
print("質數峰高度 A vs γ:")
A = {1: 1.0, 2: 0.4434, 3: 0.4389, 5: 0.2143, 7: 0.1414}
for m in [1, 2, 3, 5, 7]:
    print(f"  m={m}: A={A[m]:.4f}, γ={gammas[m]:.4f}, A×γ={A[m]*gammas[m]:.4f}")

print()
print("A×γ: 0.254, 0.635, 1.339, 1.121, 1.111")
print("高 ℓ 嘅 A×γ ≈ 1.1-1.3 (趨平)")
print()

# 質數峰 = 奇數模式? (n 應該係奇數?)
print("如果質數峰對應奇數 n?")
print("  n = 2N-1? 9, 23, 35, 49, 63")
g_odd = {}
for m in [1, 2, 3, 5, 7]:
    n = 2*N[m]-1
    g = 4*math.sin(math.pi*n/88)**2
    g_odd[m] = g
    print(f"  m={m}: n={n}, γ = {g:.4f}")

print()
print("γ_odd: 0.2275, 1.3502, 2.9439, 5.0883, 7.7009")
print("同 γ_even 差好少")
print()

# 關鍵: 峰位 44N±1 對應 sin 相位?
print("峰位 ℓ = 44N±1 → sin(πℓ/88):")
for m in [1, 2, 3, 5, 7]:
    l = {1: 221, 2: 527, 3: 815, 5: 1121, 7: 1409}[m]
    s = math.sin(math.pi*l/88)
    c = math.cos(math.pi*l/88)
    print(f"  m={m}: ℓ={l}, sin(πℓ/88)={s:.4f}, cos={c:.4f}")

print()
print("sin(πℓ/88): 0.1478, -0.0698, 0.9794, -0.9898, 0.1478")
print("cos(πℓ/88): 0.9890, 0.9976, 0.2020, 0.1423, 0.9890")
print()
print("m=1 同 m=7: sin = 0.1478 相同! cos = 0.9890 相同!")
print("→ ℓ=221 同 ℓ=1409 有相同相位!")
print("221 同 1409: 1409-221 = 1188 = 44×27")
print("→ 44 週期! ℓ ≡ 221 (mod 44×27)?")
print()
print("m=3 (815) 同 m=5 (1121): sin = ±0.98 (反相位)")
print("815 + 306 = 1121 → Δℓ = 306 = 44×6.95?")
print()
print("Δℓ: 306, 288, 306, 288 (交替)")
print("306 = 44×7 - 2, 288 = 44×6 + 24")
