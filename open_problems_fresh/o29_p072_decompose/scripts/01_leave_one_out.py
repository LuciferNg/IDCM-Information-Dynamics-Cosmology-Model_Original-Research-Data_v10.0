#!/usr/bin/env python3
"""
O29 Step 1 (v2): Leave-one-out decomposition — O5-aligned rng stream
====================================================================
CRITICAL: O5 04_significance.py consumes the rng stream in a fixed subset
order (all → lit → cold → hot → all-minus-coldspot). The p=0.072 recorded
in O5 comes from that stream position. To reproduce p=0.072 EXACTLY and
keep LOO comparable, we must consume the SAME number of rotations before
the all-minus-coldspot baseline, then continue the stream for LOO.

Stream order (mirrors O5):
  1. all (35)          — 1000 rot
  2. lit-confirmed (2) — 1000 rot
  3. smica-cold (15)   — 1000 rot
  4. smica-hot (14)    — 1000 rot
  5. all-minus-coldspot (34) — 1000 rot   ← baseline (expect p=0.072)
  6. LOO (35 × 1000 rot)
  7. Targeted removals (node hypotheses)
  8. Direction tests
"""

import numpy as np
import json
import os

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh'
O5 = f'{BASE}/o5_catalog_compare'
OUT = f'{BASE}/o29_p072_decompose/data'
NODES = np.loadtxt(f'{O5}/../cmb_cold_spot/data/a5_nodes.txt')  # ICRS RA, Dec (new numbering)
HIT_RADIUS = 5.0
N_ROT = 1000
SEED = 20260817

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


def run_rotation_test(cat_vecs, rng, n_rot=N_ROT):
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

# New-numbering nearest node for every spot (O5 stored OLD ids)
def nearest_node(v):
    dots = np.clip(node_vecs @ v, -1, 1)
    d = np.degrees(np.arccos(dots))
    return int(d.argmin()), float(d.min())

node_of = []
for i, m in enumerate(match):
    n, d = nearest_node(cat_vecs_all[i])
    node_of.append(n)

# ---- Spot set definitions (NEW node numbering) ----
cold_spot_family = [i for i in range(len(match)) if node_of[i] == 0]
print(f"Cold-spot family (nearest node 0): {len(cold_spot_family)} spots")
for i in cold_spot_family:
    print(f"   [{i:2d}] {match[i]['name']:<32} d={match[i]['nearest_deg']:.2f}°")

node9_spots = [i for i, n in enumerate(node_of) if n == 9]
print(f"Node-9 spots (nearest node 9): {len(node9_spots)}")
for i in node9_spots:
    print(f"   [{i:2d}] {match[i]['name']:<32} d={match[i]['nearest_deg']:.2f}°")

node47_spots = [i for i, n in enumerate(node_of) if n == 47]
print(f"Node-47 spots (nearest node 47): {len(node47_spots)}")

# ---- O5-aligned subset indices ----
lit_confirmed_idx = [i for i, m in enumerate(match)
                     if m['kind'] == 'lit' and m['status'] != 'sub-spot']
smica_cold_idx = [i for i, m in enumerate(match) if m['kind'] == 'cold']
smica_hot_idx = [i for i, m in enumerate(match) if m['kind'] == 'hot']
all_except_cs = [i for i, m in enumerate(match)
                 if not (m['status'] == 'confirmed' and m['nearest_deg'] < 0.01)]

rng = np.random.default_rng(SEED)
results = {}

def report(label, idx, note=""):
    cvec = cat_vecs_all[idx]
    obs, p, z, rot = run_rotation_test(cvec, rng)
    results[label] = dict(n=len(idx), obs_mean=obs, p=p, z=z,
                          rot_mean=float(rot.mean()), rot_std=float(rot.std()))
    print(f"  {label:<38} n={len(idx):2d}  obs={obs:6.2f}°  rot={rot.mean():6.2f}±{rot.std():5.2f}°  "
          f"z={z:+6.2f}σ  p={p:.4f}  {note}")
    return p

print("=" * 100)
print("O5-ALIGNED BASELINES (stream order identical to O5 04_significance.py)")
print("=" * 100)
report('all (35)', list(range(35)))
report('lit-confirmed (2)', lit_confirmed_idx)
report('smica-cold (15)', smica_cold_idx)
report('smica-hot (14)', smica_hot_idx)
p_base = report('all-minus-coldspot (34) — BASELINE', all_except_cs)
print(f"  → baseline p = {p_base:.4f} (O5 record: 0.072)")

print("\n" + "=" * 100)
print("B. LEAVE-ONE-OUT — every spot removed from the 34-set (Δp vs baseline)")
print("=" * 100)
loo = []
for i in all_except_cs:
    idx = [j for j in all_except_cs if j != i]
    cvec = cat_vecs_all[idx]
    obs, p, z, rot = run_rotation_test(cvec, rng)
    loo.append(dict(removed=i, name=match[i]['name'], kind=match[i]['kind'],
                    node=node_of[i], nearest=match[i]['nearest_deg'],
                    n=33, obs_mean=obs, p=p, z=z, dp=p - p_base))
    print(f"  remove [{i:2d}] {match[i]['name']:<32} → p={p:.4f} (Δp={p-p_base:+.4f})")

results['B_loo'] = loo
loo_sorted = sorted(loo, key=lambda r: r['p'])
print("\n  Signal carriers (removal raises p most — spot IS the signal):")
for r in loo_sorted[-5:]:
    print(f"    {r['name']:<32} p={r['p']:.4f} Δp={r['dp']:+.4f}")
print("  Anti-signal (removal lowers p — spot dilutes the signal):")
for r in loo_sorted[:5]:
    print(f"    {r['name']:<32} p={r['p']:.4f} Δp={r['dp']:+.4f}")

print("\n" + "=" * 100)
print("C. TARGETED REMOVALS — node hypotheses")
print("=" * 100)
report('C1 minus-node9-spots (c3,c11)', [i for i in all_except_cs if i not in node9_spots])
report('C2 minus-h12 (node54 hit)', [i for i in all_except_cs if i != 32])
report('C3 minus-h2 (node53 hit)', [i for i in all_except_cs if i != 22])
report('C4 minus-cold-family (6)', [i for i in all_except_cs if i not in cold_spot_family])
report('C5 minus-lit1 + node9-spots', [i for i in all_except_cs if i not in (0,) and i not in node9_spots])

print("\n" + "=" * 100)
print("D. ONE-TAILED DIRECTION TEST on residual 34-set")
print("=" * 100)
cvec = cat_vecs_all[all_except_cs]
dists = np.degrees(np.arccos(np.clip(cvec @ node_vecs.T, -1, 1))).min(axis=1)
print(f"  residual {len(all_except_cs)} spots: mean nearest = {dists.mean():.2f}°, median {np.median(dists):.2f}°")
print(f"  spots with d < 5° (hits): {(dists < 5).sum()}, d < 10°: {(dists < 10).sum()}")
rng2 = np.random.default_rng(SEED + 1)
n_hits_rot = np.zeros(N_ROT)
n_near10_rot = np.zeros(N_ROT)
for k in range(N_ROT):
    R = random_rotation_matrix(rng2)
    rot_nodes = (R @ node_vecs.T).T
    dd = np.degrees(np.arccos(np.clip(cvec @ rot_nodes.T, -1, 1))).min(axis=1)
    n_hits_rot[k] = (dd < 5).sum()
    n_near10_rot[k] = (dd < 10).sum()
ph = float((n_hits_rot >= (dists < 5).sum()).mean())
p10 = float((n_near10_rot >= (dists < 10).sum()).mean())
print(f"  hits<5°: obs {(dists < 5).sum()} vs rot {n_hits_rot.mean():.1f}±{n_hits_rot.std():.1f} → p={ph:.4f}")
print(f"  near<10°: obs {(dists < 10).sum()} vs rot {n_near10_rot.mean():.1f}±{n_near10_rot.std():.1f} → p={p10:.4f}")
results['D_direction'] = dict(n_hits=int((dists < 5).sum()), p_hits=ph,
                              n_near10=int((dists < 10).sum()), p_near10=p10,
                              mean_d=float(dists.mean()), median_d=float(np.median(dists)))

with open(f'{OUT}/decompose_results.json', 'w') as f:
    json.dump(dict(results=results, loo=loo), f, indent=2, ensure_ascii=False)
print(f"\nSaved: {OUT}/decompose_results.json")
