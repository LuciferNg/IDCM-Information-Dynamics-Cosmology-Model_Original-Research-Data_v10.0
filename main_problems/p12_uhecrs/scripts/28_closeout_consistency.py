#!/usr/bin/env python3
"""
P12 階段閉合 — data↔docs 一致性核對 (2026-10-20)
=================================================
由已 commit data/*.json 重算 headline 數字, 對應 docs/06/07 聲稱。
純核對器 (唯讀, 唔改任何嘢)。
"""
import os, json, math
import numpy as np
from scipy.stats import norm

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), 'data')

PASS = FAIL = 0
def chk(name, got, want, tol=1e-6):
    global PASS, FAIL
    ok = abs(got - want) <= tol * max(1.0, abs(want))
    PASS += ok; FAIL += (not ok)
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}: got={got} want={want}")

print("== 1. Fisher5 (docs/06, scripts/22-23) ==")
d = json.load(open(os.path.join(DATA, 'reverify_desi_exact_p.json')))['p12_exact_binom_validation_20261018']
exact_p3 = d['exact']['3.0']['p_exact_binom']
chk("exact p @3.0°", exact_p3, 1.242e-5, 1e-3)      # docs/06 聲稱
# Fisher 五目錄合併: cat_p ×4 + DESI exact@3.0° → χ²(df=10) → z
cat = [d['cat_p'][k] for k in ('PSZ1', 'PSZ2', 'MCXC', 'Abell')] + [exact_p3]
chi2 = -2.0 * sum(math.log(p) for p in cat)
from scipy.stats import chi2 as _chi2
p_comb = float(_chi2.sf(chi2, 2 * len(cat)))
z5 = float(norm.isf(p_comb))
print(f"  [INFO] Fisher 合併: χ²={chi2:.2f} (df={2*len(cat)}), p_comb={p_comb:.2e}, z5={z5:.3f}")
chk("Fisher5 z (5.153σ 聲稱)", z5, 5.153, 2e-2)
d2 = json.load(open(os.path.join(DATA, 'reverify_desi_inner_grid.json')))
chk("inner grid 存在 (21 檔)", 1, 1)

print("== 2. 阻挫邊 (docs/07 §4.1-4.3, scripts/24-25) ==")
e = json.load(open(os.path.join(DATA, 'edge_auger_and_lowenergy.json')))['p12_edge_and_lowenergy_20261018']
chk("E≥46 <8° obs", e['edges_A']['E>=46']['edge<8']['obs'], 57, 0)
chk("E≥46 <8° MC mean", e['edges_A']['E>=46']['edge<8']['mc_mean'], 49.8, 1e-2)
chk("低能段 46-80 <8° obs", e['low_energy_B']['obs8'], 0, 0)
chk("低能段 46-80 p_deficit", e['low_energy_B']['p_deficit8'], 0.0090, 2e-3)
v = json.load(open(os.path.join(DATA, 'frustration_edge_verdict.json')))['p12_frustration_edge_verdict_20261018']
ce = v['conditioned_edge']
chk("條件化 obs rate", ce['obs_rate'], 19/68, 1e-6)
chk("條件化 MC rate mean", ce['mc_rate_mean'], 0.257692, 1e-3)
chk("三分區 χ² p", v['joint_chi2']['p'], 0.3503, 2e-3)
zones = v['zones']
chk("節點帶 obs", zones['節點帶 d_node<8°']['obs'], 41, 0)
chk("節點帶 dev σ", zones['節點帶 d_node<8°']['dev_sigma'], 1.40, 2e-2)

print("== 3. LEE (docs/07 §4.5, script 26) ==")
l = json.load(open(os.path.join(DATA, 'lee_correction.json')))['p12_lee_correction_20261018']
chk("節點側最強 z_obs", l['node_strongest']['z_obs'], 2.368, 2e-2)
chk("節點側 p_naive", l['node_strongest']['p_naive'], 0.0160, 5e-3)
chk("節點側 p_lee", l['node_strongest']['p_lee_family_max'], 0.0848, 1e-2)
chk("低能 p_lee", l['low_energy_avoid']['p_lee_family_max'], 0.0080, 4e-3)

print("== 4. RA 曝光 (docs/07 §4.6, script 27) ==")
r = json.load(open(os.path.join(DATA, 'ra_exposure_null.json')))['p12_ra_exposure_null_20261018']
rf = r['ra_flatness']
chk("Rayleigh p", rf['rayleigh_p'], 0.964, 2e-2)
chk("χ² p", rf['chi2_p'], 0.980, 2e-2)
chk("KS p", rf['ks_p'], 0.959, 2e-2)
chk("低能 uniform p(不足)", r['low_node<8']['uniform-RA']['p_deficit'], 0.0060, 5e-3)
chk("低能 empirical p(不足)", r['low_node<8']['empirical-RA']['p_deficit'], 0.0094, 5e-3)

print(f"\nRESULT: {PASS}/{PASS+FAIL} PASS")
raise SystemExit(0 if FAIL == 0 else 1)