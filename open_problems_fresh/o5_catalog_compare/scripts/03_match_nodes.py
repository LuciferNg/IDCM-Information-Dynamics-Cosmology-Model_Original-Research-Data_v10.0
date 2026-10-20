#!/usr/bin/env python3
"""
O5 Step 3: Node matching — catalogue spots vs 60 A₅ nodes
==========================================================
For each catalogue spot (literature + SMICA-extracted), compute:
  1. Angular distance to nearest A₅ node
  2. Hit = distance < HIT_RADIUS (default 5° — the node's influence radius)
  3. Hit rate per catalogue + vs random expectation

Random expectation: with 60 nodes, the mean nearest-node distance for a
random point is ~13.0° (uniform on sphere). P(hit within r) ≈ 1 - (1 - f)^N
where f = fraction of sky covered by one node's disc of radius r.
For r = 5°: f = (1-cos 5°)/2 = 0.0038; P ≈ 1-(1-0.0038)^60 ≈ 0.204.
So ~20% of random spots would hit by chance — the null is NOT 0!
"""

import numpy as np
import json
import os
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o5_catalog_compare'
NODES = np.loadtxt(f'{BASE}/../cmb_cold_spot/data/a5_nodes.txt')  # ICRS RA, Dec
OUTDIR = f'{BASE}/data'
HIT_RADIUS = 5.0  # degrees

# ---- Load node unit vectors (ICRS) ----
node_ra = np.radians(NODES[:, 0])
node_dec = np.radians(NODES[:, 1])
node_vecs = np.stack([
    np.cos(node_dec) * np.cos(node_ra),
    np.cos(node_dec) * np.sin(node_ra),
    np.sin(node_dec)], axis=1)

def nearest_node_dist(ra_deg, dec_deg):
    """Angular distance (deg) from (RA, Dec) to nearest A₅ node."""
    ra, dec = np.radians(ra_deg), np.radians(dec_deg)
    v = np.array([np.cos(dec) * np.cos(ra), np.cos(dec) * np.sin(ra), np.sin(dec)])
    dots = np.clip(node_vecs @ v, -1.0, 1.0)
    return np.degrees(np.arccos(dots)).min(), int(np.argmin(dots))

def load_catalog():
    """Merge literature + SMICA catalogues into one spot list."""
    spots = []
    lit = json.load(open(f'{OUTDIR}/literature_catalog.json'))['spots']
    for s in lit:
        c = SkyCoord(l=s['l'] * u.deg, b=s['b'] * u.deg, frame='galactic').icrs
        spots.append(dict(name=f"LIT: {s['name']}", ra=float(c.ra.deg),
                          dec=float(c.dec.deg), kind='lit',
                          status=s['status'], amp=None,
                          source=s['source']))
    sm = json.load(open(f'{OUTDIR}/smica_catalog.json'))
    for kind in ['cold', 'hot']:
        for i, s in enumerate(sm[kind], 1):
            spots.append(dict(name=f"SMICA-{kind[:1]}{i}", ra=s['peak_ra'],
                              dec=s['peak_dec'], kind=kind,
                              status='smica', amp=s['amp_muK'],
                              source='SMICA 5.0° flood-fill'))
    return spots

print("=" * 66)
print("O5 STEP 3: NODE MATCHING")
print("=" * 66)

spots = load_catalog()
print(f"\nTotal spots: {len(spots)} "
      f"({sum(1 for s in spots if s['kind']=='lit')} literature, "
      f"{sum(1 for s in spots if s['kind']=='cold')} SMICA cold, "
      f"{sum(1 for s in spots if s['kind']=='hot')} SMICA hot)")

print(f"\n{'name':<28} {'RA°':>9} {'Dec°':>8} {'nearest':>7} {'node':>4} {'hit<5°':>7}")
print("-" * 70)
results = []
for s in spots:
    d, n = nearest_node_dist(s['ra'], s['dec'])
    hit = d < HIT_RADIUS
    results.append(dict(**s, nearest_deg=float(d), node=int(n), hit=bool(hit)))
    print(f"{s['name']:<28} {s['ra']:>9.2f} {s['dec']:>+8.2f} {d:>7.2f} {n:>4d} "
          f"{'✅' if hit else '—':>7}")

# ---- Hit-rate statistics ----
lit_hits = [r for r in results if r['kind'] == 'lit' and r['status'] != 'sub-spot']
lit_all = [r for r in results if r['kind'] == 'lit']
cold_hits = [r for r in results if r['kind'] == 'cold' and r['hit']]
hot_hits = [r for r in results if r['kind'] == 'hot' and r['hit']]

print(f"\n{'=' * 66}")
print("HIT RATE SUMMARY (hit = nearest node < 5°)")
print("=" * 66)
print(f"  Literature confirmed spots: {sum(1 for r in lit_hits if r['hit'])}/{len(lit_hits)} hit")
print(f"  Literature all (incl sub-spots): {sum(1 for r in lit_all if r['hit'])}/{len(lit_all)} hit")
print(f"  SMICA cold spots: {len(cold_hits)}/{sum(1 for r in results if r['kind']=='cold')} hit")
print(f"  SMICA hot spots:  {len(hot_hits)}/{sum(1 for r in results if r['kind']=='hot')} hit")

# Random expectation: exact geometric coverage
# For N=60 nodes, each with a 5° disc, what fraction of sky is covered?
# MC estimate: sample 200k random points, count fraction within 5° of a node.
rng = np.random.default_rng(42)
n_mc = 200000
# uniform on sphere
z = rng.uniform(-1, 1, n_mc)
phi = rng.uniform(0, 2 * np.pi, n_mc)
mc_vecs = np.stack([np.sqrt(1 - z**2) * np.cos(phi),
                    np.sqrt(1 - z**2) * np.sin(phi), z], axis=1)
dots = mc_vecs @ node_vecs.T
covered = (np.degrees(np.arccos(np.clip(dots, -1, 1))) < HIT_RADIUS).any(axis=1)
frac_covered = covered.mean()
print(f"\n  Random expectation: {frac_covered*100:.1f}% of sky within {HIT_RADIUS}° of a node")
print(f"  → random catalogue of M spots: expect {frac_covered*len(cold_hits + hot_hits):.1f} hits "
      f"per {len(cold_hits)+len(hot_hits)} spots")

# Save
out = dict(hit_radius=HIT_RADIUS, frac_sky_covered=float(frac_covered),
           matches=results)
with open(f'{OUTDIR}/match_results.json', 'w') as f:
    json.dump(out, f, indent=2, ensure_ascii=False)
print(f"\nSaved: data/match_results.json")

# Nearest-node distance distribution summary
dists = np.array([r['nearest_deg'] for r in results])
print(f"\nNearest-node distance: mean={dists.mean():.2f}°, median={np.median(dists):.2f}°, "
      f"min={dists.min():.2f}°, max={dists.max():.2f}°")
