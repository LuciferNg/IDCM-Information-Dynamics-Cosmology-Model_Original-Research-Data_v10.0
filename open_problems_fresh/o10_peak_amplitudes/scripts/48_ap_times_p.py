#!/usr/bin/env python3
"""
O10 48: A(p)×p 結構 — 關鍵測試
================================
A(p)×p: p=1→1.000, p=2→0.887, p=3→1.317, p=5→1.072, p=7→0.990

睇 A(p) vs c/p (c = 常數)?
或者 A(p) = 1/p × Fibonacci 修正?
"""
import numpy as np, math

phi = (1 + 5**0.5) / 2
eps = phi**-1/4
F = [1, 1, 2, 3, 5, 8, 13]

A = {1: 1.0000, 2: 0.4434, 3: 0.4389, 5: 0.2143, 7: 0.1414}

print("=" * 72)
print("A(p) × p 分析")
print("=" * 72)
print("A(p)×p: 1.000, 0.887, 1.317, 1.072, 0.990")
print()

# 平均?
vals = [A[1]*1, A[2]*2, A[3]*3, A[5]*5, A[7]*7]
print(f"平均 A×p = {np.mean(vals):.4f}")
print(f"中位數 = {np.median(vals):.4f}")
print()

# 睇 A(p) = k/p?
print("如果 A(p) = k/p:")
for k in [0.9, 1.0, 1.1]:
    print(f"  k={k}: ", end="")
    for p in [2, 3, 5, 7]:
        print(f"p={p}:{A[p]*p/k:.2f} ", end="")
    print()

print()
print("A×p 有冇 Fibonacci 修正?")
print("  A×p: 1.000, 0.887, 1.317, 1.072, 0.990")
print("  F_p: 1, 1, 2, 5, 13")
print("  A×p/F_p: 1.0, 0.887, 0.658, 0.214, 0.076")
print()

# 質數孿生對內: A(2)×2 vs A(3)×3?
print("孿生對內 A×p:")
print(f"  對1 (2,3): A2×2={A[2]*2:.4f}, A3×3={A[3]*3:.4f}, 比={A[3]*3/(A[2]*2):.4f}")
print(f"  對2 (5,7): A5×5={A[5]*5:.4f}, A7×7={A[7]*7:.4f}, 比={A[7]*7/(A[5]*5):.4f}")

print()
print("對 2 內: A5×5 ≈ A7×7 ≈ 1.07, 0.99 → 差 8%")
print("對 1 內: A2×2 = 0.887, A3×3 = 1.317 → 差 48%")
print()

# 另一個角度: A(p) = 3ε × 2/(p+1)?
print("A(p) = 3ε × 2/(p+1)?")
for p in [2, 3, 5, 7]:
    v = 3*eps*2/(p+1)
    print(f"  p={p}: {v:.4f} vs {A[p]:.4f} ({(A[p]-v)/v*100:+.1f}%)")

print()
print("A(p) = 3ε × φ^{-(p-1)/2}?")
for p in [2, 3, 5, 7]:
    v = 3*eps*phi**(-(p-1)/2)
    print(f"  p={p}: {v:.4f} vs {A[p]:.4f} ({(A[p]-v)/v*100:+.1f}%)")

print()
print("A(p) = 3ε × 2^{-(p-1)/2}?")
for p in [2, 3, 5, 7]:
    v = 3*eps*2**(-(p-1)/2)
    print(f"  p={p}: {v:.4f} vs {A[p]:.4f} ({(A[p]-v)/v*100:+.1f}%)")
