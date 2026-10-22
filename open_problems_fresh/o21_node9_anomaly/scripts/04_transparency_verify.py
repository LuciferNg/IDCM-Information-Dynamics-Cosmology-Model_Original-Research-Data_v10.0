#!/usr/bin/env python3
"""
04_transparency_verify.py — O21: 晶格透明度框架延伸驗證
====================================================
P1: Hop=1 節點集體行爲 — 高斯一致性檢驗
P2: Frustration vs Normal edge |ΔT| — 拓撲信號載體確認
P3: 透明度梯度 — BFS 距離 vs 偏離高斯程度
P4: GRF bootstrap 透明度對照 — 同層節點溫度是否異常
"""

import numpy as np
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u
import os, sys, math, json, time
from collections import defaultdict, deque
from scipy import stats

BASE = "/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh"
O21 = os.path.join(BASE, "o21_node9_anomaly")
DATA = os.path.join(O21, "data")
SMOOTH_CACHE = os.path.join(BASE, "o5_catalog_compare/data/smooth_cache")

# ─── Load data ─────────────────────────────────────────────────────
nodes = np.loadtxt(os.path.join(BASE, "cmb_cold_spot/data/a5_nodes.txt"))
sc = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg = np.array(gal.l.deg)
b_deg = np.array(gal.b.deg)

# Node temperatures from SMICA 4.17°
T_obs = np.loadtxt(os.path.join(BASE, "o3_node_temperatures/data/node_temps.txt"), skiprows=1)
T_uK = T_obs[:, 2]
hop_arr = T_obs[:, 5].astype(int)

# Coloring
color = {}
with open(os.path.join(BASE, "cmb_cold_spot/data/anchored_coloring.txt")) as f:
    for line in f:
        if line.startswith("#") or not line.strip(): continue
        parts = line.split()
        color[int(parts[0])] = int(parts[3])
color_arr = np.array([color[i] for i in range(60)])

# Build graph edges
vecs = np.array([[math.cos(math.radians(d))*math.cos(math.radians(r)),
                  math.cos(math.radians(d))*math.sin(math.radians(r)),
                  math.sin(math.radians(d))] for r, d in nodes])
edges = []
for i in range(60):
    for j in range(i+1, 60):
        ang = math.degrees(math.acos(np.clip(np.dot(vecs[i], vecs[j]), -1, 1)))
        if ang < 28.0:
            edges.append((i, j))

print("=" * 66)
print("晶格透明度框架 — 延伸驗證")
print("=" * 66)

# ─── P1: Hop=1 節點集體行爲 ──────────────────────────────────────
print("\n─── P1: Hop=1 節點集體行爲 ───")
hop1_nodes = [i for i in range(60) if hop_arr[i] == 1]
print(f"Hop=1 nodes: {hop1_nodes}")
print(f"  Node 9:  {T_uK[9]:+.2f} μK (color={color_arr[9]}, hot)")
print(f"  Node 20: {T_uK[20]:+.2f} μK (color={color_arr[20]}, hot)")
print(f"  Node 41: {T_uK[41]:+.2f} μK (color={color_arr[41]}, hot)")
print(f"  Node 50: {T_uK[50]:+.2f} μK (color={color_arr[50]}, hot)")
T_hop1 = T_uK[hop1_nodes]
print(f"  Hop=1 mean ± std: {T_hop1.mean():.2f} ± {T_hop1.std():.2f} μK")

# Full 60-node distribution (excluding node 0 cold spot)
T_rest = np.delete(T_uK, 0)
print(f"  All 59 (excl. cold spot): mean={T_rest.mean():.2f} ± {T_rest.std():.2f} μK")

# Gaussian test: Are hop=1 nodes consistent with the parent distribution?
# Method: compare hop=1 mean to bootstrap of 59-node distribution
# Draw 4 random nodes from the 59-node set 10000 times
rng = np.random.default_rng(42)
n_bootstrap = 10000
hop1_means = []
for _ in range(n_bootstrap):
    samples = rng.choice(T_rest, size=4, replace=False)
    hop1_means.append(samples.mean())
hop1_means = np.array(hop1_means)

z_hop1_mean = (T_hop1.mean() - hop1_means.mean()) / hop1_means.std()
p_hop1_mean = np.mean(hop1_means <= T_hop1.mean())
print(f"  Bootstrap 4-node mean: {hop1_means.mean():.2f} ± {hop1_means.std():.2f} μK")
print(f"  Hop=1 mean z = {z_hop1_mean:.2f}σ, p = {p_hop1_mean:.4f}")
print(f"  → Hop=1 集體行爲: {'🟢 透明（高斯一致）' if p_hop1_mean > 0.05 else '🔴 偏離高斯'}")

# Also check if hop=1 variance is extreme
hop1_vars = []
for _ in range(n_bootstrap):
    samples = rng.choice(T_rest, size=4, replace=False)
    hop1_vars.append(samples.var())
hop1_vars = np.array(hop1_vars)
z_hop1_var = (T_hop1.var() - hop1_vars.mean()) / hop1_vars.std()
p_hop1_var = np.mean(hop1_vars >= T_hop1.var()) if T_hop1.var() <= hop1_vars.mean() else np.mean(hop1_vars <= T_hop1.var())
print(f"  Bootstrap 4-node variance: {hop1_vars.mean():.2f} ± {hop1_vars.std():.2f}")
print(f"  Hop=1 variance z = {z_hop1_var:.2f}σ, p = {p_hop1_var:.4f}")
print(f"  → Hop=1 離散度: {'🟢 透明' if p_hop1_var > 0.05 else '🔴 異常'}")

# ─── P2: Frustration vs Normal edge |ΔT| ──────────────────────────
print("\n─── P2: Frustration vs Normal edge |ΔT| ───")
frust_edges = []
normal_edges = []
for i, j in edges:
    dT = abs(T_uK[i] - T_uK[j])
    if color_arr[i] == color_arr[j]:
        frust_edges.append(dT)  # same colour = frustration
    else:
        normal_edges.append(dT)  # different colour = normal

frust_arr = np.array(frust_edges)
normal_arr = np.array(normal_edges)
print(f"  Frustration edges: {len(frust_arr)} mean={frust_arr.mean():.2f} μK")
print(f"  Normal edges: {len(normal_arr)} mean={normal_arr.mean():.2f} μK")
print(f"  Gap: {normal_arr.mean() - frust_arr.mean():.2f} μK")

# Permutation test
dT_all = np.concatenate([frust_arr, normal_arr])
n_frust = len(frust_arr)
obs_gap = normal_arr.mean() - frust_arr.mean()
count = 0
for _ in range(10000):
    perm = rng.permutation(dT_all)
    gap = perm[n_frust:].mean() - perm[:n_frust].mean()
    if gap >= obs_gap:
        count += 1
p_gap = count / 10000
print(f"  Permutation p = {p_gap:.4f} ({count}/10000)")
print(f"  → Frustration 載體: {'🟢🟢 拓撲信號確認' if p_gap < 0.05 else '🟡 邊緣' if p_gap < 0.10 else '🔴 冇信號'}")

# ─── P3: 透明度梯度 — BFS hop vs 溫度 ─────────────────────────────
print("\n─── P3: 透明度梯度（BFS hop vs 溫度） ───")

# For each hop layer, compute the deviation from Gaussian expectation
# Use the 60-node distribution as parent, but exclude node 0 (cold spot anchor)
T_parent = np.delete(T_uK, 0)  # 59 nodes without cold spot

print(f"  {'Hop':>4s} {'N':>4s} {'Mean':>8s} {'Std':>8s} {'z-mean':>8s} {'p':>8s} {'Transparent?':>12s}")
print(f"  {'-'*56}")

for h in range(0, 9):
    nodes_h = [i for i in range(60) if hop_arr[i] == h]
    T_h = T_uK[nodes_h]
    n_h = len(nodes_h)
    if n_h < 2:
        continue

    # Bootstrap: draw n_h random nodes from parent 10000 times
    h_means = np.array([rng.choice(T_parent, size=n_h, replace=False).mean() for _ in range(10000)])
    z_h = (T_h.mean() - h_means.mean()) / h_means.std()
    p_h = np.mean(h_means <= T_h.mean()) if T_h.mean() <= h_means.mean() else np.mean(h_means >= T_h.mean())
    # Two-tailed
    p_h = 2 * min(p_h, 1 - p_h)

    verdict = "🟩 透明" if p_h > 0.05 else ("🟡 邊緣" if p_h > 0.01 else "🔴 不透明")
    print(f"  {h:>4d} {n_h:>4d} {T_h.mean():>+8.2f} {T_h.std():>8.2f} {z_h:>+8.2f} {p_h:>8.4f} {verdict:>12s}")

# ─── P4: GRF 透明度對照 — 同層節點喺隨機場中嘅行爲 ────────────────
print("\n─── P4: GRF 透明度對照 ───")

# Use the SMICA Cℓ from the bootstrap to generate GRF
m_smica = hp.read_map(os.path.join(SMOOTH_CACHE, "smica2_smooth4.17.fits"), field=0)
m_smica = hp.remove_dipole(m_smica)
cl_data = hp.anafast(m_smica * 1e6, lmax=128)
cl_input = np.zeros(len(cl_data))
cl_input[2:] = cl_data[2:]

NSIDE_OUT = 64
pix_out = hp.ang2pix(NSIDE_OUT, l_deg, b_deg, lonlat=True)

N_REAL = 10000
batch_size = 200
n_batches = N_REAL // batch_size
t0 = time.time()

# Track: per-hop layer, how often the mean is as extreme as observed
hop_layers = {}
for h in range(9):
    nodes_h = [i for i in range(60) if hop_arr[i] == h]
    if len(nodes_h) >= 2:
        hop_layers[h] = {
            "nodes": nodes_h,
            "n": len(nodes_h),
            "obs_mean": float(T_uK[nodes_h].mean()),
            "count_extreme": 0,
        }

print(f"  Running {N_REAL} GRF, tracking {len(hop_layers)} hop layers...")

for batch in range(n_batches):
    for i in range(batch_size):
        alm = hp.synalm(cl_input, lmax=2*NSIDE_OUT, verbose=False)
        m = hp.alm2map(alm, nside=NSIDE_OUT, verbose=False)
        T = m[pix_out]

        for h, info in hop_layers.items():
            grf_mean = T[info["nodes"]].mean()
            if abs(grf_mean) >= abs(info["obs_mean"]):
                info["count_extreme"] += 1

    elapsed = time.time() - t0
    rate = (batch+1) * batch_size / elapsed
    remaining = (n_batches - batch - 1) * batch_size / rate
    print(f"    Batch {batch+1}/{n_batches}: {elapsed:.0f}s, {rate:.0f}/s, ~{remaining:.0f}s remaining")

print(f"\n  GRF transparency test:")
for h in sorted(hop_layers):
    info = hop_layers[h]
    p_grf = info["count_extreme"] / N_REAL
    verdict = "🟩 透明" if p_grf > 0.05 else ("🟡 邊緣" if p_grf > 0.01 else "🔴 不透明")
    print(f"    Hop={h} (n={info['n']}): obs_mean={info['obs_mean']:+.2f}, "
          f"GRF extreme p={p_grf:.4f} ({info['count_extreme']}/{N_REAL}) {verdict}")

# ─── Summary ───────────────────────────────────────────────────────
print(f"\n{'='*66}")
print("透明度框架 — 驗證總結")
print(f"{'='*66}")

results = {
    "P1_hop1_mean_z": float(z_hop1_mean),
    "P1_hop1_mean_p": float(p_hop1_mean),
    "P1_verdict": "🟩 透明" if p_hop1_mean > 0.05 else "🔴 異常",
    "P2_frust_gap_uK": float(normal_arr.mean() - frust_arr.mean()),
    "P2_frust_p": float(p_gap),
    "P2_verdict": "🟢🟢 拓撲信號" if p_gap < 0.05 else "🟡 邊緣",
    "P3_layers": {str(h): {"n": info["n"], "obs_mean": info["obs_mean"],
                           "grf_p": info["count_extreme"] / N_REAL}
                  for h, info in hop_layers.items()},
    "P3_verdict": None,
    "P4_verdict": None,
}

# Overall verdict
p_values = [info["count_extreme"] / N_REAL for info in hop_layers.values()]
results["overall"] = "透明框架 🟢 成立" if all(p > 0.01 for p in p_values) else "透明框架 🔴 部分推翻"

with open(os.path.join(DATA, "transparency_verify.json"), "w") as f:
    json.dump(results, f, indent=2)

print(f"✅ Saved: transparency_verify.json")