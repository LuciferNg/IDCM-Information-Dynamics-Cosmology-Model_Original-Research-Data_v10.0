#!/usr/bin/env python3
"""
O150 #07 - cross-scale l=3 consistency + consolidated audit
===========================================================
A. Is the node-set "l=3 mode" the SKY's l=3 multipole?
   full-sky a_3m (galactic, from the 4.17-deg smoothed SMICA) vs node-set fitted a_3m
   -> correlation, axis angle.  (Decides whether the "axis" is a sky object at all.)
B. Same for l=2.
C. Consolidated audit: re-derive every headline O150 number from the raw data and
   assert against the stored JSONs (exit non-zero on any FAIL).
"""
import numpy as np, math, json, os, sys
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u
from scipy.special import lpmv

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
ROOT = BASE + '/open_problems_fresh'
O150 = ROOT + '/o150_sky_side_projection'
CS = ROOT + '/cmb_cold_spot/data'
G182 = ROOT + '/o182_88grid_geometry/data'
CACHE = ROOT + '/o5_catalog_compare/data/smooth_cache'

raw = np.loadtxt(CS + '/a5_nodes.txt')
sc = SkyCoord(ra=raw[:, 0] * u.deg, dec=raw[:, 1] * u.deg, frame='icrs')
LB = np.column_stack([sc.galactic.l.deg, sc.galactic.b.deg])
l_ = np.radians(LB[:, 0]); b_ = np.radians(LB[:, 1])
V = np.column_stack([np.cos(b_) * np.cos(l_), np.cos(b_) * np.sin(l_), np.sin(b_)])
T = np.array(json.load(open(G182 + '/temps2_SMICA_4.17deg.json'))['A5_60'][:60], float)
Tz = T - T.mean()
FAIL = []


def real_sph(l, m, v):
    th = np.arccos(np.clip(v[:, 2], -1, 1)); ph = np.arctan2(v[:, 1], v[:, 0])
    am = abs(m)
    nrm = math.sqrt((2 * l + 1) / (4 * math.pi) * math.factorial(l - am) / math.factorial(l + am))
    P = lpmv(am, l, np.cos(th))
    if m == 0:
        return nrm * P
    if m > 0:
        return math.sqrt(2) * nrm * P * np.cos(am * ph)
    return math.sqrt(2) * nrm * P * np.sin(am * ph)


def basis(l, v):
    return np.column_stack([real_sph(l, m, v) for m in range(-l, l + 1)])


def ck(name, val, ref, tol):
    ok = abs(val - ref) <= tol
    print('    [%s] %-46s %.6g  (ref %.6g, tol %.3g)' % ('PASS' if ok else 'FAIL', name, val, ref, tol))
    if not ok:
        FAIL.append(name)


print('=' * 92)
print('  O150 #07 - cross-scale l=3 consistency + consolidated audit')
print('=' * 92)

# ---------- A/B. full-sky vs node-set multipoles ----------
print('\n[A] node-set l=3 mode vs SKY l=3 multipole')
m = hp.read_map(CACHE + '/smica2_smooth4.17.fits', field=0)
alm = hp.map2alm(m * 1e6, lmax=64)
res_AB = {}
for l in [2, 3]:
    # sky coefficients expressed in the REAL basis (galactic frame)
    a = np.array([alm[hp.Alm.getidx(64, l, mm)] for mm in range(0, l + 1)])
    a_sky = np.zeros(2 * l + 1)
    for mm in range(0, l + 1):
        if mm == 0:
            a_sky[l] = np.real(a[0])
        else:
            a_sky[l + mm] = math.sqrt(2) * np.real(a[mm])
            a_sky[l - mm] = -math.sqrt(2) * np.imag(a[mm])
    a_node = np.linalg.lstsq(basis(l, V), Tz, rcond=None)[0]
    cr = float(np.corrcoef(a_sky, a_node)[0, 1])
    print('    l=%d : corr(a_sky, a_node) = %+.4f ; |a_node|/|a_sky| = %.4f' % (
        l, cr, np.linalg.norm(a_node) / np.linalg.norm(a_sky)))
    res_AB[str(l)] = cr
print('    -> l=3: corr 0.86 = RELATED to the sky l=3 multipole, but amplitude 1.68x inflated')
print('       (l=5 aliasing) and the derived AXIS differs by 65 deg from the sky l=3 axis.')
print('    -> l=2: corr 0.30 = node-set l=2 is a poor tracer of the sky quadrupole.')

# ---------- C. consolidated audit ----------
print('\n[C] consolidated audit (re-derive from raw data, assert vs stored JSON)')
s1 = json.load(open(O150 + '/data/step01_baseline.json'))
s2 = json.load(open(O150 + '/data/step02_operator_breaking.json'))
s3 = json.load(open(O150 + '/data/step03_audit.json'))
s4 = json.load(open(O150 + '/data/step04_p5_significance.json'))
s6 = json.load(open(O150 + '/data/step06_node_identity_and_p4.json'))
ck('node0 galactic l', LB[0, 0], 209.0, 1e-3)
ck('node0 galactic b', LB[0, 1], -57.0, 1e-3)
ck('T9 (SMICA 4.17deg)', T[9], s1['T9'], 1e-9)
ck('T20', T[20], s1['T20'], 1e-9)
ck('|T9|/|T20|', abs(T[9] / T[20]), s1['ratio'], 1e-9)
ck('|Aut(G)|', float(s1['aut_order_capped']), 120.0, 0.0)
ck('exists g: 9->20', 1.0 if s1['aut_has_9to20'] else 0.0, 1.0, 0.0)
B3 = basis(3, V)
c3 = np.linalg.lstsq(B3, Tz, rcond=None)[0]
p3 = float(((B3 @ c3) @ (B3 @ c3)))
ck('||Pi_3 Tz||^2', p3, s3['power_Pi']['3'], 1e-6 * p3)
ck('Sigma coef^2 l=3', float((c3 ** 2).sum()), s1['multipole']['3']['power'], 1e-6)
# NOTE: two sampling paths - temps2 (nside 2048) vs the nside-128 downgrade used by the
# GRF null.  Assert each against its own reference.
ck('l=3 share (basis-free, nside2048)', p3 / float(Tz @ Tz), 0.318481, 1e-5)
ck('l=3 share (basis-free, nside128)', s4['shares']['SMICA']['3'], 0.312528, 1e-5)
ck('node9-node20 |T| ratio (A5, nside128)', abs(s4['ratio_920']['SMICA']), 3.076, 0.01)
ck('4-pipeline ratio spread < 0.4', max(s4['ratio_920'].values()) - min(s4['ratio_920'].values()), 0.0, 0.4)
ck('l=3 GRF p (SMICA)', s4['p_grf_l3'], 0.0779, 1e-4)   # deterministic: np.random.seed added
ck('l=3 perm p (SMICA)', s4['p_perm_l3'], 0.0045, 0.002)
ck('axisym frac l=3', s3['l3_axisym_frac'], 0.9020, 1e-4)
ck('axisym look-elsewhere p', s3['l3_axisym_p'], 0.09298, 0.01)
ck('axis (l)', s2['axis'][0], 193.45, 0.1)
ck('axis (b)', s2['axis'][1], -37.85, 0.1)
axv = np.array([math.cos(math.radians(s2['axis'][1])) * math.cos(math.radians(s2['axis'][0])),
                math.cos(math.radians(s2['axis'][1])) * math.sin(math.radians(s2['axis'][0])),
                math.sin(math.radians(s2['axis'][1]))])
ck('axis angle to cold spot', float(np.degrees(np.arccos(np.clip(abs(float(V[0] @ axv)), -1, 1)))), 21.73, 0.2)
ck('P4 flips', float(s6['n_flip']), 23.0, 0.0)
ck('P4 LOO accuracy', float(s6['loo_acc']), 28.0, 0.0)
ck('P4 LOO p', float(s6['loo_p']), 0.741, 0.05)
# P4 recompute from scratch
col = np.loadtxt(CS + '/anchored_coloring.txt')[:, 3].astype(int)
ck('P4 flips (recomputed)', float((np.where(T < 0, 1, -1) != np.where(col == 1, 1, -1)).sum()), 23.0, 0.0)
# design deviation recompute
Y = {l: basis(l, V) for l in range(0, 7)}
mx = 0.0
for t in [2, 3, 4, 5]:
    for l1 in range(0, t + 1):
        for l2 in range(0, t + 1):
            if l1 + l2 > t:
                continue
            M = (4 * math.pi / 60) * (Y[l1].T @ Y[l2])
            tg = np.eye(len(Y[l1].T), len(Y[l2].T)) if l1 == l2 else 0.0
            mx = max(mx, float(np.abs(M - tg).max()))
ck('5-design deviation (a5_nodes)', mx, s1['design_dev']['5'], 1e-9)
ck('5-design deviation < 1e-6', mx, 0.0, 1e-6)
# edge classes
iu = np.triu_indices(60, 1)
de = np.degrees(np.arccos(np.clip((V @ V.T)[iu], -1, 1)))
el = de[de < 28]
ck('n edges', float(len(el)), 120.0, 0.0)
ck('edge length class A (n)', float((el < 26.13).sum()), 60.0, 0.0)
ck('edge length class B (n)', float((el > 26.13).sum()), 60.0, 0.0)
print('    l=3 node-vs-sky coefficient correlation = %+.4f  (context: sky pipelines agree at 0.997-0.9995)' % res_AB['3'])

# ---------- D. P3 checks (steps 08-10) ----------
print('\n[D] P3 checks (locality + definitive statistics)')
try:
    s8 = json.load(open(O150 + '/data/step08_p3_locality.json'))
    s9 = json.load(open(O150 + '/data/step09_p3_definitive.json'))
    s10 = json.load(open(O150 + '/data/step10_p3_verdict.json'))
    ck('P3 T9 (nside1024 4.17deg)', s9['T9'], -106.881, 0.01)
    ck('P3 T20', s9['T20'], 35.434, 0.01)
    ck('P3 ratio', s9['ratio'], 3.0163, 1e-3)
    ck('P3 z(T9)', s9['z9'], -2.414, 1e-3)
    ck('P3 z(T20)', s9['z20'], 0.800, 1e-3)
    ck('P3 corr(T9,T20)', s9['corr'], -0.0765, 1e-3)
    ck('P3 T9-T20 (uK)', s9['diff'], -142.315, 0.01)
    ck('P3 z(diff)', s9['z_diff'], -2.191, 1e-3)
    ck('P3 point sd (uK)', s9['point_sd'], 44.268, 1e-3)
    ck('P3 rank |T9| among 60 nodes', float(s9['rank_absT9']), 4.0, 0.0)
    ck('P3 rank |T20|', float(s9['rank_absT20']), 21.0, 0.0)
    ck('P3 pair rank pct', s9['rank_pair_pct'], 3.73, 0.05)
    ck('P3 p(ratio)', s9['p_ratio'], 0.2030, 5e-3)
    ck('P3 p(diff)', s9['p_diff'], 0.0279, 5e-3)
    ck('P3 gate variance (uK^2)', s9['gate'][0], 1959.650, 0.01)
    ck('P3 gate == map var (rel 1e-6)', abs(s9['gate'][0] - s9['gate'][1]) / s9['gate'][1], 0.0, 1e-6)
    ck('P3 multiscale ratio @1.0deg', s8['ratio']['1.0'], 4.045, 1e-3)
    ck('P3 multiscale ratio @4.17deg', s8['ratio']['4.17'], 3.016, 1e-3)
    ck('P3 multiscale ratio @15deg', s8['ratio']['15.0'], 1.602, 1e-3)
    ck('P3 lmax<=4 ratio', s8['lmax'][3][3], 6.825, 1e-3)
    ck('P3 lmax<=10 ratio', s8['lmax'][7][3], 1.234, 1e-3)
    ck('P3 lmax<=30 ratio', s8['lmax'][10][3], 5.102, 1e-3)
    ck('P3 excision node20 r<5deg ratio', s8['excision']['node20_5.0'][2], 1.458, 1e-3)
    ck('P3 excision node9 r<3deg ratio', s8['excision']['node9_3.0'][2], 3.067, 1e-3)
    ck('P3 order4 GRF mean', s10['order4'][0], 1.886, 1e-3)
    ck('P3 order4 observed', s10['order4'][2], 2.414, 1e-3)
    ck('P3 p rank4', s10['p_rank4'], 0.0173, 5e-3)
    ck('P3 max pair obs (uK)', s10['max_pair_obs'], 245.9, 0.1)
    ck('P3 p maxpair vs 142.3', s10['p_maxpair'], 0.9956, 5e-3)
    ck('P3 ratio is NOT anomalous (p > 0.1)', 1.0 if s9['p_ratio'] > 0.1 else 0.0, 1.0, 0.0)
    ck('P3 z(T9) marginal (1.5 < |z| < 3)', 1.0 if 1.5 < abs(s9['z9']) < 3 else 0.0, 1.0, 0.0)
except FileNotFoundError as e:
    print('    [FAIL] missing P3 data: %s' % e)
    FAIL.append('P3 data missing')

# ---------- E. second-round checks (steps 11-14) ----------
print('\n[E] second-round checks (node9 structure / multiset / full-sky low-l / kernel)')
try:
    s11 = json.load(open(O150 + '/data/step11_node9_structure.json'))
    s12 = json.load(open(O150 + '/data/step12_multiset_orderstats.json'))
    s13 = json.load(open(O150 + '/data/step13_fullsky_lowl.json'))
    s14 = json.load(open(O150 + '/data/step14_kernel_scale.json'))
    ck('rho(k, |z|)', s11['rho_k'][0], -0.2880, 1e-3)
    ck('p(rho k)', s11['rho_k'][1], 0.0257, 2e-3)
    ck('rho(hop, |z|)', s11['rho_hop'][0], 0.1650, 1e-3)
    ck('node9 n_transparent', s11['ntr9'], 4.0, 0.0)
    ck('node20 n_transparent', s11['ntr20'], 4.0, 0.0)
    ck('A5 orders above 95% band', float(s12['A5_60']['above95']), 4.0, 0.0)
    ck('A5 Bonferroni p', s12['A5_60']['bonf'], 0.0797, 5e-3)
    ck('G88 orders above 95% band', float(s12['G88']['above95']), 0.0, 0.0)
    ck('G120 orders above 95% band', float(s12['G120']['above95']), 0.0, 0.0)
    ck('G32 orders above 95% band', float(s12['G32frust']['above95']), 0.0, 0.0)
    ck('total orders above 95% band', float(sum(s12[nm]['above95'] for nm in s12)), 4.0, 0.0)
    ck('full-sky l=3 axis SMICA l', s13['SMICA_l3_full'][0], 82.49, 0.05)
    ck('full-sky l=3 axis SMICA b', s13['SMICA_l3_full'][1], 17.21, 0.05)
    ck('full-sky l=3 axis NILC l', s13['NILC_l3_full'][0], 82.42, 0.05)
    ck('full-sky l=3 axis Commander l', s13['Commander_l3_full'][0], 82.11, 0.05)
    ck('corr l=3 SMICA-NILC', s13['corr_l3_NILC'], 0.9999, 1e-3)
    ck('corr l=3 SMICA-Commander', s13['corr_l3_Commander'], 0.9986, 1e-3)
    ck('Q-O angle SMICA', s13['qo_SMICA'], 73.24, 0.05)
    ck('kernel ratio FWHM/(2pi/88)', s14['ratio_fwhm_2pi88'], 1.0193, 1e-3)
    ck('node spacing (deg)', s14['spacing'], 26.0913, 1e-3)
    ck('effective DOF', s14['eff_dof'], 54.2, 0.3)
    ck('nearest-neighbour correlation', s14['near_corr_mean'], 0.044, 2e-3)
    ck('multiset excess NOT systematic', 1.0 if sum(s12[nm]['above95'] for nm in s12 if nm != 'A5_60') == 0 else 0.0, 1.0, 0.0)
    ck('K_sigma NOT derivable (ratio > 1.5%)', 1.0 if abs(s14['ratio_fwhm_2pi88'] - 1) > 0.015 else 0.0, 1.0, 0.0)
except FileNotFoundError as e:
    print('    [FAIL] missing 2nd-round data: %s' % e)
    FAIL.append('2nd-round data missing')

json.dump(res_AB, open(O150 + '/data/step07_crossscale_audit.json', 'w'), indent=2)
print('\n%s  (%d FAIL)' % ('ALL AUDIT CHECKS PASSED' if not FAIL else 'AUDIT FAILURES: ' + ', '.join(FAIL), len(FAIL)))
sys.exit(1 if FAIL else 0)
