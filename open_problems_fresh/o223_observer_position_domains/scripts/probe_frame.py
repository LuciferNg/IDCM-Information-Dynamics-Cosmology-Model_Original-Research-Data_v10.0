#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe6: DECISIVE -- which 2-fold axis set is V's true symmetry group?"""
import os, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CS = os.path.join(os.path.dirname(ROOT), "cmb_cold_spot", "data")

phi = (1 + 5 ** 0.5) / 2
inv_phi = 1 / phi

def nrm(v):
    n = math.sqrt(sum(x * x for x in v))
    return tuple(x / n for x in v)

verts = [(sx, sy, sz) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
for sx in (-1, 1):
    for sy in (-1, 1):
        verts.append((0, sx * inv_phi, sy * phi))
        verts.append((sx * inv_phi, sy * phi, 0))
        verts.append((sx * phi, 0, sy * inv_phi))
faces = []
for sx in (-1, 1):
    for sy in (-1, 1):
        faces.append((0, sx, sy * phi))
        faces.append((sx, sy * phi, 0))
        faces.append((sx * phi, 0, sy))
verts_n = np.array([nrm(v) for v in verts]); faces_n = np.array([nrm(v) for v in faces])
edges = []
for i in range(20):
    for j in range(i + 1, 20):
        d = np.linalg.norm(verts_n[i] - verts_n[j])
        if abs(d - 2 * math.sqrt(2) / math.sqrt(3)) < 0.01:
            mid = np.array(nrm(verts_n[i] + verts_n[j]))
            if not any(np.allclose(mid, e) or np.allclose(mid, -e) for e in edges):
                edges.append(mid)
edges_n = np.array(edges)

def rot(axis, ang):
    a = np.asarray(axis, float); a = a / np.linalg.norm(a)
    c, s = math.cos(ang), math.sin(ang)
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + s * K + (1 - c) * K @ K

g1 = rot(faces_n[0], 2 * math.pi / 5); g2 = rot(verts_n[0], 2 * math.pi / 3)
def build(gens):
    grp = [np.eye(3)]; seen = {tuple(np.eye(3).flatten())}; q = [np.eye(3)]
    while q:
        M = q.pop(0)
        for g in gens:
            new = g @ M; k = tuple(np.round(new.flatten(), 10))
            if k not in seen:
                seen.add(k); grp.append(new); q.append(new)
    return grp
Gs = build([g1, g2])              # script's group (standard frame)
print("script group size:", len(Gs))

# quaternion group (O213 frame)
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
Gq = []
# build quaternion group directly
qq = [np.array([1.0, 0, 0, 0])]; seenq = {tuple(np.round(qq[0], 8))}; st = [qq[0]]
gens_q = [np.array([0.5, 0.5, 0.5, 0.5]), np.array([0.5, s, 1/(4*s), 0.0]), np.array([0.5, 0.0, s, 1/(4*s)])]
while st:
    q = st.pop(); q = q / np.linalg.norm(q); k = tuple(np.round(q, 8))
    if k in seenq: continue
    seenq.add(k); qq.append(q)
    for g in gens_q: st.append(qmul(q, g))
Gq = []
for q in qq:
    M = q2m(q)
    if not any(np.allclose(M, N2, atol=1e-9) for N2 in Gq): Gq.append(M)
print("quaternion group size:", len(Gq))

# are they the same set?
same = len(Gs) == len(Gq) and all(any(np.allclose(A, B, atol=1e-8) for B in Gq) for A in Gs)
print("Gs == Gq ?", same)

V = np.array([[math.cos(math.radians(d)) * math.cos(math.radians(r)),
               math.cos(math.radians(d)) * math.sin(math.radians(r)),
               math.sin(math.radians(d))]
              for r, d in [tuple(map(float, l.split())) for l in open(os.path.join(CS, "a5_nodes.txt"))]])

def invariant(V, G, tol=1e-5):
    worst = 0.0
    for M in G:
        W = V @ M.T
        for w in W:
            worst = max(worst, math.degrees(math.acos(min(1, float(np.max(V @ w))))))
    return worst

print("\n--- is V invariant under each group? (max residual deg) ---")
print("  under Gs:", "%.8f" % invariant(V, Gs))
print("  under Gq:", "%.8f" % invariant(V, Gq))

def axes2(G):
    out = []
    for M in G:
        if abs(np.trace(M) + 1) < 1e-8:
            w, v = np.linalg.eig(M)
            ax = np.real(v[:, int(np.argmin(np.abs(w - 1)))]); ax /= np.linalg.norm(ax)
            out.append(ax)
    arr = np.array(out)
    arr = np.array([a if a[np.argmax(np.abs(a))] > 0 else -a for a in arr])
    return np.unique(np.round(arr, 6), axis=0)

def dvm(v, axes):
    return min(90 - math.degrees(math.acos(min(1, abs(float(v @ a))))) for a in axes)

a_s, a_q = axes2(Gs), axes2(Gq)
print("\n--- 2-fold axes ---")
print("  Gs axes:", len(a_s), " Gq axes:", len(a_q))
print("  identical sets?", len(a_s) == len(a_q) and all(any(np.allclose(x, y, atol=1e-6) for y in a_q) for x in a_s))
print("\n--- delta_m (deviation of node 0 from the nearest mirror plane) ---")
print("  using Gs axes: %.6f deg" % dvm(V[0], a_s))
print("  using Gq axes: %.6f deg" % dvm(V[0], a_q))
print("  using edges_n : %.6f deg" % dvm(V[0], edges_n))
print("  (O213/O223 recorded delta_m = 2.670063)")

# the mirror axis at ~87.33 deg for each set
for tag, ax in (("Gs", a_s), ("Gq", a_q)):
    angs = sorted(90 - math.degrees(math.acos(min(1, abs(float(V[0] @ a))))) for a in ax)
    print("  %s nearest-to-perpendicular deviations: %s" % (tag, np.round(angs[:4], 6)))
