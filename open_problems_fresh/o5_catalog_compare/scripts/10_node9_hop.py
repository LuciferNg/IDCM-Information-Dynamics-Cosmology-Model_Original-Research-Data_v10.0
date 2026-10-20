#!/usr/bin/env python3
"""O5 node9: hop-level temperature comparison at 3.0 deg."""
import os
import numpy as np
import healpy as hp
from collections import deque, defaultdict
from astropy.coordinates import SkyCoord
import astropy.units as u

nodes = np.loadtxt('/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt')

# CRITICAL: SMICA is GALACTIC. Convert ICRS -> Galactic first.
sc_all = SkyCoord(ra=nodes[:, 0] * u.deg, dec=nodes[:, 1] * u.deg, frame='icrs')
gal_all = sc_all.galactic
NODES_L = gal_all.l.deg
NODES_B = gal_all.b.deg

ra, dec = np.radians(NODES_L), np.radians(NODES_B)
vecs = np.stack([np.cos(dec) * np.cos(ra),
                 np.cos(dec) * np.sin(ra),
                 np.sin(dec)], axis=1)
n = len(nodes)
adj = {}
for i in range(n):
    d = np.degrees(np.arccos(np.clip(vecs @ vecs[i], -1, 1)))
    adj[i] = set(np.where((d > 25) & (d < 28))[0])

hop = {0: 0}
q = deque([0])
while q:
    u = q.popleft()
    for v in adj[u]:
        if v not in hop:
            hop[v] = hop[u] + 1
            q.append(v)

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data/smooth_cache')
m_s = hp.read_map(f'{CACHE_DIR}/smica2_smooth3.0.fits', field=0)
nside = hp.get_nside(m_s)
T = m_s * 1e6
pix = hp.ang2pix(nside, NODES_L, NODES_B, lonlat=True)
node_T = T[pix]

groups = defaultdict(list)
for i in range(60):
    groups[hop[i]].append((i, node_T[i]))

print('Hop-level temperature stats at 3.0 deg:')
for h in sorted(groups):
    vals = [t for _, t in groups[h]]
    arr = np.array(vals)
    cmin = min(groups[h], key=lambda x: x[1])
    print(f'  hop {h}: n={len(vals)}, mean={arr.mean():+.1f}, std={arr.std():+.1f}, '
          f'min={arr.min():+.1f} (node{cmin[0]})')

print()
print('Hop=1 nodes at 3.0 deg:')
h1_sorted = sorted(groups[1], key=lambda x: x[1])
for i, t in h1_sorted:
    print(f'  node{i}: {t:+.1f} uK')

h1 = np.array([t for _, t in groups[1]])
z9 = (node_T[9] - h1.mean()) / h1.std()
print(f'\nnode9 z within hop1: {z9:+.2f}')
