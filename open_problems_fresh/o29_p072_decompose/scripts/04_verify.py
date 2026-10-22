#!/usr/bin/env python3
"""
O29 File simulation verifier — read ACTUAL data files, verify every claimed number.
====================================================================================
User-mandated no-hallucination close-out: every number in NN_results.md must be
re-verified by reading the SAVED JSONs directly (not script output).

Verification layers:
  1. File existence — every data file exists
  2. Baseline reproduction — p=0.042 / 0.072 / 0.365 / 0.385
  3. LOO ranking — top signal carriers & anti-signal spots
  4. Leverage table — Δobs values
  5. Node9/node47 claims — from o21_docking.json
  6. Bootstrap numbers — from bootstrap_decompose.json
  7. O21 docking — z, p from O21's own saved data
"""

import json
import os
import sys

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat/open_problems_fresh'
O29 = f'{BASE}/o29_p072_decompose'
O21 = f'{BASE}/o21_node9_anomaly'
O5 = f'{BASE}/o5_catalog_compare'

checks = []
def check(label, ok, detail=""):
    checks.append((label, bool(ok), detail))
    print(f"  [{'✅' if ok else '❌'}] {label}  {detail}")

# ============ 1. FILE EXISTENCE ============
print("=" * 70)
print("1. FILE EXISTENCE")
print("=" * 70)
files = [
    f'{O29}/data/decompose_results.json',
    f'{O29}/data/bootstrap_decompose.json',
    f'{O29}/data/o21_docking.json',
    f'{O21}/data/bootstrap_results.json',
    f'{O5}/data/match_results.json',
    f'{O5}/scripts/04_significance.py',
    f'{BASE}/cmb_cold_spot/data/a5_nodes.txt',
    f'{O29}/NN_results.md',
]
for f in files:
    check(f'exists: {os.path.basename(f)}', os.path.exists(f), f)

# ============ 2. BASELINE REPRODUCTION ============
print("\n" + "=" * 70)
print("2. BASELINE REPRODUCTION (from saved JSONs)")
print("=" * 70)
dec = json.load(open(f'{O29}/data/decompose_results.json'))
boot = json.load(open(f'{O29}/data/bootstrap_decompose.json'))
dock = json.load(open(f'{O29}/data/o21_docking.json'))

r = dec['results']
# A1 all-35
check('all-35 p = 0.042', abs(r['all (35)']['p'] - 0.042) < 0.002, f"got {r['all (35)']['p']}")
check('all-35 z = -1.77σ', abs(r['all (35)']['z'] - (-1.77)) < 0.05, f"got {r['all (35)']['z']}")
check('all-35 obs = 8.60°', abs(r['all (35)']['obs_mean'] - 8.60) < 0.01, f"got {r['all (35)']['obs_mean']}")
# baseline 34
b34 = r['all-minus-coldspot (34) — BASELINE']
check('baseline-34 p = 0.072', abs(b34['p'] - 0.072) < 0.002, f"got {b34['p']}")
check('baseline-34 obs = 8.85°', abs(b34['obs_mean'] - 8.85) < 0.01, f"got {b34['obs_mean']}")
check('baseline-34 z = -1.58σ', abs(b34['z'] - (-1.58)) < 0.05, f"got {b34['z']}")
# cold family removal
cf = r['C4 minus-cold-family (6)']
check('minus-cold-family p = 0.365', abs(cf['p'] - 0.365) < 0.005, f"got {cf['p']}")
check('minus-cold-family z = -0.30σ', abs(cf['z'] - (-0.30)) < 0.05, f"got {cf['z']}")
check('minus-cold-family obs = 9.95°', abs(cf['obs_mean'] - 9.95) < 0.01, f"got {cf['obs_mean']}")
# node9 removal
n9r = r['C1 minus-node9-spots (c3,c11)']
check('minus-node9 p = 0.051', abs(n9r['p'] - 0.051) < 0.005, f"got {n9r['p']}")
# hi-rot
hr = boot['high_rotation']
check('hi-rot baseline p ≈ 0.066', abs(hr['baseline-34']['p'] - 0.066) < 0.005, f"got {hr['baseline-34']['p']}")
check('hi-rot minus-cold-family p = 0.385', abs(hr['minus-cold-family']['p'] - 0.385) < 0.005, f"got {hr['minus-cold-family']['p']}")
check('hi-rot minus-node9 p = 0.042', abs(hr['minus-node9-spots']['p'] - 0.042) < 0.005, f"got {hr['minus-node9-spots']['p']}")

# ============ 3. LOO RANKING ============
print("\n" + "=" * 70)
print("3. LOO RANKING (from saved JSON)")
print("=" * 70)
loo = dec['loo']
by_p = sorted(loo, key=lambda x: x['p'])
# top carriers
carriers = by_p[-5:]
names_c = {x['name'] for x in carriers}
check('top carrier: sub-spot B p≈0.101',
      any('sub-spot B' in x['name'] and abs(x['p'] - 0.101) < 0.005 for x in carriers),
      f"names: {[x['name'] for x in carriers]}")
check('top carrier: h2 p≈0.099',
      any('SMICA-h2' in x['name'] and abs(x['p'] - 0.099) < 0.005 for x in carriers),
      f"got {[x['name'] for x in carriers]}")
# anti-signal
anti = by_p[:5]
check('anti-signal: h8 p≈0.030',
      any('SMICA-h8' in x['name'] and abs(x['p'] - 0.030) < 0.005 for x in anti),
      f"names: {[x['name'] for x in anti]}")
check('anti-signal: h14 p≈0.035',
      any('SMICA-h14' in x['name'] and abs(x['p'] - 0.035) < 0.005 for x in anti),
      f"got {[x['name'] for x in anti]}")
# c3 anti-signal
c3 = [x for x in loo if 'SMICA-c3' in x['name']][0]
check('c3 removal p≈0.041', abs(c3['p'] - 0.041) < 0.005, f"got {c3['p']}")

# ============ 4. LEVERAGE ============
print("\n" + "=" * 70)
print("4. DETERMINISTIC LEVERAGE (from saved JSON)")
print("=" * 70)
lev = boot['leverage']
lev_by = sorted(lev, key=lambda x: x['d_obs'], reverse=True)
top5 = lev_by[:5]
check('leverage top: c2 +0.245°',
      any('SMICA-c2' in x['name'] and abs(x['d_obs'] - 0.245) < 0.005 for x in top5),
      f"got {[(x['name'], round(x['d_obs'],3)) for x in top5]}")
check('leverage top: sub-spot B +0.234°',
      any('sub-spot B' in x['name'] and abs(x['d_obs'] - 0.234) < 0.005 for x in top5),
      f"got {[(x['name'], round(x['d_obs'],3)) for x in top5]}")
check('3 of top5 are node-0 family',
      sum(1 for x in top5 if x['node'] == 0) == 3, f"got {[x['node'] for x in top5]}")
# worst anti
bot5 = lev_by[-5:]
check('leverage bottom: h14 -0.271°',
      any('SMICA-h14' in x['name'] and abs(x['d_obs'] - (-0.271)) < 0.005 for x in bot5),
      f"got {[(x['name'], round(x['d_obs'],3)) for x in bot5]}")

# ============ 5. NODE9 / NODE47 ============
print("\n" + "=" * 70)
print("5. NODE9 / NODE47 CLAIMS (from o21_docking.json)")
print("=" * 70)
check('node9 spots count = 2', len(dock['node9_spots']) == 2, f"got {len(dock['node9_spots'])}")
n9names = [s['name'] for s in dock['node9_spots']]
check('node9 spots are c3, c11', 'SMICA-c3' in n9names and 'SMICA-c11' in n9names, f"got {n9names}")
check('node9 c3 d=10.34°', any(abs(s['d'] - 10.34) < 0.02 for s in dock['node9_spots']), f"got {dock['node9_spots']}")
check('node9 c11 d=12.37°', any(abs(s['d'] - 12.37) < 0.02 for s in dock['node9_spots']), f"got {dock['node9_spots']}")
check('node47 spots count = 0', len(dock['node47_spots']) == 0, f"got {len(dock['node47_spots'])}")
check('node47 nearest spot 23.18°', abs(dock['node47_nearest_spot']['d'] - 23.18) < 0.05,
      f"got {dock['node47_nearest_spot']}")
check('O21 node9 z = -1.46σ', abs(dock['o21_node9']['z'] - (-1.46)) < 0.02, f"got {dock['o21_node9']['z']}")
check('O21 node9 p = 0.082', abs(dock['o21_node9']['p'] - 0.082) < 0.005, f"got {dock['o21_node9']['p']}")
check('O21 node9 T = -107.0', abs(dock['o21_node9']['T'] - (-107.0)) < 0.5, f"got {dock['o21_node9']['T']}")

# ============ 6. BOOTSTRAP ============
print("\n" + "=" * 70)
print("6. BOOTSTRAP NUMBERS (from saved JSON)")
print("=" * 70)
b = dock['bootstrap']
check('bootstrap frac p<0.05 = 0.222', abs(b['frac_p_lt_005'] - 0.222) < 0.01, f"got {b['frac_p_lt_005']}")
check('bootstrap frac p<0.10 = 0.443', abs(b['frac_p_lt_010'] - 0.443) < 0.01, f"got {b['frac_p_lt_010']}")
check('bootstrap p mean = 0.163', abs(b['p_mean'] - 0.163) < 0.01, f"got {b['p_mean']}")
check('bootstrap p median = 0.116', abs(b['p_median'] - 0.116) < 0.01, f"got {b['p_median']}")

# ============ 7. NODE9 DIRECT PERMUTATION ============
print("\n" + "=" * 70)
print("7. NODE9 DIRECT PERMUTATION (from saved JSON)")
print("=" * 70)
n9d = boot['node9_direct']
check('node9 spots mean d = 11.36°', abs(n9d['d_node9'] - 11.36) < 0.05, f"got {n9d['d_node9']}")
check('rest mean d = 8.69°', abs(n9d['d_rest'] - 8.69) < 0.05, f"got {n9d['d_rest']}")
check('diff = +2.66°', abs(n9d['diff'] - 2.66) < 0.05, f"got {n9d['diff']}")
check('p(closer) = 0.7925', abs(n9d['p_closer'] - 0.7925) < 0.01, f"got {n9d['p_closer']}")

# ============ SUMMARY ============
print("\n" + "=" * 70)
passed = sum(1 for _, ok, _ in checks if ok)
print(f"TALLY: {passed}/{len(checks)} PASS")
print("=" * 70)
for label, ok, detail in checks:
    if not ok:
        print(f"  FAILED: {label} — {detail}")
sys.exit(0 if passed == len(checks) else 1)
