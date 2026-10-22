#!/usr/bin/env python3
"""
O219 scripts/01 -- Index Reconstruction from Coordinates (coordinate-only)
=========================================================================
O219 = pt<->mode index premise audit (O137 Round-19 audit item A3).

IRON RULE of this O: NEVER trust an index claim written in a file.
Every index set below is rebuilt from polytope COORDINATES + saved tensors
by exact rational arithmetic (no floats, no numpy, no cytools).

Index spaces audited
--------------------
  Delta   (CY36_98 polytope, o53 sage export) : 48 pts, bare labels 0..47
  Delta*  (mirror/polar dual, o137 data file) : 85 pts, bare labels 0..84
  phi     (GKZ period vector, triangulation of Delta*) : 73 entries
  kappa   (triple intersection tensor) : 36^3 saved (full keys 0..36)
  chain modes : n = 1..44 (44-site chain), 1..88 (88-ring), 1..176

Checks are grouped A..H. Every check prints [PASS]/[FAIL] plus the reason.
Output: stdout + ../data/01_checks.json + ../data/01_index_charter.json

Run from the O219 root:   /usr/bin/python3 scripts/01_index_charter_verify.py

NOTE (lesson, costs 2 runs): the exact determinant MUST use Fraction.
A "bareiss without dividing by the previous pivot" routine is fine for
zero/nonzero tests (vertex tests B1/B6) but returns a RESCALED value, so
it silently corrupted the phi volume sum. Use det_exact() for magnitudes.
"""

import json
import os
import hashlib
import itertools
from fractions import Fraction
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__))
O219 = os.path.dirname(HERE)
REPO = os.path.dirname(O219)                       # open_problems_fresh/
O137 = os.path.join(REPO, "o137_cy3_topological_resonance")
O53 = os.path.join(REPO, "o53_cy3_reality")

F_DELTA = os.path.join(O53, "data", "polytopes", "cy36_98_sage_export.json")
F_DUAL = os.path.join(O137, "data", "dual_polytope_points.json")
F_GKZ = os.path.join(O137, "data", "gkz_period_data.json")
F_TRI = os.path.join(O137, "data", "dual_triangulation_data.json")
F_SUB44 = os.path.join(O137, "data", "sub_glsm_44_indices.json")
F_KAPPA = os.path.join(O53, "data", "polytopes", "cy36_98_intersection_full.json")
F_DOC14 = os.path.join(O137, "docs", "14_task_bc_decoupling.md")
F_DOC19 = os.path.join(O137, "docs", "19_open_problems_attack.md")
F_DOC06 = os.path.join(O137, "docs", "06_phase4_derivation.md")

RESULTS = []


def ck(name, ok, detail=""):
    RESULTS.append({"check": name, "ok": bool(ok), "detail": str(detail)})
    print("  [%s] %s%s" % ("PASS" if ok else "FAIL", name,
                           ("  -- " + str(detail)) if detail else ""))
    return bool(ok)


def close(a, b, tol=1e-12):
    return abs(a - b) <= tol * max(1.0, abs(b))


# ----------------------------------------------------------------- exact helpers
def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def det_exact(rows):
    """Exact rational determinant (Gaussian elimination over Fraction)."""
    M = [[Fraction(int(x)) for x in r] for r in rows]
    n = len(M)
    det = Fraction(1)
    for c in range(n):
        p = None
        for r in range(c, n):
            if M[r][c] != 0:
                p = r
                break
        if p is None:
            return Fraction(0)
        if p != c:
            M[c], M[p] = M[p], M[c]
            det = -det
        piv = M[c][c]
        det *= piv
        for r in range(c + 1, n):
            if M[r][c] == 0:
                continue
            f = M[r][c] / piv
            for cc in range(c, n):
                M[r][cc] -= f * M[c][cc]
    return det


def simplex_volume(pt_list):
    """4-volume of a 4-simplex given as 5 lattice points (exact integer)."""
    rows = [[p[0], p[1], p[2], p[3], 1] for p in pt_list]
    d = det_exact(rows)
    assert d.denominator == 1, "volume not integral: %s" % d
    return abs(int(d))


def facets_through(pol_pts, dual_pts):
    """Number of polar-partner facets containing each point of dual_pts.
    Facets of {y : <y,v> >= -1} are {y : <y,v> = -1} for v a vertex of pol_pts.
    Pure integer arithmetic."""
    cnt = [0] * len(dual_pts)
    sizes = []
    for v in pol_pts:
        S = [i for i, y in enumerate(dual_pts) if dot(y, v) == -1]
        sizes.append(len(S))
        for i in S:
            cnt[i] += 1
    return cnt, sizes


def extreme_points(pts, facet_normals):
    """Vertices: >= 4 linearly independent facets through the point
    (zero/nonzero test only -- rescaling does not matter)."""
    out = []
    for i, y in enumerate(pts):
        S = [v for v in facet_normals if dot(y, v) == -1]
        if len(S) < 4:
            continue
        if any(det_exact(c) != 0 for c in itertools.combinations(S, 4)):
            out.append(i)
    return out


# ----------------------------------------------------------------- load data
print("=" * 78)
print("O219 / 01  Index reconstruction from coordinates (no index claim trusted)")
print("=" * 78)
delta = json.load(open(F_DELTA))
dual = json.load(open(F_DUAL))
gkz = json.load(open(F_GKZ))
tri = json.load(open(F_TRI))
sub44 = json.load(open(F_SUB44))
kappa = json.load(open(F_KAPPA))

D_pts = [list(map(int, p)) for p in delta["points"]]
D_vts = [list(map(int, p)) for p in delta["vertices"]]
S_pts = [list(map(int, p)) for p in dual["points"]]
phi = list(gkz["gkz_phi"])
simps = [list(map(int, s)) for s in tri["simplices"]]

print("\n--- A. source integrity ---")
md5 = hashlib.md5(open(F_DELTA, "rb").read()).hexdigest()
ck("A1 Delta file md5 starts 63536d1776 (docs/36 s2 provenance claim)",
   md5.startswith("63536d1776"), "md5=" + md5)
ck("A2 Delta = 48 pts / 6 vertices / h11 36 / h21 98 (file fields)",
   len(D_pts) == 48 and len(D_vts) == 6 and delta["h11"] == 36 and delta["h21"] == 98,
   "n_pts=%d n_vert=%d h11=%d h21=%d" % (len(D_pts), len(D_vts), delta["h11"], delta["h21"]))
ck("A3 Delta* = 85 pts (file field == list length)",
   dual["n_points"] == 85 and len(S_pts) == 85,
   "n_points_file=%d len=%d" % (dual["n_points"], len(S_pts)))
ck("A4 phi vector = 73 entries, sum 1800, phi[0] 360, phi[1] 176",
   len(phi) == 73 and sum(phi) == 1800 and phi[0] == 360 and phi[1] == 176,
   "len=%d sum=%d phi0=%d phi1=%d" % (len(phi), sum(phi), phi[0], phi[1]))

print("\n--- B. coordinate-only reconstruction of both label spaces ---")
cntS, sizesS = facets_through(D_vts, S_pts)            # facets of Delta*
vertS = extreme_points(S_pts, list(D_vts))             # vertices of Delta*
ck("B1 Delta vertices (rebuilt) = {1,2,3,4,5,7}",
   sorted([D_pts.index(v) for v in D_vts]) == [1, 2, 3, 4, 5, 7],
   str(sorted([D_pts.index(v) for v in D_vts])))
ck("B2 facets(Delta*) = 6 (= number of Delta vertices)",
   len(sizesS) == 6, "facet sizes=%s" % sorted(sizesS))
facet_int_S = [i for i, c in enumerate(cntS) if c == 1]
interior_S = [i for i, c in enumerate(cntS) if c == 0]
nonfacet_S = [i for i, c in enumerate(cntS) if c != 1]
ck("B3 Delta* facet-interior labels = 73..84 (12 pts)",
   facet_int_S == list(range(73, 85)), str(facet_int_S))
ck("B4 origin (label 0) is the only Delta* interior point", interior_S == [0], str(interior_S))
ck("B5 Delta* non-facet labels = 0..72 exactly (73 = origin + 72 rays)",
   nonfacet_S == list(range(73)),
   "n=%d labels %d..%d" % (len(nonfacet_S), nonfacet_S[0], nonfacet_S[-1]))

VERTS = [S_pts[i] for i in vertS]
cntD, sizesD = facets_through(VERTS, D_pts)            # facets of Delta
facet_int_D = [i for i, c in enumerate(cntD) if c == 1]
interior_D = [i for i, c in enumerate(cntD) if c == 0]
nonfacet_D = [i for i, c in enumerate(cntD) if c != 1]
ck("B6 Delta* extreme points = 7 -> facets(Delta) = 7", len(vertS) == 7, "vertices=%s" % vertS)
ck("B7 Delta facet-interior labels = 37..47 (11 pts)",
   facet_int_D == list(range(37, 48)), str(facet_int_D))
ck("B8 Delta non-facet labels = 0..36 exactly (37 = origin + 36 rays = h11)",
   nonfacet_D == list(range(37)) and len(nonfacet_D) - 1 == delta["h11"],
   "n=%d labels %d..%d h11=%d" % (len(nonfacet_D), nonfacet_D[0], nonfacet_D[-1],
                                  delta["h11"]))
ck("B9 origin is the only Delta interior point", interior_D == [0], str(interior_D))

used = sorted({i for s in simps for i in s})
ck("B10 triangulation label set = {0..72} == Delta* non-facet labels "
   "(phi index == Delta* label, labels NOT compacted)",
   used == nonfacet_S, "n_used=%d max=%d" % (len(used), used[-1]))

print("\n--- C. independent recomputation of the GKZ phi vector ---")
vol_of = {}
for s in simps:
    vol_of[tuple(s)] = simplex_volume([S_pts[i] for i in s])
tot_vol = sum(vol_of.values())
ck("C1 SUM of simplex 4-volumes = 360 = Sigma(phi)/5 (saved simplicial complex tiles Delta*)",
   tot_vol == 360 and sum(phi) == 5 * tot_vol,
   "total vol=%d  sum(phi)=%d" % (tot_vol, sum(phi)))
phi_re = [0] * len(S_pts)
for s in simps:
    v = vol_of[tuple(s)]
    for i in s:
        phi_re[i] += v
bad = [(i, phi[i], phi_re[i]) for i in range(73) if phi_re[i] != phi[i]]
ck("C2 phi recomputed from saved simplices x exact volumes == saved vector (73/73)",
   bad == [], "mismatched=%s" % (bad[:4] if bad else "none"))
ck("C3 phi[1] = 176 = 2*88", phi[1] == 176, "phi[1]=%d" % phi[1])

print("\n--- D. the phi=9 layer, rebuilt from coordinates ---")
lab9 = [i for i, v in enumerate(phi) if v == 9]
ck("D1 phi=9 labels = {33,37,41,44,45,47,48,50,51} (9 pts)",
   lab9 == [33, 37, 41, 44, 45, 47, 48, 50, 51] and len(lab9) == 9, str(lab9))

TABLE14 = {33: [-1, 0, 0, 1], 37: [-1, 0, 0, 5], 41: [-1, 0, 0, 9],
           44: [-1, 0, 1, 0], 45: [-1, 0, 1, 1], 47: [-1, 0, 1, 3],
           48: [-1, 0, 1, 4], 50: [-1, 0, 1, 6], 51: [-1, 0, 1, 7]}
ck("D2 docs/14 coordinate table (9 rows) matches Delta* coords at those labels",
   all(S_pts[i] == v for i, v in TABLE14.items()),
   str({i: S_pts[i] for i in TABLE14}))


def law9(p):
    """docs/19 s3 selection law, written ONLY in x2/x3 coordinates."""
    x2, x3 = p[2], p[3]
    return (x2 == 0 and x3 % 4 == 1) or (x2 == 1 and x3 in (0, 1, 3, 4, 6, 7))


law_phi_space = [i for i in range(73) if law9(S_pts[i])]
ck("D3 coordinate law (x2=0 & x3=1 mod 4) or (x2=1 & x3 in {0,1,3,4,6,7}) "
   "selects exactly the 9 phi=9 points",
   law_phi_space == lab9, "law_set=%s" % law_phi_space)
law_full = [i for i, p in enumerate(S_pts) if law9(p)]
extra = [i for i in law_full if i not in lab9]
ck("D3b on the FULL 85-point set the same law also selects 3 facet-interior pts "
   "-> needs the qualifier 'among the 73 phi-indexed points'",
   extra == [74, 78, 79], "extra=%s" % extra)
G1 = [i for i in lab9 if S_pts[i][2] == 0]
G2 = [i for i in lab9 if S_pts[i][2] == 1]
ck("D4 G1 (x2=0) = 3 pts with x3 = {1,5,9} = 1+4k", len(G1) == 3 and
   [S_pts[i][3] for i in G1] == [1, 5, 9], str([S_pts[i][3] for i in G1]))
ck("D5 G2 (x2=1) = 6 pts with x3 in {0,1,3,4,6,7} = (3k,3k+1)",
   len(G2) == 6 and sorted(S_pts[i][3] for i in G2) == [0, 1, 3, 4, 6, 7],
   str(sorted(S_pts[i][3] for i in G2)))

print("\n--- E. docs/19 s2 numerical claims ---")
ck("E1 Delta* pt[33] = (-1,0,0,1) with phi=9",
   S_pts[33] == [-1, 0, 0, 1] and phi[33] == 9, "pt=%s phi=%d" % (S_pts[33], phi[33]))
ck("E2 Delta* pt[11] = (-1,0,-1,3) with phi=18",
   S_pts[11] == [-1, 0, -1, 3] and phi[11] == 18, "pt=%s phi=%d" % (S_pts[11], phi[11]))


def gamma(n):
    import math
    return 4.0 * math.sin(math.pi * n / 88.0) ** 2


ck("E3 gamma_33 = 2+sqrt2, gamma_11 = 2-sqrt2, sum = 4",
   close(gamma(33), 2 + 2 ** 0.5) and close(gamma(11), 2 - 2 ** 0.5) and
   close(gamma(33) + gamma(11), 4.0),
   "g33=%.12f g11=%.12f sum=%.12f" % (gamma(33), gamma(11), gamma(33) + gamma(11)))

low = [i for i, v in enumerate(phi) if v <= 12]
high = [i for i, v in enumerate(phi) if v > 12]
low_sorted = sorted(low)
ck("E4 phi<=12 test: pt[33] in low (9), pt[11] not in low (18)",
   33 in low and 11 not in low, "phi33=%d phi11=%d" % (phi[33], phi[11]))
ck("E5 low-phi set = 44 pts (= N_d), high-phi set = 29 pts (= L_7)",
   len(low) == 44 and len(high) == 29, "low=%d high=%d" % (len(low), len(high)))
ck("E6 low-phi label list == O137 data/sub_glsm_44_indices.json",
   low_sorted == list(sub44["phi_le12_indices"]), str(low_sorted))

bys = {}
for i, v in enumerate(phi):
    bys.setdefault(v, []).append(i)
cls = {v: len(bys.get(v, [])) for v in (6, 8, 9, 12)}
ck("E7 GKZ phi partition = 44 = 2 + 5 + 9 + 28 (phi = 6 / 8 / 9 / 12), "
   "the 'GKZ phi layer' identity registered in O137 docs/24 L162",
   cls == {6: 2, 8: 5, 9: 9, 12: 28} and sum(cls.values()) == 44,
   "phi=6:%d labels=%s | phi=8:%d labels=%s | phi=12:%d" %
   (cls[6], bys[6], cls[8], bys[8], cls[12]))
MODES13 = [n for n in range(1, 14) if n not in (6, 8, 10, 12)]
ck("E8 the A5 9-mode set = first 13 integers minus the 4 even {6,8,10,12} "
   "(O137 docs/24 L260) -- pure mode-side arithmetic, no polytope index",
   MODES13 == [1, 2, 3, 4, 5, 7, 9, 11, 13], str(MODES13))

print("\n--- F. the actual premise: 'pt index = mode index' ---")
MODES9 = [1, 2, 3, 4, 5, 7, 9, 11, 13]      # A5 chiral I-60 orbit (O137 docs/31, O209 docs/09)
inter9 = sorted(set(lab9) & set(MODES9))
ck("F1 A3 raw observation: phi=9 label set INTERSECT 9-mode set = EMPTY",
   inter9 == [], "labels9=%s modes9=%s" % (lab9, MODES9))
out_of_range = [i for i in lab9 if i > 44]
ck("F2 range check: 5 of the 9 phi=9 labels exceed the 44-chain mode range 1..44",
   out_of_range == [45, 47, 48, 50, 51], str(out_of_range))
ck("F3 same integer, different polytope: label 33 of Delta vs of Delta* differ",
   D_pts[33] != S_pts[33], "Delta[33]=%s  Delta*[33]=%s" % (D_pts[33], S_pts[33]))

orders = {
    "file": list(range(85)),
    "lex": sorted(range(85), key=lambda i: tuple(S_pts[i])),
    "norm_lex": sorted(range(85), key=lambda i: (sum(x * x for x in S_pts[i]), tuple(S_pts[i]))),
    "reversed": list(range(84, -1, -1)),
}
idx_of = {}
for nm, order in orders.items():
    pos = {order[k]: k for k in range(85)}
    idx_of[nm] = {"pt33": pos[33], "pt11": pos[11]}
print("      index of the point (-1,0,0,1) under 4 enumerations: %s"
      % {k: v["pt33"] for k, v in idx_of.items()})
ck("F4 the labels 33 / 11 are NOT enumeration-invariant "
   "(they are artefacts of the data-file ordering)",
   len({v["pt33"] for v in idx_of.values()}) > 1, str(idx_of))

pair = (11, 33)
label_map = {n: (n in low) for n in pair}
rankmap = {n: low_sorted[n - 1] for n in range(1, 45)}
rank_ok = {n: (rankmap[n] in low) for n in pair}
ck("F5 label-map verdict: 33 allowed, 11 excluded (the docs/19 s2 mechanism)",
   label_map[33] is True and label_map[11] is False, str(label_map))
ck("F6 rank-map verdict on the same pair: BOTH allowed -> test is vacuous "
   "(all 44 rank-mapped modes are low-phi by construction)",
   rank_ok[33] is True and rank_ok[11] is True,
   "mode33->label%d mode11->label%d" % (rankmap[33], rankmap[11]))
allowed_by_label = [n for n in range(1, 45) if n in low]
ck("F7 label-map excludes 21 of the 44 modes, incl. the 2-adic candidates 1 and 7 "
   "(phi[1]=176, phi[7]=20)",
   len(allowed_by_label) == 23 and 1 not in allowed_by_label and 7 not in allowed_by_label,
   "allowed n<=44 = %s" % allowed_by_label)

P_empty = Fraction(comb(64, 9), comb(73, 9))
p_pair = Fraction(2 * 44 * 29, 73 * 72)
ck("F8 density baseline: P(random 9 of 73 disjoint from the 9-mode set) = %.4f"
   % float(P_empty), float(P_empty) > 0.2,
   "exact=%s  (N_search=1, d_obs=0, median d=1)" % P_empty)
ck("F9 density baseline: P(a random phi layer splits a given pair one-low-one-high) = %.4f"
   % float(p_pair), float(p_pair) > 0.4, "exact=%s" % p_pair)

print("\n--- G. kappa / divisor index space (docs/06 s1) ---")
K = kappa["kappa"]
ck("G1 kappa saved shape = 36^3", kappa["shape"] == [36, 36, 36] and len(K) == 36,
   str(kappa.get("shape")))
ck("G2 K[0,0,0] = -360 (docs/06 'index 0 = pt 0 = origin' claim)",
   close(K[0][0][0], -360.0), str(K[0][0][0]))
nz = sum(1 for i in range(36) for j in range(36) for k in range(36) if K[i][j][k] != 0)
ck("G3 kappa nonzero count (reported, no external claim)", nz > 0, "nonzero=%d" % nz)
doc06_txt = open(F_DOC06, encoding="utf-8").read()
ck("G4 the premise sentence exists verbatim in docs/06 s1 (quoted for the record)",
   "= pt index = mode index" in doc06_txt and "divisor label" in doc06_txt,
   "CYTools divisor label = 1-36 (1-based) = pt index = mode index (1-based)")

print("\n--- H. verdict summary ---")
n_pass = sum(1 for r in RESULTS if r["ok"])
print("  RESULT: %d/%d PASS" % (n_pass, len(RESULTS)))
print("  SURVIVES : coordinate-anchored facts (B, C, D, E, G) -- all order-free")
print("  DIES     : 'pt index = mode index' as a derivation (F3..F7 + F8/F9 density)")

registry = {
    "note": "index-space registry rebuilt from coordinates (O219 scripts/01)",
    "files": {
        "Delta": "o53_cy3_reality/data/polytopes/cy36_98_sage_export.json",
        "Delta_star": "o137_cy3_topological_resonance/data/dual_polytope_points.json",
        "triangulation": "o137_cy3_topological_resonance/data/dual_triangulation_data.json",
        "phi": "o137_cy3_topological_resonance/data/gkz_period_data.json",
        "kappa": "o53_cy3_reality/data/polytopes/cy36_98_intersection_full.json",
    },
    "Delta": {"n_points": 48, "bare_label_range": "0..47", "origin_label": 0,
              "vertices": [1, 2, 3, 4, 5, 7], "n_facets": 7,
              "facet_interior_labels": "37..47", "non_facet_labels": "0..36",
              "non_facet_count": 37, "meaning": "origin + 36 prime toric divisors (h11)"},
    "Delta_star": {"n_points": 85, "bare_label_range": "0..84", "origin_label": 0,
                   "n_extreme_points": len(vertS), "extreme_point_labels": vertS,
                   "facet_interior_labels": "73..84", "non_facet_labels": "0..72",
                   "non_facet_count": 73, "meaning": "origin + 72 rays"},
    "phi": {"n_entries": 73, "sum": 1800, "total_polytope_volume": tot_vol,
            "index_space": "Delta* non-facet labels 0..72 (identity mapping, NOT compacted)",
            "index_convention": "phi[i] <-> Delta* label i, i = 0..72",
            "charges_q": "q[i] = phi[0] - phi[i+1], i = 0..71 (charge index = label - 1)",
            "verified": "sum of simplex 4-volumes x vertices reproduces all 73 entries"},
    "kappa": {"shape": "36^3", "index_space": "Delta non-facet labels 0..35 (sub-tensor of 0..36)",
              "origin_index": 0, "K000": -360,
              "note": "cytools intersection_numbers() keys 0..36 with 0 = origin (script 03)"},
    "chain_modes": {"44_chain": "n = 1..44", "88_ring": "n = 1..88", "176": "n = 1..176",
                    "note": "phi=9 layer as a SET is order-free; its labels are not"},
    "forbidden": "chain mode n <-> polytope label n (no structural map; label order is an artefact)",
}
os.makedirs(os.path.join(O219, "data"), exist_ok=True)
json.dump(RESULTS, open(os.path.join(O219, "data", "01_checks.json"), "w"), indent=1,
          ensure_ascii=False)
json.dump(registry, open(os.path.join(O219, "data", "01_index_charter.json"), "w"), indent=1,
          ensure_ascii=False)
print("  wrote data/01_checks.json, data/01_index_charter.json")
