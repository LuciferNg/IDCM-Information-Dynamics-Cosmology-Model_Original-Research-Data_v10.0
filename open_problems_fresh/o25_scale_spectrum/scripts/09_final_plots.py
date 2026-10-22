#!/usr/bin/env python3
"""
09_final_plots.py — O25 一次過: 最終合併圖
===========================================
fig5: 全尺度譜 (0.3°-20°) — 冷熱差 + node9 + node0
fig6: ΔE0 比例全譜 (V形 + 大尺度回升)
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import json, os

OUT = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh/o25_scale_spectrum"
FIGS = os.path.join(OUT, "figs")
os.makedirs(FIGS, exist_ok=True)

with open(os.path.join(OUT, "data/scale_spectrum.json")) as f:
    R10 = json.load(f)
with open(os.path.join(OUT, "data/scale_spectrum_large.json")) as f:
    RL = json.load(f)

SCALES10 = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 4.17, 5.0, 7.0, 10.0]
EXT = [12.0, 15.0, 20.0]
ALL = SCALES10 + EXT

# SMICA 10 尺度 + NILC 延伸 (近似 SMICA 大尺度)
diff = [abs(R10['SMICA'][str(s)]['cold_hot_diff_uK']) for s in SCALES10] + \
       [abs(RL['NILC'][str(s)]['cold_hot_diff']) for s in EXT]
n9 = [R10['SMICA'][str(s)]['node9'] for s in SCALES10] + \
     [RL['NILC'][str(s)]['node9'] for s in EXT]
n0 = [R10['SMICA'][str(s)]['node0'] for s in SCALES10] + \
     [RL['NILC'][str(s)]['node0'] for s in EXT]
zero = [R10['SMICA'][str(s)]['zeroE_ratio'] for s in SCALES10] + \
       [RL['NILC'][str(s)]['zeroE_ratio'] for s in EXT]

x = np.array(ALL)
plt.rcParams.update({"font.size": 11, "axes.grid": True, "grid.alpha": 0.3})

# ---- fig5: 全尺度 ----
fig, ax1 = plt.subplots(figsize=(11, 6))
ax1.semilogx(x, np.abs(diff), "o-", color="#d62728", lw=2, ms=7, label="|冷熱差|")
ax1.semilogx(x, np.abs(n0), "s-", color="#1f77b4", lw=2, ms=7, label="|node0 冷斑|")
ax1.semilogx(x, np.abs(n9), "^-", color="#2ca02c", lw=2, ms=7, label="|node9|")
ax1.set_xlabel("平滑尺度 FWHM (°, log)")
ax1.set_ylabel("|T| (μK)")
ax1.set_title("O25: 全尺度譜 0.3°-20° — 冷斑 vs node9 交叉")
ax1.legend(fontsize=10)
# 交叉點標記
ax1.axvline(4.17, color="gray", ls=":", alpha=0.6)
ax1.text(4.17, 200, "4.17°", ha="center", fontsize=9, color="gray")
plt.tight_layout()
plt.savefig(os.path.join(FIGS, "05_full_spectrum.png"), dpi=150)
plt.close()

# ---- fig6: ΔE0 全譜 ----
fig, ax = plt.subplots(figsize=(11, 6))
ax.semilogx(x, zero, "o-", color="#9467bd", lw=2, ms=8, label="ΔE0 比例 (全60)")
ax.axhline(1.0, color="gray", ls=":", alpha=0.6)
ax.axvline(4.17, color="gray", ls=":", alpha=0.5)
ax.text(4.17, 1.02, "4.17°", ha="center", fontsize=9, color="gray")
ax.set_xlabel("平滑尺度 FWHM (°, log)")
ax.set_ylabel("ΔE0 節點 mean|T| / 其他")
ax.set_title("O25: ΔE0 零能量壓制全譜 — V形 @4-5° + 20° 回升至 1.02")
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(FIGS, "06_zeroE_full.png"), dpi=150)
plt.close()

print("✅ figs/05,06 saved")
