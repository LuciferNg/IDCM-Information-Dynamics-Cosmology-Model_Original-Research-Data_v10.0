#!/usr/bin/env python3
"""
O2 Step 9b: Save cross-map validation results
==============================================
Fast version: compute key positions at scales, save to file.
Uses single-pass smoothing (smooth each map once per scale).
"""

import numpy as np
import healpy as hp
import os

SMICA = '/tmp/smica2.fits'
NILC = '/tmp/nilc.fits'
COMMANDER = '/tmp/commander.fits'
OUTDIR = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o2_hot_spot_levels/data'
os.makedirs(OUTDIR, exist_ok=True)

print("O2 STEP 9b: SAVING CROSS-MAP RESULTS")

# Load maps (all RING)
m_sm = hp.read_map(SMICA, field=0)
m_nc = hp.read_map(NILC, field=0, nest=True)
m_nc = hp.reorder(m_nc, n2r=True)
m_cd = hp.read_map(COMMANDER, field=0, nest=True)
m_cd = hp.reorder(m_cd, n2r=True)

nside = 2048
maps = {'SMICA': m_sm, 'NILC': m_nc, 'Commander': m_cd}

# Key positions
positions = {'F6_hotspot': (157.8, -70.3),
             'F7_hotspot': (0.2, -37.9),
             'Cold_spot': (209.0, -57.0)}

scales = [0.0, 0.5, 1.0, 1.5, 3.0, 5.0]

with open(os.path.join(OUTDIR, 'cross_map_validation.txt'), 'w') as f:
    f.write("# Cross-map validation results\n")
    f.write(f"# Maps: SMICA, NILC, Commander\n")
    f.write(f"# All maps NSIDE=2048, RING ordering after processing\n\n")
    f.write("# Key positions (T in uK)\n")
    
    for FWHM in scales:
        if FWHM == 0.0:
            # Raw maps
            print(f"Scale {FWHM} (raw)...")
            f.write(f"# {FWHM}deg raw\n")
            for pos_name, (l, b) in positions.items():
                f.write(f"{FWHM} {pos_name} ")
                for mname, mm in maps.items():
                    pix = hp.ang2pix(nside, l, b, lonlat=True)
                    T = mm[pix] * 1e6
                    f.write(f"{mname}={T:.1f} ")
                f.write("\n")
        else:
            sigma = np.radians(FWHM) / (2*np.sqrt(2*np.log(2)))
            print(f"Scale {FWHM}...")
            f.write(f"# {FWHM}deg smoothed\n")
            for pos_name, (l, b) in positions.items():
                f.write(f"{FWHM} {pos_name} ")
                for mname, mm in maps.items():
                    mm_s = hp.remove_dipole(hp.smoothing(mm, sigma=sigma))
                    pix = hp.ang2pix(nside, l, b, lonlat=True)
                    T = mm_s[pix] * 1e6
                    f.write(f"{mname}={T:.1f} ")
                f.write("\n")
    
    # Correlation matrix (3° smoothing, 60 nodes)
    print("Computing 60-node correlation...")
    from astropy.coordinates import SkyCoord
    import astropy.units as u
    NODES = '/home/wsl/Projects/IDCM/IDCM-v10.0/main_problems/p4_cmb_cold_spot/data/a5_nodes.txt'
    nodes_radec = np.loadtxt(NODES)
    sc = SkyCoord(ra=nodes_radec[:,0]*u.deg, dec=nodes_radec[:,1]*u.deg, frame='icrs')
    gal = sc.galactic
    l_deg, b_deg = gal.l.deg, gal.b.deg
    
    sigma = np.radians(3.0) / (2*np.sqrt(2*np.log(2)))
    node_T = {}
    for mname, mm in maps.items():
        mm_s = hp.remove_dipole(hp.smoothing(mm, sigma=sigma))
        T_nodes = np.array([mm_s[hp.ang2pix(nside, l_deg[i], b_deg[i], lonlat=True)] for i in range(60)]) * 1e6
        node_T[mname] = T_nodes
    
    f.write("\n# 60-node correlation matrix (3 deg smoothing)\n")
    mnames = list(maps.keys())
    for m1 in mnames:
        for m2 in mnames:
            r = np.corrcoef(node_T[m1], node_T[m2])[0, 1]
            f.write(f"corr_{m1}_{m2} {r:.4f}\n")

print("✅ Saved: data/cross_map_validation.txt")
print("O2 STEP 9b COMPLETE")