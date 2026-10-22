#!/usr/bin/env python3
"""
O150 #09 - P3 definitive: is the node9/node20 contrast statistically anomalous?
================================================================================
Section 08 showed the RATIO |T9|/|T20| is unstable (T20 wanders near zero) and never
significant under a GRF.  Here we settle the question with ROBUST statistics:

A. GRF variance gate for the node-set sampling.
B. Analytic GRF covariance C_ij = sum (2l+1)C_l P_l(cos g_ij)/4pi
   -> individual z-scores of T9, T20 and of the difference T9 - T20.
C. Non-parametric ranks: where do |T9|, |T20|, |T9-T20| sit among the 60 nodes /
   among all 60x59 ordered pairs?
D. GRF null (seeded) for the difference and for the ratio.
E. Robust restatement of the "3.02x" claim.
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
T417 = np.array(json.load(open(G182 + '/temps2_SMICA_4.17deg.json'))['A5_60'][:60], float)

print('=' * 92)
print('  O150 #09 - P3 definitive: statistical status of the node9/node20 contrast')
print('=' * 92)

m = hp.ud_grade(hp.read_map(CACHE + '/smica2_smooth4.17.fits', field=0), NS) * 1e6
T = m[PIX]
print('\n[A] sampling gate (nside %d, 4.17 deg cache)' % NS)
print('    max|my T - temps2| = %.3f uK' % np.abs(T - T417).max())
print('    T9 = %+8.3f  T20 = %+8.3f  ratio = %.4f' % (T[9], T[20], abs(T[9] / T[20])))
print('    map std = %.2f uK' % m.std())

# ---------- B. analytic GRF covariance ----------
print('\n[B] analytic GRF covariance from the map own C_l')
cl = hp.anafast(m, lmax=3 * NS - 1)
ells = np.arange(len(cl))
gate = np.sum((2 * ells + 1) * cl / (4 * np.pi))
print('    GRF variance gate: sum(2l+1)C_l/4pi = %.3f uK^2 ; map var = %.3f uK^2' % (gate, m.var()))
LMAX = 3 * NS - 1
w = (2 * np.arange(LMAX + 1) + 1) / (4 * np.pi) * cl
# Legendre recurrence (scipy>=1.18 removed lpn):
# (l+1)P_{l+1} = (2l+1) x P_l - l P_{l-1}
C = np.zeros((60, 60))
Pm1 = np.ones_like(GAM)          # P_0
P0 = GAM.copy()                  # P_1
for L in range(1, LMAX):
    P1 = ((2 * L + 1) * GAM * P0 - L * Pm1) / (L + 1)   # P_{L+1}
    C += w[L + 1] * P1
    Pm1, P0 = P0, P1
C = 0.5 * (C + C.T)
sd = np.sqrt(np.diag(C))
print('    point std sqrt(C_ii) = %.3f uK (mean over nodes) ; observed T std = %.3f uK' % (sd.mean(), T.std()))
z9 = T[9] / sd[9]; z20 = T[20] / sd[20]
d = T[9] - T[20]
sd_d = math.sqrt(C[9, 9] + C[20, 20] - 2 * C[9, 20])
print('    corr(T9,T20) = C_9,20/sqrt(C99 C20,20) = %.4f' % (C[9, 20] / (sd[9] * sd[20])))
print('    z(T9)  = %+7.3f   z(T20) = %+7.3f   (standard normal under GRF)' % (z9, z20))
print('    T9 - T20 = %+8.3f uK ; sd(diff) = %.3f uK ; z(diff) = %+7.3f' % (d, sd_d, d / sd_d))
zz = np.array([T[i] / sd[i] for i in range(60)])
print('    all-node |z|: max = %.3f (node %d) ; node9 %.3f ; node20 %.3f' % (
    np.abs(zz).max(), int(np.argmax(np.abs(zz))), z9, z20))

# ---------- C. non-parametric ranks ----------
print('\n[C] non-parametric ranks')
print('    rank of |T9|  among the 60 nodes (1 = most extreme): %d' % (
    1 + int((np.abs(T) > abs(T[9])).sum())))
print('    rank of |T20| among the 60 nodes: %d' % (1 + int((np.abs(T) > abs(T[20])).sum())))
R = np.abs(T[:, None] - T[None, :])
off = ~np.eye(60, dtype=bool)
print('    rank of |T9-T20| = %.1f among all 60x59 ordered pairs: %d / %d (%.1f%%)' % (
    abs(d), 1 + int((R[off] > abs(d)).sum()), off.sum(), 100 * (1 + int((R[off] > abs(d)).sum())) / off.sum()))
print('    median |Ti-Tj| over all pairs = %.1f uK ; 95th pct = %.1f uK' % (
    np.median(R[off]), np.percentile(R[off], 95)))

# ---------- D. GRF null ----------
print('\n[D] GRF null (seeded) for the difference and the ratio')
# The 60 node values under a GRF are JOINTLY GAUSSIAN with covariance C (already includes the
# 4.17-deg beam).  Drawing directly from N(0, C) is exact and avoids 2000 full-map syntheses.
np.random.seed(15091)
NMC = 200000
SAMP = np.random.multivariate_normal(np.zeros(60), C, size=NMC)
D_ = np.abs(SAMP[:, 9] - SAMP[:, 20])
with np.errstate(divide='ignore', invalid='ignore'):
    RT = np.abs(SAMP[:, 9] / SAMP[:, 20])
RT = RT[np.isfinite(RT)]
Z9 = SAMP[:, 9] / sd[9]; Z20 = SAMP[:, 20] / sd[20]
print('    (analytic: 60-node GRF draws from N(0, C), %d samples - exact, no map synthesis)' % NMC)
print('    |T9-T20| : obs = %.1f uK ; GRF = %.1f +- %.1f ; p = %.4f' % (
    abs(d), D_.mean(), D_.std(), (1 + int((D_ >= abs(d)).sum())) / (1 + NMC)))
print('    |T9/T20| : obs = %.3f ; GRF median = %.3f (mean %.1f, huge tails) ; p = %.4f' % (
    abs(T[9] / T[20]), np.median(RT), RT.mean(),
    (1 + int((RT >= abs(T[9] / T[20])).sum())) / (1 + len(RT))))
print('    z(T9)  GRF: %.3f +- %.3f ; obs %+.3f  -> p = %.4f' % (
    Z9.mean(), Z9.std(), z9, (1 + int((np.abs(Z9) >= abs(z9)).sum())) / (1 + NMC)))
print('    z(T20) GRF: %.3f +- %.3f ; obs %+.3f  -> p = %.4f' % (
    Z20.mean(), Z20.std(), z20, (1 + int((np.abs(Z20) >= abs(z20)).sum())) / (1 + NMC)))
# how often does a GRF pair 43 deg apart reach ratio >= 3.02 ?
print('    P(GRF |ratio| >= 3.0216) = %.4f' % ((1 + int((RT >= 3.0216).sum())) / (1 + len(RT))))

# ---------- E. restatement ----------
print('\n[E] robust restatement')
print('    O143 framing: "|T9|/|T20| = 3.02 = 3x amplitude difference between automorphic nodes"')
print('    - the ratio is a fragile statistic: T20 is small (+35 uK vs field sd %.0f uK)' % sd[20])
print('    - the ratio swings 0.5 -> 6.8 -> 1.2 -> 5.1 as the l-cutoff moves (T20 crosses zero)')
print('    - under the physical GRF null the ratio is TYPICAL: p = %.3f' % (
    (1 + int((RT >= 3.0216).sum())) / (1 + len(RT))))
print('    robust equivalent: T9 - T20 = %.1f uK = %.2f sigma of the field-difference' % (abs(d), abs(d) / sd_d))
print('    rank of |T9-T20| among the 60x59 node pairs: %.1f%% (median pair difference = %.0f uK)' % (
    100 * (1 + int((R[off] > abs(d)).sum())) / off.sum(), np.median(R[off])))
print('    -> the contrast is a GENERIC two-point sky difference; no anomaly to explain.')

json.dump({'T9': float(T[9]), 'T20': float(T[20]), 'ratio': float(abs(T[9] / T[20])),
           'z9': float(z9), 'z20': float(z20), 'corr': float(C[9, 20] / (sd[9] * sd[20])),
           'diff': float(d), 'sd_diff': float(sd_d), 'z_diff': float(d / sd_d),
           'rank_absT9': int(1 + (np.abs(T) > abs(T[9])).sum()),
           'rank_absT20': int(1 + (np.abs(T) > abs(T[20])).sum()),
           'rank_pair_pct': float(100 * (1 + int((R[off] > abs(d)).sum())) / off.sum()),
           'p_diff': float((1 + int((D_ >= abs(d)).sum())) / (1 + NMC)),
           'p_ratio': float((1 + int((RT >= 3.0216).sum())) / (1 + len(RT))),
           'p_z9': float((1 + int((np.abs(Z9) >= abs(z9)).sum())) / (1 + NMC)),
           'p_z20': float((1 + int((np.abs(Z20) >= abs(z20)).sum())) / (1 + NMC)),
           'grf_ratio_median': float(np.median(RT)), 'grf_diff_mean': float(D_.mean()),
           'median_pair_diff': float(np.median(R[off])), 'point_sd': float(sd.mean()),
           'gate': [float(gate), float(m.var())]},
          open(O150 + '/data/step09_p3_definitive.json', 'w'), indent=2)
print('\nOK saved: %s/data/step09_p3_definitive.json' % O150)
