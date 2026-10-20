#!/usr/bin/env python3
"""
04_ladder_corr.py — O3: 溫度 vs BFS 距離相關
=============================================
1. Spearman 相關 (溫度 vs BFS 距離)
2. 每層 BFS 距離平均溫度 (ladder 檢驗)
3. Fibonacci ladder 模型 (F₅@d0, F₄@d1, F₃@≥d2) vs 觀測
4. 冷斑距離-溫度衰減趨勢檢驗
"""
import numpy as np
from scipy import stats
import os

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
DATA = os.path.join(BASE, "o3_node_temperatures/data")

# ============ 載入 ============
rows = []
with open(os.path.join(DATA, "node_temps.txt")) as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        p = line.split()
        rows.append((int(p[0]), int(p[1]), float(p[2]), float(p[3]), float(p[4]), int(p[5])))
T = np.array([r[2] for r in rows])
color = np.array([r[1] for r in rows])
hop = np.array([r[5] for r in rows])

print("=" * 66)
print("O3: 溫度 vs BFS 距離")
print("=" * 66)

# ============ 1. Spearman 相關 ============
print("\n=== 1. Spearman 相關 ===")
rho, p_rho = stats.spearmanr(T, hop)
print(f"T vs hop: rho={rho:.4f}, p={p_rho:.4f}")
rho_abs, p_abs = stats.spearmanr(np.abs(T), hop)
print(f"|T| vs hop: rho={rho_abs:.4f}, p={p_abs:.4f}")
# 剔除節點 0 (冷斑本身) 再算
mask1 = np.arange(60) != 0
rho2, p2 = stats.spearmanr(T[mask1], hop[mask1])
print(f"T vs hop (剔除節點0): rho={rho2:.4f}, p={p2:.4f}")

# ============ 2. 每層 BFS 平均 ============
print("\n=== 2. 每層 BFS 距離平均溫度 ===")
print("hop  n   mean_T   std_T   median_T")
for h in range(9):
    sel = hop == h
    if sel.sum() > 0:
        print(f"  {h}  {sel.sum():2d}  {T[sel].mean():+8.2f}  {T[sel].std(ddof=1):6.2f}  {np.median(T[sel]):+8.2f}")

# 層間趨勢檢驗 (Jonckheere-Terpstra)
print("\n--- 層間趨勢檢驗 ---")
# 簡單: 第一層 vs 其他
d0 = T[hop == 0]
d1 = T[hop == 1]
d2p = T[hop >= 2]
print(f"d0 (冷斑): {d0[0]:+.2f} μK")
print(f"d1 (4 節點): mean={d1.mean():+.2f}")
print(f"d≥2 (55 節點): mean={d2p.mean():+.2f}")
tt = stats.ttest_ind(d1, d2p, equal_var=False)
print(f"d1 vs d≥2 Welch t: p={tt.pvalue:.4f}")

# ============ 3. Fibonacci ladder 模型 ============
print("\n=== 3. Fibonacci ladder 模型 ===")
# IDCM ladder: F₅=150μK@d0, F₄=90μK@d1, F₃=60μK@d≥2
# 但節點有正負號 (冷=負, 熱=正) — 模型應該比較 |T|
# 用 BFS 距離分層嘅 |T| 期望
F5, F4, F3 = 150, 90, 60  # μK 單位振幅
model_amp = np.where(hop == 0, F5, np.where(hop == 1, F4, F3))
obs_amp = np.abs(T)
print("hop  n   |T| mean   model   ratio")
for h in range(9):
    sel = hop == h
    if sel.sum() > 0:
        print(f"  {h}  {sel.sum():2d}  {obs_amp[sel].mean():7.2f}  {model_amp[sel][0]:5d}  {obs_amp[sel].mean()/model_amp[sel][0]:.3f}")

# 相關 (觀測 |T| vs 模型)
rho_m, p_m = stats.spearmanr(obs_amp, model_amp)
print(f"|T| vs model amplitude: rho={rho_m:.4f}, p={p_m:.4f}")

# 交替模型: 連續衰減 A = F₅·φ^(-d/2)
phi = (1 + 5**0.5) / 2
model_cont = 150 * phi**(-hop/2)
rho_c, p_c = stats.spearmanr(obs_amp, model_cont)
print(f"|T| vs 連續模型 (F₅φ^(-d/2)): rho={rho_c:.4f}, p={p_c:.4f}")

# ============ 4. 冷斑衰減輪廓 ============
print("\n=== 4. 冷斑衰減輪廓 ===")
# 冷色節點嘅 |T| 按 hop
print("冷色節點 |T| 按層:")
for h in range(9):
    sel = (hop == h) & (color == 1)
    if sel.sum() > 0:
        print(f"  d{h}: n={sel.sum()}, |T| mean={np.abs(T[sel]).mean():7.2f}, sign match={np.mean((T[sel]<0)):.0%}")

# 冷色節點溫度應該隨距離遞減 (ladder) — 但帶正負號
# 冷色節點平均溫度 vs hop
print("\n冷色節點平均溫度 (帶符號):")
for h in range(9):
    sel = (hop == h) & (color == 1)
    if sel.sum() > 0:
        print(f"  d{h}: n={sel.sum()}, T mean={T[sel].mean():+7.2f}")

# ============ 5. 對徑點檢查 ============
print("\n=== 5. 對徑點 (節點 57) ===")
i57 = 57
print(f"節點 57: T={T[i57]:+.2f} μK, hop={hop[i57]}, 色={'冷' if color[i57]==1 else '熱'}")
print(f"距離冷斑: 8 hops (對徑)")

# 對徑點嘅「冷色但正溫」謎題: 檢查佢係咪孤例
other_cold_pos = [(i, T[i]) for i in range(60) if color[i] == 1 and T[i] > 0]
print(f"\n冷色但正溫節點: {len(other_cold_pos)} 個")
for i, t in other_cold_pos:
    print(f"  #{i}: T={t:+.2f} μK, hop={hop[i]}")
other_hot_neg = [(i, T[i]) for i in range(60) if color[i] == 0 and T[i] < 0]
print(f"熱色但負溫節點: {len(other_hot_neg)} 個")
for i, t in other_hot_neg:
    print(f"  #{i}: T={t:+.2f} μK, hop={hop[i]}")

print("\n✅ Ladder 檢驗完成")
