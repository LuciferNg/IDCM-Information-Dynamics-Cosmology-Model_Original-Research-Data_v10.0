#!/usr/bin/env python3
"""
O53 A2: J* 嘅 φ⁻⁵ 量子化結構
================================
jstar_quantized.json 嘅 t_i 值:
0.09014 ≈ 1/φ⁵ = 0.0901699

分析所有 37 個值: 係咪 φ 指數嘅整數倍?
"""
import os, json, math, sys
import numpy as np

print("=" * 70)
print("O53 A2: J* φ⁻⁵ 量子化")
print("=" * 70)

phi = (1 + math.sqrt(5)) / 2
phi5 = phi ** 5  # ≈ 11.09
inv_phi5 = 1.0 / phi5  # ≈ 0.09017

# 讀 quantized J*
orig_base = "/home/wsl/Projects/IDCM-Original/ICDM-v6.0--Information-Dynamics-Cosmology-Model/data/cy_search/data"
with open(os.path.join(orig_base, "jstar_quantized.json")) as f:
    qt = json.load(f)
t_i = np.array(qt['t_i'])

print(f"[1] quantized t_i (37 個):")
print(f"  unit = 1/φ⁵ = {inv_phi5:.10f}")

# 每個值 ÷ 1/φ⁵
ratios = t_i / inv_phi5
print(f"\n[2] t_i ÷ (1/φ⁵):")
for i, (t, r) in enumerate(zip(t_i, ratios)):
    n = round(r)
    delta = abs(r - n)
    star = " ★" if delta < 0.05 else ""
    print(f"  t_{i:2d} = {t:.10f} → r = {r:.4f} (n≈{n}, Δ={delta:.4f}){star}")

# 統計
deltas = np.abs(ratios - np.round(ratios))
n_near = sum(deltas < 0.05)
print(f"\n[3] 近整數 (Δ<0.05): {n_near}/{len(t_i)} = {n_near/len(t_i)*100:.0f}%")

# 對照: 隨機 37 值用同單位
rng = np.random.default_rng(42)
rand_deltas = []
for _ in range(1000):
    rand = rng.uniform(0, 0.5, 37)  # same range as t_i (0-0.43)
    r_rand = rand / inv_phi5
    rand_deltas.append(np.mean(np.abs(r_rand - np.round(r_rand))))
rand_deltas = np.array(rand_deltas)
print(f"  隨機 mean Δ = {np.mean(rand_deltas):.4f}")
print(f"  觀測 mean Δ = {np.mean(deltas):.4f}")
z = (np.mean(rand_deltas) - np.mean(deltas)) / np.std(rand_deltas)
print(f"  z = {z:.2f}")

# 特殊值: 0.09014 × 特定整數
print(f"\n[4] φ 關係:")
for i, t in enumerate(t_i):
    n = round(t / inv_phi5)
    if n in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13, 21, 34]:
        print(f"  t_{i} = {t:.6f} ≈ {n} × φ⁻⁵")

# 對比 Jstar_36D
with open(os.path.join(orig_base, "Jstar_36D.json")) as f:
    js = json.load(f)
J0 = np.array(js['Jstar_36D'])
print(f"\n[5] Jstar_36D (36 個) ÷ (1/φ⁵):")
r_j = J0 / inv_phi5
d_j = np.abs(r_j - np.round(r_j))
n_j = sum(d_j < 0.05)
print(f"  近整數: {n_j}/{len(J0)} = {n_j/len(J0)*100:.0f}%")
print(f"  mean Δ = {np.mean(d_j):.4f}")

print("\n" + "=" * 70)
print("完成")
print("=" * 70)