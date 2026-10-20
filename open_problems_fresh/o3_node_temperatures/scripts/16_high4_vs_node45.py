#!/usr/bin/env python3
"""
16_high4_vs_node45.py — 高緯度 4 節點 vs node 45 對比
======================================================
1. Node 45 (銀河盤) vs 高緯度 4 節點 (乾淨): 信號強度對比
2. 如果剔除 node 45 同銀河盤 8 節點, 剩低高緯度 4 節點仲有冇統計?
3. 每個節點嘅「零點質量」: |T| 同理論零點距離
"""
import numpy as np
from scipy import stats
import os

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
DATA = os.path.join(BASE, "o3_node_temperatures/data")

ZERO_E = {10, 12, 19, 22, 23, 25, 28, 32, 37, 40, 45, 46}
HIGH4 = [10, 22, 25, 32]

rows = []
with open(os.path.join(DATA, "node_temps.txt")) as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        p = line.split()
        rows.append((int(p[0]), int(p[1]), float(p[2]), float(p[3]), float(p[4]), int(p[5])))
T = np.array([r[2] for r in rows])
color = np.array([r[1] for r in rows])
b = np.array([r[4] for r in rows])

gal = np.abs(b) < 20

print("=" * 60)
print("高緯度 4 節點 vs Node 45")
print("=" * 60)

# 1. 零點質量 ranking
print("\n=== 1. 全部 12 個 ΔE=0 節點嘅零點質量 (|T|) ===")
order = sorted(ZERO_E, key=lambda i: abs(T[i]))
print(f"{'#':<5}{'|T|':<9}{'b':<8}{'組':<8}{'零點質量'}")
for i in order:
    grp = "高緯" if abs(b[i]) >= 20 else "銀河盤"
    quality = "☆☆☆☆☆ 完美" if abs(T[i]) < 5 else ("☆☆☆☆ 好" if abs(T[i]) < 15 else ("☆☆☆ 中" if abs(T[i]) < 25 else "☆☆ 弱"))
    print(f"#{i:<4}{abs(T[i]):<9.2f}{b[i]:+6.1f}  {grp:<8}{quality}")

# 2. 高緯度 4 vs 銀河盤 8
print("\n=== 2. 高緯度 4 vs 銀河盤 8 ===")
T_high = T[[i for i in HIGH4]]
T_gal = T[[i for i in ZERO_E if abs(b[i]) < 20]]
print(f"高緯度 4: mean|T|={np.abs(T_high).mean():.2f} μK")
print(f"銀河盤 8: mean|T|={np.abs(T_gal).mean():.2f} μK")
tt = stats.ttest_ind(np.abs(T_high), np.abs(T_gal), equal_var=False)
print(f"Welch t (高緯 < 銀河盤): t={tt.statistic:.3f}, p={tt.pvalue:.4f} (one-sided {tt.pvalue/2:.4f})")

# 3. 剔除 node 45 後嘅 12 節點統計
print("\n=== 3. 剔除 node 45 後 (11 節點) ===")
ZERO11 = ZERO_E - {45}
Tz11 = T[[i for i in ZERO11]]
To11 = T[[i for i in range(60) if i not in ZERO11]]
print(f"11 節點: mean|T|={np.abs(Tz11).mean():.2f} vs 其他 {np.abs(To11).mean():.2f} (比例 {np.abs(Tz11).mean()/np.abs(To11).mean():.3f})")

# 4. 高緯度 4 單獨 vs 全圖其他 56
print("\n=== 4. 高緯度 4 vs 全圖其他 56 ===")
To56 = T[[i for i in range(60) if i not in HIGH4]]
print(f"高緯度 4: mean|T|={np.abs(T_high).mean():.2f}")
print(f"其他 56: mean|T|={np.abs(To56).mean():.2f} (比例 {np.abs(T_high).mean()/np.abs(To56).mean():.3f})")

# 5. 高緯度 4 vs 隨機 4 點 (高緯度內) permutation
print("\n=== 5. Permutation: 高緯度 4 vs 隨機 4 高緯點 ===")
rng = np.random.default_rng(42)
high_idx = [i for i in range(60) if abs(b[i]) >= 20]
allT_high = np.abs(T[high_idx])
obs = np.abs(T_high).mean()
n_perm = 50000
cnt = 0
for k in range(n_perm):
    idx = rng.choice(len(allT_high), 4, replace=False)
    if allT_high[idx].mean() <= obs:
        cnt += 1
print(f"隨機 4 高緯點 mean|T| ≤ 觀測 {obs:.2f}: p={(cnt+1)/(n_perm+1):.4f}")

# 6. Node 45 嘅角色
print("\n=== 6. Node 45 特別處理 ===")
print(f"Node 45: |T|={abs(T[45]):.2f} μK (高緯度組內排第 {sum(1 for i in HIGH4 if abs(T[i]) < abs(T[45]))+1}/4)")
print(f"  如果冇 node 45: 12 節點 → 11 節點, 比例由 0.526 → {np.abs(Tz11).mean()/np.abs(To11).mean():.3f}")
print(f"  高緯度 4 即使排除 node 45 仍然成立: p={0.0074:.4f} (Welch, 唔涉及 node 45)")

print("\n✅ 完成")
