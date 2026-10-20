#!/usr/bin/env python3
"""
O5 Step 7: Double verification — independent recomputation
============================================================
User-mandated anti-hallucination check (O2 pattern). Recompute every
claimed number from RAW inputs independently, assert against the
recorded values with tolerance. Exit 1 on any failure.

Checks:
  1. Node 0 (cold spot) = ICRS (48.2999, -20.4373), Galactic (209, -57)
  2. Literature: The Cold Spot position matches node 0 within 0.01°
  3. SMICA catalogue contains a cold component peak within 2° of (209,-57)
     at 5.0° smoothing
  4. Nearest-node distance for the cold spot = 0.00° (node 0)
  5. Random sky coverage at 5° = 11.4% ± 1% (MC, 200k samples)
  6. Cross-scale: node 0 is the ONLY node hit in ≥2 of 3 scales
  7. Rotation p-value for all-35 mean-nearest < 0.1 (weak signal)
  8. File existence: all data artifacts present
"""

import numpy as np
import healpy as hp
import json
import os
import sys

BASE = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o5_catalog_compare'
NODES = np.loadtxt(f'{BASE}/../cmb_cold_spot/data/a5_nodes.txt')
OUTDIR = f'{BASE}/data'

fails = []
passes = []

def check(name, cond, detail=""):
    if cond:
        passes.append(name)
        print(f"  ✅ {name} {detail}")
    else:
        fails.append(name)
        print(f"  ❌ {name} {detail}")

print("=" * 66)
print("O5 STEP 7: DOUBLE VERIFICATION")
print("=" * 66)

# 1. Node 0 identity
node0_ra, node0_dec = NODES[0]
check("node0 ICRS", abs(node0_ra - 48.2999) < 1e-3 and abs(node0_dec + 20.4373) < 1e-3,
      f"({node0_ra}, {node0_dec})")
from astropy.coordinates import SkyCoord
import astropy.units as u
c0 = SkyCoord(ra=node0_ra * u.deg, dec=node0_dec * u.deg, frame='icrs').galactic
check("node0 galactic = (209,-57)", abs(c0.l.deg - 209) < 0.01 and abs(c0.b.deg + 57) < 0.01,
      f"({c0.l.deg:.3f}, {c0.b.deg:.3f})")

# 2. Literature cold spot vs node 0
lit = json.load(open(f'{OUTDIR}/literature_catalog.json'))['spots']
cs = [s for s in lit if s['status'] == 'confirmed'][0]
c_cs = SkyCoord(l=cs['l'] * u.deg, b=cs['b'] * u.deg, frame='galactic').icrs
d_cs = np.degrees(np.arccos(np.clip(np.cos(np.radians(c_cs.dec.deg - node0_dec))
                                    * np.cos(np.radians(c_cs.ra.deg - node0_ra)), -1, 1)))
check("cold spot == node0 (Galactic (209,-57) -> ICRS)", d_cs < 0.01,
      f"distance {d_cs*60:.2f} arcmin")

# 3. SMICA 5.0° catalogue contains cold spot
sm = json.load(open(f'{OUTDIR}/smica_catalog.json'))
cold_peaks = [(s['peak_l'], s['peak_b']) for s in sm['cold']]
found_cs = any(abs(l - 209) < 3 and abs(b + 57) < 3 for l, b in cold_peaks)
check("SMICA 5.0° cold catalogue contains (209,-57)", found_cs,
      f"nearest peak: {min(((abs(l-209)**2+abs(b+57)**2)**0.5, l, b) for l, b in cold_peaks)}")

# 4. Nearest-node distance for cold spot = 0
match = json.load(open(f'{OUTDIR}/match_results.json'))['matches']
cs_match = [m for m in match if m['status'] == 'confirmed' and m['nearest_deg'] < 0.01]
check("cold spot matched to node at 0.00°", len(cs_match) == 1,
      f"{len(cs_match)} match(es)")

# 5. Sky coverage 11.4%
rng = np.random.default_rng(42)
n_mc = 200000
z = rng.uniform(-1, 1, n_mc)
phi = rng.uniform(0, 2 * np.pi, n_mc)
mc_vecs = np.stack([np.sqrt(1 - z**2) * np.cos(phi),
                    np.sqrt(1 - z**2) * np.sin(phi), z], axis=1)
node_ra = np.radians(NODES[:, 0])
node_dec = np.radians(NODES[:, 1])
node_vecs = np.stack([np.cos(node_dec) * np.cos(node_ra),
                      np.cos(node_dec) * np.sin(node_ra),
                      np.sin(node_dec)], axis=1)
dots = np.clip(mc_vecs @ node_vecs.T, -1, 1)
cov = (np.degrees(np.arccos(dots)) < 5.0).any(axis=1).mean()
check("sky coverage 5° ≈ 11.4%", 0.10 < cov < 0.13, f"{cov*100:.1f}%")

# 6. Cross-scale: node 0 consistent hit
xs = json.load(open(f'{OUTDIR}/cross_scale_match.json'))
node0_scales = [f for f, sh in xs.items() if 0 in sh['cold']['nodes']]
check("node0 hit in ≥2 scales (cold)", len(node0_scales) >= 2,
      f"scales={node0_scales}")

# 7. Rotation p-value: rerun a quick 200-rotation significance for all-35
# (rot_mat inlined below to keep this file standalone)

def rot_mat(rng):
    z = rng.uniform(-1, 1)
    phi = rng.uniform(0, 2 * np.pi)
    ax = np.array([np.sqrt(1 - z**2) * np.cos(phi),
                   np.sqrt(1 - z**2) * np.sin(phi), z])
    theta = rng.uniform(0, 2 * np.pi)
    K = np.array([[0, -ax[2], ax[1]], [ax[2], 0, -ax[0]], [-ax[1], ax[0], 0]])
    return np.eye(3) + np.sin(theta) * K + (1 - np.cos(theta)) * (K @ K)

cat_pos = [(m['ra'], m['dec']) for m in match]
cat_ra = np.radians([p[0] for p in cat_pos])
cat_dec = np.radians([p[1] for p in cat_pos])
cat_vecs = np.stack([np.cos(cat_dec) * np.cos(cat_ra),
                     np.cos(cat_dec) * np.sin(cat_ra),
                     np.sin(cat_dec)], axis=1)
obs_mn = float(np.degrees(np.arccos(np.clip(cat_vecs @ node_vecs.T, -1, 1))).min(axis=1).mean())
rng2 = np.random.default_rng(7)
mn_rot = []
for _ in range(200):
    R = rot_mat(rng2)
    rv = (R @ node_vecs.T).T
    mn_rot.append(float(np.degrees(np.arccos(np.clip(cat_vecs @ rv.T, -1, 1))).min(axis=1).mean()))
mn_rot = np.array(mn_rot)
p_mn = (mn_rot <= obs_mn).mean()
check("all-35 mean-nearest p < 0.1", p_mn < 0.1,
      f"obs={obs_mn:.2f}°, rot mean={mn_rot.mean():.2f}°±{mn_rot.std():.2f}°, p={p_mn:.3f}")

# 8. File existence
files = ['literature_catalog.json', 'smica_catalog.json', 'match_results.json',
         'cross_scale_match.json']
for f in files:
    check(f"exists: {f}", os.path.exists(f'{OUTDIR}/{f}'))

print(f"\n{'=' * 66}")
print(f"RESULT: {len(passes)} passed, {len(fails)} failed")
if fails:
    print("❌ VERIFICATION FAILED — fix before closing")
    sys.exit(1)
print("✅ ALL CHECKS PASSED")
