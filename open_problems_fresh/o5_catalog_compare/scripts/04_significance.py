#!/usr/bin/env python3
"""
O5 Step 4: Significance — hit rate vs 1000 random rotations
=============================================================
Null hypothesis: the A₅ node set has NO special alignment with the
observed cold/hot spot catalogue. Under the null, rotating the node
set (preserving its network structure) gives the same expected hit rate.

Test statistic: # hits (spots within HIT_RADIUS of a node).
p-value = fraction of rotations with ≥ observed hits.

Also computed: mean nearest-node distance for the catalogue vs the
rotation distribution (a stronger, distance-based statistic).

Key subtlety: the catalogue itself (SMICA flood-fill) was derived from
the SAME map used to verify the cold spot at node 0 — so the SMICA
catalogue is NOT fully independent of the node positions. We therefore
report:
  (a) full-catalogue p-value (optimistic)
  (b) leave-one-out: exclude the cold spot itself → honest p-value
"""

import numpy as np
import json
import os

BASE = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o5_catalog_compare'
NODES = np.loadtxt(f'{BASE}/../cmb_cold_spot/data/a5_nodes.txt')
OUTDIR = f'{BASE}/data'
HIT_RADIUS = 5.0
N_ROT = 1000

node_ra = np.radians(NODES[:, 0])
node_dec = np.radians(NODES[:, 1])
node_vecs = np.stack([
    np.cos(node_dec) * np.cos(node_ra),
    np.cos(node_dec) * np.sin(node_ra),
    np.sin(node_dec)], axis=1)

def random_rotation_matrix(rng):
    """Random Rodrigues rotation (uniform on SO(3))."""
    # random axis
    z = rng.uniform(-1, 1)
    phi = rng.uniform(0, 2 * np.pi)
    ax = np.array([np.sqrt(1 - z**2) * np.cos(phi),
                   np.sqrt(1 - z**2) * np.sin(phi), z])
    theta = rng.uniform(0, 2 * np.pi)
    K = np.array([[0, -ax[2], ax[1]],
                  [ax[2], 0, -ax[0]],
                  [-ax[1], ax[0], 0]])
    return np.eye(3) + np.sin(theta) * K + (1 - np.cos(theta)) * (K @ K)

def hit_counts(cat_vecs, node_set, radius_deg):
    """# catalogue spots within radius of any node."""
    dots = np.clip(cat_vecs @ node_set.T, -1, 1)
    dists = np.degrees(np.arccos(dots))
    return int((dists < radius_deg).any(axis=1).sum())

def mean_nearest(cat_vecs, node_set):
    dots = np.clip(cat_vecs @ node_set.T, -1, 1)
    dists = np.degrees(np.arccos(dots))
    return float(dists.min(axis=1).mean())

# Load catalogue positions (ICRS)
match = json.load(open(f'{OUTDIR}/match_results.json'))['matches']
cat_pos = [(m['ra'], m['dec']) for m in match]
cat_ra = np.radians([p[0] for p in cat_pos])
cat_dec = np.radians([p[1] for p in cat_pos])
cat_vecs = np.stack([np.cos(cat_dec) * np.cos(cat_ra),
                     np.cos(cat_dec) * np.sin(cat_ra),
                     np.sin(cat_dec)], axis=1)

# Subsets:
# (a) all 35 spots
# (b) confirmed literature only (2: cold spot + gp10)
# (c) SMICA cold only (15)
# (d) SMICA hot only (14)
# (e) all minus the cold spot itself (honest: catalogue derived from same map)
lit_conf_idx = [i for i, m in enumerate(match)
                if m['kind'] == 'lit' and m['status'] != 'sub-spot']
smica_cold_idx = [i for i, m in enumerate(match) if m['kind'] == 'cold']
smica_hot_idx = [i for i, m in enumerate(match) if m['kind'] == 'hot']
all_except_cs = [i for i, m in enumerate(match)
                 if not (m['status'] == 'confirmed' and m['nearest_deg'] < 0.01)]

subsets = {
    'all (35)': list(range(len(match))),
    'lit-confirmed (2)': lit_conf_idx,
    'smica-cold (15)': smica_cold_idx,
    'smica-hot (14)': smica_hot_idx,
    'all-minus-coldspot (34)': all_except_cs,
}

print("=" * 66)
print("O5 STEP 4: SIGNIFICANCE — 1000 RANDOM ROTATIONS")
print("=" * 66)
rng = np.random.default_rng(20260817)

for label, idx in subsets.items():
    cvec = cat_vecs[idx]
    obs_hits = hit_counts(cvec, node_vecs, HIT_RADIUS)
    obs_mean = mean_nearest(cvec, node_vecs)

    rot_hits = np.zeros(N_ROT, dtype=int)
    rot_mean = np.zeros(N_ROT)
    for k in range(N_ROT):
        R = random_rotation_matrix(rng)
        rot_nodes = (R @ node_vecs.T).T
        rot_hits[k] = hit_counts(cvec, rot_nodes, HIT_RADIUS)
        rot_mean[k] = mean_nearest(cvec, rot_nodes)

    p_hit = (rot_hits >= obs_hits).mean()
    p_mean = (rot_mean <= obs_mean).mean()
    z_mean = (obs_mean - rot_mean.mean()) / rot_mean.std()

    print(f"\n  {label}:")
    print(f"    observed hits: {obs_hits} | rotation mean {rot_hits.mean():.1f} ± "
          f"{rot_hits.std():.1f} | p(hits≥obs) = {p_hit:.4f}")
    print(f"    observed mean-nearest: {obs_mean:.2f}° | rotation {rot_mean.mean():.2f}° ± "
          f"{rot_mean.std():.2f}° | z = {z_mean:+.2f}σ | p = {p_mean:.4f}")

print(f"\n  N_ROT = {N_ROT}, hit radius = {HIT_RADIUS}°")
print("  Interpretation:")
print("    p < 0.05 → 🟢 alignment significant (nodes ARE the structure)")
print("    0.05 ≤ p < 0.2 → 🟡 weak/marginal")
print("    p ≥ 0.2 → 🔴 no evidence (null not rejected)")
