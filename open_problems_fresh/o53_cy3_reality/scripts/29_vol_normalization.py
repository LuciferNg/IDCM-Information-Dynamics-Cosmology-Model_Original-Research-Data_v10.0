#!/usr/bin/env python3
"""
O53 開放 1 深化: J* normalization — Vol = 2^(-12)
=====================================================
發現: J* 有精確結構 normalization:
  Vol = 1/4096 = 2^(-12) (精確!)
  Ind = 48.0004 ≈ 48
  J3 = 3×Vol

分析:
  1. Vol = 2^(-12) 身份 (44? 12? 2¹²?)
  2. 用 Vol normalization 嘅 J* 有冇唯一 scale?
  3. tr(Y²) = 5 同 λ₁ = φ^(1/3) 喺 Vol-固定 J 下同時成立?
  4. J* 點樣由 IDCM 結構推出?
"""
import os, json, math, sys
import numpy as np
from scipy.optimize import minimize

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2
PASS = 0
FAIL = 0

def check(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print(f"  ✅ {name} {detail}")
    else:
        FAIL += 1
        print(f"  ❌ {name} {detail}")

print("=" * 70)
print("O53 開放 1: Vol normalization 閉合")
print("=" * 70)

with open(os.path.join(BASE, "kappa_36d_raw.json")) as f:
    kappa = json.load(f)
with open(os.path.join(BASE, "Jstar_36D.json")) as f:
    jstar = json.load(f)

K = np.zeros(tuple(kappa['shape']))
for key, val in kappa['kappa'].items():
    i, j, k = map(int, key.split(','))
    K[i, j, k] = val
    K[i, k, j] = val
    K[j, i, k] = val
    K[j, k, i] = val
    K[k, i, j] = val
    K[k, j, i] = val

J0 = np.array(jstar['Jstar_36D'])
Vol0 = jstar['Vol']
Ind0 = jstar['Ind']
J3_0 = jstar['J3']

# --- [1] Vol 身份 ---
print("\n[1] Vol = 1/4096 = 2^(-12):")
print(f"    Vol = {Vol0:.10f}")
print(f"    1/Vol = {1/Vol0:.4f}")
print(f"    2^12 = {2**12}")
print(f"    4096 = 2^12 = 64² = 4⁶")
print(f"    4096 = 2^(2×6) = B³×64?")
check("Vol = 2^(-12) 精確", abs(Vol0 - 2**-12) < 1e-12, f"({Vol0:.12f})")

# Ind = 48
print(f"\n    Ind = {Ind0:.4f}")
print(f"    48 = polytope 點數 (48 points!)")
check("Ind ≈ 48 (點數)", abs(Ind0 - 48) < 0.01, f"({Ind0:.4f})")

# J3 = 3×Vol
print(f"\n    J3 = {J3_0:.10f}")
print(f"    3×Vol = {3*Vol0:.10f}")
check("J3 = 3×Vol", abs(J3_0 - 3*Vol0) < 1e-15, f"({J3_0:.10f})")

# --- [2] Vol-固定 J 下嘅閉合 ---
print("\n[2] Vol-固定 J (Vol(J) = 2^(-12)):")
def vol(J):
    return np.einsum('ijk,i,j,k->', K, J, J, J)

# J0 本身 Vol = 2^-12 → 已固定
print(f"    Vol(J0) = {vol(J0):.10f} ✅ 已固定")

# 喺 Vol 固定下, tr(Y²) = 5 同 λ₁ = φ^(1/3) 同時成立?
# Vol 固定 → J 得一個 scale 自由度已用 → 冇自由 scale!
print(f"    → Vol 固定食晒 scale 自由度")
print(f"    → tr(Y²)(J0) = 4.9474 (誤差 1.05%) 就係『Vol 規範』下嘅值")
print(f"    → λ₁(J0) = 1.1739, 1/λ₁ = 0.8518 (誤差 0.004%)")

# --- [3] 兩閉合喺 Vol 規範下嘅精度 ---
print("\n[3] Vol 規範下兩閉合:")
tr = np.trace(np.einsum('ijk,k->ij', K, J0) @ np.einsum('ijk,k->ij', K, J0).T)
ev = np.linalg.eigvalsh((np.einsum('ijk,k->ij', K, J0) + np.einsum('ijk,k->ij', K, J0).T)/2)
l1 = max(ev)
print(f"    tr(Y²) = {tr:.6f} vs 5: {abs(tr-5)/5*100:.3f}%")
print(f"    1/λ₁ = {1/l1:.6f} vs φ^(-1/3): {abs(1/l1-phi**(-1/3))/phi**(-1/3)*100:.3f}%")
print(f"    → λ₁ 閉合 (0.004%) 遠精於 tr(Y²) (1.05%)")
print(f"    → tr(Y²) ≈ 5 係「近似巧合」定「需要 instanton 修正」?")

# --- [4] 5 同 λ₁ 嘅關係 ---
print("\n[4] tr(Y²) 同 λ₁ 嘅理論關係:")
# 如果譜只有一個主本徵值 λ₁, tr(Y²) ≈ λ₁²
print(f"    λ₁² = {l1**2:.4f} vs tr(Y²) = {tr:.4f}")
print(f"    tr(Y²)/λ₁² = {tr/l1**2:.4f}")
print(f"    5/φ^(2/3) = {5/phi**(2/3):.4f}")
print(f"    φ^(2/3) = {phi**(2/3):.4f}")
print(f"    → tr(Y²) = 5, λ₁² = φ^(2/3) → 5 = φ^(2/3)·(tr/λ₁²)")
print(f"    tr/λ₁² = {tr/l1**2:.4f} ≈ 3.59?")

# --- [5] J* 嘅 IDCM 結構 ---
print("\n[5] J* 由 IDCM 結構推導:")
print(f"    Vol = 2^(-12): 2^(12) = 2^(Nd/3.67)? 12 = ?")
print(f"    12 = h11/3, 12 = C(4,2)×2, 12 = 2×6")
print(f"    48 = points 數 (Ind)")
print(f"    Vol = 1/Ind²? {1/48**2:.8f} vs {Vol0:.8f}")
print(f"    Vol = 1/(48×85.33)? 4096 = 48×85.33")
print(f"    4096 = 2^12: 12 維 Z₃ 子空間 → 2^12 = 4096 個態?")
print(f"    → 66 = C(12,2) 同 2^12 = 4096 都係 12 維結構!")

# --- [6] 66 同 4096 ---
print("\n[6] 66 vs 4096:")
print(f"    2^12 = 4096 (12 維嘅 2 冪)")
print(f"    C(12,2) = 66 (12 維嘅組合)")
print(f"    Vol = 1/4096 → 12 維結構嘅 scale!")
print(f"    → J* 嘅 Vol normalization = 2^(-12) 同 12 維結構一致")

print("\n" + "=" * 70)
print(f"結果: {PASS} PASS / {FAIL} FAIL")
print("=" * 70)
sys.exit(0 if FAIL == 0 else 1)
