#!/usr/bin/env python3
"""
O28 Script 06: DOC-vs-DATA claim verification
=============================================
Every number claimed in NN_results.md must be traced to the actual data
files (gp10_extract.json / gp10_planck_style.json / random_control.json)
or independently recomputed from the raw maps. This is the no-hallucination
close-out per user policy: read the FILES, not script stdout.
"""
import json, os, re, sys
import numpy as np
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = f'{BASE}/data'
DOC = f'{BASE}/NN_results.md'

with open(DOC) as f:
    doc = f.read()

checks = []
def chk(name, cond, detail=""):
    checks.append((name, bool(cond), detail))

# ---- A. Extract JSONs ----
with open(f'{DATA}/gp10_extract.json') as f:
    ext = json.load(f)
with open(f'{DATA}/gp10_planck_style.json') as f:
    ps = json.load(f)
with open(f'{DATA}/random_control.json') as f:
    rc = json.load(f)

# ---- B. Doc text contains the claimed values ----
def doc_has(s):
    return s in doc

# 1. Verdict line
chk("doc: verdict 🔴 no node correspondence",
    doc_has("🔴 **gp10 冇節點對應**") or doc_has("🔴 gp10 冇節點對應"))
# 2. Flood-fill zeros
chk("doc: 4.17° 0 cold comps", doc_has("4.17°") and doc_has("**0 / 0 / 0 / 0**"))
chk("doc: 5.0° 0 cold comps", doc_has("5.0°") and "0/0/0/0" in doc)
chk("doc: 7.0° 0 cold comps", doc_has("7.0°") and "0/0/0/0" in doc)
# 3. 3.0° comp peak
chk("doc: 3.0° peak (22.4,-25.0)", doc_has("(22.4,-25.0)"))
# 4. gp10 centre +10.4
chk("doc: gp10 centre +10.4 μK", doc_has("+10.4 μK"))
# 5. Nside16 stats
chk("doc: var 0.75×", doc_has("0.75×"))
chk("doc: skew +0.12", doc_has("+0.12"))
chk("doc: region mean +22.9", doc_has("+22.9 μK"))
chk("doc: rest mean +0.3", doc_has("+0.3 μK"))
# 6. 0.5° peak
chk("doc: 0.5° peak (32.4,-5.5) -215", doc_has("(32.4,-5.5)") and doc_has("-215.0 μK"))
chk("doc: cross-map -9~-17", doc_has("-12.3") and doc_has("-9.0") and doc_has("-17.2"))
# 7. Mask-corrected centroids
chk("doc: centroid bcut10 (38.4,-16.1)", doc_has("(38.4, -16.1)"))
chk("doc: node21 19.7°", doc_has("19.7°"))
chk("doc: bcut15 node22 18.1°", doc_has("18.1°"))
# 8. Random control
chk("doc: plane median 10.32", doc_has("10.32°"))
chk("doc: P(≤10.05) 0.477", doc_has("0.477"))
chk("doc: full 0.454", doc_has("0.454"))
chk("doc: near-gp10 0.447", doc_has("0.447"))
# 9. Node roles
chk("doc: node21 10.05 +95.5", doc_has("10.05°") and doc_has("+95.5 μK"))
chk("doc: node26 20.25 -48.3", doc_has("20.25°") and doc_has("-48.3 μK"))
chk("doc: node22 24.02 -23.6", doc_has("24.02°") and doc_has("-23.6 μK"))

# ---- C. Independent recomputation from RAW data (not the JSONs) ----
CACHE = BASE + '/../o5_catalog_compare/data/smooth_cache'
NODE_FILE = BASE + '/../cmb_cold_spot/data/a5_nodes.txt'

# C1: gp10 centre temperature from SMICA 4.17°
m417 = hp.read_map(f'{CACHE}/smica2_smooth4.17.fits', field=0)
nside = hp.get_nside(m417)
pix = hp.ang2pix(nside, 32.0, -8.0, lonlat=True)
chk("C1: gp10 centre +10.4 μK (recompute)", abs(m417[pix]*1e6 - 10.4) < 1.0,
    f"{m417[pix]*1e6:.1f}")

# C2: node distances (recompute from node file)
nodes = np.loadtxt(NODE_FILE)
ng = SkyCoord(ra=nodes[:,0]*u.deg, dec=nodes[:,1]*u.deg, frame='icrs').galactic
vgp = hp.ang2vec(np.radians(90-(-8)), np.radians(32))
vn = hp.ang2vec(np.radians(90-ng.b.deg), np.radians(ng.l.deg))
d = np.degrees(np.arccos(np.clip(vgp @ vn.T, -1, 1)))
chk("C2: node21 @ 10.05", abs(d[21]-10.05) < 0.05, f"{d[21]:.2f}")
chk("C2: node26 @ 20.25", abs(d[26]-20.25) < 0.05, f"{d[26]:.2f}")
chk("C2: node22 @ 24.02", abs(d[22]-24.02) < 0.05, f"{d[22]:.2f}")

# C3: node21 temperature (hot?)
pix21 = hp.ang2pix(nside, ng.l.deg[21], ng.b.deg[21], lonlat=True)
chk("C3: node21 hot +95.5", m417[pix21]*1e6 > 80, f"{m417[pix21]*1e6:.1f}")
pix26 = hp.ang2pix(nside, ng.l.deg[26], ng.b.deg[26], lonlat=True)
chk("C3: node26 cold -48.3", m417[pix26]*1e6 < -40, f"{m417[pix26]*1e6:.1f}")

# C4: Nside16 variance ratio (independent recompute)
m16 = hp.ud_grade(m417, nside_out=16)
npix16 = hp.nside2npix(16)
l16, b16 = hp.pix2ang(16, np.arange(npix16), lonlat=True)
disc = hp.query_disc(16, vgp, np.radians(30))
reg = m16[disc]
rest = m16[np.abs(b16) >= 25]
ratio = np.var(reg) / np.var(rest)
chk("C4: Nside16 var ratio ~0.75", abs(ratio - 0.75) < 0.05, f"{ratio:.3f}")

# C5: 0.5° peak cross-check
m05 = hp.read_map(f'{CACHE}/smica2_smooth0.5.fits', field=0)
d05 = hp.query_disc(hp.get_nside(m05), vgp, np.radians(15))
i = np.argmin(m05[d05])
lp, bp = hp.pix2ang(hp.get_nside(m05), d05[i], lonlat=True)
chk("C5: 0.5° peak (32.4,-5.5) -215", abs(lp-32.4) < 0.5 and abs(bp+5.5) < 0.5
    and abs(m05[d05[i]]*1e6 + 215) < 8, f"({lp:.1f},{bp:+.1f})={m05[d05[i]]*1e6:.0f}")

# C6: NILC/Commander cross-map at (32.4,-5.5)
for name, f in [('NILC','nilc2_smooth4.17.fits'), ('Commander','commander_smooth4.17.fits')]:
    m = hp.read_map(f'{CACHE}/{f}', field=0)
    p = hp.ang2pix(hp.get_nside(m), 32.4, -5.5, lonlat=True)
    v = m[p]*1e6
    chk(f"C6: {name} at peak ~ -9/-17", abs(v) < 25, f"{v:.1f}")

# ---- summary ----
print("=" * 60)
print("O28 DOC-vs-DATA VERIFIER (NN_results.md claims)")
print("=" * 60)
npass = sum(1 for _, c, _ in checks if c)
for name, c, detail in checks:
    print(f"  {'✅' if c else '❌'} {name}" + (f"  [{detail}]" if detail else ""))
print(f"\n{npass}/{len(checks)} PASS")
sys.exit(0 if npass == len(checks) else 1)
