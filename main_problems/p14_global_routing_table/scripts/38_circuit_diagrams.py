#!/usr/bin/env python3
"""
GRT-38: 模擬電路原理圖 — 5節點阻挫環 + 節點模組 + A5 全網接線
================================================================
畫出可以照住砌嘅電路圖:
1. 5 節點阻挫環 (Minimal Frustrated Loop)
2. 單節點模組 (Wien bridge 振盪器 + 相位指示 LED)
3. 60 節點 A5 全網接線示意 (阻挫邊 = 反相器)
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle, FancyBboxPatch
import numpy as np
import math
import sys, os

# 中文字形 (文泉驛正黑)
import matplotlib.font_manager as fm
for f in fm.fontManager.ttflist:
    if 'WenQuanYi' in f.name or 'Noto Sans CJK' in f.name:
        plt.rcParams['font.sans-serif'] = [f.name]
        break
plt.rcParams['axes.unicode_minus'] = False

sys.path.insert(0, ".")
from grt_common import (build_graph, compute_frustration_edges,
                        edge_threshold_from_histogram, load_colors,
                        load_nodes, ang_deg)

OUT = "../data"
os.makedirs(OUT, exist_ok=True)

# ============================================================
# 圖 1: 5 節點阻挫環
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(8, 8))
ax.set_aspect('equal')
ax.axis('off')

# 5 節點喺圓上
N5 = 5
angles = [math.pi/2 + 2*math.pi*i/N5 for i in range(N5)]  # 頂部開始
pos5 = [(math.cos(a)*3, math.sin(a)*3) for a in angles]

# 畫邊: 4 正常 (電阻) + 1 阻挫 (反相器)
for i in range(N5):
    j = (i+1) % N5
    p1, p2 = pos5[i], pos5[j]
    mid = ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2)
    if i == 4:  # 阻挫邊 (4,0)
        # 反相放大器符號: 三角形
        tri = mpatches.Polygon([
            (mid[0]-0.35, mid[1]-0.45), (mid[0]-0.35, mid[1]+0.45), (mid[0]+0.4, mid[1])
        ], closed=True, fc='#ffcccc', ec='red', lw=2)
        ax.add_patch(tri)
        ax.plot([p1[0], tri.xy[0][0]], [p1[1], tri.xy[0][1]], 'k-', lw=1.5)
        ax.plot([tri.xy[2][0], p2[0]], [tri.xy[2][1], p2[1]], 'k-', lw=1.5)
        ax.text(mid[0]+0.2, mid[1]+0.55, '反相器\n(π 相移)', fontsize=8, ha='center', color='red')
    else:  # 正常邊: 電阻 (鋸齒符號)
        # 畫線 + 電阻標記
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], 'k-', lw=1.5)
        # 電阻鋸齒 (3 個 Z)
        t = np.linspace(0.3, 0.7, 3)
        for tt in t:
            xm = p1[0] + (p2[0]-p1[0])*tt
            ym = p1[1] + (p2[1]-p1[1])*tt
            ax.plot(xm, ym, 'ks', ms=2)
        # 中點標記
        ax.text(mid[0]+0.15, mid[1]+0.15, 'R', fontsize=9, color='blue')

# 節點
for i, (x, y) in enumerate(pos5):
    circ = Circle((x, y), 0.35, fc='#ffffcc', ec='black', lw=2)
    ax.add_patch(circ)
    ax.text(x, y, f'{i}', fontsize=12, ha='center', va='center', fontweight='bold')

ax.set_title('圖 1: 5 節點阻挫環 (Minimal Frustrated Loop)\n4 正常邊 (電阻 R) + 1 阻挫邊 (反相器, π 相移)',
             fontsize=11)
plt.tight_layout()
plt.savefig(f'{OUT}/circuit_5node_loop.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ 圖 1: 5 節點阻挫環 → circuit_5node_loop.png")

# ============================================================
# 圖 2: 單節點模組 (Wien bridge 振盪器 + LED 指示)
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(10, 8))
ax.set_aspect('equal')
ax.axis('off')

# 佈局
# TL074 (Wien bridge): 中央
# 電阻 R1 R2 (10k), 電容 C1 C2 (10nF)
# 輸出 Vout → 邊耦合電阻
# LED 指示 (兩顆反向並聯)

# 運算放大器符號 (三角形, 中央)
opamp = mpatches.Polygon([
    (0, 0.8), (0, -0.8), (1.6, 0)
], closed=True, fc='#ccffcc', ec='black', lw=2)
ax.add_patch(opamp)
ax.text(0.55, 0.0, '+', fontsize=14, ha='center', va='center')  # 非反相輸入
ax.text(0.55, -0.45, '-', fontsize=14, ha='center', va='center')  # 反相輸入
ax.text(1.75, 0.35, 'TL074', fontsize=10, color='green')

# 輸入端引線
ax.plot([-1.5, 0], [0.45, 0.45], 'k-', lw=1.5)   # + 輸入
ax.plot([-1.5, 0], [-0.45, -0.45], 'k-', lw=1.5)  # - 輸入
ax.text(-2.0, 0.45, 'Vin+', fontsize=9)
ax.text(-2.0, -0.45, 'Vin-', fontsize=9)

# 輸出
ax.plot([1.6, 3.0], [0, 0], 'k-', lw=1.5)
ax.text(3.1, 0.1, 'Vout', fontsize=10, fontweight='bold')

# Wien bridge 網絡 (反饋): R1-C1 串聯 + R2-C2 並聯 (畫喺 - 輸入)
# R1 (上方)
ax.plot([0, -0.9], [-0.45, -1.8], 'k-', lw=1.5)
ax.plot([-0.9, -0.9], [-1.8, -1.3], 'k-', lw=1.5)
# 電阻 R1
ax.plot([-0.9, -1.7], [-1.3, -1.3], 'k-', lw=1.5)
ax.plot([-1.7, -1.7], [-1.3, -1.8], 'k-', lw=1.5)
ax.plot([-1.7, -0.9], [-1.8, -1.8], 'k-', lw=1.5)
ax.text(-1.3, -1.15, 'R1', fontsize=9, color='blue')
# 電容 C1
ax.plot([-0.9, -0.9], [-1.8, -2.4], 'k-', lw=1.5)
ax.plot([-1.2, -0.6], [-2.4, -2.4], 'k-', lw=1.5)
ax.plot([-1.2, -0.6], [-2.55, -2.55], 'k-', lw=1.5)
ax.text(-1.5, -2.35, 'C1', fontsize=9, color='red')
# 接地
ax.plot([-0.9, -0.9], [-2.55, -2.85], 'k-', lw=1.5)
ax.plot([-1.4, -0.4], [-2.85, -2.85], 'k-', lw=1.5)

# 輸出 → 邊耦合 (接去其他節點)
ax.plot([3.0, 3.0], [0, 1.6], 'k-', lw=1.5)
ax.plot([3.0, 4.5], [1.6, 1.6], 'k-', lw=1.5)
# 電阻 Rout
ax.plot([4.5, 4.5], [1.6, 0.9], 'k-', lw=1.5)
ax.plot([4.8, 5.4], [0.9, 0.9], 'k-', lw=1.5)
ax.plot([5.4, 5.4], [0.9, 1.6], 'k-', lw=1.5)
ax.plot([5.4, 6.2], [1.6, 1.6], 'k-', lw=1.5)
ax.text(5.1, 0.7, 'Rout\n10k', fontsize=8, color='blue')
ax.text(6.4, 1.6, '→ 鄰近節點', fontsize=9)

# LED 指示 (兩顆反向並聯, 接到節點)
# 節點電壓輸出 tap
ax.plot([3.0, 3.0], [0, -1.8], 'k-', lw=1.5)
ax.plot([3.0, 4.2], [-1.8, -1.8], 'k-', lw=1.5)
# LED1 (向上, 紅色)
ax.plot([4.2, 4.2], [-1.8, -2.6], 'k-', lw=1.5)
tri1 = mpatches.Polygon([(4.0, -2.6), (4.4, -2.6), (4.2, -3.0)], closed=True, fc='#ff6666', ec='red', lw=1)
ax.add_patch(tri1)
ax.plot([4.2, 4.2], [-3.0, -3.8], 'k-', lw=1.5)
ax.text(3.6, -3.1, 'LED1\n(紅)', fontsize=8, color='red')
# LED2 (向下, 綠色)
ax.plot([5.0, 5.0], [-1.8, -2.6], 'k-', lw=1.5)
tri2 = mpatches.Polygon([(4.8, -3.0), (5.2, -3.0), (5.0, -2.6)], closed=True, fc='#66ff66', ec='green', lw=1)
ax.add_patch(tri2)
ax.plot([5.0, 5.0], [-3.0, -3.8], 'k-', lw=1.5)
ax.text(5.5, -3.1, 'LED2\n(綠)', fontsize=8, color='green')
ax.plot([4.2, 5.0], [-3.8, -3.8], 'k-', lw=1.5)
ax.text(4.6, -4.1, '反並聯\n(正交=熄滅)', fontsize=8, ha='center')

# 電源
ax.text(-2.5, 1.6, '+Vcc', fontsize=10, color='purple')
ax.text(-2.5, -1.2, '-Vcc', fontsize=10, color='purple')
ax.plot([-2.2, -2.2], [1.3, 0.8], 'k-', lw=1.5)
ax.plot([-2.2, -2.2], [-0.8, -1.3], 'k-', lw=1.5)

ax.set_title('圖 2: 單節點模組 - Wien Bridge 振盪器 (TL074)\n+ 反並聯 LED 相位指示 (正交 = 兩顆都熄滅)\n+ 輸出耦合電阻 Rout -> 鄰近節點',
             fontsize=11)
plt.tight_layout()
plt.savefig(f'{OUT}/circuit_node_module.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ 圖 2: 單節點模組 → circuit_node_module.png")

# ============================================================
# 圖 3: 60 節點 A5 全網接線圖
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(10, 10))
ax.set_aspect('equal')
ax.axis('off')

nodes, vecs = load_nodes()
thresh, dists = edge_threshold_from_histogram(vecs)
adj = build_graph(vecs, thresh)
colors = load_colors()
frust = compute_frustration_edges(adj, colors)

# 投影到 2D (用球面 → 平面, 簡單: x=ra, y=dec 或正規化)
# 用 vecs 嘅前兩個分量 (近似)
pos = {}
for i in range(len(nodes)):
    x = vecs[i][0] * 4.2
    y = vecs[i][1] * 4.2
    pos[i] = (x, y)

# ΔE=0 節點標記
zero_nodes = set()
for i in range(len(nodes)):
    k = sum(1 for j in adj[i] if (min(i,j), max(i,j)) in frust)
    if k == 2:
        zero_nodes.add(i)

# 畫邊
n_normal = 0
n_frust = 0
for i in range(len(nodes)):
    for j in adj[i]:
        if j > i:
            p1, p2 = pos[i], pos[j]
            is_frust = (i, j) in frust
            if is_frust:
                n_frust += 1
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], '-', color='red', lw=1.0, alpha=0.6)
            else:
                n_normal += 1
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], '-', color='gray', lw=0.7, alpha=0.5)

# 畫節點
for i in range(len(nodes)):
    x, y = pos[i]
    c = colors[i]
    if i == 0:  # 冷斑
        fc = '#0044ff'
        ec = 'black'
        lw = 2.5
        size = 0.32
    elif i in zero_nodes:  # ΔE=0
        fc = '#ffff00' if c == 1 else '#ffdd00'
        ec = 'black'
        lw = 2.0
        size = 0.28
    else:
        fc = '#88ccff' if c == 1 else '#ff8888'
        ec = 'gray'
        lw = 1.0
        size = 0.20
    circ = Circle((x, y), size, fc=fc, ec=ec, lw=lw)
    ax.add_patch(circ)
    if i in zero_nodes or i == 0:
        ax.text(x, y, str(i), fontsize=6, ha='center', va='center')

# 圖例
legend_elements = [
    mpatches.Patch(fc='#0044ff', ec='black', label='冷斑 (node 0, 錨定)'),
    mpatches.Patch(fc='#ffff00', ec='black', label='ΔE=0 節點 (零能量寫入, LED 熄滅)'),
    mpatches.Patch(fc='#88ccff', ec='gray', label='冷色節點'),
    mpatches.Patch(fc='#ff8888', ec='gray', label='熱色節點'),
    mpatches.Patch(fc='none', ec='red', label=f'阻挫邊 ×{n_frust} (反相器)'),
    mpatches.Patch(fc='none', ec='gray', label=f'正常邊 ×{n_normal} (電阻)'),
]
ax.legend(handles=legend_elements, loc='upper left', fontsize=8, framealpha=0.9)

ax.set_title('圖 3: 60 節點 A5 晶網 — 完整模擬電路接線圖\n紅線 = 阻挫邊 (反相器, π 相移) ×32 | 灰線 = 正常邊 (電阻) ×88\n黃色 = ΔE=0 節點 (零能量寫入位, LED 熄滅) ×12 | 藍色 = 冷斑錨定',
             fontsize=11)
plt.tight_layout()
plt.savefig(f'{OUT}/circuit_a5_full.png', dpi=150, bbox_inches='tight')
plt.close()
print(f"✅ 圖 3: 60 節點 A5 → circuit_a5_full.png (阻挫 {n_frust}, 正常 {n_normal})")

# ============================================================
# 圖 4: 注入寫入示意 (可選)
# ============================================================
fig, ax = plt.subplots(1, 1, figsize=(8, 6))
ax.set_aspect('equal')
ax.axis('off')

# 節點 + 注入
node_pos = (0, 0)
circ = Circle(node_pos, 0.5, fc='#ffff00', ec='black', lw=2)
ax.add_patch(circ)
ax.text(0, 0, 'ΔE=0\n節點', fontsize=9, ha='center', va='center')

# 注入訊號源
ax.plot([0, 0], [0.5, 1.5], 'k-', lw=2)
ax.plot([0, 0], [1.5, 2.5], 'k-', lw=2)
# 訊號源符號 (圓圈 + ~)
sig = Circle((0, 2.5), 0.5, fc='#ccffff', ec='black', lw=2)
ax.add_patch(sig)
ax.text(0, 2.5, '~', fontsize=16, ha='center', va='center')
ax.text(0, 3.3, '注入訊號\nf = 1 kHz\n相位 = θ+π', fontsize=9, ha='center')
ax.annotate('', xy=(0, 1.0), xytext=(0, 1.6),
            arrowprops=dict(arrowstyle='->', lw=2, color='red'))
ax.text(0.7, 1.3, '注入鎖定\n(相位滑移 π)', fontsize=9, color='red')

# 寫入結果
ax.text(3.5, 0, '→ 相位翻轉 π', fontsize=11, ha='center', color='blue')
ax.annotate('', xy=(2.5, 0), xytext=(0.7, 0),
            arrowprops=dict(arrowstyle='->', lw=2, color='blue'))

# 阻挫圖案
ax.plot([0.5, 2.0], [0.8, 0.8], 'r-', lw=2)
ax.plot([2.0, 2.0], [0.8, -0.8], 'r-', lw=2)
ax.plot([2.0, 0.5], [-0.8, -0.8], 'r-', lw=2)
ax.text(3.3, 0.9, '阻挫圖案\n改變\n(訊息寫入)', fontsize=9, color='red')

ax.set_title('圖 4: 注入鎖定寫入示意\n外加反相信號 → ΔE=0 節點相位滑移 π → 阻挫圖案改變',
             fontsize=11)
plt.tight_layout()
plt.savefig(f'{OUT}/circuit_injection_write.png', dpi=150, bbox_inches='tight')
plt.close()
print("✅ 圖 4: 注入寫入 → circuit_injection_write.png")

print("\n✅ 4 張電路圖全部生成!")
