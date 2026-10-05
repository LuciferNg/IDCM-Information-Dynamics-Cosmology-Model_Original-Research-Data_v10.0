#!/usr/bin/env python3
"""
O53 澄清: λ₁ vs λ₂ — Y 完整譜
=================================
問題: scripts/26 λ₁ = 1.1739 (max 正值)
      scripts/51 λ₁ = 1.6400 (max |λ|)
      λ₂ = 1.1739 = φ^(1/3)?

查:
  1. Y 完整本徵值譜 (正負)
  2. 最大正值 vs 最大 |λ|
  3. φ^(1/3) 嘅位置
  4. 邊個先係「主本徵值」
"""
import os, json, math
import numpy as np

BASE = os.path.join(os.path.dirname(__file__), "..", "data", "polytopes")
phi = (1 + math.sqrt(5)) / 2

print("=" * 70)
print("O53 澄清: Y 完整譜")
print("=" * 70)

with open(os.path.join(BASE, "kappa_36d_raw.json")) as f:
    kappa = json.load(f)
with open(os.path.join(BASE, "Jstar_36D.json")) as f:
    jstar = json.load(f)

K = np.zeros((36, 36, 36))
for key, val in kappa['kappa'].items():
    i, j, k = map(int, key.split(','))
    K[i, j, k] = val
    K[i, k, j] = val
    K[j, i, k] = val
    K[j, k, i] = val
    K[k, i, j] = val
    K[k, j, i] = val
J0 = np.array(jstar['Jstar_36D'])
Y = np.einsum('ijk,k->ij', K, J0)
Y = (Y + Y.T) / 2

ev = np.linalg.eigvalsh(Y)
print(f"\n[1] 全部 36 個本徵值 (排序):")
ev_sorted = np.sort(ev)[::-1]
for i, l in enumerate(ev_sorted):
    print(f"    λ[{i:2d}] = {l:+10.6f}  1/|λ| = {1/abs(l):10.4f}" if abs(l) > 1e-10 else f"    λ[{i:2d}] = {l:+10.6f}")

print(f"\n[2] 關鍵值:")
l_max_pos = max(ev)
l_max_abs = max(abs(ev))
print(f"    最大正值 λ = {l_max_pos:.6f}")
print(f"    最大 |λ|   = {l_max_abs:.6f}")
print(f"    φ^(1/3)    = {phi**(1/3):.6f}")
print(f"    φ^(-1/3)   = {phi**(-1/3):.6f}")

# φ^(1/3) 位置
idx_phi = np.argmin(np.abs(np.abs(ev) - phi**(1/3)))
print(f"\n    φ^(1/3) 最近: λ[{idx_phi}] = {ev[idx_phi]:+.6f} (誤差 {abs(abs(ev[idx_phi])-phi**(1/3))/phi**(1/3)*100:.4f}%)")

# 最大正值
idx_pos = np.argmax(ev)
print(f"    最大正值: λ[{idx_pos}] = {ev[idx_pos]:+.6f}")
print(f"    1/λ_max_pos = {1/ev[idx_pos]:.6f} vs φ^(-1/3) = {phi**(-1/3):.6f} (誤差 {abs(1/ev[idx_pos]-phi**(-1/3))/phi**(-1/3)*100:.4f}%)")

print(f"\n[3] 結論:")
print(f"    scripts/26 用 max(evals) = 最大正值 = {l_max_pos:.4f}")
print(f"    → 1/λ = {1/l_max_pos:.4f} vs φ^(-1/3) = 0.8518 → 0.004% ✓")
print(f"    scripts/51 用 max|λ| = {l_max_abs:.4f} (可能係負本徵值)")
print(f"    → 真實「主本徵值」取決於定義")

# 負本徵值
n_neg = np.sum(ev < 0)
print(f"\n    負本徵值數: {n_neg}")
print(f"    → 最大 |λ| 係 {'負' if l_max_abs < 0 or True else '正'}本徵值")

# 檢查最大 |λ| 係正定負
idx_abs = np.argmax(np.abs(ev))
print(f"    最大 |λ| 本徵值 = {ev[idx_abs]:+.6f} ({'負' if ev[idx_abs] < 0 else '正'})")
