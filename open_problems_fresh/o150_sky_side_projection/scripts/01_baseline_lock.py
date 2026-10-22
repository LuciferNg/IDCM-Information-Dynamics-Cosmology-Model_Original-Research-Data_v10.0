#!/usr/bin/env python3
"""
O150 #01 - Baseline reproduction + structure lock (P0)
======================================================
Reproduce EVERY inherited number from O143/O159 before building anything new.

A. Coordinate pipeline: a5_nodes.txt (RA/Dec ICRS) -> galactic unit vectors
B. Node temperatures: T9, T20, ratio 3.02 ; identity (k, hop) of node9/node20
C. Multipole power l=1..6 + permutation null  ->  9458 / p=0.002
D. l=3 axis scan (Fibonacci, normalised)  ->  (193.45, -37.85)
E. Spherical design strength t=1..8 (aliasing matrix M) -> 5-design exact
F. l<=2 protection + l'=5 leakage into l=3
G. Graph: 60 nodes / 120 edges / 4-regular / |Aut| = 120 / vertex-transitive
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
rng = np.random.default_rng(20260921)

# ---------- A. coordinates ----------
raw = np.loadtxt(CS + '/a5_nodes.txt')
sc = SkyCoord(ra=raw[:, 0] * u.deg, dec=raw[:, 1] * u.deg, frame='icrs')
LB = np.column_stack([sc.galactic.l.deg, sc.galactic.b.deg])


def uvec(lb):
    l = np.radians(lb[:, 0]); b = np.radians(lb[:, 1])
    return np.column_stack([np.cos(b) * np.cos(l), np.cos(b) * np.sin(l), np.sin(b)])


V = uvec(LB)                      # true galactic unit vectors
Vbug = uvec(raw)                  # the O143 scripts/22-24 bug (RA/Dec as l/b)
R = np.linalg.norm(V, axis=1)
print('=' * 84)
print('  O150 #01 - baseline reproduction + structure lock')
print('=' * 84)
print('[A] coordinate pipeline')
print('    a5_nodes.txt: RA/Dec ICRS -> galactic via SkyCoord')
print('    |v| min/max = %.12f / %.12f  (must be 1)' % (R.min(), R.max()))
print('    node0  (l,b) = (%.4f, %.4f)   [cold spot, expect ~(209, -57)]' % (LB[0, 0], LB[0, 1]))

# ---------- B. node temperatures ----------
J = json.load(open(G182 + '/temps2_SMICA_4.17deg.json'))
T = np.array(J['A5_60'][:60], float)
Tbug_order = T
print('\n[B] node temperatures (SMICA 4.17 deg, A5_60)')
print('    T[9]  = %+8.3f uK' % T[9])
print('    T[20] = %+8.3f uK' % T[20])
print('    |T9|/|T20| = %.4f   (O143: 3.02, 107.0 vs 35.4)' % (abs(T[9]) / abs(T[20])))
print('    node0 (cold spot) = %+8.3f uK   (O41 anchor -134.19)' % T[0])

# graph identity of node 9 / 20
ac = np.loadtxt(CS + '/anchored_coloring.txt')
col = ac[:, 3].astype(int)
kk = ac[:, 4].astype(int)
adj = [set() for _ in range(60)]
edges = []
for i in range(60):
    for j in range(i + 1, 60):
        if math.degrees(math.acos(np.clip(float(V[i] @ V[j]), -1, 1))) < 28.0:
            adj[i].add(j); adj[j].add(i); edges.append((i, j))
deg = np.array([len(a) for a in adj])
hop = np.full(60, -1)
k2 = np.where(kk == 2)[0]
from collections import deque
dq = deque(k2); hop[k2] = 0
while dq:
    x = dq.popleft()
    for y in adj[x]:
        if hop[y] < 0:
            hop[y] = hop[x] + 1; dq.append(y)
print('    node9 : k=%d hop=%d color=%d deg=%d  nbrk=%s' %
      (kk[9], hop[9], col[9], deg[9], sorted(kk[j] for j in adj[9])))
print('    node20: k=%d hop=%d color=%d deg=%d  nbrk=%s' %
      (kk[20], hop[20], col[20], deg[20], sorted(kk[j] for j in adj[20])))
print('    geo distance node9-node20 = %.4f deg' % math.degrees(
    math.acos(np.clip(float(V[9] @ V[20]), -1, 1))))
print('    dist node0 -> node9 = %.2f deg ; node0 -> node20 = %.2f deg' % (
    math.degrees(math.acos(np.clip(float(V[0] @ V[9]), -1, 1))),
    math.degrees(math.acos(np.clip(float(V[0] @ V[20]), -1, 1)))))


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


def lpow(T_, l, v, nperm=3000, seed=20260919):
    rr = np.random.default_rng(seed)
    Tz = T_ - T_.mean()
    B = basis(l, v)
    c, *_ = np.linalg.lstsq(B, Tz, rcond=None)
    obs = float((c ** 2).sum())
    nl = np.empty(nperm)
    for i in range(nperm):
        cc, *_ = np.linalg.lstsq(B, rr.permutation(Tz), rcond=None)
        nl[i] = (cc ** 2).sum()
    p = (1 + int((nl >= obs).sum())) / (1 + nperm)
    return obs, p, float(nl.mean())


# ---------- C. multipole power ----------
print('\n[C] multipole power l=1..6 (permutation null, 3000)')
print('     l      power    share   null_mean       p')
tot = 0.0
pw = {}
for l in range(1, 7):
    o, p, nm = lpow(T, l, V)
    pw[l] = (o, p, nm); tot += o
for l in range(1, 7):
    o, p, nm = pw[l]
    print('    %2d  %9.1f  %6.1f%%  %9.1f  %7.4f' % (l, o, 100 * o / tot, nm, p))
print('    (O143: l=3 power 9458, 44.3%, p=0.002)')

# ---------- D. axis scan ----------
def fib_sphere(n):
    idx = np.arange(n) + 0.5
    z = 1 - 2 * idx / n
    az = math.pi * (1 + 5 ** 0.5) * idx
    r_ = np.sqrt(np.clip(1 - z * z, 0, None))
    return np.column_stack([r_ * np.cos(az), r_ * np.sin(az), z])


def axis_scan(T_, v, nax=200000):
    x = T_ - T_.mean()
    ax = fib_sphere(nax)
    ct = v @ ax.T
    P3 = (5 * ct ** 3 - 3 * ct) / 2
    P3 = P3 - P3.mean(0)
    rr = np.abs(P3.T @ x) / (np.linalg.norm(P3, axis=0) * np.linalg.norm(x) + 1e-30)
    i = int(np.argmax(rr))
    a = ax[i]
    return float(rr[i]), a, math.degrees(math.atan2(a[1], a[0])) % 360, math.degrees(math.asin(a[2]))


r3, AX, l3, b3 = axis_scan(T, V)
print('\n[D] l=3 axis scan (200k Fibonacci, normalised)')
print('    axis = (%.2f, %.2f) deg   r = %.4f   |a| = %.10f' % (l3, b3, r3, np.linalg.norm(AX)))
print('    (O143 corrected: (193.45, -37.85))')
print('    axis . node0(cold spot) angle = %.2f deg' % math.degrees(
    math.acos(np.clip(abs(float(V[0] @ AX)), -1, 1))))

# ---------- E. design strength ----------
print('\n[E] spherical design strength (aliasing matrix M)')
N = 60
Y = {}
for l in range(0, 9):
    Y[l] = basis(l, V)
dev = {}
for t in range(1, 9):
    mx = 0.0
    for l1 in range(0, t + 1):
        for l2 in range(0, t + 1):
            if l1 + l2 > t:
                continue
            M = (4 * np.pi / N) * (Y[l1].T @ Y[l2])
            tgt = np.eye(len(Y[l1].T), len(Y[l2].T)) if l1 == l2 else 0.0
            mx = max(mx, float(np.abs(M - tgt).max()))
    dev[t] = mx
for t in range(1, 9):
    print('    t=%d  max|M - delta| = %.3e   %s' % (t, dev[t], 'OK' if dev[t] < 1e-6 else 'BREAK'))

# ---------- F. protection + leakage ----------
print('\n[F] l<=2 protection and l\'=5 leakage into l=3')
for l in range(0, 6):
    M = (4 * np.pi / N) * (Y[l].T @ Y[l])
    print('    ||M_%d%d - I||_max = %.3e' % (l, l, float(np.abs(M - np.eye(2 * l + 1)).max())))
for lp in [0, 1, 2, 4, 5, 6]:
    M = (4 * np.pi / N) * (Y[lp].T @ Y[3])
    print('    ||M[l\'=%d -> l=3]||_F = %.3e' % (lp, float(np.linalg.norm(M, 'fro'))))

# ---------- G. graph automorphism ----------
print('\n[G] graph: 60 nodes / %d edges / degree set %s' % (len(edges), sorted(set(deg.tolist()))))
import networkx as nx
Gn = nx.Graph(); Gn.add_nodes_from(range(60)); Gn.add_edges_from(edges)
gm = nx.algorithms.isomorphism.GraphMatcher(Gn, Gn)
cnt = 0; found920 = False; orbits = None
for iso in gm.isomorphisms_iter():
    cnt += 1
    if iso.get(9) == 20:
        found920 = True
    if cnt > 200:
        break
print('    |Aut(G)| (counted, capped at 200) = %d' % cnt)
print('    exists g in Aut with g(9)=20 : %s' % found920)
print('    (O143: |Aut| = 120 = I_h, vertex-transitive)')

# ---------- save ----------
out = {
    'node0_lb': [float(LB[0, 0]), float(LB[0, 1])],
    'T9': float(T[9]), 'T20': float(T[20]), 'ratio': float(abs(T[9]) / abs(T[20])),
    'multipole': {str(l): {'power': pw[l][0], 'p': pw[l][1], 'null_mean': pw[l][2]} for l in pw},
    'axis': [float(l3), float(b3)], 'axis_r': float(r3),
    'design_dev': {str(t): dev[t] for t in dev},
    'aut_order_capped': cnt, 'aut_has_9to20': bool(found920),
    'n_edges': len(edges), 'degrees': sorted(set(deg.tolist())),
}
os.makedirs(O150 + '/data', exist_ok=True)
json.dump(out, open(O150 + '/data/step01_baseline.json', 'w'), indent=2)
print('\nOK saved: %s/data/step01_baseline.json' % O150)
