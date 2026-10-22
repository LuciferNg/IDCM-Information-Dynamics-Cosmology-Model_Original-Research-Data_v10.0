#!/usr/bin/env python3
"""
O150 #02 - P1 operator form + P3 minimal breaking input + blind tests
=====================================================================
P1: what is the correct sky-side operator family?  Is it I_h-covariant sampling?
P3: what is the minimal symmetry-breaking input delta-psi giving T9/T20 = 3.02?

A. l-resolved node values: T9^l, T20^l  -> which multipole carries the 3.02?
B. Operator family: P60[f]_i = (K_sigma * f)(n_i).  I_h-covariance + non-invariance.
C. Axisymmetry of the l=3 field in the best frame (is the "axis" a real object?)
D. Model comparison: axisymmetric A*P3(cosTheta)+c (3 par) vs general l=3 (7 par)
E. LOO band-limited test + held-out prediction of T9/T20 (zero sky parameters)
F. Cross-map + cross-node-set blind test (G88 / G32 independent node sets)
"""
import numpy as np, math, json, os
from astropy.coordinates import SkyCoord
import astropy.units as u
from scipy.special import lpmv

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
ROOT = BASE + '/open_problems_fresh'
O150 = ROOT + '/o150_sky_side_projection'
CS = ROOT + '/cmb_cold_spot/data'
G182 = ROOT + '/o182_88grid_geometry/data'
rng = np.random.default_rng(150)

raw = np.loadtxt(CS + '/a5_nodes.txt')
sc = SkyCoord(ra=raw[:, 0] * u.deg, dec=raw[:, 1] * u.deg, frame='icrs')
LB = np.column_stack([sc.galactic.l.deg, sc.galactic.b.deg])


def uvec(lb):
    l = np.radians(lb[:, 0]); b = np.radians(lb[:, 1])
    return np.column_stack([np.cos(b) * np.cos(l), np.cos(b) * np.sin(l), np.sin(b)])


def to_gal_vec(p):
    s = SkyCoord(ra=p[:, 0] * u.deg, dec=p[:, 1] * u.deg, frame='icrs')
    return uvec(np.column_stack([s.galactic.l.deg, s.galactic.b.deg]))


V = uvec(LB)
V88 = to_gal_vec(np.loadtxt(G182 + '/g88_nodes.txt'))
V32 = to_gal_vec(np.loadtxt(G182 + '/g32_frustration_midpoints.txt'))

TMAP = {}
for nm in ['SMICA', 'Commander', 'SEVEM']:
    J = json.load(open(G182 + '/temps2_%s_4.17deg.json' % nm))
    TMAP[nm] = np.array(J['A5_60'][:60], float)
    TMAP[nm + '_88'] = np.array(J['G88'], float)
    TMAP[nm + '_32'] = np.array(J['G32frust'], float)
T = TMAP['SMICA']


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


def proj(l, v, x):
    B = basis(l, v)
    return B @ np.linalg.lstsq(B, x, rcond=None)[0]


def fib_sphere(n):
    idx = np.arange(n) + 0.5
    z = 1 - 2 * idx / n
    az = math.pi * (1 + 5 ** 0.5) * idx
    r_ = np.sqrt(np.clip(1 - z * z, 0, None))
    return np.column_stack([r_ * np.cos(az), r_ * np.sin(az), z])


def frame_z(a):
    a = a / np.linalg.norm(a)
    tmp = np.array([0.0, 0.0, 1.0]) if abs(a[2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    x = np.cross(tmp, a); x /= np.linalg.norm(x)
    y = np.cross(a, x)
    return np.column_stack([x, y, a])


AXGRID = fib_sphere(200000)


def p3_axis_stats(x, v, axgrid=AXGRID):
    """vectorised: returns (best |r|, best axis, min residual rms of A*P3+c model)"""
    xc = x - x.mean()
    ct = v @ axgrid.T
    P = (5 * ct ** 3 - 3 * ct) / 2
    P = P - P.mean(0)
    num = P.T @ xc
    den = np.linalg.norm(P, axis=0) * np.linalg.norm(xc) + 1e-30
    rr = np.abs(num) / den
    i = int(np.argmax(rr))
    # axisym fit residual: ||x||^2 - (x.c)^2/||c||^2  (x centred, constant col absorbed)
    rms = float(np.sqrt(max((xc @ xc) - (num[i] ** 2) / (np.linalg.norm(P[:, i]) ** 2), 0.0) / len(x)))
    return float(rr[i]), axgrid[i], rms


print('=' * 86)
print('  O150 #02 - P1 operator form + P3 minimal breaking input + blind tests')
print('=' * 86)
Tz = T - T.mean()
LS = [1, 2, 3, 4, 5, 6]

# ---------- A. l-resolved node values ----------
print('\n[A] l-resolved contributions at node9 / node20  (T9 = %.3f, T20 = %.3f, mean = %.3f)' % (
    T[9], T[20], T.mean()))
comp = {l: proj(l, V, Tz) for l in LS}
print('     l      T9^l       T20^l    |T9|/|T20|')
for l in LS:
    s = '   n/a' if abs(comp[l][20]) < 1e-9 else '%6.3f' % (abs(comp[l][9]) / abs(comp[l][20]))
    print('    %2d  %+9.3f  %+9.3f   %s' % (l, comp[l][9], comp[l][20], s))
tot = sum(comp[l] for l in LS)
print('    sum   %+9.3f  %+9.3f   %.3f' % (tot[9], tot[20], abs(tot[9]) / abs(tot[20])))
c12 = comp[1] + comp[2]
c46 = comp[4] + comp[5] + comp[6]
print('    l<=2 : %+9.3f  %+9.3f   %.3f' % (c12[9], c12[20], abs(c12[9]) / abs(c12[20])))
print('    l=3  : %+9.3f  %+9.3f   %.3f' % (comp[3][9], comp[3][20], abs(comp[3][9]) / abs(comp[3][20])))
print('    l>=4 : %+9.3f  %+9.3f   %.3f' % (c46[9], c46[20], abs(c46[9]) / abs(c46[20])))

# ---------- B. operator covariance ----------
print('\n[B] operator family P60[f]_i = (K_sigma * f)(n_i): I_h-covariance')
import networkx as nx
edges = [(i, j) for i in range(60) for j in range(i + 1, 60)
         if math.degrees(math.acos(np.clip(float(V[i] @ V[j]), -1, 1))) < 28.0]
Gn = nx.Graph(); Gn.add_nodes_from(range(60)); Gn.add_edges_from(edges)
gmap = None
for iso in nx.algorithms.isomorphism.GraphMatcher(Gn, Gn).isomorphisms_iter():
    if iso.get(9) == 20:
        gmap = iso; break
perm = np.array([gmap[i] for i in range(60)])
print('    automorphism g (g(9)=20): fixed points = %d' % int((perm == np.arange(60)).sum()))
U, S, Vt = np.linalg.svd(V[perm].T @ V)
Rg = U @ Vt
if np.linalg.det(Rg) < 0:
    U[:, -1] *= -1; Rg = U @ Vt
print('    sphere rotation R_g realising g: max|V[g] - V R_g^T| = %.3e  det = %+.6f' % (
    np.abs(V[perm] - V @ Rg.T).max(), np.linalg.det(Rg)))
print('    -> node set I_h-symmetric; P60 is I_h-COVARIANT (not invariant)')
d = np.array([comp[l][9] - comp[l][20] for l in LS])
print('    (T9 - T20) = %+.3f uK decomposed by l:' % (T[9] - T[20]))
for i, l in enumerate(LS):
    print('      l=%d : %+8.3f uK  %5.1f%%' % (l, d[i], 100 * d[i] / d.sum()))
print('    l>=3 share of the difference = %.1f%%' % (100 * d[2:].sum() / d.sum()))

# ---------- C. axisymmetry of l=3 ----------
print('\n[C] axisymmetry of the l=3 node field (SMICA)')
r3, AX, rms_ax_scan = p3_axis_stats(Tz, V)
l3 = math.degrees(math.atan2(AX[1], AX[0])) % 360
b3 = math.degrees(math.asin(AX[2]))
print('    best axis (l,b) = (%.2f, %.2f), r = %.4f' % (l3, b3, r3))
M = frame_z(AX)
B3 = basis(3, V)
B3f = basis(3, V @ M)
c3f = np.linalg.lstsq(B3f, Tz, rcond=None)[0]
pw = c3f ** 2
names = ['m=-3', 'm=-2', 'm=-1', 'm=0', 'm=1', 'm=2', 'm=3']
print('    l=3 coefficients in the axis frame:')
for nm, cc, pp in zip(names, c3f, pw):
    print('      %-5s %+9.3f   power %9.2f  %5.1f%%' % (nm, cc, pp, 100 * pp / pw.sum()))
f0 = float(pw[3] / pw.sum())
print('    m=0 power fraction = %.4f' % f0)
nll = []
for _ in range(4000):
    ac = rng.normal(size=7)
    af = np.linalg.lstsq(B3f, B3 @ ac, rcond=None)[0]
    nll.append(af[3] ** 2 / (af ** 2).sum())
nll = np.array(nll)
p_m0 = (1 + int((nll >= f0).sum())) / (1 + len(nll))
print('    null (random l=3 field, same nodes + same frame): m=0 frac = %.4f +- %.4f, p = %.4f' % (
    nll.mean(), nll.std(), p_m0))

# ---------- D. axisymmetric model vs general l=3 ----------
print('\n[D] model comparison on the 60 nodes')
cG = np.linalg.lstsq(B3, Tz, rcond=None)[0]
rG = Tz - B3 @ cG
rmsG = float(np.sqrt((rG ** 2).mean()))
print('    general l=3 (7 par)          : residual RMS = %.3f uK' % rmsG)
print('    axisym A*P3(cosT)+c (3 par)  : residual RMS = %.3f uK   ratio = %.4f' % (
    rms_ax_scan, rms_ax_scan / rmsG))
rat = []
NMC = 400
AXN = fib_sphere(20000)
ctn = V @ AXN.T
Pn = (5 * ctn ** 3 - 3 * ctn) / 2
Pn = Pn - Pn.mean(0)
nrmP = np.linalg.norm(Pn, axis=0)
Xr = B3 @ rng.normal(size=(7, NMC))
Xc = Xr - Xr.mean(0)
num = Pn.T @ Xc
den = nrmP[:, None] * np.linalg.norm(Xc, axis=0)[None, :]
rrn = np.abs(num) / (den + 1e-30)
best = np.argmax(rrn, axis=0)
rmsA = np.sqrt(np.clip((Xc ** 2).sum(0)[None, :] - num ** 2 / (nrmP[:, None] ** 2), 0, None) / 60.0)
rmsA_best = rmsA[best, np.arange(NMC)]
rmsG_ = np.sqrt(((Xc - B3 @ np.linalg.lstsq(B3, Xc, rcond=None)[0]) ** 2).mean(0))
rat = rmsA_best / rmsG_
rat = np.array(rat)
print('    null ratio (random l=3 field, %d MC x %d axes) = %.4f +- %.4f  ; observed = %.4f' % (
    NMC, AXN.shape[0], rat.mean(), rat.std(), rms_ax_scan / rmsG))
print('    p(axisym model this good) = %.4f' % (
    (1 + int((rat <= rms_ax_scan / rmsG).sum())) / (1 + len(rat))))

# ---------- E. LOO band-limited test ----------
print('\n[E] LOO band-limited test + held-out prediction of T9 / T20')
for lmax in [3, 4, 6]:
    B = np.column_stack([basis(l, V) for l in range(1, lmax + 1)])
    c = np.linalg.lstsq(B, Tz, rcond=None)[0]
    rms_in = float(np.sqrt(((Tz - B @ c) ** 2).mean()))
    pr = np.empty(60)
    for i in range(60):
        keep = np.ones(60, bool); keep[i] = False
        pr[i] = B[i] @ np.linalg.lstsq(B[keep], Tz[keep], rcond=None)[0]
    rms_loo = float(np.sqrt(((pr - Tz) ** 2).mean()))
    print('    model l<=%d (%2d par): in-sample RMS = %.3f ; LOO RMS = %.3f' % (
        lmax, B.shape[1], rms_in, rms_loo))
print('    (LOO ~= in-sample  =>  field is genuinely band-limited, not overfit)')
for lmax in [3, 6]:
    B = np.column_stack([basis(l, V) for l in range(1, lmax + 1)])
    keep = np.ones(60, bool); keep[[9, 20]] = False
    c = np.linalg.lstsq(B[keep], Tz[keep], rcond=None)[0]
    r = Tz[keep] - B[keep] @ c
    s2 = (r ** 2).sum() / (keep.sum() - B.shape[1])
    cov = s2 * (B @ np.linalg.pinv(B[keep].T @ B[keep]) @ B.T)
    se = np.sqrt(np.clip(np.diag(cov), 0, None))
    pred = B @ c
    print('    l<=%d fit on 58 nodes -> hold out 9,20:' % lmax)
    print('      node9 : pred %+8.3f +- %6.3f   obs %+8.3f   z = %+.2f' % (
        pred[9], se[9], Tz[9], (Tz[9] - pred[9]) / se[9]))
    print('      node20: pred %+8.3f +- %6.3f   obs %+8.3f   z = %+.2f' % (
        pred[20], se[20], Tz[20], (Tz[20] - pred[20]) / se[20]))
    print('      predicted ratio |T9|/|T20| = %.3f    observed = %.3f' % (
        abs(pred[9]) / abs(pred[20]), abs(Tz[9]) / abs(Tz[20])))
B = np.column_stack([basis(l, V) for l in range(1, 4)])
keep = np.ones(60, bool); keep[[9, 20]] = False
c = np.linalg.lstsq(B[keep], Tz[keep], rcond=None)[0]
r = Tz[keep] - B[keep] @ c
s2 = (r ** 2).sum() / (keep.sum() - B.shape[1])
Cov = s2 * np.linalg.pinv(B[keep].T @ B[keep])
L = np.linalg.cholesky(Cov + 1e-16 * np.eye(15))
rq = []
for _ in range(20000):
    cc = c + L @ rng.normal(size=15)
    t20 = B[20] @ cc
    if abs(t20) > 1e-6:
        rq.append(abs(B[9] @ cc) / abs(t20))
rq = np.array(rq)
print('    l<=3 posterior ratio: median %.3f  68%% CI [%.3f, %.3f]  P(>3.0216) = %.3f' % (
    np.median(rq), np.percentile(rq, 16), np.percentile(rq, 84), float((rq > 3.0216).mean())))

# ---------- F. cross-map + cross-node-set blind test ----------
print('\n[F] cross-map and cross-node-set l=3 mode correlation')
def l3_coef(xv, v):
    return np.linalg.lstsq(basis(3, v), xv - xv.mean(), rcond=None)[0]


ref = l3_coef(T, V)
res = {'A_comp': {str(l): [float(comp[l][9]), float(comp[l][20])] for l in LS},
       'axis': [float(l3), float(b3)], 'axis_r': float(r3),
       'm0_frac': f0, 'm0_p': float(p_m0),
       'axisym_rms': float(rms_ax_scan), 'general_rms': float(rmsG),
       'axisym_ratio': float(rms_ax_scan / rmsG), 'axisym_ratio_null': [float(rat.mean()), float(rat.std())],
       'ratio_posterior': [float(np.median(rq)), float(np.percentile(rq, 16)), float(np.percentile(rq, 84))]}
for nm, vv, xx in [('SMICA_A5_60', V, TMAP['SMICA']), ('SMICA_G88', V88, TMAP['SMICA_88']),
                   ('SMICA_G32frust', V32, TMAP['SMICA_32']),
                   ('Commander_A5_60', V, TMAP['Commander']), ('SEVEM_A5_60', V, TMAP['SEVEM']),
                   ('Commander_G88', V88, TMAP['Commander_88']), ('SEVEM_G88', V88, TMAP['SEVEM_88'])]:
    cc = l3_coef(xx, vv)
    cr = float(np.corrcoef(cc, ref)[0, 1])
    ratio = float(np.linalg.norm(cc) / np.linalg.norm(ref))
    print('    %-16s corr(coef, SMICA-A5) = %+.4f   |coef| ratio = %.3f' % (nm, cr, ratio))
    res['xset_' + nm] = [cr, ratio]
print('    l=3 axis per map (A5_60):')
axs = {}
for nm in ['SMICA', 'Commander', 'SEVEM']:
    rr, aa, _ = p3_axis_stats(TMAP[nm] - TMAP[nm].mean(), V)
    lb = (math.degrees(math.atan2(aa[1], aa[0])) % 360, math.degrees(math.asin(aa[2])))
    axs[nm] = aa
    print('      %-10s (%.2f, %.2f)  r = %.4f' % (nm, lb[0], lb[1], rr))
for nm in ['Commander', 'SEVEM']:
    ang = math.degrees(math.acos(np.clip(float(axs[nm] @ axs['SMICA']), -1, 1)))
    print('      angle SMICA-%s = %.2f deg' % (nm, ang))
    res['ang_' + nm] = float(ang)

os.makedirs(O150 + '/data', exist_ok=True)
json.dump(res, open(O150 + '/data/step02_operator_breaking.json', 'w'), indent=2)
print('\nOK saved: %s/data/step02_operator_breaking.json' % O150)
