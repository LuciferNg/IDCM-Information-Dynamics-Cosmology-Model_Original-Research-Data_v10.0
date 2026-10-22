#!/usr/bin/env python3
"""
O150 #03 - Audits + look-elsewhere-corrected axisymmetry + node anomaly map
==========================================================================
A. automorphism -> sphere isometry (Kabsch, det NOT forced; I_h contains improper ops)
B. POWER-SHARE AUDIT: ||Pi_l Tz||^2 (rotation-invariant, basis-free) vs Sigma coef^2
   -> is the "44.3% l=3" a real power share or a basis-conditioning artifact?
C. l=3 axisymmetry with LOOK-ELSEWHERE-CORRECTED null (each null field picks its own axis)
D. node9/node20 detail + LOO z-score of every node (which nodes are sky outliers?)
E. where does the fitted l=3 field peak?  (relation to cold spot / structure)
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
rng = np.random.default_rng(1502)

raw = np.loadtxt(CS + '/a5_nodes.txt')
sc = SkyCoord(ra=raw[:, 0] * u.deg, dec=raw[:, 1] * u.deg, frame='icrs')
LB = np.column_stack([sc.galactic.l.deg, sc.galactic.b.deg])


def uvec(lb):
    l = np.radians(lb[:, 0]); b = np.radians(lb[:, 1])
    return np.column_stack([np.cos(b) * np.cos(l), np.cos(b) * np.sin(l), np.sin(b)])


V = uvec(LB)
J = json.load(open(G182 + '/temps2_SMICA_4.17deg.json'))
T = np.array(J['A5_60'][:60], float)
Tz = T - T.mean()


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


print('=' * 88)
print('  O150 #03 - audits + look-elsewhere-corrected axisymmetry + node anomaly map')
print('=' * 88)
LS = [1, 2, 3, 4, 5, 6]

# ---------- A. automorphism isometry ----------
print('\n[A] automorphism -> sphere isometry (Kabsch, det free)')
import networkx as nx
edges = [(i, j) for i in range(60) for j in range(i + 1, 60)
         if math.degrees(math.acos(np.clip(float(V[i] @ V[j]), -1, 1))) < 28.0]
Gn = nx.Graph(); Gn.add_nodes_from(range(60)); Gn.add_edges_from(edges)
gmap = None
for iso in nx.algorithms.isomorphism.GraphMatcher(Gn, Gn).isomorphisms_iter():
    if iso.get(9) == 20:
        gmap = iso; break
perm = np.array([gmap[i] for i in range(60)])
U, S, Vt = np.linalg.svd(V[perm].T @ V)
Rg = U @ Vt
res = float(np.abs(V[perm] - V @ Rg.T).max())
print('    g: 9 -> 20, fixed points %d ; isometry residual = %.3e ; det(R_g) = %+.6f' % (
    int((perm == np.arange(60)).sum()), res, np.linalg.det(Rg)))
print('    -> det = -1 means g is an IMPROPER isometry (I_h = I x Z2 contains inversion).')
print('    -> the node set IS I_h-symmetric, so any Aut(G) element acts as an isometry of S^2.')
# improper case: -g (antipodal map) is proper; check that too
if np.linalg.det(Rg) < 0:
    Rg2 = -Rg
    res2 = float(np.abs(V[perm] + V @ Rg2.T).max())
    print('    improper g = inversion x proper isometry; check |V[g] + V R_g^T| = %.3e' % res2)

# ---------- B. power-share audit ----------
print('\n[B] POWER-SHARE AUDIT')
print('    ||Tz||^2 = %.1f uK^2   (field variance x 60)' % (Tz @ Tz))
print('     l    ||Pi_l Tz||^2   share   Sigma coef^2   share   inflation')
tot_p = 0.0; tot_c = 0.0
Pp = {}; Cc = {}
for l in LS:
    B = basis(l, V)
    c = np.linalg.lstsq(B, Tz, rcond=None)[0]
    p = float(((B @ c) @ (B @ c)))
    cc = float((c ** 2).sum())
    Pp[l] = p; Cc[l] = cc; tot_p += p; tot_c += cc
for l in LS:
    print('    %2d  %12.1f  %6.1f%%  %12.1f  %6.1f%%   %6.3f' % (
        l, Pp[l], 100 * Pp[l] / (Tz @ Tz), Cc[l], 100 * Cc[l] / tot_c, Cc[l] / Pp[l]))
print('    sum l=1..6: ||Pi||^2 = %.1f (%.1f%% of ||Tz||^2) ; Sigma coef^2 = %.1f' % (
    tot_p, 100 * tot_p / (Tz @ Tz), tot_c))
# orthonormality check of the l=3 basis on the nodes
B3 = basis(3, V)
G3 = B3.T @ B3
print('    l=3 Gram on nodes: (4pi/60)*G3 = I + delta,  ||delta||_max = %.4f' % (
    float(np.abs((4 * math.pi / 60) * G3 - np.eye(7)).max())))
print('    -> ||Pi_l Tz||^2 is the rotation-invariant, basis-free l-power.')
print('    -> Sigma coef^2 is NOT a power: it is b^T G^-2 b (basis/conditioning dependent).')

# ---------- C. axisymmetry, look-elsewhere corrected ----------
print('\n[C] l=3 axisymmetry (look-elsewhere corrected)')
AXG = fib_sphere(200000)
B3g = basis(3, AXG)                      # Y_3m evaluated on the direction grid


def F_on_grid(a3):
    return B3g @ a3


a3 = np.linalg.lstsq(B3, Tz, rcond=None)[0]
Fg = F_on_grid(a3)
i = int(np.argmax(np.abs(Fg)))
amp = float(np.abs(Fg)[i])
frac = (4 * math.pi / 7) * amp ** 2 / float((a3 ** 2).sum())
axmax = AXG[i]
print('    fitted l=3 field F(n) = sum a3m Y3m(n)')
print('    max|F| = %.3f uK at (%.2f, %.2f)' % (
    amp, math.degrees(math.atan2(axmax[1], axmax[0])) % 360, math.degrees(math.asin(axmax[2]))))
print('    m=0 power fraction about that axis = (4pi/7)max|F|^2/Sigma|a3m|^2 = %.4f' % frac)
print('    (continuous/SO(3) formula; matches the discrete lstsq frame value)')
# null with each field choosing its OWN best axis (chunked to bound memory)
NMC = 4000
fracn = np.empty(NMC)
CH = 100
for s in range(0, NMC, CH):
    Ab = rng.normal(size=(7, CH))
    Ab /= np.linalg.norm(Ab, axis=0)
    FGb = B3g @ Ab                       # 200000 x CH
    fracn[s:s + CH] = (4 * math.pi / 7) * (np.abs(FGb).max(0)) ** 2
p_ax = (1 + int((fracn >= frac).sum())) / (1 + NMC)
print('    null (random l=3, own best axis, %d MC x %d dirs): frac = %.4f +- %.4f, max = %.4f' % (
    NMC, AXG.shape[0], fracn.mean(), fracn.std(), fracn.max()))
print('    p = %.5f   -> %s' % (p_ax, 'AXISYMMETRIC (significant)' if p_ax < 0.01 else 'not significant'))

# ---------- D. node anomaly map ----------
print('\n[D] node9 / node20 detail + LOO z-score of every node')
for nd in [0, 9, 20]:
    print('    node%-3d (l,b) = (%8.3f, %+7.3f)   T = %+9.3f uK   |b| = %.2f deg' % (
        nd, LB[nd, 0], LB[nd, 1], T[nd], abs(LB[nd, 1])))
for nd in [9, 20]:
    d = math.degrees(math.acos(np.clip(float(V[nd] @ axmax), -1, 1)))
    print('    node%-3d colatitude from l=3 axis = %.2f deg ; P3(cos) = %+.4f' % (
        nd, d, (5 * math.cos(math.radians(d)) ** 3 - 3 * math.cos(math.radians(d))) / 2))
B6 = np.column_stack([basis(l, V) for l in range(1, 7)])
z = np.empty(60)
for i2 in range(60):
    keep = np.ones(60, bool); keep[i2] = False
    c = np.linalg.lstsq(B6[keep], Tz[keep], rcond=None)[0]
    r = Tz[keep] - B6[keep] @ c
    s2 = (r ** 2).sum() / (keep.sum() - B6.shape[1])
    v = B6[i2] @ np.linalg.pinv(B6[keep].T @ B6[keep]) @ B6[i2].T
    z[i2] = (Tz[i2] - B6[i2] @ c) / math.sqrt(max(s2 * v, 1e-12))
order = np.argsort(-np.abs(z))
print('    top-8 |LOO z| (model l<=6 on 58 nodes, held out):')
for i2 in order[:8]:
    print('      node%-3d z = %+6.2f   T = %+9.3f   (l,b) = (%7.2f, %+6.2f)  k=%d' % (
        i2, z[i2], T[i2], LB[i2, 0], LB[i2, 1], 0))
print('    node9 z = %+.2f ; node20 z = %+.2f ; max|z| over 60 = %.2f' % (
    z[9], z[20], np.abs(z).max()))

# ---------- E. l=3 field peak vs structure ----------
print('\n[E] where does the fitted l=3 field peak?')
pk = np.abs(Fg)
top = np.argsort(-pk)[:5]
for j in top:
    a = AXG[j]
    lb = (math.degrees(math.atan2(a[1], a[0])) % 360, math.degrees(math.asin(a[2])))
    dc = math.degrees(math.acos(np.clip(float(a @ V[0]), -1, 1)))
    print('    F = %+8.3f uK at (%.2f, %+.2f)   angle to cold spot = %.2f deg' % (Fg[j], lb[0], lb[1], dc))
print('    axis vs cold spot = %.2f deg ; axis |b| = %.2f deg' % (
    math.degrees(math.acos(np.clip(abs(float(axmax @ V[0])), -1, 1))), abs(math.degrees(math.asin(axmax[2])))))

res = {'aut_residual': res, 'aut_det': float(np.linalg.det(Rg)),
       'power_Pi': {str(l): Pp[l] for l in LS}, 'power_coef': {str(l): Cc[l] for l in LS},
       'Tz2': float(Tz @ Tz), 'Pi_total_share': float(tot_p / (Tz @ Tz)),
       'l3_axisym_frac': float(frac), 'l3_axisym_p': float(p_ax),
       'l3_axisym_null': [float(fracn.mean()), float(fracn.std())],
       'l3_peak': [float(math.degrees(math.atan2(axmax[1], axmax[0])) % 360), float(math.degrees(math.asin(axmax[2])))],
       'loo_z': z.tolist(), 'node9_lb': [float(LB[9, 0]), float(LB[9, 1])], 'node20_lb': [float(LB[20, 0]), float(LB[20, 1])]}
json.dump(res, open(O150 + '/data/step03_audit.json', 'w'), indent=2)
print('\nOK saved: %s/data/step03_audit.json' % O150)
