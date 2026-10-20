#!/usr/bin/env python3
"""
10_red_flag_check.py — O3: 紅燈驗證 (銀河盤偏差)
================================================
重現 03_red_flag_galactic_plane.md 嘅所有關鍵數字:
1. ΔE=0 節點銀河盤集中度 (8/12, binomial p)
2. 銀河盤內外 2×2 表
3. 高緯度剔除後信號 (Welch p)
4. 節點 45 位置
"""
import numpy as np
from scipy import stats
import os

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
DATA = os.path.join(BASE, "o3_node_temperatures/data")

ZERO_E = {10, 12, 19, 22, 23, 25, 28, 32, 37, 40, 45, 46}

rows = []
with open(os.path.join(DATA, "node_temps.txt")) as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        p = line.split()
        rows.append((int(p[0]), float(p[2]), float(p[4])))
T = np.array([r[1] for r in rows])
b = np.array([r[2] for r in rows])

ze = np.array([i in ZERO_E for i in range(60)])
gal = np.abs(b) < 20

print("=" * 66)
print("O3: 紅燈驗證 — ΔE=0 銀河盤偏差")
print("=" * 66)

# 1. 集中度
n_in = (ze & gal).sum()
print(f"\n=== 1. ΔE=0 銀河盤集中度 ===")
print(f"ΔE=0 喺銀河盤: {n_in}/12")
print(f"A₅ 整體: {gal.sum()}/60 = {gal.sum()/60*100:.1f}%")
p_bin = stats.binomtest(n_in, 12, gal.sum()/60).pvalue
print(f"Binomial p = {p_bin:.4f}")

# 隨機對照
rng = np.random.default_rng(7)
cnt = np.zeros(100000)
for k in range(len(cnt)):
    idx = rng.choice(60, 12, replace=False)
    cnt[k] = (np.abs(b[idx]) < 20).sum()
print(f"隨機 12 節點 ≥{n_in} 喺銀河盤: {(cnt>=n_in).mean()*100:.2f}%")

# 2. 2×2 表
Tz_g = T[ze & gal]; To_g = T[~ze & gal]
Tz_c = T[ze & ~gal]; To_c = T[~ze & ~gal]
print(f"\n=== 2. 2×2 表 (mean|T|) ===")
print(f"銀河盤 ΔE=0 ({len(Tz_g)}): {np.abs(Tz_g).mean():.2f} vs 其他 ({len(To_g)}): {np.abs(To_g).mean():.2f}")
print(f"高緯度 ΔE=0 ({len(Tz_c)}): {np.abs(Tz_c).mean():.2f} vs 其他 ({len(To_c)}): {np.abs(To_c).mean():.2f}")
if len(Tz_c) > 3 and len(To_c) > 3:
    p_high = stats.ttest_ind(np.abs(Tz_c), np.abs(To_c), equal_var=False).pvalue
    print(f"高緯度 Welch p = {p_high:.4f}")
if len(Tz_g) > 3 and len(To_g) > 3:
    p_gal = stats.ttest_ind(np.abs(Tz_g), np.abs(To_g), equal_var=False).pvalue
    print(f"銀河盤 Welch p = {p_gal:.4f}")

# 3. 節點 45
print(f"\n=== 3. 節點 45 ===")
print(f"b = {b[45]:+.1f}° → {'🔴 銀河盤' if abs(b[45])<20 else '🟢 高緯度'}")
print(f"銀河盤非ΔE=0 節點 |T| min = {np.abs(To_g).min():.1f}")

# 4. 高緯度節點 list
print(f"\n=== 4. 高緯度 ΔE=0 節點 ===")
for i in sorted(ZERO_E):
    if abs(b[i]) >= 20:
        print(f"  #{i}: T={T[i]:+.2f}, b={b[i]:+.1f}")

# 5. 一致性
ratio_high = np.abs(Tz_c).mean() / np.abs(To_c).mean()
ratio_gal = np.abs(Tz_g).mean() / np.abs(To_g).mean()
print(f"\n=== 5. 結論 ===")
print(f"高緯度比例: {ratio_high:.3f} (p={p_high:.4f})")
print(f"銀河盤比例: {ratio_gal:.3f} (p={p_gal:.4f})")
print(f"兩個區域都 <1: {'✅ 方向一致' if ratio_high < 1 and ratio_gal < 1 else '❌ 唔一致'}")
print("信號唔係純銀河效應, 但 8/12 節點受污染")
