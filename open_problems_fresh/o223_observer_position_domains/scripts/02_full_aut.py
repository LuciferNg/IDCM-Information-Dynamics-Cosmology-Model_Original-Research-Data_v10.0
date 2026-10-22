#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O223 scripts/02 -- FULL combinatorial Aut(G) (I_h, 120) vs geometric Aut (I, 60)
================================================================================
O143/O213 establish a two-level symmetry:
  * COMBINATORIAL automorphism group of the A5 relation graph = I_h, order 120
  * GEOMETRIC isometry group of the 60-point set = I (chiral), order 60, all det=+1
The 60 non-isometric automorphisms are NOT realisable by any O(3) map.

Physical reading (this script tests it):
  - inside one GL phase domain only the 60 proper isometries act   -> gauge orbit A
  - crossing a pi phase slip (domain wall) mirrors the local frame -> the 60
    improper combinatorial automorphisms become available          -> gauge orbit B
If B strictly contains A, then "node0 -> node9" is a WALL-CROSSING relabelling
(mirror sector), not an arbitrary relabelling.

Also: cross-check data/anchored_coloring.txt, node0<->node9 specifics, and the
angular -> comoving conversion 1 deg = R_world * pi/180.

ASCII only.  /usr/bin/python3.
"""
import os, math, json
import numpy as np
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CS   = os.path.join(os.path.dirname(ROOT), "cmb_cold_spot", "data")

res = []
def check(name, cond, detail=""):
    res.append((name, bool(cond), detail))
    print(("  [OK] " if cond else "  [XX] ") + name + ("   " + detail if detail else ""))

def sph(ra, dec):
    r, d = math.radians(ra), math.radians(dec)
    return np.array([math.cos(d)*math.cos(r), math.cos(d)*math.sin(r), math.sin(d)])

nodes = [tuple(map(float, l.split())) for l in open(os.path.join(CS, "a5_nodes.txt"))]
V = np.array([sph(*n) for n in nodes])
N = len(V)
D = np.degrees(np.arccos(np.clip(V @ V.T, -1.0, 1.0)))
ds = np.sort(D[np.triu_indices(N, 1)])
thr = (ds[119] + ds[120]) / 2.0
A = (D < thr); np.fill_diagonal(A, False)
nbr = {i: [int(j) for j in np.where(A[i])[0]] for i in range(N)}

print("="*74)
print("O223 / 02 -- full combinatorial Aut(G) vs geometric Aut(G)")
print("="*74)

# ---------------------------------------------------------------- geometric Aut
def geometric_aut():
    cand = [0] + nbr[0]
    base = [cand[0]]
    for c in cand[1:]:
        if np.linalg.matrix_rank(V[base + [c]], tol=1e-9) == len(base) + 1:
            base.append(c)
        if len(base) == 3:
            break
    P0 = V[base]; Pinv = np.linalg.inv(P0)
    out = []
    for i0 in range(N):
        import itertools
        for pm in itertools.permutations(nbr[i0], 2):
            Q = V[[i0] + list(pm)]
            M = Q.T @ Pinv.T
            if not np.allclose(M.T @ M, np.eye(3), atol=1e-5):
                continue
            MV = V @ M.T
            p = np.array([int(np.argmax(MV[k] @ V.T)) for k in range(N)])
            if len(set(p.tolist())) != N:
                continue
            if np.max(np.linalg.norm(MV - V[p], axis=1)) > 1e-4:
                continue
            out.append((tuple(p.tolist()), float(np.linalg.det(M))))
    # dedupe
    seen, uni = set(), []
    for p, d in out:
        if p not in seen:
            seen.add(p); uni.append((p, d))
    return uni

geo = geometric_aut()
print("[F] geometric automorphisms (O(3)-realisable)")
print("    |GeoAut| = %d   det>0: %d   det<0: %d"
      % (len(geo), sum(1 for _, d in geo if d > 0), sum(1 for _, d in geo if d < 0)))
check("F1 |GeoAut| = 60", len(geo) == 60)
check("F2 all proper (strictly chiral I)", all(d > 0 for _, d in geo))
geo_set = set(p for p, _ in geo)

# ---------------------------------------------------------------- combinatorial Aut
print("[G] full combinatorial Aut(G) by backtracking")
# BFS order with parents
order, parent, vis = [0], {0: None}, [False]*N
vis[0] = True
q = deque([0])
while q:
    u = q.popleft()
    for w in nbr[u]:
        if not vis[w]:
            vis[w] = True; parent[w] = u; order.append(w); q.append(w)
check("G1 BFS reaches all 60 vertices", len(order) == 60)

Af = A.astype(np.int8)
img = [-1]*N; used = [False]*N; autos = []

def bt(idx):
    if len(autos) > 400:
        return
    if idx == N:
        autos.append(tuple(img)); return
    v = order[idx]
    cands = range(N) if idx == 0 else nbr[img[parent[v]]]
    for c in cands:
        if used[c]:
            continue
        ok = True
        for u in range(N):
            if img[u] != -1 and Af[v, u] != Af[c, img[u]]:
                ok = False; break
        if not ok:
            continue
        img[v] = c; used[c] = True
        bt(idx + 1)
        img[v] = -1; used[c] = False

bt(0)
print("    |Aut(G)| = %d" % len(autos))
check("G2 |Aut(G)| = 120 (I_h)", len(autos) == 120)
auto_set = set(autos)
n_geo_in = len(auto_set & geo_set)
print("    of these, O(3)-realisable = %d   pure combinatorial = %d"
      % (n_geo_in, len(auto_set) - n_geo_in))
check("G3 exactly 60 non-isometric automorphisms", len(auto_set) - n_geo_in == 60)

# ---------------------------------------------------------------- colours & temps
idx_, col_, T_ = [], [], []
for line in open(os.path.join(CS, "smica_smoothed.txt")):
    if line.startswith("#"):
        continue
    p = line.split()
    idx_.append(int(p[0])); col_.append(int(p[1])); T_.append(float(p[2]))
T = np.array(T_); col_data = np.array(col_)

anch = {}
for line in open(os.path.join(CS, "anchored_coloring.txt")):
    if line.startswith("#"):
        continue
    p = line.split()
    if len(p) >= 4:
        anch[int(p[0])] = int(p[3])          # col 3 = color(cold=1)

fe_data = set()
for line in open(os.path.join(CS, "frustration_edges.txt")):
    if line.startswith("#"):
        continue
    p = line.split()
    if len(p) >= 2:
        fe_data.add(frozenset((int(p[0]), int(p[1]))))

def bfs_color(anchor):
    c = -np.ones(N, dtype=int); c[anchor] = 1
    q = deque([anchor])
    while q:
        u = q.popleft()
        for w in nbr[u]:
            if c[w] < 0:
                c[w] = 1 - c[u]; q.append(w)
    return c

c0 = bfs_color(0)
if anch:
    same = sum(1 for k in range(N) if anch.get(k, -1) == c0[k])
    flip = sum(1 for k in range(N) if anch.get(k, -1) == 1 - c0[k])
    print("[H] anchored_coloring.txt cross-check (anchor 0)")
    print("    identical = %d   colour-flipped = %d   (of %d)" % (same, flip, len(anch)))
    check("H1 data colouring == script BFS colouring (up to global flip)",
          same == N or flip == N)
else:
    print("[H] anchored_coloring.txt empty/absent -> skipped")

def frust(c):
    return frozenset(frozenset((i, j)) for i in range(N) for j in nbr[i]
                     if i < j and c[i] == c[j])

base_set = frust(c0)
print("    anchor-0 frustration edges = %d" % len(base_set))
check("H2 32 frustration edges", len(base_set) == 32)
if fe_data:
    inter = len(base_set & fe_data)
    print("    vs data/frustration_edges.txt: overlap = %d/%d" % (inter, len(fe_data)))
    check("H2b frustration set reproduces data file exactly",
          base_set == fe_data)

# which faces do the frustrated edges bound?
tri = sum(1 for i in range(N) for j in nbr[i] for k in nbr[j]
          if k > j > i and A[i, k])
print("    triangles = %d  4-cycles = %d   (RH faces: 20 tri, 30 squares, 12 pentagons)"
      % (tri, sum(1 for i in range(N) for j in nbr[i] if j > i
                  for k in nbr[j] if k > i
                  for l in nbr[k] if l in nbr[i] and l > k)))
check("H3 20 triangles (odd faces exist -> graph NOT bipartite)", tri == 20)

# ---------------------------------------------------------------- orbits
def orbit_of_set(S, group):
    orb = set()
    for p in group:
        inv = np.empty(N, dtype=int); inv[list(p)] = np.arange(N)
        orb.add(frozenset(frozenset((int(inv[i]), int(inv[j]))) for (i, j) in
                          [tuple(e) for e in S]))
    return orb

orb_geo = orbit_of_set(base_set, geo_set)
orb_full = orbit_of_set(base_set, auto_set)
print("[I] frustration-set orbit")
print("    under GeoAut (60, chiral sector) : %d distinct sets" % len(orb_geo))
print("    under Aut    (120, incl. mirror) : %d distinct sets" % len(orb_full))
check("I1 GeoAut orbit = 30", len(orb_geo) == 30)
check("I2 full orbit < GeoAut orbit (mirror pairs sets)",
      len(orb_full) < len(orb_geo), "full=%d geo=%d" % (len(orb_full), len(orb_geo)))

# antipodal / mirror automorphism?
mI = None
for p in auto_set:
    if tuple(p) == tuple((N - 1 - k) for k in range(N)):
        mI = p
print("    is 'reverse index' an automorphism? %s" % (mI is not None))
# does any automorphism map 0 -> 57 ?
to57 = [p for p in auto_set if p[0] == 57]
to57_geo = [p for p in geo_set if p[0] == 57]
print("    automorphisms 0->57: full=%d  geometric=%d" % (len(to57), len(to57_geo)))
check("I3 some geometric automorphism maps 0->57", len(to57_geo) > 0)

# does the frustration set get FIXED by the 0->57 maps?
fixed57 = sum(1 for p in to57_geo if orbit_of_set(base_set, [p]) == {base_set})
print("    of the geometric 0->57 maps, how many fix the frustration set: %d/%d"
      % (fixed57, len(to57_geo)))
check("I4 all 0->57 geometric maps fix the frustration set", fixed57 == len(to57_geo))

# ---------------------------------------------------------------- node0 <-> node9
print("[J] node 0 -> node 9")
d09 = None
q = deque([(0, 0)]); seen0 = {0}
while q:
    u, du = q.popleft()
    if u == 9:
        d09 = du; break
    for w in nbr[u]:
        if w not in seen0:
            seen0.add(w); q.append((w, du + 1))
print("    d(0,9) = %d hop   (0's neighbours: %s)" % (d09, nbr[0]))
check("J1 node 9 is a 1-hop neighbour of node 0", d09 == 1)
print("    colours: c0[0]=%d  c0[9]=%d   (same colour => phase slip, wall edge)"
      % (c0[0], c0[9]))
print("    T: T[0]=%+.1f uK  T[9]=%+.1f uK  |dT| = %.1f uK"
      % (T[0], T[9], abs(T[0] - T[9])))
edge09 = frozenset((0, 9))
print("    edge (0,9) frustrated? %s" % (edge09 in base_set))
check("J2 (0,9) is a NORMAL edge (colours differ)",
      c0[0] != c0[9])

# how many 1-hop neighbours of 0 are frustrated vs normal
fn = sum(1 for w in nbr[0] if frozenset((0, w)) in base_set)
print("    node 0's 4 neighbours: frustrated = %d  normal = %d" % (fn, 4 - fn))

# ---------------------------------------------------------------- scale
R_world = 4129.64
deg2mpc = R_world * math.pi / 180.0
print("[K] angular -> comoving (1 deg = R_world*pi/180, R_world = %.2f Mpc)" % R_world)
print("    1 deg = %.3f Mpc" % deg2mpc)
print("    edge 26.0913 deg = %8.1f Mpc" % (26.0913 * deg2mpc))
print("    GL R*  6.022 deg = %8.1f Mpc" % (6.022 * deg2mpc))
print("    GL xi* 0.663 deg = %8.1f Mpc" % (0.663 * deg2mpc))
print("    wall d 1.364 deg = %8.1f Mpc" % (1.364 * deg2mpc))
check("K1 R* in Mpc ~ 434", abs(6.022 * deg2mpc - 434) < 3)

# ---------------------------------------------------------------- summary
npass = sum(1 for _, ok, _ in res if ok); ntot = len(res)
print("-"*74)
print("RESULT: %d/%d PASS" % (npass, ntot))
print("-"*74)
out = dict(n_pass=npass, n_total=ntot,
           geo_aut=len(geo), full_aut=len(autos),
           non_isometric=len(auto_set) - n_geo_in,
           n_frustration_edges=len(base_set), triangles=tri,
           orbit_geo=len(orb_geo), orbit_full=len(orb_full),
           d09=d09, edge09_frustrated=bool(edge09 in base_set),
           T0=T[0], T9=T[9], deg2mpc=deg2mpc)
json.dump(out, open(os.path.join(ROOT, "data", "02_full_aut.json"), "w"), indent=1)
print("wrote data/02_full_aut.json")
