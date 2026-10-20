#!/usr/bin/env python3
"""
08_zero_energy_nodes.py — O3: ΔE=0 節點溫度檢驗 (交叉檢驗 §21)
==============================================================
IDCM §21 預言: ΔE=0 節點 (12 個 k=2) 相位正交 → CMB 溫度 ≈ 0 μK
已有結果 (global_routing_table/scripts/32): ΔE=0 mean|T| = 19.05 μK vs 其他 48 19.05/36.18
本 script 喺 O3 完整統計框架下重做, 並加入:
1. 12 節點 |T| vs 48 節點 |T| 比較 (permutation)
2. 個別節點 list
3. 同 bootstrap 隨機 12 點對比
"""
import numpy as np
from scipy import stats
import os

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
DATA = os.path.join(BASE, "o3_node_temperatures/data")

# ΔE=0 節點 (k=2, 2 frustration + 2 normal edges) — 來自 topological-comm-chain
ZERO_E = {10, 12, 19, 22, 23, 25, 28, 32, 37, 40, 45, 46}

rows = []
with open(os.path.join(DATA, "node_temps.txt")) as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        p = line.split()
        rows.append((int(p[0]), int(p[1]), float(p[2])))
T = np.array([r[2] for r in rows])
color = np.array([r[1] for r in rows])

zero_mask = np.array([i in ZERO_E for i in range(60)])
other_mask = ~zero_mask

print("=" * 66)
print("O3: ΔE=0 零能量節點溫度檢驗")
print("=" * 66)

Tz = T[zero_mask]
To = T[other_mask]
print(f"\nΔE=0 節點 (12): {sorted(ZERO_E)}")
print(f"  T: {np.round(Tz, 2)}")
print(f"  mean|T| = {np.abs(Tz).mean():.2f} μK")
print(f"  mean T  = {Tz.mean():+.2f} μK")
print(f"其他 48 節點: mean|T| = {np.abs(To).mean():.2f} μK")
ratio = np.abs(Tz).mean() / np.abs(To).mean()
print(f"比例: {ratio:.3f} (<0.85 先符合預言)")

# ============ 1. Permutation test ============
rng = np.random.default_rng(99)
n_perm = 20000
allT = np.abs(T)
obs = allT[zero_mask].mean()
count = 0
for k in range(n_perm):
    idx = rng.choice(60, 12, replace=False)
    if allT[idx].mean() <= obs:
        count += 1
p_perm = (count + 1) / (n_perm + 1)
print(f"\nPermutation (20000×): 隨機 12 點 |T| mean ≤ 觀測 {obs:.2f} 嘅比例 p = {p_perm:.4f}")

# t-test vs 0
t0, p0 = stats.ttest_1samp(Tz, 0)
print(f"12 節點 t-test vs 0: t={t0:.3f}, p={p0:.4f}")

# ============ 2. 個別節點 ============
print(f"\n個別節點 (|T| 由小到大):")
for i in sorted(ZERO_E, key=lambda i: abs(T[i])):
    c = "冷" if color[i] == 1 else "熱"
    print(f"  #{i}: T={T[i]:+7.2f} μK, |T|={abs(T[i]):6.2f}, 色={c}")

# 有幾多 |T|<15?
print(f"\n|T|<15 μK: {(np.abs(Tz) < 15).sum()}/12")

# ============ 3. Bootstrap vs 隨機 12 點 ============
n_boot = 10000
boot_means = np.empty(n_boot)
for k in range(n_boot):
    idx = rng.choice(60, 12, replace=False)
    boot_means[k] = allT[idx].mean()
z = (obs - boot_means.mean()) / boot_means.std()
p_boot = (boot_means <= obs).mean()
print(f"\nBootstrap 隨機 12 點 mean|T|: mean={boot_means.mean():.2f}, std={boot_means.std():.2f}")
print(f"觀測 {obs:.2f} → z = {z:.2f}σ, p = {p_boot:.4f}")

print("\n✅ ΔE=0 節點檢驗完成")
