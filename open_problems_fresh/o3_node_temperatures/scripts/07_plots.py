#!/usr/bin/env python3
"""
07_plots.py — O3: 圖表輸出
==========================
1. 60 節點溫度分佈直方圖 + 高斯疊加
2. 冷/熱色分組盒鬚圖
3. 溫度 vs BFS 距離散點
4. 天球圖 (60 節點著色 + 溫度大小)
"""
import numpy as np
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os

BASE = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh"
DATA = os.path.join(BASE, "o3_node_temperatures/data")
FIGS = os.path.join(BASE, "o3_node_temperatures/figs")
os.makedirs(FIGS, exist_ok=True)

rows = []
with open(os.path.join(DATA, "node_temps.txt")) as f:
    for line in f:
        if line.startswith("#") or not line.strip():
            continue
        p = line.split()
        rows.append((int(p[0]), int(p[1]), float(p[2]), int(p[5])))
T = np.array([r[2] for r in rows])
color = np.array([r[1] for r in rows])
hop = np.array([r[3] for r in rows])

plt.rcParams.update({'font.size': 11})

# ============ 1. 直方圖 ============
fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(T, bins=14, color='steelblue', edgecolor='white', alpha=0.8, density=True)
xs = np.linspace(T.min()-20, T.max()+20, 200)
ax.plot(xs, stats.norm.pdf(xs, T.mean(), T.std(ddof=1)), 'r-', lw=2, label=f'高斯 (μ={T.mean():.1f}, σ={T.std(ddof=1):.1f})')
ax.axvline(T[0], color='blue', ls='--', lw=1.5, label=f'節點0 冷斑 ({T[0]:.0f}μK)')
ax.axvline(T[57], color='orange', ls='--', lw=1.5, label=f'節點57 對徑 ({T[57]:.0f}μK)')
ax.set_xlabel('T (μK)')
ax.set_ylabel('密度')
ax.set_title('O3: 60 節點 SMICA 4.17° 平滑溫度分佈')
ax.legend()
fig.tight_layout()
fig.savefig(os.path.join(FIGS, "01_temp_hist.png"), dpi=150)
plt.close(fig)
print("✅ 01_temp_hist.png")

# ============ 2. 冷熱盒鬚圖 ============
fig, ax = plt.subplots(figsize=(7, 5))
data = [T[color==1], T[color==0]]
bp = ax.boxplot(data, tick_labels=['冷色 (30)', '熱色 (30)'], patch_artist=True, widths=0.5)
bp['boxes'][0].set_facecolor('lightblue')
bp['boxes'][1].set_facecolor('lightsalmon')
for i in range(60):
    j = 0 if color[i]==1 else 1
    ax.plot(j+1 + np.random.normal(0, 0.04), T[i], 'k.', alpha=0.6, markersize=6)
ax.axhline(0, color='gray', ls=':', lw=1)
ax.set_ylabel('T (μK)')
ax.set_title(f'O3: 冷/熱色分離 (差={T[color==1].mean()-T[color==0].mean():.1f} μK, p≈0.06)')
fig.tight_layout()
fig.savefig(os.path.join(FIGS, "02_coldhot_box.png"), dpi=150)
plt.close(fig)
print("✅ 02_coldhot_box.png")

# ============ 3. 溫度 vs BFS ============
fig, ax = plt.subplots(figsize=(8, 5))
for h in range(9):
    sel = hop == h
    ax.scatter([h]*sel.sum(), T[sel], c=['steelblue' if color[i]==1 else 'salmon' for i in np.where(sel)[0]], s=60, zorder=3)
    if sel.sum() > 0:
        ax.plot(h, T[sel].mean(), 'k^', markersize=10, zorder=4)
ax.set_xlabel('BFS 距離 (到冷斑)')
ax.set_ylabel('T (μK)')
ax.set_xticks(range(9))
ax.axhline(0, color='gray', ls=':', lw=1)
ax.set_title('O3: 溫度 vs BFS 距離 (Spearman ρ=-0.05, p=0.71)')
from matplotlib.lines import Line2D
ax.legend(handles=[Line2D([0],[0], marker='o', color='w', markerfacecolor='steelblue', label='冷色'),
                   Line2D([0],[0], marker='o', color='w', markerfacecolor='salmon', label='熱色'),
                   Line2D([0],[0], marker='^', color='k', label='層平均')])
fig.tight_layout()
fig.savefig(os.path.join(FIGS, "03_temp_vs_bfs.png"), dpi=150)
plt.close(fig)
print("✅ 03_temp_vs_bfs.png")

print("\n✅ 圖表完成")
