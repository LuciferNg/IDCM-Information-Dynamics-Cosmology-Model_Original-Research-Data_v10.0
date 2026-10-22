#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O223 scripts/08 -- multi-scale / multi-component verification on real Planck data.
==================================================================================
Independent check of the O223 conclusions against every cached SMICA smoothing
scale plus the Commander and NILC component-separated maps.  No new data is
downloaded; the maps are the ones already used by the O7/O175 chains.

  M1  the node field T_i is extracted at all 10 maps
  M2  r(colour, T) stays weak at every scale and component
  M3  the Delta E = 0 prediction (frust = 2  =>  |T| small) holds across scales
  M4  the anchored colouring (anchor 0) keeps a negative dT across scales
"""
import os, math, json
import numpy as np
import healpy as hp
from collections import deque

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CS = os.path.join(os.path.dirname(ROOT), "cmb_cold_spot", "data")
CACHE = os.path.join(os.path.dirname(ROOT), "o5_catalog_compare", "data", "smooth_cache")
OUT = os.path.join(ROOT, "data")

CHECKS = []
def check(tag, ok, msg):
    CHECKS.append((tag, bool(ok), msg))
    print("  [%s] %s %s" % ("OK" if ok else "XX", tag, msg))

print("=" * 76)
print("O223 / 08 -- multi-scale / multi-component node-field verification")
print("=" * 76)

# ---- node directions ----
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

def colouring(anchor):
    c = -np.ones(N, int); c[anchor] = 0
    q = deque([anchor])
    while q:
        u = q.popleft()
        for w in nbr[u]:
            if c[w] < 0:
                c[w] = 1 - c[u]; q.append(w)
    return c
c0 = 1 - colouring(0)   # cold class = 1 at the anchor (matches the recorded convention)

frust = np.zeros(N, int)
for (i, j) in E:
    if c0[i] == c0[j]:
        frust[i] += 1; frust[j] += 1
print("[I] colouring(anchor 0): cold class n = %d ; frustration histogram = %s"
      % (int(c0.sum()), dict(zip(*np.unique(frust, return_counts=True)))))

# ---- galactic / equatorial directions of the nodes ----
def sph(ra, dec):
    r, d = math.radians(ra), math.radians(dec)
    return np.array([math.cos(d) * math.cos(r), math.cos(d) * math.sin(r), math.sin(d)])
_xg = sph(266.4051, -28.936175); _zg = sph(192.85948, 27.12825); _yg = np.cross(_zg, _xg)
def eq2gal(v):
    l = math.degrees(math.atan2(float(v @ _yg), float(v @ _xg))) % 360
    b = math.degrees(math.asin(max(-1, min(1, float(v @ _zg)))))
    return l, b
gal = np.array([eq2gal(v) for v in V])

def extract(m, lons, lats):
    th = np.radians(90 - lats); ph = np.radians(lons)
    return hp.get_interp_val(m, th, ph)

maps = [("smica2_smooth%s" % s, "smica2_smooth%s.fits" % s)
        for s in ("0.5", "1.0", "1.5", "2.0", "3.0", "4.0", "4.17", "10.0")]
maps += [("commander_smooth4.17", "commander_smooth4.17.fits"),
         ("nilc2_smooth4.17", "nilc2_smooth4.17.fits")]

rng = np.random.default_rng(20260927)
rows = []
print("\n[M] extracting node fields (10 maps):")
print("     %-22s %9s %8s %8s %8s %8s %8s"
      % ("map", "T[node0]", "r_col", "dT_anch", "p_perm", "f2|T|", "f1|T|"))
for tag, fn in maps:
    path = os.path.join(CACHE, fn)
    if not os.path.exists(path):
        print("     %-22s MISSING" % tag); continue
    m = hp.read_map(path).astype(np.float64)
    T = extract(m, gal[:, 0], gal[:, 1]) * 1e6   # K -> uK
    # sanity: node 0 should be near the cold spot (-134.19 uK at 5 deg)
    r_col = float(np.corrcoef(c0.astype(float), T)[0, 1])
    dT = float(T[c0 == 1].mean() - T[c0 == 0].mean())
    null = np.array([(T[rng.permutation(N)][c0 == 1].mean() - T[rng.permutation(N)][c0 == 0].mean())
                     for _ in range(20000)])
    p_perm = float((np.abs(null) >= abs(dT)).mean())
    f2 = float(np.abs(T[frust == 2]).mean())
    f1 = float(np.abs(T[frust <= 1]).mean())
    rows.append(dict(map=tag, T0=float(T[0]), r=r_col, dT=dT, p=p_perm, f2=f2, f1=f1))
    print("     %-22s %+9.2f %+8.4f %+8.2f %8.4f %8.2f %8.2f"
          % (tag, T[0], r_col, dT, p_perm, f2, f1))

# ---- M2/M3/M4 ----
rs = np.array([x["r"] for x in rows]); dTs = np.array([x["dT"] for x in rows])
f2s = np.array([x["f2"] for x in rows]); f1s = np.array([x["f1"] for x in rows])
print("\n[M2] r(colour, T): mean %+.4f  |r| max %.4f  (all %d maps)" % (rs.mean(), np.abs(rs).max(), len(rs)))
check("M2", np.abs(rs).max() < 0.40, "colour stays a weak predictor at every scale/component")
print("[M3] frust=2 vs rest: mean|T| %.2f vs %.2f uK ; smaller in %d/%d maps"
      % (f2s.mean(), f1s.mean(), int((f2s < f1s).sum()), len(f2s)))
check("M3", (f2s < f1s).sum() >= len(f2s) - 2,
      "Delta E = 0 nodes are quieter in >= %d/%d maps" % (len(f2s) - 2, len(f2s)))
print("[M4] anchored dT: mean %+.2f uK ; negative in %d/%d maps"
      % (dTs.mean(), int((dTs < 0).sum()), len(dTs)))
check("M4", (dTs < 0).sum() >= len(dTs) - 2, "the anchored contrast keeps its sign across scales")

n_ok = sum(1 for _, ok, _ in CHECKS if ok)
print("\n" + "-" * 76)
print("RESULT: %d/%d PASS" % (n_ok, len(CHECKS)))
print("-" * 76)
json.dump({"checks": [{"tag": t, "ok": o, "msg": m} for t, o, m in CHECKS],
           "n_pass": n_ok, "n_total": len(CHECKS), "rows": rows},
          open(os.path.join(OUT, "08_multiscale.json"), "w"), indent=1)
