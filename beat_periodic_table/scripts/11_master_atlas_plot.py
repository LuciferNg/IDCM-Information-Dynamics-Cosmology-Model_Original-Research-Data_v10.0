#!/usr/bin/env python3
"""
11_master_atlas_plot.py — 44×44 Master Atlas 方格地圖視覺化
============================================================
全正方形張量地圖 (宇宙指令總表):
- 下半 (m>n): 差頻 B = ω_m − ω_n (正向, 物質算符, viridis)
- 上半 (m<n): 差頻 B = ω_m − ω_n (負向, CPT 反物質對偶, 同一色條負值)
- 對角線 (m=n): 和頻 4sin(nπ/88) (自耦合, 獨立色)

輸出: master_atlas.png (300 DPI)
"""
import math, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import numpy as np
from matplotlib.patches import Rectangle

font_path = "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc"
if os.path.exists(font_path):
    fm.fontManager.addfont(font_path)
    plt.rcParams["font.family"] = "WenQuanYi Zen Hei"
plt.rcParams["axes.unicode_minus"] = False

Nd = 44
w = lambda n: 2 * math.sin(math.pi * n / 88)

fig, ax = plt.subplots(figsize=(13, 12), dpi=150)

# ===== 差頻矩陣 (反對稱) =====
M = np.zeros((Nd, Nd))
for n in range(Nd):
    for m in range(Nd):
        M[n, m] = w(m + 1) - w(n + 1)   # 差頻, 可負

# ===== 對角線和頻 (自耦合) =====
diag = np.array([w(n) * 2 for n in range(1, Nd + 1)])  # 4sin(nπ/88)

# 用 imshow 畫差頻 (下半+上半)
vmax = max(abs(M.min()), abs(M.max()))
im = ax.imshow(M, cmap="RdBu_r", origin="lower", vmin=-vmax, vmax=vmax,
               extent=[1, 44, 1, 44], aspect="equal")

# ===== 對角線覆蓋: 和頻自耦合 =====
for i in range(Nd):
    ax.plot(i + 1, i + 1, "s", color="black", markersize=11, zorder=6)
    # 對角線格內放和頻值 (白色字)
    ax.text(i + 1, i + 1, f"{diag[i]:.1f}", ha="center", va="center",
            fontsize=5.5, color="white", zorder=7, fontweight="bold")

# ===== 世代三重奏 =====
gen = {(8, 22): "c/s", (10, 24): "u/d", (19, 33): "t/b"}
for (n, m), name in gen.items():
    ax.plot(m, n, "o", color="lime", markersize=10, markeredgecolor="black", zorder=8)
    ax.annotate(name, (m, n), textcoords="offset points", xytext=(8, 8),
                fontsize=9, fontweight="bold", color="lime",
                path_effects=[], bbox=dict(boxstyle="round,pad=0.2", fc="black", ec="lime", alpha=0.8))

# ===== 魔術對角線 (d = m−n) =====
magic = {7: "m7", 14: "GEN", 20: "T(s->d)", 22: "half", 33: "K_tree"}
for d, label in magic.items():
    xs = np.arange(1 + d, 45)
    ys = xs - d
    ax.plot(xs, ys, "--", color="orange", alpha=0.7, lw=1.3)
    ax.text(44, 44 - d, label, fontsize=8, color="orange", va="center", ha="right",
            fontweight="bold")

# ===== 區域標註 =====
ax.text(23, 5, "下三角: 差頻 > 0\n物質算符 (946)", ha="center", fontsize=11,
        color="white", bbox=dict(boxstyle="round,pad=0.4", fc="#1f77b4", alpha=0.85), zorder=9)
ax.text(23, 40, "上三角: 差頻 < 0\nCPT 反物質對偶 (946)", ha="center", fontsize=11,
        color="white", bbox=dict(boxstyle="round,pad=0.4", fc="#d62728", alpha=0.85), zorder=9)
ax.text(33, 33, "對角線: 和頻自耦合\n4sin(nπ/88)", ha="center", fontsize=10,
        color="white", bbox=dict(boxstyle="round,pad=0.4", fc="black", alpha=0.85), zorder=9)

ax.set_xlabel("模態 m (1..44)", fontsize=13)
ax.set_ylabel("模態 n (1..44)", fontsize=13)
ax.set_title("Master Atlas: 44 × 44 宇宙算符總表\n(差頻反對稱 + 對角線自耦合 + 世代鎖定)",
             fontsize=15, fontweight="bold")
ax.set_xticks(range(1, 45, 4))
ax.set_yticks(range(1, 45, 4))
# 用 ASCII 負號避免缺字
import matplotlib.ticker as mticker
ax.xaxis.set_major_formatter(mticker.StrMethodFormatter("{x:g}"))
ax.yaxis.set_major_formatter(mticker.StrMethodFormatter("{x:g}"))
fig.colorbar(im, ax=ax, shrink=0.85, label="差頻 B(n,m) = w_m - w_n")

plt.tight_layout()
out = os.path.join(os.path.dirname(__file__), "..", "master_atlas.png")
fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
print(f"✅ 已輸出: {out}")
print(f"   44×44 = {Nd*Nd} 格, 差頻反對稱 (RdBu), 對角線自耦合 (黑格)")
