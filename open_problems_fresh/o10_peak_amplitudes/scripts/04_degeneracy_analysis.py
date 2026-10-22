#!/usr/bin/env python3
"""
O10 04: 決定性結構搜索 — CAMB lensed 高解析度
=============================================
CAMB lensed (As=2.1e-9) @ IDCM 峰位:
  A₂/A₁=0.4523, A₃/A₁=0.4430, A₄/A₁=0.1820, A₅/A₁=0.1839, A₆/A₁=0.1282, A₇/A₁=0.1423

結構線索:
  1. A₂ ≈ A₃ (簡併 1: 峰2=峰3)
  2. A₄ ≈ A₅ (簡併 2: 峰4=峰5)
  3. A₆ ≈ A₇ (簡併 3: 峰6=峰7)

→ 峰高以「對」出現! 2-3, 4-5, 6-7 係簡併對!
"""
import numpy as np, math

phi = (1+5**0.5)/2
eps = phi**-1/4

# CAMB lensed @ IDCM 峰位
A = {1: 1.0, 2: 0.4523, 3: 0.4430, 4: 0.1820, 5: 0.1839, 6: 0.1282, 7: 0.1423}

print("=" * 70)
print("峰高簡併結構: (2,3), (4,5), (6,7)")
print("=" * 70)
print()
print("簡併對平均:")
pairs = [(2, 3), (4, 5), (6, 7)]
avg = {}
for a, b in pairs:
    avg[a] = (A[a] + A[b]) / 2
    print(f"  pair ({a},{b}): avg = {avg[a]:.4f}")
print()

# 對平均做結構分析
print("簡併對平均 vs 候選:")
cands = {
    "3ε": 3*eps,
    "3ε×φ⁻¹": 3*eps*phi**-1,
    "3ε×φ⁻²": 3*eps*phi**-2,
    "3ε×φ⁻³": 3*eps*phi**-3,
    "3ε/2": 3*eps/2,
    "3ε×ε": 3*eps*eps,
    "3ε×ε²": 3*eps*eps**2,
    "3ε×(φ⁻¹)²": 3*eps*phi**-2,
    "3ε×(1/2)": 3*eps*0.5,
    "3ε×(2/3)": 3*eps*2/3,
    "ε²×19": eps**2*19,
    "ε³×8": eps**3*8,
}
print(f"  pair(2,3) avg = {avg[2]:.4f}:")
for name, v in cands.items():
    dev = abs(avg[2]-v)/v*100
    if dev < 10:
        print(f"    {name} = {v:.4f} (偏差 {dev:.2f}%)")
print()
print(f"  pair(4,5) avg = {avg[4]:.4f}:")
for name, v in cands.items():
    dev = abs(avg[4]-v)/v*100
    if dev < 10:
        print(f"    {name} = {v:.4f} (偏差 {dev:.2f}%)")
print()
print(f"  pair(6,7) avg = {avg[6]:.4f}:")
for name, v in cands.items():
    dev = abs(avg[6]-v)/v*100
    if dev < 10:
        print(f"    {name} = {v:.4f} (偏差 {dev:.2f}%)")

# 連續對比率
print()
print("對間比率 (pair 1 -> pair 2 -> pair 3):")
print(f"  avg(4,5)/avg(2,3) = {avg[4]/avg[2]:.4f}")
print(f"  avg(6,7)/avg(4,5) = {avg[6]/avg[4]:.4f}")
print()
print("候選: 0.5? φ⁻¹? 2/3? 3ε?")
print(f"  1/2 = {0.5:.4f}")
print(f"  φ⁻¹ = {phi**-1:.4f}")
print(f"  2/3 = {2/3:.4f}")
print(f"  3ε = {3*eps:.4f}")
print(f"  ε×3 = {3*eps:.4f}")
