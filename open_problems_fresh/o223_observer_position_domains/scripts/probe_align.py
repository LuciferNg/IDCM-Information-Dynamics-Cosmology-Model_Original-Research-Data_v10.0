#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe4: is node 0 the cold spot? is the data orbit a tilted RH orbit?"""
import os, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CS = os.path.join(os.path.dirname(ROOT), "cmb_cold_spot", "data")

def sph(ra, dec):
    r, d = math.radians(ra), math.radians(dec)
    return np.array([math.cos(d)*math.cos(r), math.cos(d)*math.sin(r), math.sin(d)])

# galactic -> equatorial (J2000)
NGP = sph(192.85948, 27.12825)
GC  = sph(266.4051, -28.936175)
def gal2eq(l, b):
    # build equatorial coords of galactic basis
    xg = GC                                    # l=0,b=0
    zg = NGP
    yg = np.cross(zg, xg)
    lg, bg = math.radians(l), math.radians(b)
    v = math.cos(bg)*math.cos(lg)*xg + math.cos(bg)*math.sin(lg)*yg + math.sin(bg)*zg
    ra = math.degrees(math.atan2(v[1], v[0])) % 360
    dec = math.degrees(math.asin(v[2]))
    return ra, dec

print("=== node 0 = cold spot? ===")
print("node 0 in a5_nodes.txt: RA=48.2999  Dec=-20.4373")
ra, dec = gal2eq(209.0, -57.0)
print("cold spot (l,b)=(209,-57) -> RA=%.4f  Dec=%.4f" % (ra, dec))
for l in (209.0,):
    for b in (-57.0,):
        r2, d2 = gal2eq(l, b)
        print("   residual: dRA=%.4f  dDec=%.4f deg" % (r2 - 48.2999, d2 + 20.4373))

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

p_RH = np.array([1.0, 1.0, phi ** 3]); p_RH /= np.linalg.norm(p_RH)
RH = np.unique(np.round(np.array([M @ p_RH for M in I]), 9), axis=0)
print("\n=== data orbit vs RH orbit ===")
print("RH orbit size:", len(RH))
dev = []
for v in V:
    dev.append(math.degrees(math.acos(min(1, float(np.max(v @ RH.T))))))
dev = np.array(dev)
print("angle from each data node to nearest RH node: mean %.6f  max %.6f  min %.6f"
      % (dev.mean(), dev.max(), dev.min()))

# best matching RH vertex for node 0
j = int(np.argmax(V[0] @ RH.T))
pstar = RH[j]
ang = math.degrees(math.acos(min(1, float(V[0] @ pstar))))
print("\nnode 0 -> nearest RH vertex: %.6f deg" % ang)

# mirror axes of the icosahedral group
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

# which mirror plane is pstar on?
perp = [abs(float(pstar @ a)) for a in ax2]
am = ax2[int(np.argmin(perp))]
print("pstar . a_mirror = %.3e (pstar lies on this mirror plane)" % float(pstar @ am))

# decompose the displacement V[0] - pstar
v = V[0] - pstar
out = float(v @ am)
inpl = v - out * am
print("\n--- displacement node0 - nearest_RH ---")
print("  total angle          = %.6f deg" % ang)
print("  out-of-mirror-plane  = %.6f deg" % math.degrees(math.asin(min(1, abs(out)))))
print("  in-plane             = %.6f deg" % math.degrees(math.asin(min(1, float(np.linalg.norm(inpl))))))
print("  (delta_m from the 2-fold axis test = 2.670063 deg)")

# seed angles to symmetry axes for pstar and node 0
def axes_by_order(order):
    out = []
    for M in I:
        tr = np.trace(M)
        a = math.degrees(math.acos(max(-1, min(1, (tr - 1) / 2))))
        if abs(a - 360.0/order) < 1e-6:
            w, vv = np.linalg.eig(M)
            ax = np.real(vv[:, int(np.argmin(np.abs(w - 1)))]); ax /= np.linalg.norm(ax)
            out.append(ax)
    arr = np.array(out)
    arr = np.array([a if a[np.argmax(np.abs(a))] > 0 else -a for a in arr])
    return np.unique(np.round(arr, 6), axis=0)
ax3 = axes_by_order(3); ax5 = axes_by_order(5)
print("\n--- seed angles to nearest symmetry axes (deg) ---")
print("           2-fold      3-fold      5-fold")
for tag, v2 in [("RH pstar", pstar), ("node 0", V[0])]:
    a2 = min(math.degrees(math.acos(min(1, abs(float(v2 @ a))))) for a in ax2)
    a3 = min(math.degrees(math.acos(min(1, abs(float(v2 @ a))))) for a in ax3)
    a5 = min(math.degrees(math.acos(min(1, abs(float(v2 @ a))))) for a in ax5)
    print("%-10s  %-11.4f %-11.4f %-11.4f" % (tag, a2, a3, a5))
