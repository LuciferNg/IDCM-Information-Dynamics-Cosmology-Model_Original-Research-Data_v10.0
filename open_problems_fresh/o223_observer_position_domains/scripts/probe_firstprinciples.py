#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""probe5: reproduce the construction; derive delta_m from first principles."""
import os, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CS = os.path.join(os.path.dirname(ROOT), "cmb_cold_spot", "data")

phi = (1 + 5 ** 0.5) / 2
inv_phi = 1 / phi

# ---- standard icosahedral frame in CARTESIAN (ICRS) coordinates ----
verts = []
for sx in (-1, 1):
    for sy in (-1, 1):
        for sz in (-1, 1):
            verts.append((sx, sy, sz))
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
def nrm(v):
    n = math.sqrt(sum(x * x for x in v))
    return tuple(x / n for x in v)
verts_n = np.array([nrm(v) for v in verts])
faces_n = np.array([nrm(v) for v in faces])
edges = []
for i in range(20):
    for j in range(i + 1, 20):
        d = np.linalg.norm(verts_n[i] - verts_n[j])
        if abs(d - 2 * math.sqrt(2) / math.sqrt(3)) < 0.01:
            mid = np.array(nrm(verts_n[i] + verts_n[j]))
            if not any(np.allclose(mid, e) or np.allclose(mid, -e) for e in edges):
                edges.append(mid)
edges_n = np.array(edges)
print("axes: %d 3-fold (verts) + %d 5-fold (faces) + %d 2-fold (edge mids)"
      % (len(verts_n), len(faces_n), len(edges_n)))

def rot(axis, ang):
    a = np.asarray(axis, float); a = a / np.linalg.norm(a)
    c, s = math.cos(ang), math.sin(ang)
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + s * K + (1 - c) * K @ K

g1 = rot(faces_n[0], 2 * math.pi / 5)
g2 = rot(verts_n[0], 2 * math.pi / 3)
group = [np.eye(3)]; seen = {tuple(np.eye(3).flatten())}; q = [np.eye(3)]
while q:
    M = q.pop(0)
    for gen in (g1, g2):
        new = gen @ M; k = tuple(np.round(new.flatten(), 10))
        if k not in seen:
            seen.add(k); group.append(new); q.append(new)
print("A5 group size:", len(group))

# ---- galactic -> ICRS (use the astropy-free equivalent) ----
def _sph(ra, dec):
    r, d = math.radians(ra), math.radians(dec)
    return np.array([math.cos(d) * math.cos(r), math.cos(d) * math.sin(r), math.sin(d)])
_xg = _sph(266.4051, -28.936175)      # galactic centre  (l=0, b=0)
_zg = _sph(192.85948, 27.12825)       # galactic north pole
_yg = np.cross(_zg, _xg)
def gal2eq_vec(l, b):
    lg, bg = math.radians(l), math.radians(b)
    return (math.cos(bg) * math.cos(lg) * _xg
            + math.cos(bg) * math.sin(lg) * _yg
            + math.sin(bg) * _zg)

L7, F7 = 29, 13
v_cs = gal2eq_vec(180 + L7, -(44 + F7))
print("\ncold spot (l,b) = (%d, %d) -> ICRS cart = (%.6f, %.6f, %.6f)"
      % (180 + L7, -(44 + F7), v_cs[0], v_cs[1], v_cs[2]))
ra = math.degrees(math.atan2(v_cs[1], v_cs[0])) % 360
dec = math.degrees(math.asin(v_cs[2]))
print("   -> RA = %.4f  Dec = %.4f" % (ra, dec))
print("   file says RA = 48.2999  Dec = -20.4373")

# ---- regenerate the orbit and compare with the file ----
orbit = []
for M in group:
    v = M @ v_cs
    if not any(np.allclose(v, o, atol=1e-6) or np.allclose(v, -o, atol=1e-6) for o in orbit):
        orbit.append(v)
orbit = np.array(orbit)
print("\nregenerated orbit size:", len(orbit))

V = np.array([[math.cos(math.radians(d)) * math.cos(math.radians(r)),
               math.cos(math.radians(d)) * math.sin(math.radians(r)),
               math.sin(math.radians(d))]
              for r, d in [tuple(map(float, l.split())) for l in open(os.path.join(CS, "a5_nodes.txt"))]])
match = []
for v in V:
    match.append(math.degrees(math.acos(min(1, float(np.max(v @ orbit.T))))))
match = np.array(match)
print("file node -> nearest regenerated node: mean %.6f  max %.6f deg"
      % (match.mean(), match.max()))

# ---- delta_m from first principles ----
def dev_from_mirror(v, axes):
    return min(90 - math.degrees(math.acos(min(1, abs(float(v @ a))))) for a in axes)
print("\n--- first-principles angles ---")
print("cold spot -> nearest 2-fold axis : %.6f deg  -> delta_m = %.6f deg"
      % (90 - dev_from_mirror(v_cs, edges_n), dev_from_mirror(v_cs, edges_n)))
print("cold spot -> nearest 3-fold axis : %.6f deg"
      % min(math.degrees(math.acos(min(1, abs(float(v_cs @ a))))) for a in verts_n))
print("cold spot -> nearest 5-fold axis : %.6f deg"
      % min(math.degrees(math.acos(min(1, abs(float(v_cs @ a))))) for a in faces_n))
print("(recorded: delta_m = 2.670063 ; 2-fold 15.8393 ; 3-fold 15.1086 ; 5-fold 22.6509)")

# ---- is delta_m convention-dependent? rotate the icosahedral frame ----
print("\n--- convention sensitivity: rotate the whole icosahedral frame ---")
rng = np.random.default_rng(7)
vals = []
for _ in range(2000):
    A = rng.normal(size=(3, 3)); Qm, _ = np.linalg.qr(A)
    if np.linalg.det(Qm) < 0: Qm[:, 0] *= -1
    vals.append(dev_from_mirror(Qm @ v_cs, edges_n))
vals = np.array(vals)
print("random frame reorientations: delta_m mean %.3f  min %.3f  max %.3f deg"
      % (vals.mean(), vals.min(), vals.max()))
print("observed (standard frame) delta_m = %.6f deg  -> percentile %.1f%%"
      % (dev_from_mirror(v_cs, edges_n), 100 * (vals <= dev_from_mirror(v_cs, edges_n)).mean()))

# ---- structural candidates for delta_m (dictionary check, no fitting) ----
d = dev_from_mirror(v_cs, edges_n)
print("\n--- structural candidate check (report only; no fitting) ---")
cands = {
    "1/phi^4 deg": math.degrees(1 / phi ** 4),
    "1/(B*L5) deg": math.degrees(1 / (4 * 11)),
    "1/21 deg": math.degrees(1 / 21),
    "phi^-1/4 deg": math.degrees(inv_phi / 4),
    "180/67.4 deg": 180 / 67.4,
}
for k, v in cands.items():
    print("   %-14s = %.6f  (dev %.3f%%)" % (k, v, 100 * abs(v - d) / d))
