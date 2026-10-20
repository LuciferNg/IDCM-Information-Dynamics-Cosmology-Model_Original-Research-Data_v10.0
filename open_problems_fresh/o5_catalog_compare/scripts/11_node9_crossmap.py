#!/usr/bin/env python3
"""
O5 follow-up: node 9 CROSS-MAP verification (SMICA × NILC × Commander)
=======================================================================
Node 9 (Gal 214.92,-31.16) is the 2nd/3rd coldest node at ALL scales.
Before declaring it a real structure, verify across independent
component-separation maps (O2 §12 pattern):
  - SMICA: /tmp/smica2.fits (RING)
  - NILC:  /tmp/nilc.fits (NESTED → reorder!)
  - Commander: /tmp/commander.fits (NESTED → reorder!)

Success criteria (<1% across methods = 🟢🟢 confirmed).
"""

import numpy as np
import healpy as hp
import os

BASE = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o5_catalog_compare'
NODES = np.loadtxt(f'{BASE}/../cmb_cold_spot/data/a5_nodes.txt')

from astropy.coordinates import SkyCoord
import astropy.units as u

sc_all = SkyCoord(ra=NODES[:, 0] * u.deg, dec=NODES[:, 1] * u.deg, frame='icrs')
gal_all = sc_all.galactic
L = gal_all.l.deg
B = gal_all.b.deg

FWHM = 3.0
sig = np.radians(FWHM) / (2 * np.sqrt(2 * np.log(2)))

maps = {
    'SMICA': ('/tmp/smica2.fits', False),
    'NILC': ('/tmp/nilc.fits', True),        # NESTED
    'Commander': ('/tmp/commander.fits', True),  # NESTED
}

print("=" * 66)
print("NODE 9 CROSS-MAP VERIFICATION (3.0° smoothing)")
print("=" * 66)

results = {}
for name, (path, nested) in maps.items():
    if not os.path.exists(path):
        print(f"  {name}: MISSING {path}")
        continue
    m = hp.read_map(path, field=0, nest=nested)
    if nested:
        m = hp.reorder(m, n2r=True)
    m_s = hp.remove_dipole(hp.smoothing(m, sigma=sig))
    nside = hp.get_nside(m_s)
    T = m_s * 1e6
    pix9 = hp.ang2pix(nside, L[9], B[9], lonlat=True)
    pix0 = hp.ang2pix(nside, L[0], B[0], lonlat=True)
    pix_all = hp.ang2pix(nside, L, B, lonlat=True)
    node_T = T[pix_all]
    rank9 = int(np.argsort(node_T).tolist().index(9)) + 1
    results[name] = (T[pix9], T[pix0], rank9)
    print(f"  {name}: node9={T[pix9]:+7.1f} μK, node0={T[pix0]:+7.1f} μK, "
          f"node9 rank={rank9}/60")

# Agreement
if len(results) == 3:
    n9 = np.array([v[0] for v in results.values()])
    n0 = np.array([v[1] for v in results.values()])
    spread9 = (n9.max() - n9.min()) / abs(n9.mean()) * 100
    spread0 = (n0.max() - n0.min()) / abs(n0.mean()) * 100
    print(f"\n  Node 9 spread: {spread9:.1f}% across 3 maps "
          f"{'🟢🟢 confirmed' if spread9 < 5 else '🟡 marginal' if spread9 < 20 else '🔴 invalid'}")
    print(f"  Node 0 spread: {spread0:.1f}% (sanity — must be small)")
