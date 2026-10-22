#!/usr/bin/env python3
"""
O150 #10 - P3 final verdict: order statistics + look-elsewhere correction
========================================================================
09 found z(T9) = -2.41 (p = 0.016) and |T9-T20| = 142.3 uK (p = 0.028), but the pair was
selected POST HOC.  Here we apply the look-elsewhere correction honestly:

A. Order statistics of |z| for 60 correlated nodes under the GRF: expected 1st..4th largest.
B. Distribution of max|Ti-Tj| over all 1770 unordered node pairs under the GRF.
C. Family-wise p-values for the observed values.
D. Final verdict table.
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
NS = 1024

raw = np.loadtxt(CS + '/a5_nodes.txt')
sc = SkyCoord(ra=raw[:, 0] * u.deg, dec=raw[:, 1] * u.deg, frame='icrs')
LB = np.column_stack([sc.galactic.l.deg, sc.galactic.b.deg])
PIX = hp.ang2pix(NS, LB[:, 0], LB[:, 1], lonlat=True)
l_ = np.radians(LB[:, 0]); b_ = np.radians(LB[:, 1])
V = np.column_stack([np.cos(b_) * np.cos(l_), np.cos(b_) * np.sin(l_), np.sin(b_)])
GAM = np.clip(V @ V.T, -1, 1)

print('=' * 92)
print('  O150 #10 - P3 final verdict: order statistics + look-elsewhere')
print('=' * 92)

m = hp.ud_grade(hp.read_map(CACHE + '/smica2_smooth4.17.fits', field=0), NS) * 1e6
T = m[PIX]
cl = hp.anafast(m, lmax=3 * NS - 1)
LMAX = 3 * NS - 1
w = (2 * np.arange(LMAX + 1) + 1) / (4 * np.pi) * cl
C = np.zeros((60, 60))
Pm1 = np.ones_like(GAM); P0 = GAM.copy()
for L in range(1, LMAX):
    P1 = ((2 * L + 1) * GAM * P0 - L * Pm1) / (L + 1)
    C += w[L + 1] * P1
    Pm1, P0 = P0, P1
C = 0.5 * (C + C.T)
sd = np.sqrt(np.diag(C))
zobs = T / sd
print('\n[A] order statistics of |z| (60 correlated nodes, GRF from the map own C_l)')
np.random.seed(15101)
NMC = 20000
S = np.random.multivariate_normal(np.zeros(60), C, size=NMC)
Z = S / sd[None, :]
AZ = np.abs(Z)
osamp = -np.sort(-AZ, axis=1)          # descending
print('    observed |z| descending: ' + ' '.join('%.2f' % v for v in np.sort(np.abs(zobs))[::-1][:6]))
print('    %-10s %10s %10s %10s' % ('order', 'GRF mean', 'GRF 95%', 'observed'))
res = {}
for k in range(1, 6):
    gm = osamp[:, k - 1].mean(); g95 = np.percentile(osamp[:, k - 1], 95)
    ob = np.sort(np.abs(zobs))[::-1][k - 1]
    print('    %-10d %10.3f %10.3f %10.3f' % (k, gm, g95, ob))
    res['order%d' % k] = [float(gm), float(g95), float(ob)]
# where does the 4th largest (node9) sit?
k = 4
p4 = (1 + int((osamp[:, k - 1] >= np.sort(np.abs(zobs))[::-1][k - 1]).sum())) / (1 + NMC)
print('    node9 is rank 4/60 with |z| = %.3f ; GRF P(4th largest >= that) = %.4f' % (
    np.sort(np.abs(zobs))[::-1][3], p4))
res['p_rank4'] = float(p4)

print('\n[B] max pairwise difference over all %d unordered node pairs (GRF)' % (60 * 59 // 2))
iu = np.triu_indices(60, 1)
Dg = np.abs(S[:, iu[0]] - S[:, iu[1]])
mx = Dg.max(1)
Dobs = np.abs(T[iu[0]] - T[iu[1]])
print('    observed max|Ti-Tj| = %.1f uK ; GRF mean = %.1f, 95%% = %.1f' % (
    Dobs.max(), mx.mean(), np.percentile(mx, 95)))
print('    observed |T9-T20| = %.1f uK ; GRF P(max pair diff >= that) = %.4f' % (
    abs(T[9] - T[20]), (1 + int((mx >= abs(T[9] - T[20])).sum())) / (1 + NMC)))
res['max_pair_obs'] = float(Dobs.max())
res['max_pair_grf'] = [float(mx.mean()), float(np.percentile(mx, 95))]
res['p_maxpair'] = float((1 + int((mx >= abs(T[9] - T[20])).sum())) / (1 + NMC))
# rank of the (9,20) difference among the pairs, and its look-elsewhere p
r = 1 + int((Dobs > abs(T[9] - T[20])).sum())
print('    |T9-T20| rank among %d unordered pairs: %d (%.2f%%)' % (len(Dobs), r, 100 * r / len(Dobs)))
res['pair_rank'] = int(r)

print('\n[C] family-wise correction summary')
print('    %-34s %10s %10s' % ('statement', 'raw p', 'look-elsewhere p'))
rows = [('|T9/T20| = 3.02 (O143 framing)', 0.2030, 0.2030),
        ('z(T9) = -2.41 (single node)', 0.0159, p4),
        ('|T9-T20| = 142.3 uK (selected pair)', 0.0279, float((1 + int((mx >= abs(T[9] - T[20])).sum())) / (1 + NMC)))]
for a, b, c in rows:
    print('    %-34s %10.4f %10.4f' % (a, b, c))
res['rows'] = rows

print('\n[D] verdict')
print('    - the RATIO 3.02 is NOT anomalous (p = 0.20) and is unstable in the l-cutoff')
print('    - the underlying content is node9 being a cold excursion: z = -2.41, rank 4/60')
print('    - the 4th-largest |z| out of 60 is expected to be ~%.2f (95%%: %.2f); observed %.2f' % (
    res['order4'][0], res['order4'][1], res['order4'][2]))
print('    - look-elsewhere corrected: p = %.3f  ->  NOT significant at any conventional threshold' % p4)
print('    - node20 is unremarkable (z = +0.80, rank 21/60)')
print('    => the node9/node20 contrast is a GENERIC sky realisation:')
print('       ~2.4 sigma single-node excursion, no look-elsewhere survival.')
print('       The O143 theorem (graph-invariant => T9 = T20) is a STRUCTURAL statement and')
print('       is untouched; but there is no ANOMALY here requiring a sky-side mechanism.')

json.dump(res, open(O150 + '/data/step10_p3_verdict.json', 'w'), indent=2)
print('\nOK saved: %s/data/step10_p3_verdict.json' % O150)
