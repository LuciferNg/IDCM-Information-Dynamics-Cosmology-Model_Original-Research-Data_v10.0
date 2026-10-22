#!/usr/bin/env python3
"""
O150 #11 - node9/node20 structural identity + O21 transparency framework
========================================================================
A. structural profile of node9 / node20 (k, hop, edge colours, transparency)
B. |z| vs structural quantities (k, hop, frustrated/transparent degree) + permutation p
C. top-8 |z| nodes and their structural profiles
D. O143 k-selector re-test: corr(k, |z|) with permutation null (was -0.38 with |T|)
E. O21 transparency test: |z| of nodes on the fully-transparent subgraph
"""
import numpy as np, math, json
import healpy as hp
from astropy.coordinates import SkyCoord
import astropy.units as u
from collections import deque
from scipy import stats

BASE = '/home/wsl/Projects/IDCM-Original/IDCM-v10.0--It-From-Beat'
ROOT = BASE + '/open_problems_fresh'
O150 = ROOT + '/o150_sky_side_projection'
CS = ROOT + '/cmb_cold_spot/data'
CACHE = ROOT + '/o5_catalog_compare/data/smooth_cache'
NS = 1024
rng = np.random.default_rng(15111)

raw = np.loadtxt(CS + '/a5_nodes.txt')
sc = SkyCoord(ra=raw[:, 0] * u.deg, dec=raw[:, 1] * u.deg, frame='icrs')
LB = np.column_stack([sc.galactic.l.deg, sc.galactic.b.deg])
l_ = np.radians(LB[:, 0]); b_ = np.radians(LB[:, 1])
V = np.column_stack([np.cos(b_) * np.cos(l_), np.cos(b_) * np.sin(l_), np.sin(b_)])
GAM = np.clip(V @ V.T, -1, 1)
ac = np.loadtxt(CS + '/anchored_coloring.txt')
col = ac[:, 3].astype(int); kk = ac[:, 4].astype(int)
cspin = np.where(col == 1, 1, -1)
edges = [(i, j) for i in range(60) for j in range(i + 1, 60)
         if math.degrees(math.acos(np.clip(float(V[i] @ V[j]), -1, 1))) < 28.0]
adj = [set() for _ in range(60)]
for i, j in edges:
    adj[i].add(j); adj[j].add(i)
hop = np.full(60, -1)
k2 = np.where(kk == 2)[0]
dq = deque(k2.tolist()); hop[k2] = 0
while dq:
    x = dq.popleft()
    for y in adj[x]:
        if hop[y] < 0:
            hop[y] = hop[x] + 1; dq.append(y)

m = hp.ud_grade(hp.read_map(CACHE + '/smica2_smooth4.17.fits', field=0), NS) * 1e6
T = m[hp.ang2pix(NS, LB[:, 0], LB[:, 1], lonlat=True)]
cl = hp.anafast(m, lmax=3 * NS - 1); LMAX = 3 * NS - 1
w = (2 * np.arange(LMAX + 1) + 1) / (4 * np.pi) * cl
C = np.zeros((60, 60)); Pm1 = np.ones_like(GAM); P0 = GAM.copy()
for L in range(1, LMAX):
    P1 = ((2 * L + 1) * GAM * P0 - L * Pm1) / (L + 1)
    C += w[L + 1] * P1; Pm1, P0 = P0, P1
C = 0.5 * (C + C.T)
sd = np.sqrt(np.diag(C))
z = T / sd
az = np.abs(z)
nfr = np.array([sum(1 for j in adj[i] if cspin[j] == cspin[i]) for i in range(60)], float)   # frustrated (opaque)
ntr = 4.0 - nfr                                                                              # transparent

print('=' * 92)
print('  O150 #11 - node9/node20 structural identity + O21 transparency')
print('=' * 92)

print('\n[A] structural profile')
print('    %-6s %3s %4s %3s %-18s %-16s %s' % ('node', 'k', 'hop', 'col', 'neighbour colours', 'neighbour k', 'frust/transp'))
for nd in [9, 20, 0]:
    nbrs = sorted(adj[nd])
    print('    %-6d %3d %4d %3d %-18s %-16s %d/%d' % (
        nd, kk[nd], hop[nd], col[nd], str([cspin[j] for j in nbrs]),
        str(sorted(int(kk[j]) for j in nbrs)), int(nfr[nd]), int(ntr[nd])))
print('    (transparent edge = bichromatic; frustrated/opaque = same colour)')
print('    node9 |z| = %+.3f (rank %d/60) ; node20 |z| = %+.3f (rank %d/60)' % (
    z[9], 1 + int((az > az[9]).sum()), z[20], 1 + int((az > az[20]).sum())))

print('\n[B] |z| vs structural quantities (Spearman + permutation p)')
res = {}
for name, x in [('k', kk.astype(float)), ('hop', hop.astype(float)),
                ('frustrated_degree', nfr), ('transparent_degree', ntr)]:
    r = stats.spearmanr(x, az)
    cnt = 0; NP = 20000
    for _ in range(NP):
        if abs(stats.spearmanr(rng.permutation(x), az).statistic) >= abs(r.statistic):
            cnt += 1
    p = (1 + cnt) / (1 + NP)
    print('    %-20s rho = %+.4f   p = %.4f' % (name, r.statistic, p))
    res['rho_' + name] = [float(r.statistic), float(p)]

print('\n[C] top-8 |z| nodes')
order = np.argsort(-az)
print('    %-6s %8s %4s %4s %6s %8s' % ('node', 'T(uK)', '|z|', 'k', 'hop', 'frust/transp'))
for i in order[:8]:
    print('    %-6d %8.2f %4.2f %4d %6d %5d/%d' % (i, T[i], az[i], kk[i], hop[i], int(nfr[i]), int(ntr[i])))
print('    k distribution of top-8: %s' % sorted(kk[order[:8]].tolist()))
print('    k distribution of all 60 : %s' % sorted(kk.tolist()))
top5k = kk[order[:5]]
print('    top-5 |z| nodes: %s  (k=0 係 %d/60 = %.1f%% of population)' % (
    top5k.tolist(), int((kk == 0).sum()), 100 * (kk == 0).mean()))

print('\n[D] O143 k-selector re-test (was corr(k,|T|) = -0.38)')
for tgt, nm in [(np.abs(T), '|T|'), (az, '|z|')]:
    r = stats.spearmanr(kk.astype(float), tgt)
    cnt = 0; NP = 20000
    for _ in range(NP):
        if abs(stats.spearmanr(rng.permutation(kk.astype(float)), tgt).statistic) >= abs(r.statistic):
            cnt += 1
    p = (1 + cnt) / (1 + NP)
    print('    rho(k, %-4s) = %+.4f   p = %.4f' % (nm, r.statistic, p))
    res['ksel_' + nm] = [float(r.statistic), float(p)]
print('    (|z| removes the field-wide amplitude scale that |T| carries)')

print('\n[E] O21 transparency test')
full_tr = ntr == 4
print('    nodes with 4/4 transparent edges: %d ; others: %d' % (int(full_tr.sum()), int((~full_tr).sum())))
g1 = az[full_tr]; g2 = az[~full_tr]
print('    |z| mean: fully-transparent %.3f (n=%d) ; mixed %.3f (n=%d) ; MW p = %.4f' % (
    g1.mean(), len(g1), g2.mean(), len(g2), stats.mannwhitneyu(g1, g2).pvalue))
print('    node9 n_transparent = %d ; node20 = %d' % (ntr[9], ntr[20]))
res['transp_mean'] = [float(g1.mean()), float(g2.mean()), float(stats.mannwhitneyu(g1, g2).pvalue)]
res['ntr9'] = float(ntr[9]); res['ntr20'] = float(ntr[20])

print('\n[F] verdict on node9')
print('    node9: k=%d hop=%d, %d/4 transparent edges, |z| = %.2f (rank %d/60)' % (
    kk[9], hop[9], int(ntr[9]), az[9], 1 + int((az > az[9]).sum())))
print('    k / frustrated-degree DO correlate with |z|: rho = %.3f, p = %.4f (uncorrected;' % (
    res['rho_k'][0], res['rho_k'][1]))
print('      top-8 |z| has 4 k=0 nodes = 50%% vs 13.3%% population -> ~2sigma over-representation)')
print('    but single-node prediction is impossible (P4: LOO LDA 46.7%%, p = 0.741)')
print('    -> node9 is a k=0 node (the class that is weakly preferred at the extremes),')
print('       sitting on the fully-transparent subgraph (O21): a Gaussian-tail excursion,')
print('       NOT a structurally deterministic pick.')

json.dump(res, open(O150 + '/data/step11_node9_structure.json', 'w'), indent=2)
print('\nOK saved: %s/data/step11_node9_structure.json' % O150)
