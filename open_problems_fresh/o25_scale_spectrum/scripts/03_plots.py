#!/usr/bin/env python3
"""
03_plots.py — O25: 尺度譜圖表
===============================
fig1: 冷熱差 |ΔT| vs 尺度 (雙指數擬合)
fig2: 高緯 ΔE0 比例 vs 尺度 (V形 + 二次擬合)
fig3: node0/node9/node57 vs 尺度
fig4: 三地圖一致性 per 尺度
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
    R = json.load(f)
with open(os.path.join(OUT, "data/decay_analysis.json")) as f:
    D = json.load(f)

SCALES = [0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 4.17, 5.0, 7.0, 10.0]
S = np.array(SCALES)

plt.rcParams.update({"font.size": 11, "axes.grid": True, "grid.alpha": 0.3})

# ---- fig1: 冷熱差 ----
sm = R["SMICA"]
diffs = np.array([sm[str(s)]["cold_hot_diff_uK"] for s in SCALES])
fig, ax = plt.subplots(figsize=(9, 5.5))
ax.plot(S, np.abs(diffs), "o-", color="#d62728", lw=2, ms=7, label="|冷-熱差| (SMICA)")
# 雙指數擬合
a1, t1, a2, t2, c = D["decay_models"]["exp5"]["params"]
theta = np.linspace(0.4, 10.5, 300)
fit = a1*np.exp(-theta/t1) + a2*np.exp(-theta/t2) + c
ax.plot(theta, fit, "--", color="black", lw=1.5, alpha=0.7,
        label=f"雙指數: {a1:.1f}e^(−θ/{t1:.2f}) + {a2:.1f}e^(−θ/{t2:.2f}) + {c:.1f}")
# 結構尺度標記
for x, lbl in [(4.17, "4.17°"), (5.0, "5.0°"), (6.75, "φ·4.17")]:
    ax.axvline(x, color="gray", ls=":", alpha=0.7)
    ax.text(x, ax.get_ylim()[1]*0.95, lbl, ha="center", fontsize=9, color="gray")
ax.set_xlabel("平滑尺度 FWHM (°)")
ax.set_ylabel("|冷色 mean − 熱色 mean| (μK)")
ax.set_title("O25: 冷熱差隨平滑尺度衰減 (雙指數, BIC=−31.7)")
ax.legend(loc="upper right", fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(FIGS, "01_coldhot_decay.png"), dpi=150)
plt.close()

# ---- fig2: 高緯 ΔE0 比例 ----
ratios = np.array(D["hi_zero_ratios"].values()) if isinstance(D["hi_zero_ratios"], dict) else np.array(list(D["hi_zero_ratios"].values()))
ratios = np.array([D["hi_zero_ratios"][str(s)] for s in SCALES])
fig, ax = plt.subplots(figsize=(9, 5.5))
ax.plot(S, ratios, "s-", color="#1f77b4", lw=2, ms=7, label="高緯 ΔE0 mean|T| / 其他 (SMICA)")
# 二次擬合
a, b, c = D["hi_zero_quad_fit"]["a"], D["hi_zero_quad_fit"]["b"], D["hi_zero_quad_fit"]["c"]
fit = a*theta**2 + b*theta + c
ax.plot(theta, fit, "--", color="black", lw=1.5, alpha=0.7,
        label=f"二次: r(θ)={a:.4f}θ²{b:+.3f}θ{c:+.3f}")
ts = D["hi_zero_quad_fit"]["theta_star"]
ax.axvline(ts, color="red", ls="--", alpha=0.8)
ax.text(ts+0.2, 0.55, f"θ*={ts:.1f}°", color="red", fontsize=10)
ax.axhline(1.0, color="gray", ls=":", alpha=0.6)
for x, lbl in [(4.17, "4.17°"), (5.0, "5.0°")]:
    ax.axvline(x, color="gray", ls=":", alpha=0.5)
    ax.text(x, 0.85, lbl, ha="center", fontsize=9, color="gray")
ax.set_xlabel("平滑尺度 FWHM (°)")
ax.set_ylabel("ΔE0 節點 mean|T| / 其他節點 mean|T|")
ax.set_title("O25: ΔE0 零能量壓制 V 形 — 最小值 @ ~5-6°")
ax.legend(loc="upper right", fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(FIGS, "02_zeroE_vshape.png"), dpi=150)
plt.close()

# ---- fig3: 特殊節點 ----
node0 = np.array([sm[str(s)]["node0"] for s in SCALES])
node9 = np.array([sm[str(s)]["node9"] for s in SCALES])
node57 = np.array([sm[str(s)]["node57"] for s in SCALES])
fig, ax = plt.subplots(figsize=(9, 5.5))
ax.plot(S, node0, "o-", color="#d62728", lw=2, ms=7, label="node0 冷斑")
ax.plot(S, node9, "s-", color="#1f77b4", lw=2, ms=7, label="node9 第二冷")
ax.plot(S, node57, "^-", color="#2ca02c", lw=2, ms=7, label="node57 對徑")
ax.axhline(0, color="gray", ls=":", alpha=0.6)
ax.axvline(4.17, color="gray", ls=":", alpha=0.5)
ax.text(4.17, 50, "4.17°", ha="center", fontsize=9, color="gray")
ax.set_xlabel("平滑尺度 FWHM (°)")
ax.set_ylabel("T (μK)")
ax.set_title("O25: 特殊節點溫度尺度譜")
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(FIGS, "03_special_nodes.png"), dpi=150)
plt.close()

# ---- fig4: 三地圖 ----
fig, axes = plt.subplots(1, 3, figsize=(15, 4.5), sharex=True)
for ax, m in zip(axes, ["SMICA", "NILC", "Commander"]):
    r = R[m]
    d = np.array([r[str(s)]["cold_hot_diff_uK"] for s in SCALES])
    z = np.array([r[str(s)]["zeroE_ratio"] for s in SCALES])
    ax.plot(S, np.abs(d), "o-", color="#d62728", lw=2, ms=6, label="|冷熱差|")
    ax2 = ax.twinx()
    ax2.plot(S, z, "s-", color="#1f77b4", lw=2, ms=6, label="ΔE0比")
    ax2.set_ylabel("ΔE0 比例", color="#1f77b4")
    ax2.tick_params(axis="y", labelcolor="#1f77b4")
    ax.set_title(m)
    ax.set_xlabel("FWHM (°)")
    ax.set_ylabel("|冷熱差| (μK)", color="#d62728")
    ax.tick_params(axis="y", labelcolor="#d62728")
plt.tight_layout()
plt.savefig(os.path.join(FIGS, "04_three_maps.png"), dpi=150)
plt.close()

print("✅ figs/01-04 saved")
