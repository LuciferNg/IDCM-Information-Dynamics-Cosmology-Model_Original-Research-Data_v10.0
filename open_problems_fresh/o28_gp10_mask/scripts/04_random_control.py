#!/usr/bin/env python3
"""
O28 Script 04: random control for gp10 node-distance under same mask
====================================================================
gp10 sits at b=-8° inside the |b|<20° galactic-plane zone. Its nearest
node is node21 at 10.05° (hot +95.5 μK). Is 10.05° unusual for a
random position in the SAME region (near-plane zone, similar |b|)?

Control design:
- Draw N random positions on the sky, constrained to the galactic-plane
  strip |b| < 20° (same mask situation as gp10)
- Compute nearest-node distance for each
- Compare: what fraction of random positions have nearest node <= 10.05°?
- Also do the full-sky control for reference.

This answers: is gp10's "no node within 10°" just the normal expectation
in a region with few nodes, or unusually empty?
"""
import numpy as np
import healpy as hp
import json, os

BASE = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh'
OUT = BASE + '/o28_gp10_mask/data'
NODE_FILE = BASE + '/cmb_cold_spot/data/a5_nodes.txt'
from astropy.coordinates import SkyCoord
import astropy.units as u

nodes = np.loadtxt(NODE_FILE)
node_gal = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs').galactic
node_l, node_b = node_gal.l.deg, node_gal.b.deg
node_vec = hp.ang2vec(np.radians(90-node_b), np.radians(node_l))  # (60,3)

def nearest_dist(l, b, n=1000):
    """Vectorized nearest-node distance for n random positions at (l,b)."""
    # random uniform on sphere
    rng = np.random.default_rng(42)
    z = rng.uniform(-1, 1, n)
    phi = rng.uniform(0, 2*np.pi, n)
    theta = np.arccos(z)
    vecs = np.stack([np.sin(theta)*np.cos(phi), np.sin(theta)*np.sin(phi), np.cos(theta)], axis=1)
    # all-to-all angular distance (n x 60)
    dots = np.clip(vecs @ node_vec.T, -1, 1)
    ang = np.degrees(np.arccos(dots))
    return ang.min(axis=1)

# ---- 1. Galactic-plane strip control (|b|<20°) ----
rng = np.random.default_rng(42)
n = 20000
z = rng.uniform(-1, 1, n)
phi = rng.uniform(0, 2*np.pi, n)
theta = np.arccos(z)
l_r = np.degrees(phi) % 360
b_r = 90 - np.degrees(theta)
# keep |b|<20
sel = np.abs(b_r) < 20
l_r, b_r = l_r[sel][:10000], b_r[sel][:10000]
vecs = hp.ang2vec(np.radians(90-b_r), np.radians(l_r))
dots = np.clip(vecs @ node_vec.T, -1, 1)
ang = np.degrees(np.arccos(dots))
nearest_plane = ang.min(axis=1)

# ---- 2. Full-sky control ----
vecs2 = hp.ang2vec(np.radians(90-b_r), np.radians(l_r))  # reuse same count
dots2 = np.clip(vecs2 @ node_vec.T, -1, 1)
ang2 = np.degrees(np.arccos(dots2))
nearest_full = ang2.min(axis=1)  # note: same positions, no |b| restriction
# regenerate full-sky properly
z2 = rng.uniform(-1, 1, 10000)
phi2 = rng.uniform(0, 2*np.pi, 10000)
theta2 = np.arccos(z2)
vecs3 = np.stack([np.sin(theta2)*np.cos(phi2), np.sin(theta2)*np.sin(phi2), np.cos(theta2)], axis=1)
dots3 = np.clip(vecs3 @ node_vec.T, -1, 1)
ang3 = np.degrees(np.arccos(dots3))
nearest_full = ang3.min(axis=1)

# ---- 3. Near-gp10 control: random positions within 30° of gp10 ----
gp_vec = hp.ang2vec(np.radians(90-(-8)), np.radians(32))
rng3 = np.random.default_rng(7)
n3 = 10000
# random points in cap of 30° around gp10 via rejection
pts = []
while len(pts) < n3:
    zz = rng3.uniform(-1, 1, 4*n3)
    pp = rng3.uniform(0, 2*np.pi, 4*n3)
    tt = np.arccos(zz)
    vv = np.stack([np.sin(tt)*np.cos(pp), np.sin(tt)*np.sin(pp), np.cos(tt)], axis=1)
    dots_gp = np.clip(vv @ gp_vec, -1, 1)
    keep = np.degrees(np.arccos(dots_gp)) <= 30
    pts.extend(vv[keep][:n3-len(pts)])
pts = np.array(pts)
dots_gp2 = np.clip(pts @ node_vec.T, -1, 1)
ang_gp = np.degrees(np.arccos(dots_gp2))
nearest_gp = ang_gp.min(axis=1)

print("=== Random-control nearest-node distance ===")
print(f"gp10 actual nearest node: 10.05° (node21, HOT +95.5 μK)")
print(f"\nGalactic-plane strip |b|<20° (n={len(nearest_plane)}):")
print(f"  mean={nearest_plane.mean():.2f}°, median={np.median(nearest_plane):.2f}°, "
      f"p5={np.percentile(nearest_plane,5):.2f}°, p95={np.percentile(nearest_plane,95):.2f}°")
print(f"  P(nearest <= 10.05°) = {(nearest_plane <= 10.05).mean():.3f}")
print(f"  P(nearest <= 5°) = {(nearest_plane <= 5).mean():.3f}")
print(f"\nFull sky (n={len(nearest_full)}):")
print(f"  mean={nearest_full.mean():.2f}°, median={np.median(nearest_full):.2f}°")
print(f"  P(nearest <= 10.05°) = {(nearest_full <= 10.05).mean():.3f}")
print(f"  P(nearest <= 5°) = {(nearest_full <= 5).mean():.3f}")
print(f"\nWithin 30° of gp10 (n={len(nearest_gp)}):")
print(f"  mean={nearest_gp.mean():.2f}°, median={np.median(nearest_gp):.2f}°, "
      f"p5={np.percentile(nearest_gp,5):.2f}°")
print(f"  P(nearest <= 10.05°) = {(nearest_gp <= 10.05).mean():.3f}")
print(f"  P(nearest <= 5°) = {(nearest_gp <= 5).mean():.3f}")

# save
res = dict(
    gp10_nearest=10.05, gp10_nearest_node=21,
    plane=dict(mean=float(nearest_plane.mean()), median=float(np.median(nearest_plane)),
               p_le_1005=float((nearest_plane <= 10.05).mean()),
               p_le_5=float((nearest_plane <= 5).mean()),
               n=int(len(nearest_plane))),
    full=dict(mean=float(nearest_full.mean()), median=float(np.median(nearest_full)),
              p_le_1005=float((nearest_full <= 10.05).mean()),
              p_le_5=float((nearest_full <= 5).mean()), n=int(len(nearest_full))),
    near_gp10=dict(mean=float(nearest_gp.mean()), median=float(np.median(nearest_gp)),
                   p_le_1005=float((nearest_gp <= 10.05).mean()),
                   p_le_5=float((nearest_gp <= 5).mean()), n=int(len(nearest_gp))))
with open(f'{OUT}/random_control.json', 'w') as f:
    json.dump(res, f, indent=2, ensure_ascii=False)
print(f"\nSaved: {OUT}/random_control.json")
