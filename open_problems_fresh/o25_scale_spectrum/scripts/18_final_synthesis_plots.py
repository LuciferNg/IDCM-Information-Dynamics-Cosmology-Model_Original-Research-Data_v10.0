#!/usr/bin/env python3
"""
18_final_synthesis_plots.py — O25: 合併分析最終圖
==================================================
fig9: 冷區中心徑向剖面 (0-90°) + 模式分解註記
fig10: 模式分解 bar chart (l=1-10 @ 冷區中心)
"""
import healpy as hp
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
CACHE = os.path.join(BASE, "o25_scale_spectrum", "data", "smooth_cache_large")
FIGS = os.path.join(BASE, "o25_scale_spectrum", "figs")
os.makedirs(FIGS, exist_ok=True)

cold_center = {"l": 197.74, "b": -20.26}
node9 = {"l": 214.92, "b": -31.16}
node0 = {"l": 209.00, "b": -57.00}

m = hp.read_map(os.path.join(CACHE, "Commander_smooth15.0.fits"), field=0)
m_low = hp.ud_grade(m, 512)
nside_low = 512

plt.rcParams.update({"font.size": 11, "axes.grid": True, "grid.alpha": 0.3})

# ---- fig9: 徑向剖面 ----
def ring_profiles(l_deg, b_deg, max_r=90, step=5):
    vec = hp.ang2vec(l_deg, b_deg, lonlat=True)
    rings = []
    for r0 in range(0, max_r, step):
        r1 = r0 + step
        d_out = hp.query_disc(nside_low, vec, np.radians(r1))
        if r0 == 0:
            ring = d_out
        else:
            d_in = hp.query_disc(nside_low, vec, np.radians(r0))
            ring = np.setdiff1d(d_out, d_in)
        rings.append((r0+step/2, m_low[ring].mean()*1e6))
    return np.array(rings)

prof_cc = ring_profiles(cold_center["l"], cold_center["b"])
prof_n9 = ring_profiles(node9["l"], node9["b"], max_r=46, step=2)

fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(prof_cc[:, 0], prof_cc[:, 1], "o-", color="#d62728", lw=2, ms=5, label="冷區中心 (197.7°, -20.3°)")
ax.plot(prof_n9[:, 0], prof_n9[:, 1], "s-", color="#1f77b4", lw=2, ms=5, label="node9 (透明節點)")
ax.axhline(0, color="gray", ls=":", alpha=0.6)
ax.axvline(52.5, color="orange", ls="--", alpha=0.7, label="52.5° 熱環峰 (回落)")
ax.text(30, 18, "compensated void\n(中心冷 + 外圍熱 + 回落)", ha="center", fontsize=10,
        bbox=dict(boxstyle="round", facecolor="orange", alpha=0.2))
ax.set_xlabel("距離中心半徑 (°)")
ax.set_ylabel("T (μK)")
ax.set_title("O25: 冷區中心 = 大尺度 compensated void (l=3 octupole 主導)")
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(FIGS, "09_coldcenter_profile.png"), dpi=150)
plt.close()

# ---- fig10: 模式分解 ----
alm = hp.map2alm(m_low, lmax=10)
n_alm = hp.Alm.getsize(10)
pix_cc = hp.ang2pix(nside_low, cold_center["l"], cold_center["b"], lonlat=True)
pix_n9 = hp.ang2pix(nside_low, node9["l"], node9["b"], lonlat=True)
pix_n0 = hp.ang2pix(nside_low, node0["l"], node0["b"], lonlat=True)

def mode_contrib(l, pix):
    alm_l = np.zeros(n_alm, dtype=complex)
    for mm in range(-l, l+1):
        idx = hp.Alm.getidx(10, l, abs(mm))
        alm_l[idx] = alm[idx]
    mod_map = hp.alm2map(alm_l, nside_low, lmax=10)
    return mod_map[pix] * 1e6

ls = list(range(1, 11))
v_cc = [mode_contrib(l, pix_cc) for l in ls]
v_n9 = [mode_contrib(l, pix_n9) for l in ls]
v_n0 = [mode_contrib(l, pix_n0) for l in ls]

fig, ax = plt.subplots(figsize=(10, 6))
x = np.arange(len(ls))
w = 0.28
ax.bar(x - w, v_cc, w, label="冷區中心", color="#d62728")
ax.bar(x, v_n9, w, label="node9", color="#1f77b4")
ax.bar(x + w, v_n0, w, label="冷斑 node0", color="#2ca02c")
ax.axhline(0, color="gray", lw=0.8)
ax.set_xticks(x)
ax.set_xticklabels([f"l={l}" for l in ls])
ax.set_xlabel("球諧模式 l")
ax.set_ylabel("貢獻 (μK)")
ax.set_title("O25: 冷區中心模式分解 — l=3 (octupole) 主導 −30 μK")
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(FIGS, "10_mode_decomposition.png"), dpi=150)
plt.close()

print("✅ figs/09,10 saved")
