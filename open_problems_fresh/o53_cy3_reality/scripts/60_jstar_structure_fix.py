#!/usr/bin/env python3
"""
O53 路徑一 (修正): J* 結構重檢
==================================
J* ∈ [0.0012, 0.0385] — 全部細過 1

正確形式: J*_i = A·φ^(-k_i), k_i > 0
ln(J*) = ln(A) − k·lnφ → k = (lnA − lnJ)/lnφ

但 A 係全局 normalization — 需要 fit
"""
import os, json, math
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2
lnphi = math.log(phi)

with open(os.path.join(BASE, "Jstar_36D.json")) as f:
    jstar = json.load(f)
J0 = np.array(jstar['Jstar_36D'])
lnJ = np.log(J0)

print("=" * 70)
print("O53 路徑一修正: J* 結構")
print("=" * 70)

print(f"\n[1] J* 基本:")
print(f"    J* ∈ [{J0.min():.4f}, {J0.max():.4f}]")
print(f"    lnJ ∈ [{lnJ.min():.2f}, {lnJ.max():.2f}]")

# 假設 J* = φ^(-k), k = -lnJ/lnφ (A=1)
k = -lnJ/lnphi
print(f"\n[2] J* = φ^(-k) (A=1):")
print(f"    k 範圍: {k.min():.2f} 至 {k.max():.2f}")
print(f"    k 近整數: {np.sum(np.abs(k - np.round(k)) < 0.2)}/36")
print(f"    k 值 (排序): {np.array2string(np.sort(k), precision=2)}")

# k 近半整數?
print(f"\n[3] k 近 n/2:")
k_half = np.abs(k - np.round(k*2)/2)
print(f"    k 離 n/2 格點 mean: {k_half.mean():.4f}")

# k 近 n/3?
k_third = np.abs(k - np.round(k*3)/3)
print(f"    k 離 n/3 格點 mean: {k_third.mean():.4f}")

# k 近 n/4?
k_q = np.abs(k - np.round(k*4)/4)
print(f"    k 離 n/4 格點 mean: {k_q.mean():.4f}")

# k 近 n/6?
k_6 = np.abs(k - np.round(k*6)/6)
print(f"    k 離 n/6 格點 mean: {k_6.mean():.4f}")

# k 近 n/12?
k_12 = np.abs(k - np.round(k*12)/12)
print(f"    k 離 n/12 格點 mean: {k_12.mean():.4f}")

# 隨機對照
rng = np.random.default_rng(1)
rand_k = rng.uniform(k.min(), k.max(), 36)
rand_12 = np.abs(rand_k - np.round(rand_k*12)/12)
print(f"    隨機 n/12 mean: {rand_12.mean():.4f}")

print(f"\n[4] k 結構:")
print(f"    k ∈ [{k.min():.2f}, {k.max():.2f}] — 13.99 至 6.77")
print(f"    k 值分佈:")
ks = np.sort(k)
print(f"    {np.array2string(ks, precision=2)}")
# 有冇 cluster?
print(f"    k < 8: {np.sum(k < 8)}")
print(f"    k 8-10: {np.sum((k >= 8) & (k <= 10))}")
print(f"    k > 10: {np.sum(k > 10)}")

print("\n[5] 結論:")
print(f"    J* = φ^(-k), k ∈ [6.77, 13.99]")
print(f"    → k 就係 J* 嘅 φ 指數 (負)")
print(f"    → k 近整數率: {np.sum(np.abs(k - np.round(k)) < 0.2)}/36")
print(f"    → 之前『J* ≈ φ^(-n) 72%』係用 threshold 0.35")
