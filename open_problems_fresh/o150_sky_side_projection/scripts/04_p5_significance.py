#!/usr/bin/env python3
"""
O150 #04 - P5: GRF null (physical) vs permutation null, QML masked l=3 test, 4-map check
========================================================================================
A. Observed l-power shares (basis-free ||Pi_l Tz||^2/||Tz||^2) on the 60 nodes, sampled
   from the SAME nside-128 downgrade used by the null.
B. Permutation null (O143's null) vs GRF null built from the map's OWN C_l (correct null).
C. QML: GLS chi^2_7 test of the l=3 amplitude with a galactic mask (|b|>cut) - uses the
   full node covariance instead of subset splitting.
D. Four independent component-separation pipelines: SMICA / NILC / Commander / SEVEM.
"""
import numpy as np, math, json, os
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u
from scipy.special import lpmv
from scipy import stats

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
ROOT = BASE + '/open_problems_fresh'
O150 = ROOT + '/o150_sky_side_projection'
CS = ROOT + '/cmb_cold_spot/data'
G182 = ROOT + '/o182_88grid_geometry/data'
CACHE = ROOT + '/o5_catalog_compare/data/smooth_cache'
rng = np.random.default_rng(1504)
NS = 128

raw = np.loadtxt(CS + '/a5_nodes.txt')
sc = SkyCoord(ra=raw[:, 0] * u.deg, dec=raw[:, 1] * u.deg, frame='icrs')
LB = np.column_stack([sc.galactic.l.deg, sc.galactic.b.deg])
l_ = np.radians(LB[:, 0]); b_ = np.radians(LB[:, 1])
V = np.column_stack([np.cos(b_) * np.cos(l_), np.cos(b_) * np.sin(l_), np.sin(b_)])
PIX = hp.ang2pix(NS, LB[:, 0], LB[:, 1], lonlat=True)


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


def shares(Tv, lmax=6):
    x = Tv - Tv.mean()
    tot = x @ x
    out = {}
    for l in range(1, lmax + 1):
        B = basis(l, V)
        p = B @ np.linalg.lstsq(B, x, rcond=None)[0]
        out[l] = float((p @ p) / tot)
    return out


print('=' * 90)
print('  O150 #04 - P5: GRF null vs permutation null, QML masked test, 4-map check')
print('=' * 90)

# ---------- A. observed, consistent sampling ----------
print('\n[A] observed l-power shares (basis-free) - nside %d downgrade, same path as null' % NS)
MAPS = {}
for nm, fn in [('SMICA', 'smica2_smooth4.17.fits'), ('NILC', 'nilc2_smooth4.17.fits'),
               ('Commander', 'commander_smooth4.17.fits')]:
    m = hp.read_map(CACHE + '/' + fn, field=0)
    MAPS[nm] = hp.ud_grade(m, NS)
J = json.load(open(G182 + '/temps2_SEVEM_4.17deg.json'))
MAPS['SEVEM'] = None   # SEVEM: use the JSON node values (verified pipeline)
TJSON = {nm: np.array(json.load(open(G182 + '/temps2_%s_4.17deg.json' % nm))['A5_60'][:60], float)
         for nm in ['SMICA', 'Commander', 'SEVEM']}
TOBS = {}
for nm in ['SMICA', 'NILC', 'Commander']:
    TOBS[nm] = MAPS[nm][PIX] * 1e6
TOBS['SEVEM'] = TJSON['SEVEM']
for nm in ['SMICA', 'Commander', 'SEVEM']:
    d = np.abs(TOBS[nm] - TJSON[nm]).max()
    print('    consistency %-9s : max|nside128 - temps2(2048)| = %.3f uK' % (nm, d))
sh_obs = {nm: shares(TOBS[nm]) for nm in TOBS}
print('    %-10s %8s %8s %8s %8s %8s %8s   %s' % ('map', 'l=1', 'l=2', 'l=3', 'l=4', 'l=5', 'l=6', 'l=3 / l<=2'))
for nm in ['SMICA', 'NILC', 'Commander', 'SEVEM']:
    s = sh_obs[nm]
    print('    %-10s %7.1f%% %7.1f%% %7.1f%% %7.1f%% %7.1f%% %7.1f%%   %6.1f' % (
        nm, 100 * s[1], 100 * s[2], 100 * s[3], 100 * s[4], 100 * s[5], 100 * s[6],
        s[3] / (s[1] + s[2])))
print('    node9/node20 |ratio|: ' + '  '.join('%s %.3f' % (nm, abs(TOBS[nm][9] / TOBS[nm][20])) for nm in TOBS))

# ---------- B. nulls ----------
print('\n[B] nulls for the l=3 share (SMICA)')
T0 = TOBS['SMICA']
sh0 = sh_obs['SMICA']
# permutation
nperm = 4000
perm = np.empty(nperm)
x0 = T0 - T0.mean()
B3 = basis(3, V)
for i in range(nperm):
    xx = rng.permutation(x0)
    p = B3 @ np.linalg.lstsq(B3, xx, rcond=None)[0]
    perm[i] = (p @ p) / (xx @ xx)
print('    permutation null (O143 style, 4000): l=3 share = %.4f +- %.4f' % (perm.mean(), perm.std()))
print('      observed %.4f   p = %.4f' % (sh0[3], (1 + int((perm >= sh0[3]).sum())) / (1 + nperm)))
# GRF from the map's own C_l
m0 = MAPS['SMICA']
cl = hp.anafast(m0 * 1e6, lmax=3 * NS - 1)
ells = np.arange(len(cl))
pred_var = np.sum((2 * ells + 1) * cl / (4 * np.pi))
print('    GRF sanity: sum(2l+1)C_l/4pi = %.2f uK^2 vs map var %.2f uK^2' % (pred_var, (m0 * 1e6).var()))
clin = np.zeros(len(cl)); clin[2:] = cl[2:]
ngrf = 1000
# hp.synalm draws from the GLOBAL numpy RNG (healpy 1.19), NOT from our Generator object.
# Seed it explicitly so this null is reproducible.
np.random.seed(15041)
grf = np.empty((ngrf, 7))
sh_g = {l: np.empty(ngrf) for l in range(1, 7)}
for i in range(ngrf):
    alm = hp.synalm(clin, lmax=len(cl) - 1)
    mp = hp.alm2map(alm, nside=NS)
    Tv = mp[PIX]
    s = shares(Tv)
    for l in range(1, 7):
        sh_g[l][i] = s[l]
for l in range(1, 7):
    p = (1 + int((sh_g[l] >= sh0[l]).sum())) / (1 + ngrf)
    print('    GRF null  l=%d : share = %.4f +- %.4f (null mean) ; obs %.4f ; p = %.4f' % (
        l, sh_g[l].mean(), sh_g[l].std(), sh0[l], p))
p_grf3 = (1 + int((sh_g[3] >= sh0[3]).sum())) / (1 + ngrf)
print('    -> l=3: permutation p = %.4f ; GRF p = %.4f' % (
    (1 + int((perm >= sh0[3]).sum())) / (1 + nperm), p_grf3))

# ---------- C. QML / GLS masked l=3 test ----------
print('\n[C] QML: GLS chi^2_7 test of the l=3 amplitude with galactic mask')
gam = V @ V.T
gam = np.clip(gam, -1, 1)
def cov_from_cl(cl_in):
    C = np.zeros((60, 60))
    for l in range(len(cl_in)):
        C += (2 * l + 1) / (4 * np.pi) * cl_in[l] * np.polynomial.legendre.legval(gam, [0] * l + [1])
    return C


Pl = {}
for l in range(0, 40):
    Pl[l] = np.polynomial.legendre.legval(gam, [0] * l + [1])
Cfull = np.zeros((60, 60))
for l in range(2, 40):
    Cfull += (2 * l + 1) / (4 * np.pi) * cl[l] * Pl[l]
# variant: exclude l=3 and replace by the mean of l=4,5,6 (smooth C_l trend)
cl_trend = cl.copy()
cl_trend[3] = np.mean(cl[4:7])
Ctrend = np.zeros((60, 60))
for l in range(2, 40):
    Ctrend += (2 * l + 1) / (4 * np.pi) * cl_trend[l] * Pl[l]
A3 = basis(3, V)
print('    %-14s %6s %10s %10s %12s %10s' % ('mask', 'n', 'chi2_7', 'p(full Cl)', 'chi2_7(trend)', 'p(trend)'))
res_qml = {}
for cut in [0.0, 20.0, 30.0, 40.0]:
    keep = np.abs(LB[:, 1]) > cut if cut > 0 else np.ones(60, bool)
    n = int(keep.sum())
    A = A3[keep]
    row = []
    for C in [Cfull, Ctrend]:
        Ck = C[np.ix_(keep, keep)]
        Ci = np.linalg.inv(Ck)
        M = A.T @ Ci @ A
        Tk = T0[keep] - T0[keep].mean()
        s = Tk @ Ci @ A @ np.linalg.solve(M, A.T @ Ci @ Tk)
        p = 1 - stats.chi2.cdf(s, 7)
        row.append((s, p))
    print('    |b|>%-8.0f %6d %10.2f %10.4f %12.2f %10.4f' % (
        cut, n, row[0][0], row[0][1], row[1][0], row[1][1]))
    res_qml[str(cut)] = {'n': n, 'chi2_full': float(row[0][0]), 'p_full': float(row[0][1]),
                         'chi2_trend': float(row[1][0]), 'p_trend': float(row[1][1])}
print('    (chi2_7 under H0: a_3 = 0 ; QML uses the full node covariance, no subset splitting)')

# ---------- D. per-map l=3 significance with GRF null ----------
print('\n[D] l=3 share significance per pipeline (GRF null from each map own C_l)')
res = {'shares': {nm: sh_obs[nm] for nm in sh_obs},
       'ratio_920': {nm: float(abs(TOBS[nm][9] / TOBS[nm][20])) for nm in TOBS},
       'qml': res_qml, 'p_perm_l3': float((1 + int((perm >= sh0[3]).sum())) / (1 + nperm)),
       'p_grf_l3': float(p_grf3), 'grf_null_l3': [float(sh_g[3].mean()), float(sh_g[3].std())]}
for nm in ['SMICA', 'NILC', 'Commander', 'SEVEM']:
    if nm == 'SEVEM':
        print('    %-10s (no nside-128 cache; JSON node values only) l=3 share = %.4f' % (nm, sh_obs[nm][3]))
        continue
    mm = MAPS[nm]
    clm = hp.anafast(mm * 1e6, lmax=3 * NS - 1)
    clm_in = np.zeros(len(clm)); clm_in[2:] = clm[2:]
    ng = 600
    np.random.seed(15042 + ['SMICA', 'NILC', 'Commander'].index(nm))   # reproducible per map
    s3 = np.empty(ng)
    for i in range(ng):
        mp = hp.alm2map(hp.synalm(clm_in, lmax=len(clm) - 1), nside=NS)
        s3[i] = shares(mp[PIX])[3]
    p = (1 + int((s3 >= sh_obs[nm][3]).sum())) / (1 + ng)
    print('    %-10s l=3 share = %.4f ; GRF null %.4f +- %.4f ; p = %.4f' % (
        nm, sh_obs[nm][3], s3.mean(), s3.std(), p))
    res['grf_' + nm] = {'share': sh_obs[nm][3], 'null': [float(s3.mean()), float(s3.std())], 'p': float(p)}

json.dump(res, open(O150 + '/data/step04_p5_significance.json', 'w'), indent=2)
print('\nOK saved: %s/data/step04_p5_significance.json' % O150)
