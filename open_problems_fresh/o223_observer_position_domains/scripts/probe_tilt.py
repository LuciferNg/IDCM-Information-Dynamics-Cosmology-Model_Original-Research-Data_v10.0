#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe3: is the strain exactly the mirror-plane tilt of the RH seed?"""
import os, math
import numpy as np

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

ax2 = []
for M in I:
    if abs(np.trace(M) + 1) < 1e-8:
        w, v = np.linalg.eig(M)
        ax = np.real(v[:, int(np.argmin(np.abs(w - 1)))]); ax /= np.linalg.norm(ax)
        ax2.append(ax)
ax2 = np.array(ax2)
ax2 = np.array([a if a[np.argmax(np.abs(a))] > 0 else -a for a in ax2])
ax2 = np.unique(np.round(ax2, 6), axis=0)
print("2-fold axes:", len(ax2))

p_RH = np.array([1.0, 1.0, phi ** 3]); p_RH /= np.linalg.norm(p_RH)
x0 = V[0]
# mirror axis = the one closest to perpendicular
devs = [90 - math.degrees(math.acos(max(-1, min(1, abs(float(p_RH @ a)))))) for a in ax2]
a_mirror = ax2[int(np.argmin(devs))]
print("p_RH . a_mirror = %.3e (should be 0)" % float(p_RH @ a_mirror))
print("x0   . a_mirror = %+.9f  -> angle %.6f deg" % (float(x0 @ a_mirror),
      math.degrees(math.acos(min(1, abs(float(x0 @ a_mirror)))))))
print("dist(x0, p_RH) = %.6f deg" % math.degrees(math.acos(min(1, float(x0 @ p_RH)))))

def spectrum(p):
    o = np.unique(np.round(np.array([M @ p for M in I]), 9), axis=0)
    if len(o) != 60: return None
    DD = np.degrees(np.arccos(np.clip(o @ o.T, -1, 1)))
    return np.sort(DD[0])[1:5]

print("\n--- tilt toward +a_mirror ---")
for d in [1.0, 2.0, 2.5, 2.670063, 2.8, 3.0]:
    p = math.cos(math.radians(d)) * p_RH + math.sin(math.radians(d)) * a_mirror
    p /= np.linalg.norm(p)
    sp = spectrum(p)
    print("  d=%7.4f  nn=%s  split=%.4f  dist_to_x0=%.4f deg"
          % (d, np.round(sp, 4), sp.max() - sp.min(),
             math.degrees(math.acos(min(1, abs(float(p @ x0)))))))
print("--- tilt toward -a_mirror ---")
for d in [1.0, 2.0, 2.5, 2.670063, 2.8, 3.0]:
    p = math.cos(math.radians(d)) * p_RH - math.sin(math.radians(d)) * a_mirror
    p /= np.linalg.norm(p)
    sp = spectrum(p)
    print("  d=%7.4f  nn=%s  split=%.4f  dist_to_x0=%.4f deg"
          % (d, np.round(sp, 4), sp.max() - sp.min(),
             math.degrees(math.acos(min(1, abs(float(p @ x0)))))))
print("  DATA     nn=%s  split=%.4f" % (np.round(np.sort(D[0])[1:5], 4), 26.1664 - 26.0913))

# in-plane component of the x0 - p_RH displacement
v = x0 - p_RH
perp = v - (v @ a_mirror) * a_mirror
print("\n|displacement| = %.6f deg ; along mirror-normal = %.6f deg ; in-plane = %.6f deg"
      % (math.degrees(math.acos(min(1, float(x0 @ p_RH)))),
         math.degrees(math.asin(min(1, abs(float(x0 @ a_mirror))))),
         math.degrees(math.asin(min(1, float(np.linalg.norm(perp)))))))
