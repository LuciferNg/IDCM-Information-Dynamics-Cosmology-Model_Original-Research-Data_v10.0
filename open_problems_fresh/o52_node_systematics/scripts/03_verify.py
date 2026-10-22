#!/usr/bin/env python3
"""
O52 File simulation verifier — read ACTUAL saved JSONs, verify NN_results.md
============================================================================
User-mandated no-hallucination close-out: every number in NN_results.md must
be re-verified from the SAVED data files directly.

Layers:
  1. File existence
  2. Multiscale systematics (o52_systematics.json) — z values, means, counts
  3. R3 mask: 45/60 unmasked (frame-corrected)
  4. Stacking profile (o52_stacking.json) — annulus values, z, inner p
  5. Doc structure — key claims present in NN_results.md
"""
import json
import os
import sys

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
O52 = f'{BASE}/open_problems_fresh/o52_node_systematics'
O27 = f'{BASE}/open_problems_fresh/o27_node47_foreground'
O5 = f'{BASE}/open_problems_fresh/o5_catalog_compare'

checks = []
def check(label, ok, detail=""):
    checks.append((label, bool(ok), detail))
    print(f"  [{'✅' if ok else '❌'}] {label}  {detail}")

# ============ 1. FILE EXISTENCE ============
print("=" * 70)
print("1. FILE EXISTENCE")
print("=" * 70)
files = [
    f'{O52}/data/o52_systematics.json',
    f'{O52}/data/o52_stacking.json',
    f'{O52}/scripts/01_node_vs_random_mean.py',
    f'{O52}/scripts/02_stacking_profile.py',
    f'{O52}/NN_results.md',
    f'{O5}/data/smooth_cache/smica2_smooth3.0.fits',
    f'{O27}/data/COM_Mask_CMB-common-Mask-Int_2048_R3.00.fits',
]
for f in files:
    check(f'exists: {os.path.basename(f)}', os.path.exists(f), f)

# ============ 2. MULTISCALE SYSTEMATICS ============
print("\n" + "=" * 70)
print("2. MULTISCALE SYSTEMATICS (o52_systematics.json)")
print("=" * 70)
sys_data = json.load(open(f'{O52}/data/o52_systematics.json'))
for fwhm in ['0.5', '1.0', '2.0', '3.0', '4.0', '5.0', '7.0', '10.0']:
    r = sys_data[fwhm]
    check(f'[{fwhm}°] 60-node z_vs_sky within ±0.5',
          abs(r['z_vs_sky']) < 0.5, f"got {r['z_vs_sky']}")
    check(f'[{fwhm}°] z_vs_ctrl within ±0.5',
          abs(r['z_vs_ctrl']) < 0.5, f"got {r['z_vs_ctrl']}")
check('R3 mask n_um = 45 (frame-corrected)',
      sys_data['3.0']['um_n'] == 45, f"got {sys_data['3.0']['um_n']}")
check('high-lat n = 31', sys_data['3.0']['hl_n'] == 31, f"got {sys_data['3.0']['hl_n']}")
check('3.0° node_mean ≈ -1.52', abs(sys_data['3.0']['node_mean'] - (-1.52)) < 0.05,
      f"got {sys_data['3.0']['node_mean']}")
check('3.0° z_vs_sky ≈ -0.27', abs(sys_data['3.0']['z_vs_sky'] - (-0.27)) < 0.05,
      f"got {sys_data['3.0']['z_vs_sky']}")
check('5.0° z_vs_sky ≈ -0.24', abs(sys_data['5.0']['z_vs_sky'] - (-0.24)) < 0.05,
      f"got {sys_data['5.0']['z_vs_sky']}")
check('10.0° z_vs_sky ≈ -0.20', abs(sys_data['10.0']['z_vs_sky'] - (-0.20)) < 0.05,
      f"got {sys_data['10.0']['z_vs_sky']}")
# high-lat values
check('3.0° z_hl ≈ -0.51', abs(sys_data['3.0']['z_hl'] - (-0.51)) < 0.05,
      f"got {sys_data['3.0']['z_hl']}")
check('5.0° z_hl ≈ -0.54', abs(sys_data['5.0']['z_hl'] - (-0.54)) < 0.05,
      f"got {sys_data['5.0']['z_hl']}")
# unmasked/masked
check('3.0° z_um ≈ -0.39', abs(sys_data['3.0']['z_um'] - (-0.39)) < 0.05,
      f"got {sys_data['3.0']['z_um']}")
check('3.0° masked mean ≈ +1.76', abs(sys_data['3.0']['msk_mean'] - 1.76) < 0.1,
      f"got {sys_data['3.0']['msk_mean']}")
# cold/hot counts
check('3.0° cold/hot = 29/31', sys_data['3.0']['n_cold'] == 29 and sys_data['3.0']['n_hot'] == 31,
      f"got {sys_data['3.0']['n_cold']}/{sys_data['3.0']['n_hot']}")
check('3.0° 2σ cold/hot = 4/2', sys_data['3.0']['n_cold_2sig'] == 4 and sys_data['3.0']['n_hot_2sig'] == 2,
      f"got {sys_data['3.0']['n_cold_2sig']}/{sys_data['3.0']['n_hot_2sig']}")
check('0.5° cold/hot = 30/30', sys_data['0.5']['n_cold'] == 30 and sys_data['0.5']['n_hot'] == 30,
      f"got {sys_data['0.5']['n_cold']}/{sys_data['0.5']['n_hot']}")
# removed node0/9
check('3.0° rem_mean ≈ +2.83', abs(sys_data['3.0']['rem_mean'] - 2.83) < 0.1,
      f"got {sys_data['3.0']['rem_mean']}")
check('3.0° z_rem ≈ +0.46', abs(sys_data['3.0']['z_rem'] - 0.46) < 0.05,
      f"got {sys_data['3.0']['z_rem']}")
check('10.0° z_rem ≈ +0.44', abs(sys_data['10.0']['z_rem'] - 0.44) < 0.05,
      f"got {sys_data['10.0']['z_rem']}")

# ============ 3. STACKING ============
print("\n" + "=" * 70)
print("3. STACKING PROFILE (o52_stacking.json)")
print("=" * 70)
st = json.load(open(f'{O52}/data/o52_stacking.json'))
check('stacking fwhm = 3.0', abs(st['fwhm'] - 3.0) < 0.01, f"got {st['fwhm']}")
check('n_random = 1000', st['n_random'] == 1000, f"got {st['n_random']}")
p = st['profile']
check('inner 0-2 obs_all ≈ -1.29', abs(p['0-2']['obs_all'] - (-1.29)) < 0.05,
      f"got {p['0-2']['obs_all']}")
check('inner 0-2 z_all ≈ -0.21', abs(p['0-2']['z_all'] - (-0.21)) < 0.05,
      f"got {p['0-2']['z_all']}")
check('inner 0-2 z_unmasked ≈ -0.37', abs(p['0-2']['z_unmasked'] - (-0.37)) < 0.05,
      f"got {p['0-2']['z_unmasked']}")
check('outer 12-14 z_all ≈ -0.39', abs(p['12-14']['z_all'] - (-0.39)) < 0.05,
      f"got {p['12-14']['z_all']}")
check('inner_p ≈ 0.411', abs(st['inner_p'] - 0.411) < 0.01, f"got {st['inner_p']}")
# all |z| < 0.6 claim
all_small = all(abs(p[k]['z_all']) < 0.6 and abs(p[k]['z_unmasked']) < 0.6 for k in p)
check('all annulus |z| < 0.6', all_small, "")

# ============ 4. DOC STRUCTURE ============
print("\n" + "=" * 70)
print("4. DOC STRUCTURE (NN_results.md key claims)")
print("=" * 70)
doc = open(f'{O52}/NN_results.md').read()
key_claims = [
    ('冇系統性微冷/微熱', 'verdict headline'),
    ('只有 node0/node9 係真異常', 'verdict headline 2'),
    ('全部尺度 |z| < 0.4σ', 'all-scale claim'),
    ('R3 mask 45/60', 'mask claim'),
    ('最內圈 (0-2°) z=-0.21', 'inner z'),
    ('node0 (大冷斑): -134.19 μK', 'node0 temp'),
    ('λ₂=φ⁻²', 'math closure survives'),
]
for phrase, label in key_claims:
    check(f'doc contains: {label}', phrase in doc, phrase)

# ============ SUMMARY ============
print("\n" + "=" * 70)
passed = sum(1 for _, ok, _ in checks if ok)
print(f"TALLY: {passed}/{len(checks)} PASS")
print("=" * 70)
for label, ok, detail in checks:
    if not ok:
        print(f"  FAILED: {label} — {detail}")
sys.exit(0 if passed == len(checks) else 1)
