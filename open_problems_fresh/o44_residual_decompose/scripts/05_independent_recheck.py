#!/usr/bin/env python3
"""
O29 independent re-derivation — fresh seed, raw data only
=========================================================
Purpose: verify O29 claims WITHOUT reusing the original scripts' rng stream.
All rotation tests use fresh seeds; conclusions must be stable across seeds.

Re-derives:
  1. Cold-spot family membership (spots nearest node 0) — deterministic
  2. Baseline 34 mean-nearest p (fresh seed, 10000 rot)
  3. Cold-family removal p (fresh seed, 10000 rot) — the decisive test
  4. Node9 spots distances vs rest (permutation, fresh seed)
  5. Node47 nearest spot distance
  6. Bootstrap frac p<0.05 (fresh seed, 500 draws)
  7. Deterministic leverage ranking (no MC noise)
"""
import numpy as np
import json
import os

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh'
O5 = f'{BASE}/o5_catalog_compare'
NODES = np.loadtxt(f'{BASE}/cmb_cold_spot/data/a5_nodes.txt')

node_ra = np.radians(NODES[:, 0])
node_dec = np.radians(NODES[:, 1])
node_vecs = np.stack([np.cos(node_dec)*np.cos(node_ra),
                      np.cos(node_dec)*np.sin(node_ra),
                      np.sin(node_dec)], axis=1)

def random_rotation_matrix(rng):
    z = rng.uniform(-1, 1)
    phi = rng.uniform(0, 2*np.pi)
    ax = np.array([np.sqrt(1-z**2)*np.cos(phi), np.sqrt(1-z**2)*np.sin(phi), z])
    theta = rng.uniform(0, 2*np.pi)
    K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    return np.eye(3) + np.sin(theta)*K + (1-np.cos(theta))*(K @ K)

def mean_nearest(cat_vecs, node_set):
    dots = np.clip(cat_vecs @ node_set.T, -1, 1)
    return float(np.degrees(np.arccos(dots)).min(axis=1).mean())

def rotation_test(cat_vecs, rng, n_rot):
    obs = mean_nearest(cat_vecs, node_vecs)
    rot = np.zeros(n_rot)
    for k in range(n_rot):
        R = random_rotation_matrix(rng)
        rot[k] = mean_nearest(cat_vecs, (R @ node_vecs.T).T)
    p = float((rot <= obs).mean())
    z = float((obs - rot.mean()) / rot.std())
    return obs, p, z, rot

match = json.load(open(f'{O5}/data/match_results.json'))['matches']
cat_ra = np.radians([m['ra'] for m in match])
cat_dec = np.radians([m['dec'] for m in match])
cat_vecs = np.stack([np.cos(cat_dec)*np.cos(cat_ra),
                     np.cos(cat_dec)*np.sin(cat_ra),
                     np.sin(cat_dec)], axis=1)

def nearest_node(v):
    dots = np.clip(node_vecs @ v, -1, 1)
    d = np.degrees(np.arccos(dots))
    return int(d.argmin()), float(d.min())

node_of = [nearest_node(cat_vecs[i])[0] for i in range(len(match))]

# 1. Cold family
cold_family = [i for i, n in enumerate(node_of) if n == 0]
print("=" * 70)
print("1. COLD-SPOT FAMILY (nearest node 0) — deterministic")
print("=" * 70)
for i in cold_family:
    print(f"  [{i}] {match[i]['name']:<34} d={match[i]['nearest_deg']:.2f}°")
assert len(cold_family) == 6, f"expected 6, got {len(cold_family)}"

all_except_cs = [i for i, m in enumerate(match)
                 if not (m['status'] == 'confirmed' and m['nearest_deg'] < 0.01)]
n9_spots = [i for i, n in enumerate(node_of) if n == 9]
n47_spots = [i for i, n in enumerate(node_of) if n == 47]

# 2-3. Fresh-seed rotation tests
print("\n" + "=" * 70)
print("2. FRESH-SEED ROTATION TESTS (10000 rot, seed=777)")
print("=" * 70)
rng = np.random.default_rng(777)
obs, p, z, _ = rotation_test(cat_vecs[all_except_cs], rng, 10000)
print(f"  baseline-34:  obs={obs:.3f}°  z={z:+.2f}σ  p={p:.4f}   (record: 0.072/0.066)")

obs, p, z, _ = rotation_test(cat_vecs[[i for i in all_except_cs if i not in cold_family]], rng, 10000)
print(f"  minus-family: obs={obs:.3f}°  z={z:+.2f}σ  p={p:.4f}   (record: 0.365/0.385)")

obs, p, z, _ = rotation_test(cat_vecs[[i for i in all_except_cs if i not in n9_spots]], rng, 10000)
print(f"  minus-node9:  obs={obs:.3f}°  z={z:+.2f}σ  p={p:.4f}   (record: 0.051/0.042)")

# 4. Node9 distances permutation
print("\n" + "=" * 70)
print("3. NODE9 SPOTS vs REST (permutation, seed=778)")
print("=" * 70)
idx34 = np.array(all_except_cs)
d_all = np.degrees(np.arccos(np.clip(cat_vecs[idx34] @ node_vecs.T, -1, 1))).min(axis=1)
n9_idx = np.array([i for i, s in enumerate(all_except_cs) if all_except_cs[i] in n9_spots])
d_n9 = d_all[n9_idx]
d_rest = d_all[[i for i in range(len(d_all)) if i not in n9_idx]]
print(f"  node9 spots: {d_n9.mean():.2f}° ± {d_n9.std():.2f}° (n={len(d_n9)})")
print(f"  rest:        {d_rest.mean():.2f}° ± {d_rest.std():.2f}° (n={len(d_rest)})")
rng2 = np.random.default_rng(778)
obs_diff = d_n9.mean() - d_rest.mean()
cnt = 0
for _ in range(10000):
    perm = rng2.permutation(d_all)
    cnt += (perm[:len(d_n9)].mean() - perm[len(d_n9):].mean() <= obs_diff)
print(f"  diff = {obs_diff:+.2f}°  P(node9 closer) = {cnt/10000:.4f}  (record: +2.66°, 0.7925)")

# 5. Node47
print("\n" + "=" * 70)
print("4. NODE47")
print("=" * 70)
print(f"  spots nearest node47: {n47_spots}  (record: 0)")
if not n47_spots:
    d47 = np.degrees(np.arccos(np.clip(node_vecs[47] @ cat_vecs.T, -1, 1)))
    i_min = int(d47.argmin())
    print(f"  nearest catalogue spot: {match[i_min]['name']} at {d47.min():.2f}°  (record: 23.18°)")

# 6. Bootstrap (fresh seed, 500 draws)
print("\n" + "=" * 70)
print("5. BOOTSTRAP (seed=779, 500 draws × 1000 rot)")
print("=" * 70)
rng3 = np.random.default_rng(779)
boot_p = np.zeros(500)
n34 = len(all_except_cs)
base_vecs = cat_vecs[all_except_cs]
for b in range(500):
    idx = rng3.integers(0, n34, n34)
    obs = mean_nearest(base_vecs[idx], node_vecs)
    rot = np.zeros(1000)
    for k in range(1000):
        R = random_rotation_matrix(rng3)
        rot[k] = mean_nearest(base_vecs[idx], (R @ node_vecs.T).T)
    boot_p[b] = (rot <= obs).mean()
print(f"  frac p<0.05 = {(boot_p < 0.05).mean():.3f}  (record: 0.222)")
print(f"  frac p<0.10 = {(boot_p < 0.10).mean():.3f}  (record: 0.443)")
print(f"  p mean = {boot_p.mean():.3f}  (record: 0.163)")

# 7. Deterministic leverage
print("\n" + "=" * 70)
print("6. DETERMINISTIC LEVERAGE (no MC noise)")
print("=" * 70)
obs_all = mean_nearest(cat_vecs[all_except_cs], node_vecs)
lev = []
for i in all_except_cs:
    idx = [j for j in all_except_cs if j != i]
    lev.append((i, mean_nearest(cat_vecs[idx], node_vecs) - obs_all))
lev_sorted = sorted(lev, key=lambda x: -x[1])
print("  top-5 leverage (removal makes mean NEARER = spot is signal):")
for i, d in lev_sorted[:5]:
    print(f"    +{d:+.3f}°  {match[i]['name']:<32} (node {node_of[i]}, d={match[i]['nearest_deg']:.2f}°)")
print("  bottom-3 (removal makes mean FARTHER = anti-signal):")
for i, d in lev_sorted[-3:]:
    print(f"    {d:+.3f}°  {match[i]['name']:<32} (node {node_of[i]}, d={match[i]['nearest_deg']:.2f}°)")

print("\n✅ O29 independent re-derivation complete")
