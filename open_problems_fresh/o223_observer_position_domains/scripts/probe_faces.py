#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe: face-resolved edge lengths + seed mirror deviation."""
import os, math, json
import numpy as np
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CS = os.path.join(os.path.dirname(ROOT), "cmb_cold_spot", "data")

def sph(ra, dec):
    r, d = math.radians(ra), math.radians(dec)
    return np.array([math.cos(d)*math.cos(r), math.cos(d)*math.sin(r), math.sin(d)])

V = np.array([sph(*tuple(map(float, l.split()))) for l in open(os.path.join(CS, "a5_nodes.txt"))])
N = 60
D = np.degrees(np.arccos(np.clip(V @ V.T, -1, 1)))
dss = np.sort(D[np.triu_indices(N, 1)]); thr = (dss[119] + dss[120]) / 2
A = (D < thr); np.fill_diagonal(A, False)
nbr = {i: [int(j) for j in np.where(A[i])[0]] for i in range(N)}

# rotation system -> faces
rot = {}
for v in range(N):
    n = V[v]
    e1 = V[nbr[v][0]] - n * (V[nbr[v][0]] @ n); e1 /= np.linalg.norm(e1)
    e2 = np.cross(n, e1)
    o = sorted((math.atan2((V[w]-n*(V[w]@n)) @ e2, (V[w]-n*(V[w]@n)) @ e1), w) for w in nbr[v])
    rot[v] = [w for _, w in o]
def nd(u, v):
    i = rot[v].index(u); return v, rot[v][(i-1) % len(rot[v])]
seen = set(); faces = []
for u in range(N):
    for v in nbr[u]:
        if (u, v) in seen: continue
        f = []; cu, cv = u, v
        while (cu, cv) not in seen:
            seen.add((cu, cv)); f.append(cu); cu, cv = nd(cu, cv)
        if f: faces.append(f)
fs = Counter(len(f) for f in faces)
print("faces:", dict(fs))

# edge length per face type
print("\n=== face-resolved edge lengths ===")
for k in (3, 4, 5):
    sub = [f for f in faces if len(f) == k]
    rows = []
    for f in sub:
        L = [D[f[i], f[(i+1) % len(f)]] for i in range(len(f))]
        rows.append(L)
    arr = np.array(rows)
    print("  %d-gons (n=%d): edge-length pattern" % (k, len(sub)))
    for i in range(k):
        col = arr[:, i]
        print("     edge slot %d: %.4f .. %.4f  (unique rounded: %s)"
              % (i, col.min(), col.max(), sorted(set(np.round(col, 4).tolist()))[:4]))
    print("     all edges: unique = %s" % sorted(set(np.round(arr.flatten(), 4).tolist())))

# which edges are long vs short -> what faces do they bound
long_set = set()
for i in range(N):
    for j in nbr[i]:
        if i < j and D[i, j] > (dss[59] + dss[60]) / 2:
            long_set.add(frozenset((i, j)))
print("\nlong edges: %d, short edges: %d" % (len(long_set), 120 - len(long_set)))
cnt = Counter()
for f in faces:
    for i in range(len(f)):
        e = frozenset((f[i], f[(i+1) % len(f)]))
        cnt[(len(f), e in long_set)] += 1
print("face-type x edge-length incidence:", dict(cnt))

# icosahedral group + 2-fold axes
phi = (1 + 5 ** 0.5) / 2
def qmul(a, b):
    w1, x1, y1, z1 = a; w2, x2, y2, z2 = b
    return np.array([w1*w2-x1*x2-y1*y2-z1*z2, w1*x2+x1*w2+y1*z2-z1*y2,
                     w1*y2-x1*z2+y1*w2+z1*x2, w1*z2+x1*y2-y1*x2+z1*w2])
def q2m(q):
    w, x, y, z = q
    return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)],
                     [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)],
                     [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])
s = (1 + 5 ** 0.5) / 4
gens = [np.array([0.5, 0.5, 0.5, 0.5]), np.array([0.5, s, 1/(4*s), 0.0]), np.array([0.5, 0.0, s, 1/(4*s)])]
seenq = set(); QL = []; st = [np.array([1.0, 0, 0, 0])]
while st:
    q = st.pop(); q = q / np.linalg.norm(q); k = tuple(np.round(q, 8))
    if k in seenq: continue
    seenq.add(k); QL.append(q)
    for g in gens: st.append(qmul(q, g))
I = []
for q in QL:
    M = q2m(q)
    if not any(np.allclose(M, N2, atol=1e-9) for N2 in I): I.append(M)
print("\n|I| =", len(I))
# 2-fold axes: trace = -1
axes = []
for M in I:
    if abs(np.trace(M) + 1) < 1e-8:
        w, v = np.linalg.eig(M)
        ax = np.real(v[:, int(np.argmin(np.abs(w - 1)))]); ax /= np.linalg.norm(ax)
        axes.append(ax)
ax2 = np.unique(np.round(np.array(axes), 6), axis=0)
ax2 = np.array([a if a[np.argmax(np.abs(a))] > 0 else -a for a in ax2])
ax2 = np.unique(np.round(ax2, 6), axis=0)
print("2-fold axes:", len(ax2), "(expect 15)")

p_RH = np.array([1.0, 1.0, phi ** 3]); p_RH /= np.linalg.norm(p_RH)
devs = [90 - math.degrees(math.acos(max(-1, min(1, float(abs(p_RH @ a)))))) for a in ax2]
k = int(np.argmin(devs)); a_near = ax2[k]
print("p_RH -> nearest 2-fold axis: %.6f deg (90 expected)" % math.degrees(math.acos(abs(float(p_RH @ a_near)))))

x0 = V[0]
devs0 = [90 - math.degrees(math.acos(max(-1, min(1, float(abs(x0 @ a)))))) for a in ax2]
k0 = int(np.argmin(devs0)); a0 = ax2[k0]
ang = math.degrees(math.acos(max(-1, min(1, float(abs(x0 @ a0))))))
print("DATA seed (node 0) -> nearest 2-fold axis: %.4f deg -> delta_m = %.6f deg" % (ang, 90 - ang))

# RH orbit edge lengths vs tilt delta about a_near (same azimuth as data seed)
print("\n=== edge-length spectrum of I * p(delta) vs tilt off the mirror plane ===")
def orb_edges(p, tag):
    o = np.array([M @ p for M in I])
    o = np.unique(np.round(o, 9), axis=0)
    if len(o) != 60:
        return None
    DD = np.degrees(np.arccos(np.clip(o @ o.T, -1, 1)))
    nn = np.sort(DD[0])[1:5]
    return len(o), nn
for d in [0.0, 0.5, 1.0, 2.0, 2.670063, 3.0, 4.0, 5.0]:
    p = math.cos(math.radians(d)) * p_RH + math.sin(math.radians(d)) * a_near
    p /= np.linalg.norm(p)
    r = orb_edges(p, d)
    if r:
        print("  delta = %7.4f deg -> |orbit|=%d  4 nearest = %s" % (d, r[0], np.round(r[1], 4)))
# data
print("  DATA                        |orbit|=60  4 nearest = %s" % np.round(np.sort(D[0])[1:5], 4))
