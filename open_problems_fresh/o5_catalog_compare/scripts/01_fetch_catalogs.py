#!/usr/bin/env python3
"""
O5 Step 1: Literature cold-spot catalogue extraction
=====================================================
Extract all confirmed cold/hot spot coordinates from the published
literature PDFs downloaded to data/catalogs/.

Key finding (2026-08-17): The literature does NOT contain a "10+ cold spot
catalogue" — Cruz 2005 & 2007, Vielva 2004, Planck 2013/2015 all focus on
THE Cold Spot at (209°, -57°). The only additional entries are:
  - Planck 2013: second prominent cold spot at (l,b) = (32°, -8°) (gp10 region)
  - Cruz 2005 Table 4: 4 sub-spots of the unresolved Cold Spot (before 4° Gaussian filter)

This script records the verified literature positions with full provenance.
"""

import json
import os

OUTDIR = '/home/wsl/Projects/IDCM/IDCM-v10.0/open_problems_fresh/o5_catalog_compare/data'
os.makedirs(OUTDIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Literature catalogue (verified from PDF text extraction, 2026-08-17)
# Format: (name, l_deg, b_deg, source, note, scale_deg, status)
# ---------------------------------------------------------------------------
LITERATURE_SPOTS = [
    # The Cold Spot — confirmed in EVERY paper (Vielva 2004, Cruz 2005/2006/2007,
    # Planck 2013 Table 30, Planck 2015 XVI). Position (l,b) = (209°, -57°).
    dict(name='The Cold Spot (Vielva 2004)', l=209.0, b=-57.0,
         source='astro-ph/0310273 (Vielva et al. 2004)',
         note='Official WMAP detection at SMHW scale R8=4.17°. IDCM node 0.',
         scale_deg=4.17, status='confirmed'),

    # Planck 2013: "we consider a prominent cold spot at b=-8°, l=32°,
    # partially masked by the Galactic plane" (gp10 region, skewness analysis)
    dict(name='Planck gp10 cold spot', l=32.0, b=-8.0,
         source='1303.5083 (Planck 2013 XXIII) Sect. 4.4',
         note='Second prominent cold spot, partially masked by Galactic plane. '
              'Near Galactic centre — foreground caveat.',
         scale_deg=10.0, status='confirmed'),

    # Cruz 2005 Table 4: sub-spots of the unresolved Cold Spot before filtering.
    # These are the SAME structure, decomposed at high threshold (ν=-2).
    dict(name='CS sub-spot A (Cruz 2005 T4)', l=213.0, b=-60.0,
         source='astro-ph/0405341 (Cruz et al. 2005) Table 4',
         note='Sub-component of The Cold Spot before 4° Gaussian filter. '
              'Amplitude -346 μK, area 46 px.',
         scale_deg=4.17, status='sub-spot'),
    dict(name='CS sub-spot B (Cruz 2005 T4)', l=210.0, b=-56.0,
         source='astro-ph/0405341 (Cruz et al. 2005) Table 4',
         note='Sub-component of The Cold Spot. Amplitude -398 μK, area 67 px.',
         scale_deg=4.17, status='sub-spot'),
    dict(name='CS sub-spot C (Cruz 2005 T4)', l=211.0, b=-54.0,
         source='astro-ph/0405341 (Cruz et al. 2005) Table 4',
         note='Sub-component of The Cold Spot. Amplitude -331 μK, area 42 px.',
         scale_deg=4.17, status='sub-spot'),
    dict(name='CS sub-spot D (Cruz 2005 T4)', l=203.0, b=-56.0,
         source='astro-ph/0405341 (Cruz et al. 2005) Table 4',
         note='Sub-component of The Cold Spot. Amplitude -317 μK, area 88 px.',
         scale_deg=4.17, status='sub-spot'),
]

# ---------------------------------------------------------------------------
# Also record the "not found" claims — what the SESSION_START.md expected but
# the literature does NOT contain (anti-hallucination record).
# ---------------------------------------------------------------------------
NOT_FOUND = [
    'Cruz 2005 "~10+ cold spots catalogue" — NO such table exists. '
    'Cruz 2005 (astro-ph/0405341) is a Gaussianity study; Table 4 lists only '
    'sub-spots of the single Cold Spot.',
    'Cruz 2007 (astro-ph/0603859) — same single Cold Spot, no catalogue.',
    'Hou 2009 (0903.4446) — statistical study of hot/cold spot populations, '
    'no coordinate catalogue.',
    'Vielva 2007 hot spot catalogue — mis-remembered; Planck 2013/2015 mention '
    'an anomalous HOT area (see O2: F6=277.6μK at (157.8°,-70.3°), confirmed).',
    'Gurzadyan 2007 cold spot statistics — arXiv search shows no such catalogue; '
    'Gurzadyan 2014 (1404.6347) re-analyzes the SAME Cold Spot.',
]

with open(os.path.join(OUTDIR, 'literature_catalog.json'), 'w') as f:
    json.dump({'spots': LITERATURE_SPOTS, 'not_found': NOT_FOUND},
              f, indent=2, ensure_ascii=False)

print("=" * 66)
print("O5 STEP 1: LITERATURE CATALOGUE EXTRACTION")
print("=" * 66)
print(f"\nExtracted {len(LITERATURE_SPOTS)} literature spots:")
print(f"{'#':>2} {'name':<28} {'l':>7} {'b':>7}  status")
print("-" * 60)
for i, s in enumerate(LITERATURE_SPOTS):
    print(f"{i+1:>2} {s['name']:<28} {s['l']:>7.1f} {s['b']:>7.1f}  {s['status']}")

print(f"\n{'=' * 66}")
print("NOT-FOUND CLAIMS (anti-hallucination record):")
for nf in NOT_FOUND:
    print(f"  ✗ {nf}")

# Quick sanity: convert to ICRS for later use
import numpy as np
from astropy.coordinates import SkyCoord
import astropy.units as u

print("\nGalactic -> ICRS (RA, Dec) conversion:")
for s in LITERATURE_SPOTS:
    c = SkyCoord(l=s['l']*u.deg, b=s['b']*u.deg, frame='galactic')
    icrs = c.icrs
    print(f"  {s['name'][:30]:<32} (l,b)=({s['l']:6.1f},{s['b']:6.1f}) -> "
          f"RA={icrs.ra.deg:8.3f} Dec={icrs.dec.deg:+8.3f}")

print("\nSaved: data/literature_catalog.json")
