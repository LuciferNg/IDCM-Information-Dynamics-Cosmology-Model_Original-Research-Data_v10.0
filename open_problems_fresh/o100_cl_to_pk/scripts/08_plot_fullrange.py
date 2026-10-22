#!/usr/bin/env python3
"""
O100: P_3D(k) IDCM 線譜 vs BOSS DR12 (Gil-Marín 2016 全範圍) — 合併圖
====================================================================
左: log-log P(k) — BOSS CMASS/LOWZ post-recon 點 + IDCM 9 線 (三角)
右: wiggle P/P_smooth — 峰位 + IDCM 線位 (垂直虛線), 標出 0.5% 命中
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["font.sans-serif"] = ["WenQuanYi Zen Hei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["mathtext.fontset"] = "dejavusans"

WORK = "/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o100_cl_to_pk"
DATA = f"{WORK}/data/gilmarin16"

def load_measurement(path):
    k, p = [], []
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        try:
            k.append(float(parts[0])); p.append(float(parts[1]))
        except ValueError:
            pass
    return np.array(k), np.array(p)

lines = np.loadtxt(f"{WORK}/data/P3D_lines.dat")
k_h = lines[:, 3]; P_id_h = lines[:, 6] / 0.6727**3

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5.2))

colors = {"CMASS": "#d62728", "LOWZ": "#1f77b4"}
for name, fname in [
    ("CMASS", "post-recon/cmass/GilMarin_2016_CMASSDR12_measurement_monopole_post_recon.txt"),
    ("LOWZ",  "post-recon/lowz/GilMarin_2016_LOWZDR12_measurement_power_spectrum_monopole_post_recon.txt"),
]:
    k, P = load_measurement(f"{DATA}/{fname}")
    m = (k >= 0.02) & (k <= 0.30)
    ax1.loglog(k[m], P[m], "o-", ms=3.5, lw=0.8, color=colors[name], label=f"{name} (zeff={0.57 if name=='CMASS' else 0.32})")
    # wiggle
    from scipy.ndimage import gaussian_filter1d
    logP = np.log(P)
    Ps = np.exp(gaussian_filter1d(logP, sigma=3, mode="nearest"))
    mm = (k >= 0.02) & (k <= 0.30)
    ax2.plot(k[mm], P[mm] / Ps[mm] - 1, "o-", ms=3.5, lw=0.8, color=colors[name], label=name)

ax1.scatter(k_h, P_id_h, marker="^", s=90, color="k", zorder=5, label="IDCM 9 線 (O100)")
for i, (kk, pp) in enumerate(zip(k_h, P_id_h)):
    ax1.annotate(f"$\\ell_{{{i+1}}}$", (kk, pp), textcoords="offset points", xytext=(6, 6), fontsize=9)
ax1.set_xlabel("k  [h/Mpc]"); ax1.set_ylabel("P(k)  [(Mpc/h)$^3$]")
ax1.set_title("P(k): BOSS DR12 post-recon vs IDCM 線譜")
ax1.legend(fontsize=8); ax1.grid(alpha=0.3)

for i, kk in enumerate(k_h):
    if kk <= 0.32:
        ax2.axvline(kk, color="k", ls="--", lw=0.9, alpha=0.8)
        ax2.annotate(f"$\\ell_{{{i+1}}}$", (kk, 0.012), rotation=90, fontsize=8, alpha=0.8)
ax2.axhline(0, color="gray", lw=0.7)
ax2.set_xlabel("k  [h/Mpc]"); ax2.set_ylabel("wiggle  P/P$_{smooth}$ - 1")
ax2.set_title("Wiggle 極值 vs IDCM 線位 (線2 Δ=+0.5%)")
ax2.legend(fontsize=8); ax2.grid(alpha=0.3)

fig.suptitle("O100-A: IDCM 逆投影線譜 vs BOSS DR12 全範圍 P(k) (Gil-Marín 2016 官方數據)", fontsize=12)
fig.tight_layout(rect=[0, 0, 1, 0.95])
out = f"{WORK}/data/P3D_vs_BOSS_fullrange.png"
fig.savefig(out, dpi=140)
print("saved:", out)