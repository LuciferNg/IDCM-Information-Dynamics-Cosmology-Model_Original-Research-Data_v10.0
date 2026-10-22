#!/usr/bin/env python3
"""
O150 #05 - P2: provenance of the l=3 axis
=========================================
A. Node-set l=3 axes: A5_60, G88, G32 (independent node sets) x 4 pipelines + MC uncertainty
B. Full-sky l=2 / l=3 preferred axes from the smoothed SMICA map (Land-Magueijo m=0 sense)
   -> quadrupole-octupole alignment angle, comparison with the literature AoE (l,b) = (250,60)
C. Structural direction catalogue: 31 I_h symmetry axes (6 C5 + 10 C3 + 15 C2), 62 face normals,
   60 node directions, 120 edge midpoints  ->  alignment p-values
D. Verdict: structural prediction, external-field alignment, or generic sky freedom?
"""
import numpy as np, math, json, os, re
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
rng = np.random.default_rng(1505)

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
TM = {}
for nm in ['SMICA', 'Commander', 'SEVEM']:
    J = json.load(open(G182 + '/temps2_%s_4.17deg.json' % nm))
    TM[nm] = np.array(J['A5_60'][:60], float)
    TM[nm + '_88'] = np.array(J['G88'], float)
    TM[nm + '_32'] = np.array(J['G32frust'], float)


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


def fib_sphere(n):
    idx = np.arange(n) + 0.5
    z = 1 - 2 * idx / n
    az = math.pi * (1 + 5 ** 0.5) * idx
    r_ = np.sqrt(np.clip(1 - z * z, 0, None))
    return np.column_stack([r_ * np.cos(az), r_ * np.sin(az), z])


def lb_of(a):
    return (math.degrees(math.atan2(a[1], a[0])) % 360, math.degrees(math.asin(np.clip(a[2], -1, 1))))


def ang(a, b):
    return math.degrees(math.acos(np.clip(abs(float(a @ b)), -1, 1)))


AXG = fib_sphere(400000)


def l3_axis_coef(xv, v):
    a = np.linalg.lstsq(basis(3, v), xv - xv.mean(), rcond=None)[0]
    F = basis(3, AXG) @ a
    i = int(np.argmax(np.abs(F)))
    return AXG[i], a


print('=' * 92)
print('  O150 #05 - P2: provenance of the l=3 axis')
print('=' * 92)

# ---------- A. node-set axes ----------
print('\n[A] l=3 preferred axes (Land-Magueijo m=0 sense) per node set and pipeline')
rows = [('SMICA A5_60', V, TM['SMICA']), ('Commander A5_60', V, TM['Commander']), ('SEVEM A5_60', V, TM['SEVEM']),
        ('SMICA G88', V88, TM['SMICA_88']), ('Commander G88', V88, TM['Commander_88']),
        ('SEVEM G88', V88, TM['SEVEM_88']),
        ('SMICA G32frust', V32, TM['SMICA_32']), ('Commander G32frust', V32, TM['Commander_32'])]
axes = {}
for nm, vv, xx in rows:
    a, co = l3_axis_coef(xx, vv)
    axes[nm] = a
    lb = lb_of(a)
    print('    %-18s (l,b) = (%7.2f, %+6.2f)   |b| = %5.2f deg' % (nm, lb[0], lb[1], abs(lb[1])))
print('    pairwise angles to SMICA A5_60 axis:')
for nm in axes:
    if nm != 'SMICA A5_60':
        print('      %-18s %.2f deg' % (nm, ang(axes[nm], axes['SMICA A5_60'])))

# MC uncertainty of the A5_60 axis
B3 = basis(3, V)
x = TM['SMICA'] - TM['SMICA'].mean()
c = np.linalg.lstsq(B3, x, rcond=None)[0]
res = x - B3 @ c
s2 = (res @ res) / (60 - 7)
Cov = s2 * np.linalg.pinv(B3.T @ B3)
L = np.linalg.cholesky(Cov + 1e-16 * np.eye(7))
B3g = basis(3, AXG)
dev = []
for _ in range(600):
    cc = c + L @ rng.normal(size=7)
    F = B3g @ cc
    dev.append(ang(AXG[int(np.argmax(np.abs(F)))], axes['SMICA A5_60']))
dev = np.array(dev)
print('    A5_60 axis MC uncertainty: median dev = %.2f deg ; 68%% = %.2f deg ; 95%% = %.2f deg' % (
    np.median(dev), np.percentile(dev, 68), np.percentile(dev, 95)))

# ---------- B. full-sky l=2 / l=3 axes ----------
print('\n[B] full-sky l=2 / l=3 preferred axes (smoothed SMICA 4.17 deg)')
m = hp.read_map(CACHE + '/smica2_smooth4.17.fits', field=0)
alm = hp.map2alm(m * 1e6, lmax=64)
AOE = uvec(np.array([[250.0, 60.0]]))[0]
out_sky = {}
lb60 = hp.pix2ang(hp.get_nside(m), np.arange(hp.nside2npix(hp.get_nside(m))), lonlat=True)[1]
mask = np.abs(lb60) > 20.0
alm_cut = hp.map2alm((m * 1e6) * mask, lmax=64)
print('    (unmasked / |b|>20-cut pseudo-a_lm ; low-l from a cut sky is biased, indicative only)')
for l in [2, 3]:
    for tag, aa in [('full', alm), ('b>20', alm_cut)]:
        a = np.array([aa[hp.Alm.getidx(64, l, mm)] for mm in range(0, l + 1)])
        F = np.zeros(len(AXG))
        for mm in range(0, l + 1):
            ar = np.real(a[mm]); ai = np.imag(a[mm]) if mm > 0 else 0.0
            if mm == 0:
                F += ar * real_sph(l, 0, AXG)
            else:
                F += math.sqrt(2) * ar * real_sph(l, mm, AXG)
                F -= math.sqrt(2) * ai * real_sph(l, -mm, AXG)
        i = int(np.argmax(np.abs(F)))
        ax = AXG[i]
        lb = lb_of(ax)
        out_sky[str(l) + '_' + tag] = [float(lb[0]), float(lb[1])]
        print('    l=%d [%s] axis (l,b) = (%7.2f, %+6.2f) ; |b| = %5.2f ; to AoE = %5.2f deg ; to node axis = %5.2f deg' % (
            l, tag, lb[0], lb[1], abs(lb[1]), ang(ax, AOE), ang(ax, axes['SMICA A5_60'])))
print('    literature AoE (Land-Magueijo 2005 / de Oliveira-Costa 2004): (l,b) ~ (250, 60) i.e. -110,60')

# ---------- C. structural direction catalogue ----------
print('\n[C] structural direction catalogue vs the A5_60 l=3 axis')
ax = axes['SMICA A5_60']
txt = open(CS + '/faces.txt').read().splitlines()
faces = {}
for ln in txt:
    mm = re.match(r'([PS T])\s*\[([^\]]+)\]', ln.strip())
    if mm:
        t = mm.group(1)
        idx = [int(z) for z in mm.group(2).split(',')]
        faces.setdefault(t, []).append(idx)
cats = {}
cats['pentagon centres (C5)'] = np.array([V[i].sum(0) / np.linalg.norm(V[i].sum(0)) for i in faces['P']])
cats['triangle centres (C3)'] = np.array([V[i].sum(0) / np.linalg.norm(V[i].sum(0)) for i in faces['T']])
cats['square centres'] = np.array([V[i].sum(0) / np.linalg.norm(V[i].sum(0)) for i in faces['S']])
em = np.array([(V[i] + V[j]) / np.linalg.norm(V[i] + V[j]) for i in range(60) for j in range(i + 1, 60)
               if math.degrees(math.acos(np.clip(float(V[i] @ V[j]), -1, 1))) < 28.0])
cats['edge midpoints (C2)'] = em
cats['nodes'] = V
sym = np.vstack([cats['pentagon centres (C5)'], cats['triangle centres (C3)'], cats['edge midpoints (C2)']])
cats['31 I_h symmetry axes'] = sym
cats['62 face normals'] = np.vstack([cats['pentagon centres (C5)'], cats['triangle centres (C3)'], cats['square centres']])
RA = fib_sphere(200000)
dn = np.degrees(np.arccos(np.clip(np.abs(RA @ ax), -1, 1)))
res = {'axes': {nm: [float(lb_of(axes[nm])[0]), float(lb_of(axes[nm])[1])] for nm in axes},
       'axis_uncertainty': [float(np.median(dev)), float(np.percentile(dev, 68))],
       'fullsky': out_sky}
print('    %-24s %8s %10s %10s %8s' % ('catalogue', 'N', 'min angle', 'null mean', 'p'))
for nm, S in cats.items():
    d = float(np.degrees(np.arccos(np.clip(np.abs(S @ ax), -1, 1))).min())
    dn2 = np.degrees(np.arccos(np.clip(np.abs(S @ RA.T), -1, 1))).min(0)
    p = float((1 + int((dn2 <= d).sum())) / (1 + len(dn2)))
    print('    %-24s %8d %9.2f%s %9.2f%s %8.4f' % (nm, len(S), d, '', dn2.mean(), '', p))
    res['cat_' + nm] = [float(d), float(dn2.mean()), p]
# random-axis angle distribution reference
print('    (random axis: expected nearest-catalogue angle as tabulated; 5%% tail ~ %.2f deg)' % np.percentile(dn, 5))
res['rand_angle_5pct'] = float(np.percentile(dn, 5))
res['angle_to_AoE'] = float(ang(ax, AOE))
res['angle_axis_to_coldspot'] = float(ang(ax, V[0]))
print('    angle axis vs AoE literature axis (250,60) = %.2f deg' % ang(ax, AOE))
print('    angle axis vs cold spot node0 = %.2f deg' % ang(ax, V[0]))

json.dump(res, open(O150 + '/data/step05_axis_provenance.json', 'w'), indent=2)
print('\nOK saved: %s/data/step05_axis_provenance.json' % O150)
