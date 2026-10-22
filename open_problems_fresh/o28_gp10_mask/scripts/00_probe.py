#!/usr/bin/env python3
"""
O28 probe: gp10 (l=32,b=-8) node-distance cross-check
======================================================
Resolve discrepancy: SESSION_START says nearest node21 (10.1°),
match_results.json says node49 (10.05°). Verify node indexing,
ICRS->Galactic conversion, and sample SMICA temperatures.

Also: which nodes sit within ~20° of gp10, their temperatures,
and the galactic-plane context (gp10 at b=-8°).
"""
import numpy as np
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh'
NODE_FILE = BASE + '/cmb_cold_spot/data/a5_nodes.txt'
CACHE = BASE + '/o5_catalog_compare/data/smooth_cache'

# --- gp10 (Galactic, from Planck 2013 XXIII Sect 4.4) ---
gp_l, gp_b = 32.0, -8.0
sc = SkyCoord(l=gp_l*u.deg, b=gp_b*u.deg, frame='galactic')
icrs = sc.icrs
print(f"gp10 Galactic (l={gp_l}, b={gp_b}) -> ICRS (RA={icrs.ra.deg:.4f}, Dec={icrs.dec.deg:.4f})")

# --- nodes (ICRS RA/Dec) ---
nodes = np.loadtxt(NODE_FILE)
print(f"Nodes: {nodes.shape[0]}, first: {nodes[0]}, last: {nodes[-1]}")

# node ICRS -> Galactic
node_gal = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs').galactic
node_l = node_gal.l.deg
node_b = node_gal.b.deg

# angular distances from gp10 (in Galactic frame, same as nodes)
def angdist(l1,b1,l2,b2):
    v1 = hp.ang2vec(np.radians(90-b1), np.radians(l1))
    v2 = hp.ang2vec(np.radians(90-b2), np.radians(l2))
    return np.degrees(np.arccos(np.clip(v1 @ v2.T, -1, 1)))

d = angdist(gp_l, gp_b, node_l, node_b)
order = np.argsort(d)
print(f"\n{'idx':>3} {'dist°':>7} {'node_l':>8} {'node_b':>8} {'RA':>10} {'Dec':>9}")
for i in order[:12]:
    print(f"{i:>3} {d[i]:>7.2f} {node_l[i]:>8.2f} {node_b[i]:>8.2f} {nodes[i,0]:>10.3f} {nodes[i,1]:>9.3f}")

# --- sample SMICA 4.17° at these nodes (galactic coords!) ---
m = hp.read_map(f'{CACHE}/smica2_smooth4.17.fits', field=0)
nside = hp.get_nside(m)
print(f"\nSMICA 4.17° cache: nside={nside}")
print(f"\n{'idx':>3} {'dist°':>7} {'T μK':>8}  (frame-corrected galactic sampling)")
for i in order[:12]:
    pix = hp.ang2pix(nside, node_l[i], node_b[i], lonlat=True)
    print(f"{i:>3} {d[i]:>7.2f} {m[pix]*1e6:>8.1f}")

# --- cross-check: match_results.json node 49 claim ---
# node49 in file (0-indexed) = line 50 = (104.7318, 15.2120)
n49 = nodes[49]
print(f"\nnode49 (file): RA={n49[0]}, Dec={n49[1]}")
g49 = SkyCoord(ra=n49[0]*u.deg, dec=n49[1]*u.deg, frame='icrs').galactic
print(f"node49 galactic: l={g49.l.deg:.2f}, b={g49.b.deg:.2f}")
print(f"node49 <-> gp10 distance: {angdist(gp_l, gp_b, g49.l.deg, g49.b.deg):.2f}°")

# --- gp10 region context: what's around (32,-8)? ---
# Sample a small grid to see the local temperature structure
print("\ngp10 neighbourhood (SMICA 4.17°):")
for dl in [0, 5, 10, 15]:
    for db in [0, -5, 5]:
        ll = gp_l + dl
        bb = gp_b + db
        pix = hp.ang2pix(nside, ll, bb, lonlat=True)
        print(f"  l={ll:>5.1f} b={bb:>+4.1f}  T={m[pix]*1e6:+7.1f} μK")

# --- where is the galactic plane cut? gp10 masked fraction at |b|<20 ---
npix = hp.nside2npix(nside)
l_arr, b_arr = hp.pix2ang(nside, np.arange(npix), lonlat=True)
frac_plane = np.mean(np.abs(b_arr) < 20)
print(f"\nGalactic plane |b|<20° covers {frac_plane*100:.1f}% of sky")
