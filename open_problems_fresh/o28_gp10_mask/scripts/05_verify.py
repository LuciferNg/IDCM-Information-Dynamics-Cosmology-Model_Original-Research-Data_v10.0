#!/usr/bin/env python3
"""
O28 Script 05: file verifier — read back JSON outputs, assert claims
====================================================================
No-hallucination close-out: verify every number that will go into
NN_results.md by reading the ACTUAL data files (JSON), not script stdout.
"""
import json, os, sys
import numpy as np
import healpy as hp

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = f'{BASE}/data'

checks = []
def chk(name, cond, detail=""):
    checks.append((name, bool(cond), detail))

# ---- 1. gp10_extract.json ----
with open(f'{DATA}/gp10_extract.json') as f:
    ext = json.load(f)
chk("extract: 4 scales present", set(ext.keys()) == {'3.0°','4.17°','5.0°','7.0°'}, str(ext.keys()))
chk("extract: 4.17° has 0 cold comps at all bcut", 
    all(len(ext['4.17°'][f'bcut{b}']) == 0 for b in [5,10,15,20]))
chk("extract: 5.0° has 0 cold comps at all bcut",
    all(len(ext['5.0°'][f'bcut{b}']) == 0 for b in [5,10,15,20]))
chk("extract: 7.0° has 0 cold comps at all bcut",
    all(len(ext['7.0°'][f'bcut{b}']) == 0 for b in [5,10,15,20]))
c3 = ext['3.0°']['bcut5']
chk("extract: 3.0° bcut5 has 2 comps", len(c3) == 2, f"{len(c3)}")
chk("extract: 3.0° strongest comp peak near (22.4,-25.0)",
    abs(c3[0]['peak_l']-22.4) < 0.5 and abs(c3[0]['peak_b']+25.0) < 0.5,
    f"({c3[0]['peak_l']},{c3[0]['peak_b']})")
chk("extract: 3.0° strongest comp amp ~ -83 μK", abs(c3[0]['amp_muK']+83.2) < 2,
    f"{c3[0]['amp_muK']}")

# ---- 2. gp10_planck_style.json ----
with open(f'{DATA}/gp10_planck_style.json') as f:
    ps = json.load(f)
r16 = ps['nside16_stats']['region']; rst = ps['nside16_stats']['rest']
chk("planck: region var < rest var (0.75)", r16['var'] < rst['var'],
    f"{r16['var']:.0f} vs {rst['var']:.0f}")
chk("planck: region skew POSITIVE (+0.12)", r16['skew'] > 0, f"{r16['skew']:.3f}")
chk("planck: region mean ~ +22.9", abs(r16['mean']-22.9) < 1, f"{r16['mean']}")
chk("planck: 0.5° fine peak (32.4,-5.5) amp -215", 
    abs(ps['fine']['0.5°']['peak_l']-32.4) < 0.5 and abs(ps['fine']['0.5°']['peak_b']+5.5) < 0.5 
    and abs(ps['fine']['0.5°']['amp']+215) < 8,
    f"({ps['fine']['0.5°']['peak_l']},{ps['fine']['0.5°']['peak_b']}) = {ps['fine']['0.5°']['amp']}")
chk("planck: radial 0-5° mean +24.7", abs(ps['radial']['0-5°']['mean']-24.7) < 1,
    f"{ps['radial']['0-5°']['mean']}")
chk("planck: radial 25-30° mean +20.9", abs(ps['radial']['25-30°']['mean']-20.9) < 1,
    f"{ps['radial']['25-30°']['mean']}")

# ---- 3. random_control.json ----
with open(f'{DATA}/random_control.json') as f:
    rc = json.load(f)
chk("control: gp10 nearest 10.05", abs(rc['gp10_nearest']-10.05) < 0.01)
chk("control: plane median ~10.3", abs(rc['plane']['median']-10.32) < 0.2,
    f"{rc['plane']['median']}")
chk("control: plane P(<=10.05) ~0.477", abs(rc['plane']['p_le_1005']-0.477) < 0.03,
    f"{rc['plane']['p_le_1005']}")
chk("control: full P(<=10.05) ~0.454", abs(rc['full']['p_le_1005']-0.454) < 0.03,
    f"{rc['full']['p_le_1005']}")
chk("control: near-gp10 P(<=10.05) ~0.447", abs(rc['near_gp10']['p_le_1005']-0.447) < 0.03,
    f"{rc['near_gp10']['p_le_1005']}")

# ---- 4. Probe recheck: node distances (independent recompute) ----
NODE_FILE = BASE + '/../cmb_cold_spot/data/a5_nodes.txt'
nodes = np.loadtxt(NODE_FILE)
from astropy.coordinates import SkyCoord
import astropy.units as u
ng = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs').galactic
v_gp = hp.ang2vec(np.radians(90-(-8)), np.radians(32))
vn = hp.ang2vec(np.radians(90-ng.b.deg), np.radians(ng.l.deg))
d = np.degrees(np.arccos(np.clip(v_gp @ vn.T, -1, 1)))
i21 = np.argmin(d)
chk("probe: nearest node to gp10 = node21 @ 10.05°", i21 == 21 and abs(d[21]-10.05) < 0.05,
    f"node{i21} @ {d[i21]:.2f}°")
chk("probe: node26 @ 20.25°, node22 @ 24.02°",
    abs(d[26]-20.25) < 0.05 and abs(d[22]-24.02) < 0.05,
    f"{d[26]:.2f}, {d[22]:.2f}")

# ---- summary ----
print("=" * 60)
print("O28 VERIFIER")
print("=" * 60)
npass = sum(1 for _, c, _ in checks if c)
for name, c, detail in checks:
    print(f"  {'✅' if c else '❌'} {name}" + (f"  [{detail}]" if detail else ""))
print(f"\n{npass}/{len(checks)} PASS")
sys.exit(0 if npass == len(checks) else 1)
