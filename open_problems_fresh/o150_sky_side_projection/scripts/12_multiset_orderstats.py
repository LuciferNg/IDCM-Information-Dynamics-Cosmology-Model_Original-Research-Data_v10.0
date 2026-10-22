#!/usr/bin/env python3
"""
O150 #12 - multi-node-set order statistics (is the A5 slight excess systematic?)
==============================================================================
Script 10 found the A5 |z| order statistics 2-5 sitting slightly above the GRF 95% band
(Bonferroni x5 -> p = 0.086).  Here we repeat the test on independent point sets:

A. G88 (88 transparent-edge midpoints), G120 (all 120), G32 (frustrated midpoints)
B. analytic GRF covariance per set (from the map's own C_l, correct point separations)
C. observed vs GRF order statistics for each set
D. joint assessment: is the excess systematic or a single-set fluctuation?
"""
import numpy as np, math, json
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
ROOT = BASE + '/open_problems_fresh'
O150 = ROOT + '/o150_sky_side_projection'
CS = ROOT + '/cmb_cold_spot/data'
G182 = ROOT + '/o182_88grid_geometry/data'
CACHE = ROOT + '/o5_catalog_compare/data/smooth_cache'
NS = 1024

raw = np.loadtxt(CS + '/a5_nodes.txt')
sc = SkyCoord(ra=raw[:, 0] * u.deg, dec=raw[:, 1] * u.deg, frame='icrs')
LB = np.column_stack([sc.galactic.l.deg, sc.galactic.b.deg])


def uvec(lb):
    l = np.radians(lb[:, 0]); b = np.radians(lb[:, 1])
    return np.column_stack([np.cos(b) * np.cos(l), np.cos(b) * np.sin(l), np.sin(b)])


def to_gal(p):
    s = SkyCoord(ra=p[:, 0] * u.deg, dec=p[:, 1] * u.deg, frame='icrs')
    return uvec(np.column_stack([s.galactic.l.deg, s.galactic.b.deg]))


J = json.load(open(G182 + '/temps2_SMICA_4.17deg.json'))
SETS = {
    'A5_60': (uvec(LB), np.array(J['A5_60'][:60], float)),
    'G88': (to_gal(np.loadtxt(G182 + '/g88_nodes.txt')), np.array(J['G88'], float)),
    'G32frust': (to_gal(np.loadtxt(G182 + '/g32_frustration_midpoints.txt')), np.array(J['G32frust'], float)),
    'G120': (None, np.array(J['G120_all'], float)),
}
V88 = SETS['G88'][0]; V32 = SETS['G32frust'][0]
SETS['G120'] = (np.vstack([V88, V32]), SETS['G120'][1])

print('=' * 92)
print('  O150 #12 - multi-node-set order statistics')
print('=' * 92)

m = hp.ud_grade(hp.read_map(CACHE + '/smica2_smooth4.17.fits', field=0), NS) * 1e6
cl = hp.anafast(m, lmax=3 * NS - 1)
LMAX = 3 * NS - 1
w = (2 * np.arange(LMAX + 1) + 1) / (4 * np.pi) * cl


def cov(Vv):
    GAM = np.clip(Vv @ Vv.T, -1, 1)
    C = np.zeros_like(GAM)
    Pm1 = np.ones_like(GAM); P0 = GAM.copy()
    for L in range(1, LMAX):
        P1 = ((2 * L + 1) * GAM * P0 - L * Pm1) / (L + 1)
        C += w[L + 1] * P1; Pm1, P0 = P0, P1
    return 0.5 * (C + C.T)


np.random.seed(15121)
NMC = 20000
res = {}
for nm, (Vv, Tv) in SETS.items():
    N = len(Tv)
    C = cov(Vv)
    sd = np.sqrt(np.diag(C))
    # point check: sd should equal the map std
    z = Tv / sd
    az = np.abs(z)
    S = np.random.multivariate_normal(np.zeros(N), C, size=NMC)
    Z = S / sd[None, :]
    AZ = np.abs(Z)
    osamp = -np.sort(-AZ, axis=1)
    obs = np.sort(az)[::-1]
    print('\n[%s] N = %d ; point sd mean = %.3f uK (map std %.2f) ; max|z| = %.3f' % (
        nm, N, sd.mean(), m.std(), az.max()))
    print('    %-6s %10s %10s %10s %10s' % ('order', 'GRF mean', 'GRF 95%', 'observed', 'p'))
    ks = [1, 2, 3, 4, 5] if N <= 60 else [1, 2, 3, 4, 5, 6, 8, 10]
    ps = []
    for k in ks:
        gm = osamp[:, k - 1].mean(); g95 = np.percentile(osamp[:, k - 1], 95)
        ob = obs[k - 1]
        p = (1 + int((osamp[:, k - 1] >= ob).sum())) / (1 + NMC)
        ps.append(p)
        print('    %-6d %10.3f %10.3f %10.3f %10.4f' % (k, gm, g95, ob, p))
    # combined p over the orders (Bonferroni is conservative; also report min-p count)
    nabove = sum(1 for k in ks if obs[k - 1] > np.percentile(osamp[:, k - 1], 95))
    print('    orders above their 95%% band: %d/%d ; Bonferroni min p x%d = %.4f' % (
        nabove, len(ks), len(ks), min(1.0, min(ps) * len(ks))))
    res[nm] = {'N': N, 'maxz': float(az.max()), 'above95': nabove, 'nks': len(ks),
               'bonf': float(min(1.0, min(ps) * len(ks))), 'ps': [float(x) for x in ps],
               'sd_mean': float(sd.mean())}

print('\n[D] joint assessment')
tot_above = sum(res[nm]['above95'] for nm in res)
tot_k = sum(res[nm]['nks'] for nm in res)
print('    total orders above 95%% band across all sets: %d/%d (expected ~%.1f under GRF)' % (
    tot_above, tot_k, 0.05 * tot_k))
print('    best (smallest) Bonferroni p across sets: %.4f' % min(res[nm]['bonf'] for nm in res))
print('    -> %s' % ('SYSTEMATIC excess (would need a mechanism)'
                     if tot_above > 0.15 * tot_k + 2 else 'consistent with a single-set fluctuation'))

json.dump(res, open(O150 + '/data/step12_multiset_orderstats.json', 'w'), indent=2)
print('\nOK saved: %s/data/step12_multiset_orderstats.json' % O150)
