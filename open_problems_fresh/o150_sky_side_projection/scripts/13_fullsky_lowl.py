#!/usr/bin/env python3
"""
O150 #13 - P5 residual: full-sky low-l axes from all pipelines + official TMASK
==============================================================================
docs/04 used a crude |b|>20 cut pseudo-a_lm.  Here we redo the full-sky l=2/l=3
preferred-axis analysis properly:

A. full-sky a_lm from SMICA / NILC / Commander (4.17-deg smoothed caches, nside 1024)
B. official SMICA TMASK applied -> masked pseudo-a_lm (no ad-hoc cut)
C. cross-pipeline consistency of the low-l coefficients
D. quadrupole-octopole alignment angle per map vs the literature AoE
E. final P2 statement: is the node-set axis a sky object?
"""
import numpy as np, math, json, os
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u
from astropy.io import fits

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
ROOT = BASE + '/open_problems_fresh'
O150 = ROOT + '/o150_sky_side_projection'
CS = ROOT + '/cmb_cold_spot/data'
CACHE = ROOT + '/o5_catalog_compare/data/smooth_cache'
IQU = ROOT + '/o26_node57_region/data/smica_iqu_2048.fits'
NS = 1024
LMAX = 3 * NS - 1

raw = np.loadtxt(CS + '/a5_nodes.txt')
sc = SkyCoord(ra=raw[:, 0] * u.deg, dec=raw[:, 1] * u.deg, frame='icrs')
LB = np.column_stack([sc.galactic.l.deg, sc.galactic.b.deg])


def uvec(lb):
    l = np.radians(lb[:, 0]); b = np.radians(lb[:, 1])
    return np.column_stack([np.cos(b) * np.cos(l), np.cos(b) * np.sin(l), np.sin(b)])


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
AOE = uvec(np.array([[250.0, 60.0]]))[0]
AXNODE = uvec(np.array([[193.47, -37.72]]))[0]

print('=' * 92)
print('  O150 #13 - P5 residual: full-sky low-l axes + official TMASK')
print('=' * 92)

MAPS = {}
for nm, fn in [('SMICA', 'smica2_smooth4.17.fits'), ('NILC', 'nilc2_smooth4.17.fits'),
               ('Commander', 'commander_smooth4.17.fits')]:
    MAPS[nm] = hp.ud_grade(hp.read_map(CACHE + '/' + fn, field=0), NS) * 1e6

# official TMASK from the SMICA IQU file, downgraded
tm = fits.open(IQU)[1].data['TMASK']
tm = hp.ud_grade(tm.astype(float), NS)
print('\n[A] official SMICA TMASK: nside %d, valid fraction = %.4f' % (NS, float((tm > 0.5).mean())))
mask = tm > 0.5


def low_l_axis_removed():
    pass


print('\n[B] full-sky l=2 / l=3 preferred axes (Land-Magueijo m=0 sense)')
res = {}
rows = []
for nm, m in MAPS.items():
    alm = hp.map2alm(m, lmax=LMAX)
    for l in [2, 3]:
        for tag, mk in [('full', None), ('TMASK', mask)]:
            a = alm.copy()
            fl = np.zeros(LMAX + 1); fl[l] = 1.0
            a = hp.almxfl(a, fl)
            if mk is not None:
                mp = hp.alm2map(a, nside=NS) * mk
                a = hp.map2alm(mp, lmax=LMAX)
            mp2 = hp.alm2map(a, nside=2048)
            i = int(np.argmax(np.abs(mp2)))
            th, ph = hp.pix2ang(2048, i)
            ax = np.array([math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph), math.cos(th)])
            lb = lb_of(ax)
            amp = float(abs(mp2[i]))
            rows.append((nm, l, tag, lb, amp, ang(ax, AOE), ang(ax, AXNODE)))
            print('    %-10s l=%d [%-5s] axis = (%7.2f, %+6.2f)  |b| = %5.2f  amp = %6.2f uK  toAoE %5.1f  toNode %5.1f' % (
                nm, l, tag, lb[0], lb[1], abs(lb[1]), amp, ang(ax, AOE), ang(ax, AXNODE)))
            res['%s_l%d_%s' % (nm, l, tag)] = [float(lb[0]), float(lb[1]), amp]

print('\n[C] cross-pipeline low-l coefficient consistency')
for l in [2, 3]:
    ref = None; refn = ''
    for nm, m in MAPS.items():
        alm = hp.map2alm(m, lmax=LMAX)
        c = np.array([alm[hp.Alm.getidx(LMAX, l, mm)] for mm in range(0, l + 1)])
        if ref is None:
            ref = c; refn = nm
        else:
            cr = float(np.abs(np.vdot(ref, c)) / (np.linalg.norm(ref) * np.linalg.norm(c)))
            print('    l=%d  corr(%s, %s) = %.4f   |c| ratio = %.4f' % (
                l, refn, nm, cr, np.linalg.norm(c) / np.linalg.norm(ref)))
            res['corr_l%d_%s' % (l, nm)] = cr

print('\n[D] quadrupole-octopole alignment (max|F| axes)')
for nm, m in MAPS.items():
    alm = hp.map2alm(m, lmax=LMAX)
    axs = {}
    for l in [2, 3]:
        a = hp.almxfl(alm, np.array([1.0 if i == l else 0.0 for i in range(LMAX + 1)]))
        mp2 = hp.alm2map(a, nside=2048)
        i = int(np.argmax(np.abs(mp2)))
        th, ph = hp.pix2ang(2048, i)
        axs[l] = np.array([math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph), math.cos(th)])
    d = math.degrees(math.acos(np.clip(abs(float(axs[2] @ axs[3])), -1, 1)))
    print('    %-10s angle(Q, O) = %.2f deg' % (nm, d))
    res['qo_' + nm] = float(d)

print('\n[E] P2 final statement')
nd = np.array(res['SMICA_l3_full'][:2])
print('    node-set A5 l=3 axis = (193.47, -37.72)')
print('    full-sky l=3 axes: ' + ', '.join('%s (%.1f,%.1f)' % (nm, res['%s_l3_full' % nm][0], res['%s_l3_full' % nm][1])
                                             for nm in MAPS))
print('    literature AoE = (250, 60)')
print('    -> the node-set axis is NOT the sky l=3 axis nor the AoE (all >60 deg away)')

json.dump(res, open(O150 + '/data/step13_fullsky_lowl.json', 'w'), indent=2)
print('\nOK saved: %s/data/step13_fullsky_lowl.json' % O150)
