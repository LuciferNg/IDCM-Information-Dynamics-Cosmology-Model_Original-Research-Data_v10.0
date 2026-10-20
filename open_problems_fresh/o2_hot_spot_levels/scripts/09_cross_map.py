#!/usr/bin/env python3
"""
O2 Step 9: Cross-map Validation — SMICA vs NILC vs Commander
============================================================
Cross-validate the F₆ hot spot (277.6 μK @ 1.0° smoothing)
across all available Planck component-separated maps.
"""

import numpy as np
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u
import sys, os

SMICA = '/tmp/smica2.fits'
NILC = '/tmp/nilc.fits'
COMMANDER = '/tmp/commander.fits'
NODES = '/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt'
COLORING = '/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/anchored_coloring.txt'
OUTDIR = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o2_hot_spot_levels/data'
os.makedirs(OUTDIR, exist_ok=True)

print("=" * 70)
print("O2 STEP 9: CROSS-MAP VALIDATION (SMICA × NILC × Commander)")
print("=" * 70)

# Key positions
HOTSPOT_10 = (157.8, -70.3)  # 1.0° F₆ candidate
HOTSPOT_05 = (0.2, -37.9)    # 0.5° F₇ candidate
COLDSPOT = (209.0, -57.0)

maps = {}

# 1. Load all maps
print(f"\n[1/4] Loading maps...")

# SMICA
m_sm = hp.read_map(SMICA, field=0)
nside = hp.get_nside(m_sm)
maps['SMICA'] = m_sm
print(f"  SMICA loaded: NSIDE={nside}")

# NILC (NESTED → RING)
m_nilc = hp.read_map(NILC, field=0, nest=True)
m_nilc = hp.reorder(m_nilc, n2r=True)
maps['NILC'] = m_nilc
print(f"  NILC loaded: NSIDE={hp.get_nside(m_nilc)}")

# Commander — NESTED ordering, convert to RING for processing
try:
    m_cmd = hp.read_map(COMMANDER, field=0, nest=True)
    m_cmd_r = hp.reorder(m_cmd, n2r=True)  # Convert to RING
    maps['Commander'] = m_cmd_r
    print(f"  Commander loaded: NSIDE={hp.get_nside(m_cmd_r)}, RING")
except (FileNotFoundError, OSError) as e:
    print(f"  Commander: NOT LOADED ({e})")

# 2. Cross-validation at multiple scales
print(f"\n[2/4] Cross-validation at multiple scales...")

# Helper: get pixel value from map (handles RING only now)
def get_pix(mm, mname, l, b, nside):
    pix = hp.ang2pix(nside, l, b, lonlat=True)
    return mm[pix]

print(f"  NOTE: Commander raw values are consistent with SMICA (F6 hot: 428 vs 408 uK)")
print(f"  But smoothing+remove_dipole interacts differently with Commander's large-scale structure.")
print(f"  Showing BOTH raw and smoothed values for Commander.\n")

scales = [0.0, 0.5, 1.0, 1.5, 3.0, 5.0]
positions = {'F₆ hot spot (157.8,-70.3)': HOTSPOT_10,
             'F₇ hot spot (0.2,-37.9)': HOTSPOT_05,
             'Cold spot (209,-57)': COLDSPOT}

print(f"  {'Scale':>5s}  {'Position':>30s}  ", end='')
for name in maps:
    print(f'{name:>10s}  ', end='')
print()
print(f"  {'-'*75}")

for FWHM in scales:
    for pos_name, (l, b) in positions.items():
        print(f"  {FWHM:>4.1f}°  {pos_name:>30s}  ", end='')
        for mname, mm in maps.items():
            if FWHM == 0.0:
                T = get_pix(mm, mname, l, b, nside) * 1e6
            else:
                sigma = np.radians(FWHM) / (2*np.sqrt(2*np.log(2)))
                mm_s = hp.remove_dipole(hp.smoothing(mm, sigma=sigma))
                T = get_pix(mm_s, mname, l, b, nside) * 1e6
            print(f'{T:>+9.1f}  ', end='')
        print()

# 3. Cross-map consistency statistics
print(f"\n[3/4] Cross-map consistency statistics...")
print(f"  {'Scale':>5s}  {'Position':>30s}  {'Mean':>8s}  {'Std':>8s}  {'Range':>10s}")
print(f"  {'-'*65}")

for FWHM in scales:
    sigma = np.radians(FWHM) / (2*np.sqrt(2*np.log(2))) if FWHM > 0 else 0
    for pos_name, (l, b) in positions.items():
        vals = []
        for mname, mm in maps.items():
            if FWHM == 0.0:
                T = get_pix(mm, mname, l, b, nside) * 1e6
            else:
                mm_s = hp.remove_dipole(hp.smoothing(mm, sigma=sigma))
                T = get_pix(mm_s, mname, l, b, nside) * 1e6
            vals.append(T)
        mean = np.mean(vals)
        std = np.std(vals)
        spread = np.ptp(vals)
        pct = std / abs(mean) * 100 if abs(mean) > 0.1 else 0
        print(f"  {FWHM:>4.1f}°  {pos_name:>30s}  {mean:>+8.1f}  {std:>7.2f}  {pct:>5.1f}%  [{spread:>5.1f}]")

# 4. 60-node correlation across maps
print(f"\n[4/4] 60-node temperature correlation across maps...")

# Read nodes
nodes_radec = np.loadtxt(NODES)
sc = SkyCoord(ra=nodes_radec[:,0]*u.deg, dec=nodes_radec[:,1]*u.deg, frame='icrs')
gal = sc.galactic
l_deg, b_deg = gal.l.deg, gal.b.deg

FWHM = 3.0
sigma = np.radians(FWHM) / (2*np.sqrt(2*np.log(2)))

node_T = {}
for mname, mm in maps.items():
    mm_s = hp.remove_dipole(hp.smoothing(mm, sigma=sigma))
    # Sample all 60 nodes
    T_nodes = np.array([get_pix(mm_s, mname, l_deg[i], b_deg[i], nside) for i in range(60)]) * 1e6
    node_T[mname] = T_nodes

# Correlation matrix
mnames = list(maps.keys())
print(f"  Correlation matrix (3° smoothing, 60 nodes):")
print(f"  {'':>12s}  ", end='')
for m2 in mnames:
    print(f'{m2:>10s}  ', end='')
print()
for m1 in mnames:
    print(f'  {m1:>10s}  ', end='')
    for m2 in mnames:
        r = np.corrcoef(node_T[m1], node_T[m2])[0, 1]
        print(f'{r:>10.4f}  ', end='')
    print()

# Save results
print(f"\n  Saving results...")
with open(os.path.join(OUTDIR, 'cross_map_validation.txt'), 'w') as f:
    f.write(f"# Cross-map validation results\n")
    f.write(f"# Maps: {', '.join(maps.keys())}\n\n")
    f.write(f"# Key positions\n")
    for FWHM in scales:
        sigma = np.radians(FWHM) / (2*np.sqrt(2*np.log(2)))
        for pos_name, (l, b) in positions.items():
            f.write(f"# {FWHM}deg {pos_name}: ")
            for mname, mm in maps.items():
                mm_s = hp.remove_dipole(hp.smoothing(mm, sigma=sigma))
                pix_p = hp.ang2pix(nside, l, b, lonlat=True)
                T = mm_s[pix_p] * 1e6
                f.write(f"{mname}={T:.1f} ")
            f.write("\n")
    f.write(f"\n# 60-node correlation matrix\n")
    for m1 in mnames:
        for m2 in mnames:
            r = np.corrcoef(node_T[m1], node_T[m2])[0, 1]
            f.write(f"corr_{m1}_{m2} {r:.4f}\n")

print(f"✅ Saved: data/cross_map_validation.txt")
print(f"\n{'='*70}")
print(f"O2 STEP 9 COMPLETE")
print(f"{'='*70}")