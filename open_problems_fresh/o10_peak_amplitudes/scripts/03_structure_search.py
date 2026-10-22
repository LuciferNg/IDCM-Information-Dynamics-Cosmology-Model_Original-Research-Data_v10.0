#!/usr/bin/env python3
"""
O10 03: 峰幅度結構公式搜索 (核心)
================================
基準:
  A) Planck 2018 binned (ground truth): A₂/A₁=0.4434, A₃/A₁=0.4389, A₄/A₁=0.2143
  B) CAMB lensed (As=2.1e-9): 接近 binned

任務: 搵出 A_m/A₁ 嘅結構公式, 必須:
  1. 包含 A₂=3ε 做特例 (或解釋點解 A₂ 唔係 3ε)
  2. 有物理/結構來源 (K_Chain, K_Tree, φ, Lucas/Fibonacci)
  3. 零自由參數
"""
import numpy as np, math, json, os
from itertools import product

phi = (1+5**0.5)/2
phi_inv = 1/phi
eps = phi_inv/4

# Planck binned 真實峰比率 (自動峰)
r_true = {1: 1.0, 2: 0.4434, 3: 0.4389, 4: 0.2143, 5: 0.1414}

# 候選基礎常數
base = {
    "ε": eps,
    "3ε": 3*eps,
    "φ⁻¹": phi_inv,
    "φ⁻²": phi_inv**2,
    "φ⁻³": phi_inv**3,
    "φ⁻⁴": phi_inv**4,
    "φ⁻⁵": phi_inv**5,
    "1/2": 0.5,
    "1/3": 1/3,
    "2/3": 2/3,
    "1/4": 0.25,
    "1/8": 0.125,
    "κ=1/16": 1/16,
    "L₅/44=1/4": 11/44,
    "√ε": math.sqrt(eps),
    "√(ε/3)": math.sqrt(eps/3),
}

print("=" * 70)
print("O10 峰幅度結構搜索")
print("=" * 70)
print("目標: A₂/A₁=0.4434, A₃/A₁=0.4389, A₄/A₁=0.2143, A₅/A₁=0.1414")
print()

# 策略 1: A_m = 3ε × structure(m) — 包含 3ε 特例
print("策略 1: A_m/A₁ = 3ε × S(m)")
print(f"  S(2) = A₂/3ε = {r_true[2]/(3*eps):.4f}  (應該 ≈ 0.9568 if 3ε 略高)")
print(f"  S(3) = A₃/3ε = {r_true[3]/(3*eps):.4f}")
print(f"  S(4) = A₄/3ε = {r_true[4]/(3*eps):.4f}")
print(f"  S(5) = A₅/3ε = {r_true[5]/(3*eps):.4f}")
print()

# S(m) 有咩結構? S(2)≈0.957, S(3)≈0.947, S(4)≈0.462, S(5)≈0.305
# S(3)/S(2) = 0.9899 ≈ 1
# S(4)/S(3) = 0.4883 ≈ 1/2
# S(5)/S(4) = 0.6598 ≈ 2/3? 或 φ⁻¹? φ⁻¹=0.618, 偏差 6.8%
print("策略 2: 連續比率 A_{m+1}/A_m")
ratios = {m: r_true[m+1]/r_true[m] for m in range(1, 5)}
print(f"  A₂/A₁ = {ratios[1]:.4f}")
print(f"  A₃/A₂ = {ratios[2]:.4f}")
print(f"  A₄/A₃ = {ratios[3]:.4f}")
print(f"  A₅/A₄ = {ratios[4]:.4f}")
print()

# 候選比率公式
cand_ratios = {
    "3ε": 3*eps,
    "φ⁻¹": phi_inv,
    "φ⁻¹/√2": phi_inv/math.sqrt(2),
    "ε×3": 3*eps,
    "1/2": 0.5,
    "2/3": 2/3,
    "3/4": 0.75,
    "φ⁻²": phi_inv**2,
    "√ε": math.sqrt(eps),
    "ε×√2": eps*math.sqrt(2),
    "1-ε": 1-eps,
    "1/φ²×2": 2/phi**2,
}
print("連續比率 vs 候選:")
for m in range(2, 5):
    target = r_true[m+1]/r_true[m]
    print(f"  A_{m+1}/A_{m} = {target:.4f}:")
    for name, val in cand_ratios.items():
        dev = abs(target-val)/val*100
        if dev < 10:
            print(f"    {name} = {val:.4f}  (偏差 {dev:.2f}%)")
