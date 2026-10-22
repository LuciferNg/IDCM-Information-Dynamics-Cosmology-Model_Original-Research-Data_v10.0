#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O223 scripts/03 -- odd-face / frustration bijection, colour-temperature coupling,
                   anchor-pair structure, and the STRAIN vs the ideal RH position.
==============================================================================
Resolves the red flag inherited from cmb_cold_spot/data/graph_identity.txt
("F=51, Euler=-9, 真五邊形面: 1, 身份: 待定"): the correct face set is obtained
from the geometric rotation system (script 04), giving F = 62 = 20 tri + 30 quad
+ 12 pent, chi = 2 -> the graph IS the rhombicosidodecahedron skeleton.
graph_identity.txt's F=51 / Euler=-9 was a face-finding failure, not a structure.

Then:
 (a) frustrated edge <-> odd face bijection
 (b) colour vs temperature coupling strength
 (c) the 30-pattern / 2-anchor (diameter-pair) orbit structure
 (d) strain of the node positions vs the ideal RH orbit (1,1,phi^3)

ASCII only.  /usr/bin/python3.
"""
import os, math, json
import numpy as np
from collections import deque, Counter

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
V = np.array([sph(*n) for n in nodes]); N = 60
D = np.degrees(np.arccos(np.clip(V @ V.T, -1, 1)))
dss = np.sort(D[np.triu_indices(N, 1)]); thr = (dss[119] + dss[120]) / 2
A = (D < thr); np.fill_diagonal(A, False)
nbr = {i: [int(j) for j in np.where(A[i])[0]] for i in range(N)}
E = int(A.sum() // 2)

print("="*74)
print("O223 / 03 -- odd-face bijection, couplings, orbit, strain")
print("="*74)

print("[L] edge-length spectrum")
l1 = np.round(dss[:60], 6); l2 = np.round(dss[60:120], 6)
print("    group A (60 edges): %.6f .. %.6f" % (l1.min(), l1.max()))
print("    group B (60 edges): %.6f .. %.6f" % (l2.min(), l2.max()))
print("    gap to next: %.4f -> %.4f  (gap = %.4f)"
      % (dss[119], dss[120], dss[120] - dss[119]))
check("L1 exactly two edge-length families (60 + 60), clean gap",
      l1.max() - l1.min() < 1e-3 and l2.max() - l2.min() < 1e-3
      and dss[120] - dss[119] > 4)

# ---------------------------------------------------------------- faces
print("[M] face set from the geometric rotation system")
rot = {}
for v in range(N):
    n = V[v]
    e1 = V[nbr[v][0]] - n * (V[nbr[v][0]] @ n); e1 /= np.linalg.norm(e1)
    e2 = np.cross(n, e1)
    order = []
    for w in nbr[v]:
        d = V[w] - n * (V[w] @ n)
        order.append((math.atan2(d @ e2, d @ e1), w))
    order.sort()
    rot[v] = [w for _, w in order]

def next_dir(u, v):
    i = rot[v].index(u)
    return v, rot[v][(i - 1) % len(rot[v])]

seen = set(); faces = []
for u in range(N):
    for v in nbr[u]:
        if (u, v) in seen:
            continue
        f = []; cu, cv = u, v
        while (cu, cv) not in seen:
            seen.add((cu, cv)); f.append(cu)
            cu, cv = next_dir(cu, cv)
        if f:
            faces.append(f)
fs = Counter(len(f) for f in faces)
print("    F = %d   sizes = %s   chi = %d" % (len(faces), dict(sorted(fs.items())),
                                              N - E + len(faces)))
check("M1 F = 62 (20 triangles + 30 quads + 12 pentagons)", len(faces) == 62)
check("M2 chi = 2 -> planar embedding, genus 0 (RH skeleton)",
      N - E + len(faces) == 2)
check("M3 exactly 20 triangles / 30 quads / 12 pentagons",
      (fs.get(3), fs.get(4), fs.get(5)) == (20, 30, 12))
tri_f = [f for f in faces if len(f) == 3]
pent_f = [f for f in faces if len(f) == 5]
vt = Counter()
for f in tri_f:
    for v in f:
        vt[v] += 1
check("M4 every vertex lies in exactly 1 triangle (RH vertex figure)",
      all(vt[v] == 1 for v in range(N)))

# ---------------------------------------------------------------- frustration
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
frust = set(frozenset((i, j)) for i in range(N) for j in nbr[i]
            if i < j and c0[i] == c0[j])
print("[N] frustration set vs odd faces")
print("    |frustration| = %d   odd faces = %d" % (len(frust), len(tri_f) + len(pent_f)))
check("N1 32 frustrated edges = 20 triangles + 12 pentagons",
      len(frust) == 32 and len(tri_f) + len(pent_f) == 32)
odd = tri_f + pent_f
per_face = [sum(1 for i in range(len(f))
                if frozenset((f[i], f[(i + 1) % len(f)])) in frust) for f in odd]
print("    frustrated edges per odd face: %s" % dict(Counter(per_face)))
check("N2 every odd face contains exactly 1 frustrated edge",
      all(x == 1 for x in per_face))
check("N3 the 32 frustrated edges are 32 distinct odd faces (bijection)",
      len(set(frozenset((f[i], f[(i + 1) % len(f)])) for f in odd for i in range(len(f))
              if frozenset((f[i], f[(i + 1) % len(f)])) in frust)) == 32)

# ---------------------------------------------------------------- coupling
print("[O] colour vs temperature coupling")
T = {}
for line in open(os.path.join(CS, "smica_smoothed.txt")):
    if line.startswith("#"):
        continue
    p = line.split()
    T[int(p[0])] = float(p[2])
Tv = np.array([T[k] for k in range(N)])
cv = np.array([c0[k] for k in range(N)])
r = float(np.corrcoef(cv, Tv)[0, 1])
m1 = Tv[cv == 1].mean(); m0 = Tv[cv == 0].mean()
agree = int(((cv == 1) & (Tv < 0)).sum() + ((cv == 0) & (Tv > 0)).sum())
print("    Pearson r(colour,T) = %+.3f   gap = %+.1f uK   sign agreement %d/60"
      % (r, m1 - m0, agree))
check("O1 |r| < 0.35 (colour does NOT determine the temperature sign)", abs(r) < 0.35)
check("O2 cold-labelled mean < hot-labelled mean (set-level tendency)", m1 < m0)

# ---------------------------------------------------------------- orbit
print("[P] anchor-pair structure of the frustration orbit")
pat = {}
for a in range(N):
    ca = bfs_color(a)
    pat[a] = frozenset(frozenset((i, j)) for i in range(N) for j in nbr[i]
                       if i < j and ca[i] == ca[j])
groups = {}
for a, s in pat.items():
    groups.setdefault(s, []).append(a)
antip = {a: int(np.argmax(D[a])) for a in range(N)}
print("    distinct patterns = %d   group sizes = %s"
      % (len(groups), dict(Counter(len(v) for v in groups.values()))))
check("P1 30 distinct frustration patterns", len(groups) == 30)
check("P2 every pattern realised by exactly 2 anchors",
      all(len(v) == 2 for v in groups.values()))
ok = sum(1 for v in groups.values() if antip[v[0]] == v[1])
check("P3 the 2 anchors of each pattern are the graph-diameter pair", ok == len(groups))

# ---------------------------------------------------------------- strain
print("[Q] strain of the node set vs the ideal RH orbit (1,1,phi^3)")
phi = (1 + 5 ** 0.5) / 2
def qmul(a, b):
    w1, x1, y1, z1 = a; w2, x2, y2, z2 = b
    return np.array([w1*w2 - x1*x2 - y1*y2 - z1*z2,
                     w1*x2 + x1*w2 + y1*z2 - z1*y2,
                     w1*y2 - x1*z2 + y1*w2 + z1*x2,
                     w1*z2 + x1*y2 - y1*x2 + z1*w2])
def q2m(q):
    w, x, y, z = q
    return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                     [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                     [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])
s = (1 + 5 ** 0.5) / 4
gens = [np.array([0.5, 0.5, 0.5, 0.5]), np.array([0.5, s, 1 / (4 * s), 0.0]),
        np.array([0.5, 0.0, s, 1 / (4 * s)])]
sq = set(); QL = []; stack = [np.array([1.0, 0, 0, 0])]
while stack:
    q = stack.pop(); q = q / np.linalg.norm(q); k = tuple(np.round(q, 8))
    if k in sq:
        continue
    sq.add(k); QL.append(q)
    for g in gens:
        stack.append(qmul(q, g))
Gm = []
for q in QL:
    M = q2m(q)
    if not any(np.allclose(M, N2, atol=1e-9) for N2 in Gm):
        Gm.append(M)
p = np.array([1.0, 1.0, phi ** 3]); p /= np.linalg.norm(p)
RH = np.array([M @ p for M in Gm])
print("    ideal RH orbit size = %d" % len(np.unique(np.round(RH, 6), axis=0)))
DRH = np.degrees(np.arccos(np.clip(RH @ RH.T, -1, 1)))
rh_shells = sorted(set(np.round(DRH[0][DRH[0] > 1e-6], 3)))
dt_shells = sorted(set(np.round(D[0][D[0] > 1e-6], 3)))
print("    ideal RH shells from a vertex: %s" % rh_shells[:6])
print("    DATA   shells from node 0   : %s" % dt_shells[:6])
e_rh = 25.8786
print("    ideal RH edge = %.4f deg ; data edges = %.4f / %.4f deg"
      % (e_rh, l1.mean(), l2.mean()))
d_shell1 = abs(dt_shells[0] - rh_shells[0])
print("    nearest-shell shift = %.4f deg (%.3f%%)"
      % (d_shell1, 100 * d_shell1 / e_rh))
check("Q1 the data node set deviates from the ideal RH orbit (strain > 0.1 deg)",
      d_shell1 > 0.1, "shift = %.4f deg" % d_shell1)
check("Q2 the ideal RH has a single edge length (4 equal nearest neighbours)",
      np.ptp(np.sort(DRH[0])[1:5]) < 1e-6,
      "spread = %.6f deg" % np.ptp(np.sort(DRH[0])[1:5]))
print("    relative strain of edges: A +%.3f%%, B +%.3f%%"
      % (100 * (l1.mean() / e_rh - 1), 100 * (l2.mean() / e_rh - 1)))
# chirality angle: deficit from perfect antipodality of the diameter pair
diam = float(D[0, int(np.argmax(D[0]))])
chi_ang = 180.0 - diam
print("    diameter pair (0,57): d = %.4f deg  -> chirality angle = 180 - d = %.4f deg"
      % (diam, chi_ang))
check("Q3 chirality angle 180 - d(0,57) = 5.3401 deg (matches O213 R5 improper 5.3402)",
      abs(chi_ang - 5.3402) < 0.001, "%.4f deg" % chi_ang)

print("-"*74)
npass = sum(1 for _, o, _ in res if o); ntot = len(res)
print("RESULT: %d/%d PASS" % (npass, ntot))
print("-"*74)
out = dict(n_pass=npass, n_total=ntot, F=len(faces), face_sizes=dict(fs),
           chi=N - E + len(faces), n_frustration=len(frust),
           pearson_r=r, gap_uK=float(m1 - m0), sign_agreement=agree,
           n_patterns=len(groups), antipodal_ok=ok,
           edge_A_mean=float(l1.mean()), edge_B_mean=float(l2.mean()),
           ideal_RH_edge=25.8786,
           strain_A_pct=float(100 * (l1.mean() / 25.8786 - 1)),
           strain_B_pct=float(100 * (l2.mean() / e_rh - 1)),
           nearest_shell_shift_deg=float(d_shell1),
           rh_shells=[float(x) for x in rh_shells[:6]],
           data_shells=[float(x) for x in dt_shells[:6]])
json.dump(out, open(os.path.join(ROOT, "data", "03_graph_identity.json"), "w"), indent=1)
print("wrote data/03_graph_identity.json")
