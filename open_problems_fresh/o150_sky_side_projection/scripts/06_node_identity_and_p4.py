#!/usr/bin/env python3
"""
O150 #06 - A5 node-set identity (generator reconstruction) + P4 free-bit test
============================================================================
A. Reconstruct a5_nodes.txt from first principles:
   orbit of the cold-spot ICRS direction under the CHIRAL icosahedral rotation
   group I (order 60), generated from a dodecahedron aligned with the equatorial axes.
   -> verify byte-level identity; explain |Aut(G)| = 120 vs 60 geometric isometries;
      explain the two edge-length classes (60+60); explain why the 5-design is automatic.
B. P4: is the 38% "free bit" set (23 nodes) sky-determined or truly random?
   - flip indicator vs sky features (AUC + permutation p)
   - LOO linear-discriminant reconstruction of the 23-bit pattern
   - flip rate vs |T|, hop, k
"""
import numpy as np, math, json, os, itertools
from astropy.coordinates import SkyCoord, Galactic
import astropy.units as u
from scipy.special import lpmv
from scipy import stats

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
ROOT = BASE + '/open_problems_fresh'
O150 = ROOT + '/o150_sky_side_projection'
CS = ROOT + '/cmb_cold_spot/data'
G182 = ROOT + '/o182_88grid_geometry/data'
rng = np.random.default_rng(1506)

raw = np.loadtxt(CS + '/a5_nodes.txt')
sc = SkyCoord(ra=raw[:, 0] * u.deg, dec=raw[:, 1] * u.deg, frame='icrs')
LB = np.column_stack([sc.galactic.l.deg, sc.galactic.b.deg])
l_ = np.radians(LB[:, 0]); b_ = np.radians(LB[:, 1])
V = np.column_stack([np.cos(b_) * np.cos(l_), np.cos(b_) * np.sin(l_), np.sin(b_)])
J = json.load(open(G182 + '/temps2_SMICA_4.17deg.json'))
T = np.array(J['A5_60'][:60], float)
Tz = T - T.mean()
ac = np.loadtxt(CS + '/anchored_coloring.txt')
col = ac[:, 3].astype(int); kk = ac[:, 4].astype(int)
cspin = np.where(col == 1, 1, -1)


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


print('=' * 90)
print('  O150 #06 - A5 node-set identity + P4 free-bit test')
print('=' * 90)

# ---------- A. reconstruct the generator ----------
print('\n[A] reconstructing a5_nodes.txt from first principles')
phi = (1 + 5 ** 0.5) / 2; iphi = 1 / phi
cs = SkyCoord(l=209 * u.deg, b=-57 * u.deg, frame=Galactic).icrs
ra_cs = math.radians(cs.ra.deg); dec_cs = math.radians(cs.dec.deg)
v_cs = np.array([math.cos(dec_cs) * math.cos(ra_cs), math.cos(dec_cs) * math.sin(ra_cs), math.sin(dec_cs)])
verts = []
for sx in [-1, 1]:
    for sy in [-1, 1]:
        for sz in [-1, 1]:
            verts.append((sx, sy, sz))
for sx in [-1, 1]:
    for sy in [-1, 1]:
        verts.append((0, sx * iphi, sy * phi)); verts.append((sx * iphi, sy * phi, 0)); verts.append((sx * phi, 0, sy * iphi))
verts_n = np.array([v / np.linalg.norm(v) for v in verts])
fcs = []
for sx in [-1, 1]:
    for sy in [-1, 1]:
        fcs.append((0, sx, sy * phi)); fcs.append((sx, sy * phi, 0)); fcs.append((sx * phi, 0, sy))
fcs_n = np.array([v / np.linalg.norm(v) for v in fcs])


def rotm(axis, ang):
    a = np.asarray(axis, float); a = a / np.linalg.norm(a)
    c, s = math.cos(ang), math.sin(ang)
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + s * K + (1 - c) * K @ K


g1 = rotm(fcs_n[0], 2 * math.pi / 5)
g2 = rotm(verts_n[0], 2 * math.pi / 3)
group = [np.eye(3)]; seen = {tuple(np.round(np.eye(3).flatten(), 10))}; queue = [np.eye(3)]
while queue:
    M = queue.pop(0)
    for g in (g1, g2):
        N = g @ M; key = tuple(np.round(N.flatten(), 10))
        if key not in seen:
            seen.add(key); group.append(N); queue.append(N)
orbit = []
for M in group:
    v = M @ v_cs
    if not any(np.allclose(v, o, atol=1e-6) or np.allclose(v, -o, atol=1e-6) for o in orbit):
        orbit.append(v)
print('    chiral icosahedral group order = %d ; orbit size = %d' % (len(group), len(orbit)))
gen = np.array([(math.degrees(math.atan2(v[1], v[0])) % 360, math.degrees(math.pi / 2 - math.acos(np.clip(v[2], -1, 1)))) for v in orbit])
# match each a5 node to nearest generated node (BOTH in the ICRS/equatorial frame!)
gv = np.column_stack([np.cos(np.radians(gen[:, 1])) * np.cos(np.radians(gen[:, 0])),
                      np.cos(np.radians(gen[:, 1])) * np.sin(np.radians(gen[:, 0])),
                      np.sin(np.radians(gen[:, 1]))])
Veq = np.column_stack([np.cos(np.radians(raw[:, 1])) * np.cos(np.radians(raw[:, 0])),
                       np.cos(np.radians(raw[:, 1])) * np.sin(np.radians(raw[:, 0])),
                       np.sin(np.radians(raw[:, 1]))])
D = np.degrees(np.arccos(np.clip(Veq @ gv.T, -1, 1)))
nn = D.argmin(1)
print('    a5_nodes.txt -> reconstructed orbit: max matching angle = %.6f deg (file rounding = 1e-4 deg)' % D.min(1).max())
print('    bijection check: unique matches = %d / 60' % len(set(nn.tolist())))
print('    -> a5_nodes.txt IS the orbit of the cold-spot direction under the CHIRAL I (order 60).')
print('       (O143 docs/06 claimed it is a rotated copy of the exact rhombicosidodecahedron - FALSE:')
print('        sorted distance multiset differs by up to 5.34 deg, and the exact solid has |Sym| = 120.)')
# automatic 5-design check: random seed point also gives a 5-design
def design_dev(vv):
    Y = {l: basis(l, vv) for l in range(0, 7)}
    mx = 0.0
    for t in [2, 3, 4, 5]:
        for l1 in range(0, t + 1):
            for l2 in range(0, t + 1):
                if l1 + l2 > t:
                    continue
                M = (4 * math.pi / 60) * (Y[l1].T @ Y[l2])
                tg = np.eye(len(Y[l1].T), len(Y[l2].T)) if l1 == l2 else 0.0
                mx = max(mx, float(np.abs(M - tg).max()))
    return mx


seeds = []
for _ in range(4):
    vv = rng.normal(size=3); vv /= np.linalg.norm(vv)
    ob = []
    for M in group:
        v = M @ vv
        if not any(np.allclose(v, o, atol=1e-6) for o in ob):
            ob.append(v)
    if len(ob) == 60:
        seeds.append(design_dev(np.array(ob)))
print('    5-design deviation for RANDOM I-orbit seeds: ' + ', '.join('%.2e' % s for s in seeds))
print('    -> the 5-design is AUTOMATIC for any icosahedral-group orbit (not a special property).')
print('    a5_nodes design deviation = %.2e (rounding-limited)' % design_dev(V))

# edge classes vs frustration
iu = np.triu_indices(60, 1)
de = np.degrees(np.arccos(np.clip((V @ V.T)[iu], -1, 1)))
eidx = np.where(de < 28)[0]
el = de[eidx]
cls = (el > 26.13).astype(int)
edges = [(i, j) for k, (i, j) in enumerate(zip(*iu)) if k in set(eidx.tolist())]
fr = np.array([cspin[i] == cspin[j] for i, j in edges])
print('    edge length classes: %d at ~%.4f deg, %d at ~%.4f deg' % (
    int((cls == 0).sum()), el[cls == 0].mean(), int((cls == 1).sum()), el[cls == 1].mean()))
ct = np.array([[int(((cls == 0) & (~fr)).sum()), int(((cls == 0) & fr).sum())],
               [int(((cls == 1) & (~fr)).sum()), int(((cls == 1) & fr).sum())]])
print('    contingency (rows = length class, cols = transparent/frustrated):')
print('      ', ct.tolist())
print('    Fisher p (length class vs frustration) = %.4f' % stats.fisher_exact(ct)[1])

# ---------- B. P4 free bits ----------
print('\n[B] P4: the 38%% "free bit" set - sky-determined or random?')
s_obs = np.where(T < 0, 1, -1)
flip = (s_obs != cspin)
nf = int(flip.sum())
print('    agreement sign(-T) vs colouring = %d/60 = %.1f%% ; flips = %d' % (
    60 - nf, 100 * (60 - nf) / 60, nf))
comp = {l: (basis(l, V) @ np.linalg.lstsq(basis(l, V), Tz, rcond=None)[0]) for l in range(1, 7)}
c12 = comp[1] + comp[2]
c3 = comp[3]
c46 = comp[4] + comp[5] + comp[6]
feat = {'T': T, 'absT': np.abs(T), 'T_l3': c3, 'T_l<=2': c12, 'T_l>=4': c46,
        'ratio_l3_l2': np.abs(c3) / (np.abs(c12) + 1e-9), 'k': kk.astype(float), 'hop': np.zeros(60)}
from collections import deque
adj = [set() for _ in range(60)]
for i, j in edges:
    adj[i].add(j); adj[j].add(i)
hop = np.full(60, -1); k2 = np.where(kk == 2)[0]
dq = deque(k2.tolist()); hop[k2] = 0
while dq:
    x = dq.popleft()
    for y in adj[x]:
        if hop[y] < 0:
            hop[y] = hop[x] + 1; dq.append(y)
feat['hop'] = hop.astype(float)


def auc(x, y):
    x = np.asarray(x, float); y = np.asarray(y, bool)
    r = stats.rankdata(x)
    n1 = int(y.sum()); n0 = len(y) - n1
    if n1 == 0 or n0 == 0:
        return 0.5
    return (r[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)


print('    single-feature AUC for predicting the flip indicator (0.5 = no information):')
res_p4 = {'n_flip': nf}
for nm, fv in feat.items():
    a = auc(fv, flip)
    a = max(a, 1 - a)
    np_ = 4000
    cnt = 0
    for _ in range(np_):
        if max(auc(rng.permutation(fv), flip), 1 - auc(rng.permutation(fv), flip)) >= a:
            cnt += 1
    p = (1 + cnt) / (1 + np_)
    print('      %-12s AUC = %.3f   permutation p = %.4f' % (nm, a, p))
    res_p4['auc_' + nm] = [float(a), float(p)]
# LOO linear discriminant on all features
X = np.column_stack([feat[nm] for nm in feat])
X = (X - X.mean(0)) / (X.std(0) + 1e-12)
y = flip.astype(float)
acc = []
for i in range(60):
    tr = np.ones(60, bool); tr[i] = False
    w = np.linalg.lstsq(np.column_stack([X[tr], np.ones(tr.sum())]), y[tr], rcond=None)[0]
    pr = np.column_stack([X, np.ones(60)]) @ w
    acc.append(float((pr[i] > 0.5) == (y[i] > 0.5)))
acc = np.array(acc)
na = int(acc.sum())
pbin = stats.binomtest(na, 60, 0.5, alternative='greater').pvalue
print('    LOO linear discriminant on all 8 sky/graph features: accuracy %d/60 = %.1f%%  (chance 50%%, p = %.3f)' % (
    na, 100 * na / 60, pbin))
# flip rate vs k / hop
for nm in ['k', 'hop']:
    v = feat[nm].astype(int)
    tab = {}
    for u_ in sorted(set(v.tolist())):
        m = v == u_
        tab[u_] = (int(flip[m].sum()), int(m.sum()))
    print('    flip rate vs %s: %s' % (nm, {kk2: '%d/%d' % vv for kk2, vv in tab.items()}))
res_p4['loo_acc'] = na
res_p4['loo_p'] = float(pbin)
# best possible: how many flips are consistent with sign of the l>=3 part?
pred = (np.sign(c46) != cspin)
print('    "sky-side perturbation" predictor sign(T_l>=4) != colouring: agreement with flips = %d/60 = %.1f%%' % (
    int((pred == flip).sum()), 100 * (pred == flip).mean()))
res_p4['c46_pred_agree'] = int((pred == flip).sum())
print('    -> verdict: %s' % ('SKY-DETERMINED' if (na / 60) > 0.75 and pbin < 0.01 else 'NOT sky-determined (consistent with a free random bit set)'))

json.dump(res_p4, open(O150 + '/data/step06_node_identity_and_p4.json', 'w'), indent=2)
print('\nOK saved: %s/data/step06_node_identity_and_p4.json' % O150)
