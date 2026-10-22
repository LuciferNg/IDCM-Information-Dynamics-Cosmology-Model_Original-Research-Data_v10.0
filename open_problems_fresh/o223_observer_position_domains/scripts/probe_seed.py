#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe2: seed geometry in the icosahedral frame; azimuth scan."""
import os, math
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

def axes_by_order(order):
    out = []
    for M in I:
        tr = np.trace(M)
        ang = math.degrees(math.acos(max(-1, min(1, (tr - 1) / 2))))
        if abs(ang - 360.0 / order) < 1e-6:
            w, v = np.linalg.eig(M)
            ax = np.real(v[:, int(np.argmin(np.abs(w - 1)))]); ax /= np.linalg.norm(ax)
            out.append(ax)
    arr = np.array(out)
    arr = np.array([a if a[np.argmax(np.abs(a))] > 0 else -a for a in arr])
    return np.unique(np.round(arr, 6), axis=0)

for order in (2, 3, 5):
    ax = axes_by_order(order)
    print("order %d: %d axes" % (order, len(ax)))

ax2 = axes_by_order(2); ax3 = axes_by_order(3); ax5 = axes_by_order(5)

def angs(v, axes):
    return sorted(math.degrees(math.acos(max(-1, min(1, abs(float(v @ a)))))) for a in axes)[:3]

p_RH = np.array([1.0, 1.0, phi ** 3]); p_RH /= np.linalg.norm(p_RH)
x0 = V[0]
print("\n--- angles to nearest axes (deg) ---")
print("            to 2-fold      to 3-fold      to 5-fold")
for tag, v in [("RH seed", p_RH), ("DATA seed", x0)]:
    print("%-10s  %-14s %-14s %-14s" % (tag,
          np.round(angs(v, ax2), 4), np.round(angs(v, ax3), 4), np.round(angs(v, ax5), 4)))

# seed expressed in the icosahedral frame of the nearest 5-fold / 3-fold / 2-fold axes
def frame_coords(v, ax5_, ax3_, ax2_):
    a5 = ax5_[int(np.argmax(np.abs(ax5_ @ v)))]
    a5 = a5 if a5 @ v > 0 else -a5
    a3 = ax3_[int(np.argmax(np.abs(ax3_ @ v)))]
    a3 = a3 if a3 @ v > 0 else -a3
    a2 = ax2_[int(np.argmax(np.abs(ax2_ @ v)))]
    a2 = a2 if a2 @ v > 0 else -a2
    return a5 @ v, a3 @ v, a2 @ v

print("\n--- seed cosines to nearest 5/3/2-fold axes ---")
for tag, v in [("RH seed", p_RH), ("DATA seed", x0)]:
    c5, c3, c2 = frame_coords(v, ax5, ax3, ax2)
    print("%-10s  cos5=%+.9f  cos3=%+.9f  cos2=%+.9f" % (tag, c5, c3, c2))
    print("            ang5=%.6f  ang3=%.6f  ang2=%.6f" % tuple(
        math.degrees(math.acos(max(-1, min(1, abs(x))))) for x in (c5, c3, c2)))

# azimuth scan: keep polar angle from the nearest 2-fold axis at the DATA value,
# vary azimuth, watch the edge-length split
a0 = ax2[int(np.argmax(np.abs(ax2 @ x0)))]
a0 = a0 if a0 @ x0 > 0 else -a0
theta = math.degrees(math.acos(max(-1, min(1, abs(float(x0 @ a0))))))
e1 = x0 - (x0 @ a0) * a0; e1 /= np.linalg.norm(e1)
e2 = np.cross(a0, e1)
print("\n--- azimuth scan at theta = %.4f deg (data polar angle from 2-fold axis) ---" % theta)
print("   phi(deg)   |orbit|   4 nearest (deg)                     split")
best = None
for pd in range(0, 360, 5):
    p = math.cos(math.radians(theta)) * a0 + math.sin(math.radians(theta)) * (
        math.cos(math.radians(pd)) * e1 + math.sin(math.radians(pd)) * e2)
    o = np.unique(np.round(np.array([M @ p for M in I]), 9), axis=0)
    if len(o) != 60: continue
    DD = np.degrees(np.arccos(np.clip(o @ o.T, -1, 1)))
    nn = np.sort(DD[0])[1:5]
    sp = nn.max() - nn.min()
    if pd % 30 == 0:
        print("   %7.1f   %6d   %-32s %.4f" % (pd, len(o), np.round(nn, 4), sp))
    if best is None or abs(sp - 0.0751) < best[0]:
        best = (abs(sp - 0.0751), pd, nn.copy(), sp)
print("  closest to the DATA split 0.0751: phi = %.1f  nn = %s  split = %.4f"
      % (best[1], np.round(best[2], 4), best[3]))
print("  DATA: nn = %s  split = %.4f" % (np.round(np.sort(D[0])[1:5], 4), 26.1664 - 26.0913))
