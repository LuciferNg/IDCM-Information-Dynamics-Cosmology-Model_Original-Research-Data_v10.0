#!/usr/bin/env python3
"""
O29 Step 3: O21 docking — is node9/node47 a second structure?
=============================================================
Dock the O29 decomposition results against O21's independent node-9
verification. Questions:

  Q1. Does the O5 catalogue contain any spot whose nearest node is 9
      (new numbering)? → c3 (10.34°), c11 (12.37°). Both are FARTHER than
      the mean. Removing them LOWERS p (0.072 → 0.051), i.e. they are
      ANTI-signal for the node network. Directly contradicts a
      "node9 drives p=0.072" hypothesis.

  Q2. O21 established node 9's temperature as Gaussian-random
      (z = -1.46σ, p = 8.2% @ 4.17°; z = -0.65σ @ 10°). Its "second cold
      structure" status is a real cross-map CMB feature but NOT
      significant against the GRF null. So even node-level, node 9 is
      not a network signal.

  Q3. Node 47 (O27: foreground-contaminated, b=-8.58°): no catalogue
      spot has node 47 as nearest. It cannot contribute to the
      mean-nearest statistic.

  Q4. Residual decomposition summary: the 34-spot baseline p=0.072 is
      dominated by the cold-spot family (6 spots nearest node 0:
      lit#1, c2, sub-spots A-D). Removing ALL 6 → p=0.365 (null).
      Removing only lit#1 (O5's original) leaves 5 family members
      still pulling the mean down.

  Output: structured verdict table for NN_results.md.
"""

import numpy as np
import json
import os

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh'
O5 = f'{BASE}/o5_catalog_compare'
O21 = f'{BASE}/o21_node9_anomaly'
OUT = f'{BASE}/o44_residual_decompose/data'
NODES = np.loadtxt(f'{O5}/../cmb_cold_spot/data/a5_nodes.txt')

os.makedirs(OUT, exist_ok=True)

node_ra = np.radians(NODES[:, 0])
node_dec = np.radians(NODES[:, 1])
node_vecs = np.stack([
    np.cos(node_dec) * np.cos(node_ra),
    np.cos(node_dec) * np.sin(node_ra),
    np.sin(node_dec)], axis=1)

# ---- load results ----
dec = json.load(open(f'{OUT}/decompose_results.json'))
boot = json.load(open(f'{OUT}/bootstrap_decompose.json'))
match = json.load(open(f'{O5}/data/match_results.json'))['matches']
o21 = json.load(open(f'{O21}/data/bootstrap_results.json'))

def nearest(v):
    dots = np.clip(node_vecs @ v, -1, 1)
    d = np.degrees(np.arccos(dots))
    return int(d.argmin()), float(d.min())

cat_ra = np.radians([m['ra'] for m in match])
cat_dec = np.radians([m['dec'] for m in match])
cat_vecs = np.stack([np.cos(cat_dec) * np.cos(cat_ra),
                     np.cos(cat_dec) * np.sin(cat_ra),
                     np.sin(cat_dec)], axis=1)
node_of = [nearest(cat_vecs[i])[0] for i in range(len(match))]

# Q3: node 47 spots?
n47 = [i for i, n in enumerate(node_of) if n == 47]
print("Q3: spots with nearest node 47:", len(n47))
for i in n47:
    print(f"   [{i}] {match[i]['name']}")

# Node 47 location + catalogue spot proximity
n47_pos = NODES[47]
print(f"   node 47 = ({n47_pos[0]:.2f}°, {n47_pos[1]:.2f}°) (O27: b=-8.6° foreground)")
# nearest catalogue spot to node 47
d47 = np.degrees(np.arccos(np.clip(node_vecs[47] @ cat_vecs.T, -1, 1)))
i_min = int(d47.argmin())
print(f"   nearest catalogue spot to node 47: {match[i_min]['name']} at {d47.min():.2f}°")

# Q1: node9 spots
n9 = [i for i, n in enumerate(node_of) if n == 9]
print("\nQ1: spots with nearest node 9:", len(n9))
for i in n9:
    print(f"   [{i}] {match[i]['name']} d={match[i]['nearest_deg']:.2f}° (kind={match[i]['kind']})")

# Q2: O21 numbers
print("\nQ2: O21 node-9 bootstrap (4.17°):")
print(f"   T_node9 = {o21['T_node9_obs_uK']:.1f} μK, z = {o21['z_node9']:.2f}σ, "
      f"p(T_2nd ≤ obs) = {o21['p_T_2nd_le_obs']:.4f}")

# ---- Build verdict table ----
print("\n" + "=" * 80)
print("VERDICT TABLE")
print("=" * 80)
rows = []
# baseline
r_base = dec['results']['all-minus-coldspot (34) — BASELINE']
rows.append(dict(hyp='baseline 34 (O5 pattern)', p=r_base['p'], z=r_base['z'],
                 verdict='🟡 residual 0.072'))
# cold family
r_cf = dec['results']['C4 minus-cold-family (6)']
rows.append(dict(hyp='minus cold-spot family (6)', p=r_cf['p'], z=r_cf['z'],
                 verdict='🔴 signal gone → family drives it'))
# node9
r_n9 = dec['results']['C1 minus-node9-spots (c3,c11)']
rows.append(dict(hyp='minus node-9 spots', p=r_n9['p'], z=r_n9['z'],
                 verdict='🟡 p lower → node9 spots ANTI-signal'))
# high-rot
h = boot['high_rotation']
rows.append(dict(hyp='hi-rot baseline (10k)', p=h['baseline-34']['p'], z=h['baseline-34']['z'],
                 verdict='—'))
rows.append(dict(hyp='hi-rot minus-cold-family', p=h['minus-cold-family']['p'], z=h['minus-cold-family']['z'],
                 verdict='🔴 confirms family'))
rows.append(dict(hyp='hi-rot minus-node9', p=h['minus-node9-spots']['p'], z=h['minus-node9-spots']['z'],
                 verdict='🟡 confirms anti-signal'))
# bootstrap
b = boot['bootstrap']
rows.append(dict(hyp='bootstrap frac p<0.05', p=b['frac_p_lt_005'], z=None,
                 verdict=f"{(1-b['frac_p_lt_005'])*100:.0f}% draws NS"))

for r in rows:
    zs = f"z={r['z']:+.2f}σ" if r['z'] is not None else "     "
    print(f"  {r['hyp']:<32} p={r['p']:.4f}  {zs}  {r['verdict']}")

# Save summary
summary = dict(
    baseline_34=dict(p=r_base['p'], z=r_base['z']),
    cold_family_removal=dict(p=r_cf['p'], z=r_cf['z']),
    node9_removal=dict(p=r_n9['p'], z=r_n9['z']),
    node9_spots=[dict(name=match[i]['name'], d=match[i]['nearest_deg']) for i in n9],
    node47_spots=[dict(name=match[i]['name'], d=match[i]['nearest_deg']) for i in n47],
    node47_nearest_spot=dict(name=match[i_min]['name'], d=float(d47.min())),
    o21_node9=dict(T=o21['T_node9_obs_uK'], z=o21['z_node9'], p=o21['p_T_2nd_le_obs']),
    bootstrap=b,
)
with open(f'{OUT}/o21_docking.json', 'w') as f:
    json.dump(summary, f, indent=2, ensure_ascii=False)
print(f"\nSaved: {OUT}/o21_docking.json")
