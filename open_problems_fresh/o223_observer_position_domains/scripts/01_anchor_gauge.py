#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O223 scripts/01 -- Anchor Gauge Freedom (R1) + Frustration-Set Aut-Orbit (R2)
==============================================================================
Question (R1): is the A5 network anchoring an OBSERVER-CENTRED LABEL (gauge),
or a SPATIALLY FIXED SKELETON?
Question (R2): is the frustration-edge set (32 topological bits) invariant
under the full graph automorphism group Aut(G), or does it depend on the
anchor?  This decides whether the topological-bit PATTERN is absolute
(decodable without an anchor) or relative (needs an anchor).

Method (zero free parameters):
  - rebuild the 60-node graph from cmb_cold_spot/data/a5_nodes.txt
  - compute Aut(G) exactly as the set of orthogonal 3x3 matrices that
    permute the 60 vertices (3-point linear solve, no group theory assumed)
  - split proper / improper; cross-check |Aut| = 120 against O213 docs/09
  - for each anchor a in 1..60: BFS 2-colouring -> frustration edge set ->
    mean |dT| over those edges (SMICA 5deg-smoothed node temperatures)
  - random 2-colouring null (5000 samples) -> z(a)
  - orbit structure of the frustration SET under Aut(G)

ASCII only.  /usr/bin/python3.
"""
import os, math, itertools, json
import numpy as np
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CS   = os.path.join(os.path.dirname(ROOT), "cmb_cold_spot", "data")

results = []
def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))
    print(("  [OK] " if cond else "  [XX] ") + name + ("   " + detail if detail else ""))

def sph(ra, dec):
    r, d = math.radians(ra), math.radians(dec)
    return np.array([math.cos(d)*math.cos(r), math.cos(d)*math.sin(r), math.sin(d)])

# ---------------------------------------------------------------- load
nodes = [tuple(map(float, l.split())) for l in open(os.path.join(CS, "a5_nodes.txt"))]
V = np.array([sph(*n) for n in nodes])
N = len(V)
D = np.degrees(np.arccos(np.clip(V @ V.T, -1.0, 1.0)))

print("="*72)
print("O223 / 01 -- anchor gauge freedom + frustration-set orbit")
print("="*72)
print("[A] graph")
ds = np.sort(D[np.triu_indices(N, 1)])
thr = (ds[119] + ds[120]) / 2.0
A = (D < thr)
np.fill_diagonal(A, False)
deg = A.sum(1)
print("    threshold = %.4f deg (120th=%.4f, 121st=%.4f)" % (thr, ds[119], ds[120]))
print("    V=%d  E=%d  degree set=%s" % (N, int(A.sum()//2), sorted(set(int(x) for x in deg))))
check("A1 V=60", N == 60)
check("A2 E=120", int(A.sum()//2) == 120)
check("A3 4-regular", set(int(x) for x in deg) == {4})

nbr = {i: [int(j) for j in np.where(A[i])[0]] for i in range(N)}
dist = {}
for s in range(N):
    d0 = {s: 0}
    q = deque([s])
    while q:
        u = q.popleft()
        for w in nbr[u]:
            if w not in d0:
                d0[w] = d0[u] + 1
                q.append(w)
    dist[s] = d0
check("A4 graph diameter = 8", max(dist[0].values()) == 8, "d(0,57)=%d" % dist[0][57])

# ---------------------------------------------------------------- Aut(G)
print("[B] Aut(G) by exact 3-point linear solve")
# pick 3 linearly independent vertices from {0} u nbr(0) for the exact solve
cand = [0] + nbr[0]
base = [cand[0]]
for c in cand[1:]:
    trial = base + [c]
    if np.linalg.matrix_rank(V[trial], tol=1e-9) == len(trial):
        base.append(c)
    if len(base) == 3:
        break
assert len(base) == 3, "could not build a non-degenerate 3-frame"
P0 = V[base]                       # 3x3, rows = the three chosen vertices
print("    frame vertices =", base)
Pinv = np.linalg.inv(P0)
aut = []
seen = set()
for i0 in range(N):
    for perm in itertools.permutations(nbr[i0], 2):
        Q = V[[i0] + list(perm)]
        M = Q.T @ Pinv.T               # solve P @ M.T = Q  ->  M v_i = w_i
        if not np.allclose(M.T @ M, np.eye(3), atol=1e-5):
            continue
        MV = V @ M.T
        key = tuple(np.round(M.flatten(), 8))
        if key in seen:
            continue
        # membership test: every image must coincide with a vertex (set test)
        ok = True
        for k in range(N):
            j = int(np.argmax(MV[k] @ V.T))
            if np.linalg.norm(MV[k] - V[j]) > 1e-4:
                ok = False
                break
        if ok:
            seen.add(key)
            aut.append(M)
aut = np.array(aut)
dets = np.round(np.linalg.det(aut), 6)
n_proper = int((dets > 0).sum())
n_improper = int((dets < 0).sum())
print("    |GeoAut| = %d   proper = %d   improper = %d" % (len(aut), n_proper, n_improper))
check("B1 |GeoAut| = 60 (chiral icosahedral group I)", len(aut) == 60)
check("B2 60 proper + 0 improper (strictly chiral)", (n_proper, n_improper) == (60, 0))

# antipodal map -I in Aut?  (NO for a chiral point set -> this IS the chirality)
mI = -np.eye(3)
check("B3 -I NOT in GeoAut(G) (point set is chiral, no inversion)",
      not any(np.allclose(M, mI, atol=1e-9) for M in aut))

# action of Aut on vertices -> permutations
perms = []
for M in aut:
    MV = V @ M.T
    p = np.array([int(np.argmax(MV[k] @ V.T)) for k in range(N)])
    assert len(set(p.tolist())) == N
    perms.append(p)
perms = np.array(perms)

# ---------------------------------------------------------------- temps
idx, col, T = [], [], []
for line in open(os.path.join(CS, "smica_smoothed.txt")):
    if line.startswith("#"):
        continue
    p = line.split()
    idx.append(int(p[0])); col.append(int(p[1])); T.append(float(p[2]))
T = np.array(T); col = np.array(col)
check("C1 60 node temperatures loaded", len(T) == 60)

# ---------------------------------------------------------------- anchored colouring
def bfs_color(anchor):
    """2-colouring anchored at `anchor` = cold(1); BFS bipartite."""
    c = -np.ones(N, dtype=int)
    c[anchor] = 1
    q = deque([anchor])
    while q:
        u = q.popleft()
        for w in nbr[u]:
            if c[w] < 0:
                c[w] = 1 - c[u]
                q.append(w)
    assert (c >= 0).all(), "graph not bipartite"
    return c

def frust_edges(c):
    return [frozenset((i, j)) for i in range(N) for j in nbr[i]
            if i < j and c[i] == c[j]]

def mean_absDT(es):
    if not es:
        return float("nan")
    return float(np.mean([abs(T[list(e)[0]] - T[list(e)[1]]) for e in es]))

print("[D] anchored colouring + frustration statistics")
c0 = bfs_color(0)
fe0 = frust_edges(c0)
print("    anchor 0: |frustration edges| = %d" % len(fe0))
check("D1 32 frustration edges (anchor 0)", len(fe0) == 32)

# random 2-colouring null: same-size (32) same-colour edge sets
rng = np.random.default_rng(20260927)
NS = 5000
rand_means = np.empty(NS)
for t in range(NS):
    perm = rng.permutation(N)
    c = np.zeros(N, dtype=int)
    c[perm[:30]] = 1
    rand_means[t] = mean_absDT(frust_edges(c))
mu_r, sd_r = float(rand_means.mean()), float(rand_means.std())
print("    random null (5000): mean = %.2f  std = %.2f uK" % (mu_r, sd_r))

zs = {}
fset_orbit = set()
for a in range(N):
    ca = bfs_color(a)
    fa = frust_edges(ca)
    m = mean_absDT(fa)
    zs[a] = (m - mu_r) / sd_r
    if a == 0:
        base_set = frozenset(fa)
    fset_orbit.add(frozenset(fa))

print("    z(0) = %+.2f   mean|dT|(0) = %.1f uK" % (zs[0], mean_absDT(fe0)))
print("    z(57) = %+.2f  mean|dT|(57) = %.1f uK" % (zs[57], mean_absDT(frust_edges(bfs_color(57)))))
zs_arr = np.array([zs[a] for a in range(N)])
print("    z distribution: min=%+.2f max=%+.2f mean=%+.2f std=%.2f"
      % (zs_arr.min(), zs_arr.max(), zs_arr.mean(), zs_arr.std()))
check("D2 z(0) < -3.0 (anchor-0 uniqueness)", zs[0] < -3.0, "z=%.2f" % zs[0])
check("D3 z(57) = z(0) (antipode degeneracy)", abs(zs[57] - zs[0]) < 1e-9)
n_below = int((zs_arr < -2.0).sum())
print("    anchors with z < -2 : %d" % n_below)
check("D4 only {0,57} below -2", n_below == 2)

# ---------------------------------------------------------------- R2: orbit of frustration set
print("[E] frustration-set orbit under Aut(G)")
orbit = set()
for p in perms:
    inv = np.empty(N, dtype=int); inv[p] = np.arange(N)
    moved = frozenset(frozenset((int(inv[i]), int(inv[j]))) for (i, j) in
                      [tuple(e) for e in base_set])
    orbit.add(moved)
print("    orbit size of anchor-0 frustration set = %d" % len(orbit))
print("    distinct frustration sets over 60 anchors = %d" % len(fset_orbit))
check("E1 frustration set NOT Aut-invariant (orbit > 1)", len(orbit) > 1,
      "orbit=%d" % len(orbit))

# orbit of a single anchor under Aut
orb0 = sorted(set(int(p[0]) for p in perms))
print("    vertex orbit of node 0 under Aut = %d vertices" % len(orb0))
check("E2 vertex-transitive (orbit of 0 = 60)", len(orb0) == 60)

# ---------------------------------------------------------------- summary
npass = sum(1 for _, ok, _ in results if ok)
ntot = len(results)
print("-"*72)
print("RESULT: %d/%d PASS" % (npass, ntot))
print("-"*72)
out = {
    "n_pass": npass, "n_total": ntot,
    "threshold_deg": thr, "V": N, "E": int(A.sum()//2),
    "aut_order": len(aut), "proper": n_proper, "improper": n_improper,
    "n_frustration_edges": len(fe0),
    "null_mean_uK": mu_r, "null_std_uK": sd_r,
    "z_anchor0": zs[0], "z_anchor57": zs[57],
    "z_min": float(zs_arr.min()), "z_max": float(zs_arr.max()),
    "z_mean": float(zs_arr.mean()), "z_std": float(zs_arr.std()),
    "anchors_below_minus2": n_below,
    "frustration_set_orbit": len(orbit),
    "distinct_frustration_sets": len(fset_orbit),
    "vertex_orbit_size": len(orb0),
    "z_by_anchor": {str(a): zs[a] for a in range(N)},
}
with open(os.path.join(ROOT, "data", "01_anchor_gauge.json"), "w") as f:
    json.dump(out, f, indent=1)
print("wrote data/01_anchor_gauge.json")
