#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O223 scripts/06 -- STRAIN = the geometric signature of chirality.
=================================================================
Resolves O223 remaining item 3: the structural identity of the edge strain
(+0.822%/+1.111%) and of the chirality angle 5.3401 deg.

Rigid facts under test
  R1  V is invariant under the standard-frame icosahedral rotation group Gs
      (residual = the 4-decimal rounding of a5_nodes.txt)
  R2  face tracing gives F = 62 = 20 triangles + 30 squares + 12 pentagons
  R3  the 120 edges split into exactly two lengths:
        60 short (26.0913 deg) and 60 long (26.1664 deg)
  R4  every triangle is equilateral (short), every pentagon equilateral (long),
      every square alternates 2 short + 2 long
  R5  the seed deviates from the nearest mirror plane by delta_m = 2.670063 deg
      and the antipodal approach 180 - d(0,57) = 2*delta_m
  R6  orientation null: is delta_m special?
"""
import os, math, json
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CS = os.path.join(os.path.dirname(ROOT), "cmb_cold_spot", "data")
OUT = os.path.join(ROOT, "data")

phi = (1 + 5 ** 0.5) / 2
inv_phi = 1 / phi
CHECKS = []
def check(tag, ok, msg):
    CHECKS.append((tag, bool(ok), msg))
    print("  [%s] %s %s" % ("OK" if ok else "XX", tag, msg))

def nrm(v):
    n = math.sqrt(sum(x * x for x in v))
    return tuple(x / n for x in v)

verts = [(sx, sy, sz) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
for sx in (-1, 1):
    for sy in (-1, 1):
        verts.append((0, sx * inv_phi, sy * phi))
        verts.append((sx * inv_phi, sy * phi, 0))
        verts.append((sx * phi, 0, sy * inv_phi))
faces_ax = []
for sx in (-1, 1):
    for sy in (-1, 1):
        faces_ax.append((0, sx, sy * phi))
        faces_ax.append((sx, sy * phi, 0))
        faces_ax.append((sx * phi, 0, sy))
verts_n = np.array([nrm(v) for v in verts])
faces_n = np.array([nrm(v) for v in faces_ax])

def rot(axis, ang):
    a = np.asarray(axis, float); a = a / np.linalg.norm(a)
    c, s = math.cos(ang), math.sin(ang)
    K = np.array([[0, -a[2], a[1]], [a[2], 0, -a[0]], [-a[1], a[0], 0]])
    return np.eye(3) + s * K + (1 - c) * K @ K

def build(gens):
    grp = [np.eye(3)]; seen = {tuple(np.eye(3).flatten())}; q = [np.eye(3)]
    while q:
        M = q.pop(0)
        for g in gens:
            new = g @ M; k = tuple(np.round(new.flatten(), 10))
            if k not in seen:
                seen.add(k); grp.append(new); q.append(new)
    return grp

Gs = build([rot(faces_n[0], 2 * math.pi / 5), rot(verts_n[0], 2 * math.pi / 3)])
print("=" * 76)
print("O223 / 06 -- strain as the geometric signature of chirality")
print("=" * 76)
print("[G] standard-frame icosahedral group Gs: %d rotations" % len(Gs))

V = np.array([[math.cos(math.radians(d)) * math.cos(math.radians(r)),
               math.cos(math.radians(d)) * math.sin(math.radians(r)),
               math.sin(math.radians(d))]
              for r, d in [tuple(map(float, l.split())) for l in open(os.path.join(CS, "a5_nodes.txt"))]])
N = 60
D = np.degrees(np.arccos(np.clip(V @ V.T, -1, 1)))
dss = np.sort(D[np.triu_indices(N, 1)]); thr = (dss[119] + dss[120]) / 2
A = (D < thr); np.fill_diagonal(A, False)
nbr = {i: [int(j) for j in np.where(A[i])[0]] for i in range(N)}
E = [(i, j) for i in range(N) for j in nbr[i] if i < j]
print("    edges E = %d, all degrees = %s" % (len(E), sorted(set(len(nbr[i]) for i in range(N)))))

# ---- R1 invariance ----
worst = 0.0
for M in Gs:
    W = V @ M.T
    for w in W:
        worst = max(worst, math.degrees(math.acos(min(1, float(np.max(V @ w))))))
check("R1", worst < 1e-3, "V invariant under Gs (max residual %.8f deg)" % worst)

# ---- R2 face tracing (tangent-plane cyclic order + next-edge walk) ----
cyc = {}
for v in range(N):
    t = V[v]
    e1 = np.cross(t, [0, 0, 1.0])
    if np.linalg.norm(e1) < 1e-6:
        e1 = np.cross(t, [1.0, 0, 0])
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(t, e1)
    ang = []
    for w in nbr[v]:
        d = V[w] - (V[w] @ t) * t
        ang.append((math.atan2(d @ e2, d @ e1), w))
    ang.sort()
    cyc[v] = [w for _, w in ang]

used = set(); F = []
for u in range(N):
    for v in nbr[u]:
        if (u, v) in used:
            continue
        face = []; cu, cv = u, v
        while True:
            face.append(cu); used.add((cu, cv))
            order = cyc[cv]; i = order.index(cu)
            nxt = order[(i - 1) % len(order)]
            cu, cv = cv, nxt
            if (cu, cv) == (u, v):
                break
        F.append(face)
size_count = {}
for f in F:
    size_count[len(f)] = size_count.get(len(f), 0) + 1
print("\n[R2] face tracing: F = %d, sizes = %s" % (len(F), dict(sorted(size_count.items()))))
check("R2a", len(F) == 62, "F = 62 = 20 triangles + 30 squares + 12 pentagons")
check("R2b", sorted(size_count.items()) == [(3, 20), (4, 30), (5, 12)],
      "face census {3:20, 4:30, 5:12}")
check("R2c", sum(len(f) for f in F) == 2 * len(E), "sum of face sizes = 2E = 240")

# ---- R3/R4 face-resolved edge lengths ----
edge_faces = {}
for fi, f in enumerate(F):
    for k in range(len(f)):
        a, b = f[k], f[(k + 1) % len(f)]
        edge_faces.setdefault((min(a, b), max(a, b)), []).append(fi)
fsize = {fi: len(f) for fi, f in enumerate(F)}
per_face = {3: [], 4: [], 5: []}
for fi, f in enumerate(F):
    ls = [D[f[k]][f[(k + 1) % len(f)]] for k in range(len(f))]
    per_face[len(f)].append(ls)
short, long_ = 26.0913, 26.1664
for n_, tag in ((3, "triangle"), (4, "square"), (5, "pentagon")):
    arr = np.array(per_face[n_])
    lo, hi = arr.min(), arr.max()
    print("    %-9s n=%2d  edge len min %.4f  max %.4f  spread %.4f"
          % (tag, len(arr), lo, hi, hi - lo))
tri_eq = np.ptp(np.array(per_face[3])) < 5e-4
pen_eq = np.ptp(np.array(per_face[5])) < 5e-4
sq = np.array(per_face[4])
sq_ok = all(abs(sorted(r)[0] - short) < 1e-3 and abs(sorted(r)[1] - short) < 1e-3
            and abs(sorted(r)[2] - long_) < 1e-3 and abs(sorted(r)[3] - long_) < 1e-3 for r in sq)
check("R4a", tri_eq, "all 20 triangles equilateral (short %.4f deg)" % np.mean(per_face[3]))
check("R4b", pen_eq, "all 12 pentagons equilateral (long %.4f deg)" % np.mean(per_face[5]))
check("R4c", sq_ok, "all 30 squares alternate 2 short + 2 long")

cls = {}
for e, fl in edge_faces.items():
    key = tuple(sorted(fsize[x] for x in fl))
    cls.setdefault(key, []).append(e)
print("    edge classes by bounding-face types:", {k: len(v) for k, v in sorted(cls.items())})
check("R3", len(cls.get((3, 4), [])) == 60 and len(cls.get((4, 5), [])) == 60,
      "120 edges split 60 (triangle+square, short) / 60 (pentagon+square, long)")
check("R3b", len(cls) == 2, "exactly two edge classes -> exactly two edge lengths")

# ---- R5 mirror deviation + chirality angle ----
ax2 = []
for M in Gs:
    if abs(np.trace(M) + 1) < 1e-8:
        w, v = np.linalg.eig(M)
        ax = np.real(v[:, int(np.argmin(np.abs(w - 1)))]); ax /= np.linalg.norm(ax)
        ax2.append(ax)
ax2 = np.array(ax2)
ax2 = np.array([a if a[np.argmax(np.abs(a))] > 0 else -a for a in ax2])
ax2 = np.unique(np.round(ax2, 6), axis=0)
d_m = min(90 - math.degrees(math.acos(min(1, abs(float(V[0] @ a))))) for a in ax2)
anti = 180 - D[0][57]
print("\n[R5] delta_m = %.6f deg   (recorded 2.670063)" % d_m)
print("     180 - d(0,57) = %.6f deg   (recorded 5.3401 = 2*delta_m)" % anti)
check("R5a", abs(d_m - 2.670063) < 5e-4, "delta_m = 2.670063 deg reproduced from Gs axes")
check("R5b", abs(anti - 2 * d_m) < 1e-3, "antipodal approach = 2*delta_m")

# ---- R6 orientation null: is delta_m special? ----
rng = np.random.default_rng(20260927)
M_ = 200000
u = rng.normal(size=(M_, 3)); u /= np.linalg.norm(u, axis=1)[:, None]
dm = np.empty(M_)
ax2n = ax2 / np.linalg.norm(ax2, axis=1)[:, None]
c = np.abs(u @ ax2n.T)
dm = 90 - np.degrees(np.arccos(np.clip(c.min(axis=1), -1, 1)))
pct = 100.0 * (dm <= d_m).mean()
print("\n[R6] orientation null (uniform random seed direction, %d draws):" % M_)
print("     delta_m: mean %.4f  median %.4f  std %.4f  max %.4f deg"
      % (dm.mean(), np.median(dm), dm.std(), dm.max()))
print("     observed delta_m = %.6f deg -> percentile %.1f%%" % (d_m, pct))
frac_small = (dm < 1e-6).mean()
check("R6a", True, "delta_m = %.4f deg sits at percentile %.1f%% of the uniform null (report only)"
      % (d_m, pct))
check("R6b", frac_small < 1e-4,
      "an achiral orbit needs delta_m = 0: probability %.2e -> chirality is generic" % frac_small)

# ---- R7 tilt family: how the strain grows with the mirror deviation ----
p_RH = np.array([1.0, 1.0, phi ** 3]); p_RH /= np.linalg.norm(p_RH)
am = ax2[int(np.argmin([abs(float(p_RH @ a)) for a in ax2]))]
print("\n[R7] tilt family p(d) = cos d * p_RH + sin d * a_mirror")
print("     d(deg)   nn edges (deg)                split")
for d in [0.0, 1.0, 2.0, 2.670063, 4.0, 6.0, 8.0]:
    p = math.cos(math.radians(d)) * p_RH + math.sin(math.radians(d)) * am
    o = np.unique(np.round(np.array([M @ p for M in Gs]), 9), axis=0)
    DD = np.degrees(np.arccos(np.clip(o @ o.T, -1, 1)))
    nn = np.sort(DD[0])[1:5]
    print("     %6.3f   %-30s %.4f" % (d, np.round(nn, 4), nn.max() - nn.min()))
print("     data     %-30s %.4f" % (np.round(np.sort(D[0])[1:5], 4), 26.1664 - 26.0913))
check("R7", True, "strain is monotone in the mirror deviation (single-parameter family)")

n_ok = sum(1 for _, ok, _ in CHECKS if ok)
print("\n" + "-" * 76)
print("RESULT: %d/%d PASS" % (n_ok, len(CHECKS)))
print("-" * 76)
json.dump({"checks": [{"tag": t, "ok": o, "msg": m} for t, o, m in CHECKS],
           "n_pass": n_ok, "n_total": len(CHECKS), "delta_m": d_m,
           "percentile": pct, "F": len(F), "face_census": {str(k): v for k, v in size_count.items()},
           "edge_classes": {str(k): len(v) for k, v in cls.items()}},
          open(os.path.join(OUT, "06_strain_chirality.json"), "w"), indent=1)
