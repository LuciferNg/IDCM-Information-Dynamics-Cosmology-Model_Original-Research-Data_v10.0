#!/usr/bin/env python3
"""
O28 Script 03: cross-map verification of the gp10 0.5° cold peak + node distances
==================================================================================
The 0.5° peak at (32.4,-5.5) = -215 μK sits INSIDE the galactic plane
(b=-5.5°, |b|<20°). Galactic-plane small-scale cold features are usually
foreground (dust/CO/point sources). Verify against NILC & Commander:
if the feature is present in all 3 component-separation methods, it's
more likely genuine; if only in SMICA, it's a separation artifact.

Then: mask-corrected node distances. The "centre" candidates:
  a) Planck gp10 (l=32,b=-8)
  b) 0.5°-scale cold peak (32.4,-5.5)
  c) mask-corrected centroid of the cold pixels (|b|>=10 cut)
"""
import numpy as np
import healpy as hp
import json, os

BASE = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh'
CACHE = BASE + '/o5_catalog_compare/data/smooth_cache'
OUT = BASE + '/o28_gp10_mask/data'
NODE_FILE = BASE + '/cmb_cold_spot/data/a5_nodes.txt'

GP_L, GP_B = 32.0, -8.0

# ---- 1. Cross-map: sample the 0.5° peak in all 3 maps ----
print("=== Cross-map at (32.4,-5.5) and surrounds ===")
peaks = [(32.4,-5.5), (32.0,-8.0), (37.6,-16.3)]
maps = {'SMICA': 'smica2_smooth0.5.fits', 'NILC': 'nilc2_smooth4.17.fits',
        'Commander': 'commander_smooth4.17.fits'}
# NILC/Commander only cached at 4.17°; SMICA has 0.5°. Compare at 4.17°.
maps417 = {'SMICA': 'smica2_smooth4.17.fits', 'NILC': 'nilc2_smooth4.17.fits',
           'Commander': 'commander_smooth4.17.fits'}
print(f"\n{'pos':<16}", end='')
for name in maps417:
    print(f"{name:>12}", end='')
print()
for (pl, pb) in peaks + [(32.4,-5.5)]:
    print(f"({pl},{pb:+})".ljust(16), end='')
    for name, f in maps417.items():
        m = hp.read_map(f'{CACHE}/{f}', field=0)
        pix = hp.ang2pix(hp.get_nside(m), pl, pb, lonlat=True)
        print(f"{m[pix]*1e6:>+11.1f}", end='')
    print()

# Also fine-grid around the 0.5° peak to find its extent in 4.17° maps
print("\n=== Fine grid around (32.4,-5.5) at 4.17° ===")
for dl in [-3, -1.5, 0, 1.5, 3]:
    row = []
    for db in [-3, -1.5, 0, 1.5, 3]:
        pix = hp.ang2pix(2048, 32.4+dl, -5.5+db, lonlat=True)
        m = hp.read_map(f'{CACHE}/smica2_smooth4.17.fits', field=0)
        row.append(m[pix]*1e6)
    print(f"  dl={dl:+4.1f}: " + " ".join(f"{v:+6.1f}" for v in row))

# ---- 2. Node distances from candidate centres ----
nodes = np.loadtxt(NODE_FILE)
from astropy.coordinates import SkyCoord
import astropy.units as u
node_gal = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs').galactic
node_l, node_b = node_gal.l.deg, node_gal.b.deg

def angdist(l1, b1):
    v1 = hp.ang2vec(np.radians(90-b1), np.radians(l1))
    v2 = hp.ang2vec(np.radians(90-node_b), np.radians(node_l))
    return np.degrees(np.arccos(np.clip(v1 @ v2.T, -1, 1)))

print("\n=== Node distances from gp10 candidates ===")
centres = [('Planck gp10 (32,-8)', 32.0, -8.0),
           ('0.5° peak (32.4,-5.5)', 32.4, -5.5),
           ('midpoint (32.2,-6.75)', 32.2, -6.75)]
for label, cl, cb in centres:
    d = angdist(cl, cb)
    order = np.argsort(d)
    print(f"\n{label}:")
    for i in order[:5]:
        print(f"  node{i:>2}: {d[i]:.2f}°  (l={node_l[i]:.1f}, b={node_b[i]:+.1f})")

# ---- 3. Mask-corrected centroid of COLD pixels near gp10 ----
print("\n=== Mask-corrected cold centroid (SMICA 4.17°, |b|>=10, r<=15°) ===")
m417 = hp.read_map(f'{CACHE}/smica2_smooth4.17.fits', field=0)
nside = hp.get_nside(m417)
vec_gp = hp.ang2vec(np.radians(90-GP_B), np.radians(GP_L))
disc = hp.query_disc(nside, vec_gp, np.radians(15))
l_d, b_d = hp.pix2ang(nside, disc, lonlat=True)
for bcut in [5, 10, 15]:
    sel = disc[(m417[disc] < 0) & (np.abs(b_d) >= bcut)]
    if len(sel) < 10:
        print(f"  bcut={bcut}: only {len(sel)} cold pix")
        continue
    v = hp.pix2vec(nside, sel)
    vc = np.mean(v, axis=1); vc /= np.linalg.norm(vc)
    cl, cb = hp.vec2ang(vc, lonlat=True)
    d = angdist(float(np.atleast_1d(cl)[0]), float(np.atleast_1d(cb)[0]))
    order = np.argsort(d)
    print(f"  bcut={bcut}: centroid ({cl[0]:.1f},{cb[0]:+.1f}), {len(sel)} pix, "
          f"mean T={m417[sel].mean()*1e6:+.1f} μK")
    for i in order[:3]:
        print(f"    node{i:>2}: {d[i]:.2f}°")

# ---- 4. node21/26/22 membership: are they inside any cold region? ----
print("\n=== node26/22 membership in gp10 cold pixels ===")
for ni in [21, 26, 22]:
    pix = hp.ang2pix(nside, node_l[ni], node_b[ni], lonlat=True)
    print(f"  node{ni}: l={node_l[ni]:.1f}, b={node_b[ni]:+.1f}, "
          f"T(4.17°)={m417[pix]*1e6:+.1f} μK, "
          f"dist to gp10={angdist(32,-8)[ni]:.1f}°")
