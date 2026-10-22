#!/usr/bin/env python3
"""
O29 Step 2: Bootstrap decomposition — robustness of the LOO ranking
===================================================================
LOO Δp values carry MC sampling noise (each p from 1000 rotations ≈ ±0.01-0.02).
This script quantifies the noise floor and checks whether the LOO ranking is
stable:

  1. Rotation-count sensitivity: re-run baseline + top-Δp removals at
     10,000 rotations (10× more) → stable p?
  2. Bootstrap of the catalogue: resample 34 spots with replacement
     (n=34) and recompute mean-nearest p — distribution under sampling
     noise. What fraction of bootstrap draws gives p<0.05?
  3. Per-spot leverage: for each spot, the change in the observed
     mean-nearest statistic (leave-one-out Δobs) — a deterministic
     decomposition (no MC noise):
         Δobs_i = mean_nearest(all) - mean_nearest(all \ {i})
  4. Node-9 hypothesis direct test: are spots nearest to node 9
     (c3, c11) closer than random? (Their removal LOWERED p, so the
     node-9 spots are FARTHER than the rest — quantify with a direct
     permutation.)

All rotation tests use a FRESH rng stream (seed derived per test) so
nothing depends on O5's stream order — this is the independent check.
"""

import numpy as np
import json
import os

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh'
O5 = f'{BASE}/o5_catalog_compare'
OUT = f'{BASE}/o29_p072_decompose/data'
NODES = np.loadtxt(f'{O5}/../cmb_cold_spot/data/a5_nodes.txt')
N_ROT_HI = 10000

os.makedirs(OUT, exist_ok=True)

node_ra = np.radians(NODES[:, 0])
node_dec = np.radians(NODES[:, 1])
node_vecs = np.stack([
    np.cos(node_dec) * np.cos(node_ra),
    np.cos(node_dec) * np.sin(node_ra),
    np.sin(node_dec)], axis=1)


def random_rotation_matrix(rng):
    z = rng.uniform(-1, 1)
    phi = rng.uniform(0, 2 * np.pi)
    ax = np.array([np.sqrt(1 - z**2) * np.cos(phi),
                   np.sqrt(1 - z**2) * np.sin(phi), z])
    theta = rng.uniform(0, 2 * np.pi)
    K = np.array([[0, -ax[2], ax[1]],
                  [ax[2], 0, -ax[0]],
                  [-ax[1], ax[0], 0]])
    return np.eye(3) + np.sin(theta) * K + (1 - np.cos(theta)) * (K @ K)


def mean_nearest(cat_vecs, node_set):
    dots = np.clip(cat_vecs @ node_set.T, -1, 1)
    dists = np.degrees(np.arccos(dots))
    return float(dists.min(axis=1).mean())


def rotation_test(cat_vecs, rng, n_rot):
    obs_mean = mean_nearest(cat_vecs, node_vecs)
    rot_mean = np.zeros(n_rot)
    for k in range(n_rot):
        R = random_rotation_matrix(rng)
        rot_nodes = (R @ node_vecs.T).T
        rot_mean[k] = mean_nearest(cat_vecs, rot_nodes)
    p = float((rot_mean <= obs_mean).mean())
    z = float((obs_mean - rot_mean.mean()) / rot_mean.std())
    return obs_mean, p, z, rot_mean


# ---- Load catalogue ----
match = json.load(open(f'{O5}/data/match_results.json'))['matches']
cat_ra = np.radians([m['ra'] for m in match])
cat_dec = np.radians([m['dec'] for m in match])
cat_vecs_all = np.stack([np.cos(cat_dec) * np.cos(cat_ra),
                         np.cos(cat_dec) * np.sin(cat_ra),
                         np.sin(cat_dec)], axis=1)

def nearest_node(v):
    dots = np.clip(node_vecs @ v, -1, 1)
    d = np.degrees(np.arccos(dots))
    return int(d.argmin()), float(d.min())

node_of = [nearest_node(cat_vecs_all[i])[0] for i in range(len(match))]

all_except_cs = [i for i, m in enumerate(match)
                 if not (m['status'] == 'confirmed' and m['nearest_deg'] < 0.01)]
cold_spot_family = [i for i in range(len(match)) if node_of[i] == 0]
node9_spots = [i for i, n in enumerate(node_of) if n == 9]

out = {}

# ============ 1. HIGH-ROTATION CONFIRMATION ============
print("=" * 80)
print("1. HIGH-ROTATION CONFIRMATION (10,000 rotations, fresh seeds)")
print("=" * 80)
sets = {
    'baseline-34': all_except_cs,
    'minus-cold-family': [i for i in all_except_cs if i not in cold_spot_family],
    'minus-subspot-B': [i for i in all_except_cs if i != 3],
    'minus-h2': [i for i in all_except_cs if i != 22],
    'minus-node9-spots': [i for i in all_except_cs if i not in node9_spots],
    'minus-cold-family+node9': [i for i in all_except_cs
                                if i not in cold_spot_family and i not in node9_spots],
}
hi = {}
for label, idx in sets.items():
    rng = np.random.default_rng(abs(hash(label)) % (2**32))
    obs, p, z, rot = rotation_test(cat_vecs_all[idx], rng, N_ROT_HI)
    hi[label] = dict(n=len(idx), obs=obs, p=p, z=z,
                     rot_mean=float(rot.mean()), rot_std=float(rot.std()))
    print(f"  {label:<26} n={len(idx):2d}  obs={obs:6.2f}°  z={z:+6.2f}σ  p={p:.4f}")
out['high_rotation'] = hi

# ============ 2. BOOTSTRAP OF THE 34-SET ============
print("\n" + "=" * 80)
print("2. BOOTSTRAP — resample 34 spots (with replacement), 2000 draws")
print("=" * 80)
rng = np.random.default_rng(20260818)
boot_p = np.zeros(2000)
boot_obs = np.zeros(2000)
base_vecs = cat_vecs_all[all_except_cs]
n34 = len(all_except_cs)
for b in range(2000):
    idx = rng.integers(0, n34, n34)
    cvec = base_vecs[idx]
    obs = mean_nearest(cvec, node_vecs)
    rot_mean = np.zeros(1000)
    for k in range(1000):
        R = random_rotation_matrix(rng)
        rot_nodes = (R @ node_vecs.T).T
        rot_mean[k] = mean_nearest(cvec, rot_nodes)
    boot_p[b] = (rot_mean <= obs).mean()
    boot_obs[b] = obs

out['bootstrap'] = dict(
    frac_p_lt_005=float((boot_p < 0.05).mean()),
    frac_p_lt_010=float((boot_p < 0.10).mean()),
    p_mean=float(boot_p.mean()), p_std=float(boot_p.std()),
    p_median=float(np.median(boot_p)),
    obs_mean=float(boot_obs.mean()), obs_std=float(boot_obs.std()))
print(f"  bootstrap p distribution: mean={boot_p.mean():.3f} ± {boot_p.std():.3f}, "
      f"median={np.median(boot_p):.3f}")
print(f"  fraction of draws with p < 0.05: {(boot_p < 0.05).mean():.3f}")
print(f"  fraction of draws with p < 0.10: {(boot_p < 0.10).mean():.3f}")
print(f"  observed mean-nearest spread: {boot_obs.mean():.3f} ± {boot_obs.std():.3f}°")

# ============ 3. DETERMINISTIC LEVERAGE (Δobs, no MC noise) ============
print("\n" + "=" * 80)
print("3. DETERMINISTIC LEVERAGE — Δobs per spot (no MC noise)")
print("=" * 80)
obs_all = mean_nearest(cat_vecs_all[all_except_cs], node_vecs)
lev = []
for i in all_except_cs:
    idx = [j for j in all_except_cs if j != i]
    obs_rm = mean_nearest(cat_vecs_all[idx], node_vecs)
    lev.append(dict(removed=i, name=match[i]['name'], kind=match[i]['kind'],
                    node=node_of[i], nearest=match[i]['nearest_deg'],
                    d_obs=obs_rm - obs_all))
lev_sorted = sorted(lev, key=lambda r: r['d_obs'], reverse=True)
print(f"  baseline obs (34) = {obs_all:.3f}°; removing a spot with Δobs>0 makes the")
print("  mean NEARER (spot was far → its removal strengthens signal)")
for r in lev_sorted[:6]:
    print(f"    +Δobs {r['d_obs']:+.3f}°  {r['name']:<30} (node {r['node']:2d}, d={r['nearest']:.2f}°)")
print("  ...")
for r in lev_sorted[-6:]:
    print(f"    {r['d_obs']:+.3f}°  {r['name']:<30} (node {r['node']:2d}, d={r['nearest']:.2f}°)")
out['leverage'] = lev_sorted

# ============ 4. NODE-9 SPOTS DIRECT TEST ============
print("\n" + "=" * 80)
print("4. NODE-9 SPOT DISTANCES vs REST (direct permutation)")
print("=" * 80)
d_all = np.degrees(np.arccos(np.clip(cat_vecs_all[all_except_cs] @ node_vecs.T, -1, 1))).min(axis=1)
d_n9 = d_all[[i for i, s in enumerate(all_except_cs) if all_except_cs[i] in node9_spots]]
d_rest = d_all[[i for i, s in enumerate(all_except_cs) if all_except_cs[i] not in node9_spots]]
print(f"  node-9 spots (c3,c11): d = {d_n9.mean():.2f}° ± {d_n9.std():.2f}°  (n={len(d_n9)})")
print(f"  other 32 spots:        d = {d_rest.mean():.2f}° ± {d_rest.std():.2f}°  (n={len(d_rest)})")
# permutation: is the node9 mean SMALLER (closer)?
rng = np.random.default_rng(42)
obs_diff = d_n9.mean() - d_rest.mean()
cnt = 0
for _ in range(10000):
    perm = rng.permutation(d_all)
    cnt += (perm[:len(d_n9)].mean() - perm[len(d_n9):].mean() <= obs_diff)
p_perm = cnt / 10000
print(f"  observed node9-vs-rest mean diff = {obs_diff:+.2f}°")
print(f"  P(node9 mean ≤ observed) [one-sided, closer] = {p_perm:.4f}")
print(f"  P(node9 mean ≥ observed) [one-sided, farther] = {1-p_perm:.4f}")
out['node9_direct'] = dict(d_node9=float(d_n9.mean()), d_rest=float(d_rest.mean()),
                           diff=float(obs_diff), p_closer=p_perm)

with open(f'{OUT}/bootstrap_decompose.json', 'w') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nSaved: {OUT}/bootstrap_decompose.json")
