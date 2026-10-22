#!/usr/bin/env python3
"""
O150 #08 - P3: quantifying the LOCALITY of the breaking input
=============================================================
The breaking T9/T20 = 3.02 is carried by l>=4 (98.6%).  P3 asks: at which SCALE
does it live, and is the input genuinely local?

A. Load raw SMICA I, verify ordering/units against the verified 4.17-deg cache.
B. Multiscale contrast: |T9|/|T20| vs smoothing FWHM (4 pipelines) + all-pairs percentile.
C. Harmonic low-pass: ratio(lmax) - the cumulative scale at which the contrast builds.
D. Difference-of-Gaussians: D_node(sigma) - the feature's own scale.
E. Local excision: mask a disc around node9 / node20 -> how local is the support?
F. Radial profiles at node9 / node20 / node0 / random controls.
G. GRF null (seeded) for the lmax-cutoff ratio.
"""
import numpy as np, math, json, os
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
ROOT = BASE + '/open_problems_fresh'
O150 = ROOT + '/o150_sky_side_projection'
CS = ROOT + '/cmb_cold_spot/data'
G182 = ROOT + '/o182_88grid_geometry/data'
CACHE = ROOT + '/o5_catalog_compare/data/smooth_cache'
RAW = ROOT + '/o26_node57_region/data/smica_iqu_2048.fits'
NS = 1024

raw = np.loadtxt(CS + '/a5_nodes.txt')
sc = SkyCoord(ra=raw[:, 0] * u.deg, dec=raw[:, 1] * u.deg, frame='icrs')
LB = np.column_stack([sc.galactic.l.deg, sc.galactic.b.deg])
PIX = hp.ang2pix(NS, LB[:, 0], LB[:, 1], lonlat=True)
T417 = np.array(json.load(open(G182 + '/temps2_SMICA_4.17deg.json'))['A5_60'][:60], float)

print('=' * 92)
print('  O150 #08 - P3: locality of the breaking input')
print('=' * 92)
VEC = hp.pix2vec(NS, np.arange(hp.nside2npix(NS)))   # precomputed once

# ---------- A. load + verify ----------
print('\n[A] raw SMICA I load + verification')
m = hp.read_map(RAW, field=0)
ref = hp.read_map(CACHE + '/smica2_smooth4.17.fits', field=0)
sel = np.arange(0, len(m), 3000)
c0 = np.corrcoef(m[sel], ref[sel])[0, 1]
c1 = np.corrcoef(hp.reorder(m, n2r=True)[sel], ref[sel])[0, 1]
print('    ordering check vs verified RING cache: corr(raw) = %.5f ; corr(n2r) = %.5f' % (c0, c1))
if c1 > c0:
    m = hp.reorder(m, n2r=True)
    print('    -> reordered to RING (header said NESTED but data behaved as NESTED)')
else:
    print('    -> header ORDERING=NESTED but data is ALREADY RING; no reorder')
print('    TUNIT1 = K_CMB -> map values are Kelvin; x1e6 for uK')
m = hp.ud_grade(m, NS) * 1e6
ms = hp.smoothing(m, fwhm=math.radians(4.17), lmax=3 * NS - 1)
d = np.abs(ms[PIX] - T417).max()
print('    verification: my nside-%d 4.17deg sampling vs temps2 (nside2048) max|d| = %.3f uK' % (NS, d))

# ---------- B. multiscale ----------
print('\n[B] multiscale contrast |T9|/|T20| vs smoothing FWHM')
FW = [1.0, 2.0, 3.0, 4.17, 5.0, 7.0, 10.0, 15.0, 20.0, 30.0, 40.0]
res = {'fwhm': FW, 'ratio': {}, 'T9': {}, 'T20': {}}
print('    %-8s %9s %9s %8s   %s' % ('FWHM', 'T9', 'T20', 'ratio', 'percentile of |ratio| among all 60x59 pairs'))
for f in FW:
    mm = hp.smoothing(m, fwhm=math.radians(f), lmax=min(3 * NS - 1, int(3 * 180 / f) + 60))
    Tv = mm[PIX]
    r = abs(Tv[9] / Tv[20])
    R = np.abs(Tv[:, None] / Tv[None, :])
    off = ~np.eye(60, dtype=bool)
    pct = 100 * float((R[off] <= r).mean())
    res['ratio'][str(f)] = float(r); res['T9'][str(f)] = float(Tv[9]); res['T20'][str(f)] = float(Tv[20])
    print('    %-8.2f %9.2f %9.2f %8.3f   %.1f%%' % (f, Tv[9], Tv[20], r, pct))
print('    (ratio -> 1 as smoothing kills the small-scale content that carries the contrast)')

# ---------- C. harmonic low-pass ----------
print('\n[C] harmonic low-pass: cumulative contrast ratio(lmax)')
alm = hp.map2alm(m, lmax=64)
res['lmax'] = []
print('    %-6s %9s %9s %8s   %s' % ('lmax', 'T9', 'T20', 'ratio', 'note'))
prev = None
for L in [1, 2, 3, 4, 5, 6, 8, 10, 15, 20, 30, 64]:
    fl = np.zeros(64 + 1); fl[0:L + 1] = 1.0
    if L == 1:
        fl[0] = 0.0
    a = hp.almxfl(alm, fl)
    mp = hp.alm2map(a, nside=NS)
    Tv = mp[PIX]
    r = abs(Tv[9] / Tv[20]) if abs(Tv[20]) > 1e-9 else float('nan')
    note = ''
    if prev is not None and abs(r - prev) > 0.3:
        note = '<== contrast builds here'
    print('    %-6d %9.2f %9.2f %8.3f   %s' % (L, Tv[9], Tv[20], r, note))
    res['lmax'].append([L, float(Tv[9]), float(Tv[20]), float(r)])
    prev = r

# ---------- D. difference of Gaussians ----------
print('\n[D] difference-of-Gaussians D(sigma) = T(sigma) - T(sigma*sqrt2)  [uK]')
res['dog'] = {}
print('    %-10s %9s %9s %9s' % ('sigma(deg)', 'node9', 'node20', 'node0'))
for s in [0.5, 1.0, 1.5, 2.0, 3.0, 4.17, 6.0, 8.0, 12.0]:
    a1 = hp.smoothing(m, fwhm=math.radians(s), lmax=min(3 * NS - 1, int(3 * 180 / s) + 60))
    a2 = hp.smoothing(m, fwhm=math.radians(s * math.sqrt(2)), lmax=min(3 * NS - 1, int(3 * 180 / (s * 1.414)) + 60))
    D = a1[PIX] - a2[PIX]
    res['dog'][str(s)] = [float(D[9]), float(D[20]), float(D[0])]
    print('    %-10.2f %9.3f %9.3f %9.3f' % (s, D[9], D[20], D[0]))

# ---------- E. local excision ----------
print('\n[E] local excision: mask a disc around the node, re-sample, re-contrast')
res['excision'] = {}
for target, lab in [(9, 'node9'), (20, 'node20')]:
    print('    -- excising around %s (FWHM 4.17 deg) --' % lab)
    v0 = LB[target]
    for rr in [0.0, 0.5, 1.0, 2.0, 3.0, 5.0, 8.0]:
        if rr == 0:
            mv = hp.smoothing(m, fwhm=math.radians(4.17), lmax=3 * NS - 1)
        else:
            cvec = hp.ang2vec(v0[0], v0[1], lonlat=True)
            ang = np.degrees(np.arccos(np.clip(VEC[0] * cvec[0] + VEC[1] * cvec[1] + VEC[2] * cvec[2], -1, 1)))
            disc = ang < rr
            w = (~disc).astype(float)
            sw = hp.smoothing(w, fwhm=math.radians(4.17), lmax=3 * NS - 1)
            smw = hp.smoothing(np.where(disc, 0.0, m), fwhm=math.radians(4.17), lmax=3 * NS - 1)
            mv = smw / np.clip(sw, 1e-6, None)
        Tv = mv[PIX]
        r = abs(Tv[9] / Tv[20])
        print('       excise r<%.1f deg : T9 = %+8.2f  T20 = %+8.2f  ratio = %.3f' % (rr, Tv[9], Tv[20], r))
        res['excision']['%s_%.1f' % (lab, rr)] = [float(Tv[9]), float(Tv[20]), float(r)]

# ---------- F. radial profiles ----------
print('\n[F] radial profiles (raw nside-%d map, uK): mean/min in annuli' % NS)
res['profile'] = {}
for nd in [9, 20, 0]:
    cv = hp.ang2vec(LB[nd, 0], LB[nd, 1], lonlat=True)
    ang = np.degrees(np.arccos(np.clip(VEC[0] * cv[0] + VEC[1] * cv[1] + VEC[2] * cv[2], -1, 1)))
    row = []
    for lo, hi in [(0, 1), (1, 2), (2, 3), (3, 5), (5, 8), (8, 12), (12, 20)]:
        s = (ang >= lo) & (ang < hi)
        row.append((lo, hi, float(m[s].mean()), float(m[s].min())))
    res['profile']['node%d' % nd] = row
    print('    node%-3d ' % nd + ' '.join('[%g-%g] %.0f/%.0f' % (a, b, c, d) for a, b, c, d in row))

# ---------- G. GRF null ----------
print('\n[G] GRF null (seeded) for the low-pass contrast')
cl = hp.anafast(m, lmax=64)
np.random.seed(15081)
NMC = 400
print('    %-6s %8s %10s %10s' % ('lmax', 'obs', 'GRF mean', 'p'))
res['grf'] = {}
for L in [3, 6, 10, 20, 64]:
    fl = np.zeros(65); fl[2:L + 1] = 1.0
    clin = cl * fl
    rr = np.empty(NMC)
    for i in range(NMC):
        mp = hp.alm2map(hp.synalm(clin, lmax=64), nside=NS)
        Tv = mp[PIX]
        rr[i] = abs(Tv[9] / Tv[20])
    Tob = hp.alm2map(hp.almxfl(alm, fl), nside=NS)[PIX]
    obs = abs(Tob[9] / Tob[20])
    p = (1 + int((rr >= obs).sum())) / (1 + NMC)
    print('    %-6d %8.3f %10.3f %10.4f' % (L, obs, rr.mean(), p))
    res['grf'][str(L)] = [float(obs), float(rr.mean()), float(rr.std()), float(p)]

json.dump(res, open(O150 + '/data/step08_p3_locality.json', 'w'), indent=2)
print('\nOK saved: %s/data/step08_p3_locality.json' % O150)
