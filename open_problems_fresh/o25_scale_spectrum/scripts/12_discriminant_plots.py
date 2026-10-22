#!/usr/bin/env python3
"""
12_discriminant_plots.py — O25: 判別檢驗圖
==========================================
fig7: node9 vs node0 徑向剖面 (T1)
fig8: 熱環示意 (T3) — 20°盤 vs 20-30°環
"""
import healpy as hp
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os, json

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
CACHE = os.path.join(BASE, "o25_scale_spectrum", "data", "smooth_cache_large")
FIGS = os.path.join(BASE, "o25_scale_spectrum", "figs")
os.makedirs(FIGS, exist_ok=True)

node9 = {"l": 214.92, "b": -31.16}
node0 = {"l": 209.00, "b": -57.00}

m = hp.read_map(os.path.join(CACHE, "Commander_smooth15.0.fits"), field=0)
m_low = hp.ud_grade(m, 512)
nside_low = 512

def radial_profile(l_deg, b_deg, max_r=42, step=2):
    vec = hp.ang2vec(l_deg, b_deg, lonlat=True)
    rings = []
    for r0 in range(0, max_r, step):
        r1 = r0 + step
        disc_outer = hp.query_disc(nside_low, vec, np.radians(r1))
        if r0 == 0:
            ring = disc_outer
        else:
            disc_inner = hp.query_disc(nside_low, vec, np.radians(r0))
            ring = np.setdiff1d(disc_outer, disc_inner)
        rings.append((r0+step/2, m_low[ring].mean()*1e6))
    return np.array(rings)

prof9 = radial_profile(node9["l"], node9["b"])
prof0 = radial_profile(node0["l"], node0["b"])

plt.rcParams.update({"font.size": 11, "axes.grid": True, "grid.alpha": 0.3})

# ---- fig7: 徑向剖面 ----
fig, ax = plt.subplots(figsize=(10, 6))
ax.plot(prof9[:, 0], prof9[:, 1], "o-", color="#d62728", lw=2, ms=6, label="node9 (大尺度冷區)")
ax.plot(prof0[:, 0], prof0[:, 1], "s-", color="#1f77b4", lw=2, ms=6, label="node0 (冷斑)")
ax.axhline(0, color="gray", ls=":", alpha=0.6)
# 熱環標記
ax.axvspan(20, 30, color="orange", alpha=0.15, label="20-30° 熱環區")
ax.text(25, 25, "熱環 z=+2.43σ", ha="center", fontsize=10, color="orange", fontweight="bold")
ax.set_xlabel("距離中心半徑 (°)")
ax.set_ylabel("T (μK)")
ax.set_title("O25 判別: Node9 徑向剖面 = Compensated Void (中心冷 + 外圍熱)")
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(FIGS, "07_radial_profile.png"), dpi=150)
plt.close()

# ---- fig8: 熱環 z 對比 ----
rng = np.random.default_rng(456)
ring_diffs = []
for _ in range(200):
    rv = rng.standard_normal(3)
    rv /= np.linalg.norm(rv)
    d20 = hp.query_disc(nside_low, rv, np.radians(20.0))
    r20_30 = np.setdiff1d(
        hp.query_disc(nside_low, rv, np.radians(30.0)),
        hp.query_disc(nside_low, rv, np.radians(20.0)))
    ring_diffs.append((m_low[r20_30].mean() - m_low[d20].mean()) * 1e6)
ring_diffs = np.array(ring_diffs)

fig, ax = plt.subplots(figsize=(10, 5.5))
ax.hist(ring_diffs, bins=25, color="#999", alpha=0.7, label="隨機 200 方向 (環-盤)")
for name, pos, color in [("node9", node9, "#d62728"), ("node0", node0, "#1f77b4")]:
    vec = hp.ang2vec(pos["l"], pos["b"], lonlat=True)
    d20 = hp.query_disc(nside_low, vec, np.radians(20.0))
    r20_30 = np.setdiff1d(
        hp.query_disc(nside_low, vec, np.radians(30.0)),
        hp.query_disc(nside_low, vec, np.radians(20.0)))
    diff = (m_low[r20_30].mean() - m_low[d20].mean()) * 1e6
    z = (diff - ring_diffs.mean()) / ring_diffs.std()
    ax.axvline(diff, color=color, lw=3, ls="--", label=f"{name}: {diff:+.1f} μK (z={z:+.2f}σ)")
ax.set_xlabel("環−盤 (μK)")
ax.set_ylabel("count")
ax.set_title("O25 判別: 熱環檢驗 — node9 有 ISW 熱環, 冷斑冇")
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig(os.path.join(FIGS, "08_hot_ring.png"), dpi=150)
plt.close()

print("✅ figs/07,08 saved")
