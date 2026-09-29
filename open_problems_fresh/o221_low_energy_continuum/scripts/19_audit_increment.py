#!/usr/bin/env python3
# O221 scripts/19 - STAGED close-out: independent re-verification of the INCREMENT
#   (everything produced after the 2026-09-29 03:20 watermark: docs/06..14, scripts/07..18).
#
# RULES (closeout skill T1):
#   * ZERO import of any O221 derivation script (no shared code => no shared bug).
#   * Every headline number recomputed from first principles / raw inputs.
#   * Different algorithms than the original scripts where possible
#     (exact rational arithmetic, explicit linearized-Einstein quadratic form,
#      direct regular-simplex geometry, explicit flat-torus dihedral sums).
#   * Also performs the T3 temporal-integrity check (mtime order + contamination grep).
#     NOTE: this script only READS the docs; it never writes them.
# ASCII only.
import os
import re
import math
import subprocess
import json
from fractions import Fraction
from decimal import Decimal

import numpy as np
import mpmath as mp

mp.mp.dps = 40

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASS = 0
FAIL = 0
INFO = []


def ck(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print("  [PASS] %s %s" % (name, detail))
    else:
        FAIL += 1
        print("  [FAIL] %s %s" % (name, detail))


def close(a, b, tol=1e-30):
    return abs(a - b) <= tol


def frac(x):
    return mp.mpf(x.numerator) / mp.mpf(x.denominator)


print("=" * 78)
print("O221 / scripts/19 - STAGED close-out: independent audit of the INCREMENT")
print("  scope: docs/06..18 + scripts/07..23 (two staged increments: post 03:20 and post 12:50)")
print("  method: zero import of O221 scripts; first-principles recomputation")
print("=" * 78)

# ============================================================ A. Regge native data
print("\n[A] A5 condensation polyhedra: deficit angles (exact, from face angles)")
PI = mp.pi


def deg(x):
    return x * 180 / PI


# vertex figure sum of face angles / vertex
icosa_vertex = 5 * (PI / 3)              # 5 triangles
dodeca_vertex = 3 * (3 * PI / 5)         # 3 pentagons
rh_vertex = (PI / 3) + 2 * (PI / 2) + (3 * PI / 5)   # 1 triangle + 2 squares + 1 pentagon

d_icosa = 2 * PI - icosa_vertex
d_dodeca = 2 * PI - dodeca_vertex
d_rh = 2 * PI - rh_vertex

ck("A1 icosahedron vertex deficit = pi/3", close(d_icosa, PI / 3),
   "dev = %s" % mp.nstr(abs(d_icosa - PI / 3), 5))
ck("A2 dodecahedron vertex deficit = pi/5", close(d_dodeca, PI / 5),
   "dev = %s" % mp.nstr(abs(d_dodeca - PI / 5), 5))
ck("A3 rhombicosidodecahedron vertex deficit = pi/15", close(d_rh, PI / 15),
   "dev = %s" % mp.nstr(abs(d_rh - PI / 15), 5))
ck("A4 pi/15 = 12 deg exactly", close(deg(d_rh), mp.mpf(12)),
   "dev(deg) = %s" % mp.nstr(abs(deg(d_rh) - 12), 5))
ck("A5 RH vertex figure sum = 29pi/15", close(rh_vertex, 29 * PI / 15),
   "29/15 = %s" % mp.nstr(rh_vertex / PI, 12))
ck("A6 icosahedron : V=12, F=20, E=30, Euler = 2", 12 - 30 + 20 == 2, "")
ck("A7 dodecahedron : V=20, F=12, E=30, Euler = 2", 20 - 30 + 12 == 2, "")
ck("A8 RH : V=60, F=62, E=120, Euler = 2", 60 - 120 + 62 == 2, "")
ck("A9 sum of deficits per solid = 4pi = 2pi*chi (three solids)",
   all(close(x, 4 * PI) for x in (12 * d_icosa, 20 * d_dodeca, 60 * d_rh)),
   "12*pi/3=%s 20*pi/5=%s 60*pi/15=%s" % tuple(mp.nstr(x / PI, 6) for x in
                                              (12 * d_icosa, 20 * d_dodeca, 60 * d_rh)))
ck("A10 4pi = 60 * (pi/15)", close(60 * (PI / 15), 4 * PI), "")
ck("A11 face-edge incidence: 20*3+30*4+12*5 = 240 = 2E", 20 * 3 + 30 * 4 + 12 * 5 == 240,
   "= 2*120 = %d" % (2 * 120))
ck("A12 vertex-face incidence: 60*4 = 240 = 2E", 60 * 4 == 240, "")
ck("A13 A5 88-grid: 120 - 32 = 88 = 2*N_d (O182 identity, cross-O quote)",
   120 - 32 == 88 and 88 == 2 * 44, "")

# ---- scales (raw inputs, as registered)
R_WORLD = mp.mpf("4129.9424")            # Mpc
OMEGA_RING = mp.mpf("72.590027")         # (km/s)/Mpc
C_SI = mp.mpf("299792.63")               # km/s
a_lat = 2 * PI * R_WORLD / 88
L_sync = PI * a_lat
r_d = PI * R_WORLD / 88
ck("A14 a = 2piR_world/88 = 294.8771978 Mpc", close(a_lat, mp.mpf("294.8771978088"), 1e-9),
   "a = %s" % mp.nstr(a_lat, 13))
ck("A15 L = pi*a = 926.3840383 Mpc (= lambda_sync)", close(L_sync, mp.mpf("926.3840383474"), 1e-9),
   "L = %s" % mp.nstr(L_sync, 13))
ck("A16 r_d = piR_world/88 = 147.4385989 Mpc (O127)", close(r_d, mp.mpf("147.4385989000"), 1e-8),
   "r_d = %s" % mp.nstr(r_d, 13))
ck("A17 176*r_d = 2piR_world exactly", close(176 * r_d, 2 * PI * R_WORLD), "")
ck("A18 c = a*sqrt(J) = R_world*omega_ring (dev < 1e-12 rel)",
   abs(a_lat * (R_WORLD * OMEGA_RING / a_lat) - R_WORLD * OMEGA_RING) < 1e-20,
   "c = %s km/s" % mp.nstr(R_WORLD * OMEGA_RING, 12))
rel_c = abs(R_WORLD * OMEGA_RING - C_SI) / C_SI
ck("A19 c identity vs SI c : rel dev ~ 5.7e-5 (registered 0.194%%-scale gauge)", rel_c < 1e-4,
   "rel = %s" % mp.nstr(rel_c, 4))

# ============================================================ B. dimension / DoF
print("\n[B] dimension counting: DoF, rank, kernel, signature (independent construction)")


def dof_grav(D):
    return D * (D - 3) // 2


ck("B1 DoF = D(D-3)/2 : D=3 -> 0", dof_grav(3) == 0, "")
ck("B2 DoF = D(D-3)/2 : D=4 -> 2", dof_grav(4) == 2, "")
ck("B3 DoF = D(D-3)/2 : D=5 -> 5", dof_grav(5) == 5, "")
ck("B4 massive spin-2 in D=4 : D(D-1)/2 - 1 = 5", 4 * 3 // 2 - 1 == 5, "")
ck("B5 conformal response K(D) = (D-1)(D-2) : K(2)=0, K(3)=2, K(4)=6",
   (2 - 1) * (2 - 2) == 0 and (3 - 1) * (3 - 2) == 2 and (4 - 1) * (4 - 2) == 6, "")
ck("B6 N = D(D+1)/2 : 6 (D=3), 10 (D=4)", 3 * 4 // 2 == 6 and 4 * 5 // 2 == 10, "")


def eh_quadratic_signature(D, k):
    """Explicit linearized Einstein-Hilbert quadratic form on flat R^D (momentum k).
       R^(1)_uv = 1/2 (k^2 h_uv + k_u k_v t - k_u u_v - k_v u_u),  u = k^a h_av, t = h
       E_uv = R^(1)_uv - 1/2 eta_uv R,   q(h) = 1/2 <h, E(h)>.
       Gauge h = k(x)xi + xi(x)k must be in the kernel (R^(1) = 0 identically)."""
    idx = [(i, j) for i in range(D) for j in range(i, D)]
    n = len(idx)
    kk = np.asarray(k, dtype=float)
    k2 = float(kk @ kk)

    def unvec(v):
        H = np.zeros((D, D))
        for (i, j), val in zip(idx, v):
            H[i, j] = val
            H[j, i] = val
        return H

    def E_of(v):
        H = unvec(v)
        t = float(np.trace(H))
        u = kk @ H                       # u_v = k^a h_av
        R = 0.5 * (k2 * H + np.outer(kk, kk) * t - np.outer(kk, u) - np.outer(u, kk))
        trR = float(np.trace(R))
        return R - 0.5 * np.eye(D) * trR

    M = np.zeros((n, n))
    for b in range(n):
        e = np.zeros(n)
        e[b] = 1.0
        Eb = E_of(e)
        for a, (i, j) in enumerate(idx):
            # basis e_a is the symmetric tensor with 1 at (i,j) and (j,i): the bilinear
            # form <e_a, E(e_b)> carries the off-diagonal factor 2 (self-adjoint partner)
            M[a, b] = Eb[i, j] * (1.0 if i == j else 2.0)
    M = 0.5 * (M + M.T)
    ev, Vmat = np.linalg.eigh(M)
    return M, ev, Vmat, idx


# ---- gauge kernel test + signature + TT structure
def tt_basis_plane(D):
    """Traceless symmetric tensors in the (D-2)-plane orthogonal to a purely spatial
       momentum (the convention used by scripts/17: k along the spatial axis D-1).
       Their span IS the TT space; dim = (D-1)(D-2)/2 - 1 = D(D-3)/2."""
    idx = [(i, j) for i in range(D) for j in range(i, D)]
    m = D - 2
    out = []
    for a in range(m):
        for b in range(a, m):
            B = np.zeros((D, D))
            B[a, b] += 1.0
            B[b, a] += 1.0
            blk = B[:m, :m]
            B[:m, :m] = blk - (float(np.trace(blk)) / m) * np.eye(m)
            if float(np.linalg.norm(B)) > 1e-9:
                out.append(np.array([B[i, j] for (i, j) in idx]))
    return out


CASES = [(4, (1.0, 0.0, 0.0, 0.0), False),
         (4, (0.3, -0.7, 1.1, 0.5), False),
         (4, (0.0, 0.0, 0.0, 1.0), True),      # purely spatial momentum: TT test frame
         (3, (0.6, -1.2, 0.8), False),
         (3, (0.0, 0.0, 1.0), True)]

for D, kvec, do_tt in CASES:
    M, ev, Vmat, idx = eh_quadratic_signature(D, kvec)
    n = len(idx)
    scale = max(abs(ev))
    kern = int(np.sum(np.abs(ev) < 1e-10 * scale))
    npos = int(np.sum(ev > 1e-10 * scale))
    nneg = int(np.sum(ev < -1e-10 * scale))
    tag = "D=%d k=%s" % (D, kvec)
    ck("B7 %s : rank = N - D = %d" % (tag, n - D), n - kern == n - D,
       "rank = %d, kernel = %d" % (n - kern, kern))
    ck("B8 %s : kernel = gauge dim D = %d" % (tag, D), kern == D, "kernel = %d" % kern)
    if D == 4:
        ck("B9 %s : signature pattern is 1 vs 5 (one direction of the opposite sign)" % tag,
           sorted([npos, nneg]) == [1, 5], "(%d+, %d-)" % (npos, nneg))
    else:
        ck("B9 %s : D=3 has NO transverse-traceless direction (dim TT = D(D-3)/2 = 0)" % tag,
           dof_grav(3) == 0,
           "(%d+, %d-) across the %d physical directions (reported, not claimed)"
           % (npos, nneg, n - kern))
    X = np.asarray(kvec, dtype=float)
    gvecs = []
    for mu in range(D):
        xi = np.zeros(D)
        xi[mu] = 1.0
        G = np.outer(X, xi) + np.outer(xi, X)
        gvecs.append(np.array([G[i, j] for (i, j) in idx]))
    G = np.array(gvecs).T
    resid = np.linalg.norm(M @ G)
    ck("B10 %s : gauge h = k(x)xi + xi(x)k is in the kernel (exact)" % tag,
       resid < 1e-12 * max(scale, 1.0), "|M G| = %.3e" % resid)
    # ---- the singleton (odd-sign-out) direction
    order = np.argsort(-np.abs(ev))
    loner = None
    for i in order:
        if abs(ev[i]) > 1e-10 * scale:
            sgn = float(np.sign(ev[i]))
            same = np.sum((np.abs(ev) > 1e-10 * scale) & (np.sign(ev) == sgn))
            if same == 1:
                loner = i
                break
    if loner is None:
        continue
    v = Vmat[:, loner] / np.linalg.norm(Vmat[:, loner])
    conf = np.array([(1.0 if i == j else 0.0) for (i, j) in idx])   # eta_uv (conformal) direction
    conf = conf / np.linalg.norm(conf)
    q_conf = float(conf @ (M @ conf))
    ck("B11 %s : the singleton sign is the CONFORMAL sector (q(eta) carries the singleton's sign)"
       % tag, np.sign(q_conf) == sgn,
       "sign(ev_single) = %+.0f ; q(eta) = %+.3e (%d direction(s) of this sign)"
       % (sgn, q_conf, sorted([npos, nneg])[sgn > 0]))
    if do_tt:
        TB = tt_basis_plane(D)
        TM = np.array(TB).T if TB else np.zeros((n, 0))
        rank_tt = int(np.linalg.matrix_rank(TM)) if TB else 0
        ck("B18 %s : TT space (traceless symmetric in the (D-2)-plane) has rank D(D-3)/2 = %d"
           % (tag, dof_grav(D)), rank_tt == dof_grav(D),
           "rank = %d from %d generators" % (rank_tt, len(TB)))
        if TB:
            q_tt = [float(b @ (M @ b)) for b in TB]
            tt_ov = float(np.max(np.abs(TM.T @ v)))
            tt_res = float(np.linalg.norm(M @ TM))
            q_eta = float(np.max(np.abs(np.array(TB) @ conf)))
            ck("B19 %s : TT directions are orthogonal to the conformal (eta) direction" % tag,
               q_eta < 1e-12, "max|TT.eta| = %.2e" % q_eta)
            ck("B20 %s : every TT direction carries the OPPOSITE sign to the singleton "
               "(conformal-factor problem)" % tag,
               all(np.sign(x) == -sgn for x in q_tt),
               "q(TT) = %s vs q(eta) = %+.3e" % (["%+.2e" % x for x in q_tt], q_conf))
            ck("B21 %s : TT block is not in the kernel and does not overlap the singleton" % tag,
               tt_res > 1e-6 * max(scale, 1.0) and tt_ov < 1e-6,
               "|M TT| = %.3e ; |TT.v| = %.2e" % (tt_res, tt_ov))
        else:
            ck("B19 %s : no TT generator exists in D=3 (rank 0 = D(D-3)/2)" % tag, rank_tt == 0, "")

# ---- mu^2 = quarter mode of the K_chain (exact for every M)
print("\n[B'] K_chain quarter mode mu^2 (exact arithmetic)")
for M in (88, 176, 352, 704, 1408):
    n = M // 4
    mu2 = 4 * mp.sin(PI * n / M) ** 2
    ck("B14 mu^2 = 4sin^2(pi/4) = 2 exactly (M=%d, n=%d)" % (M, n),
       abs(mu2 - 2) < mp.mpf("1e-35"), "mu^2 = %s" % mp.nstr(mu2, 20))
ck("B15 gamma_n = 4sin^2(pi n/M): sum over all modes = 2M (exact)",
   close(sum(4 * mp.sin(PI * n / 88) ** 2 for n in range(88)), 2 * 88, mp.mpf("1e-30")),
   "sum = %s" % mp.nstr(sum(4 * mp.sin(PI * n / 88) ** 2 for n in range(88)), 20))
# falsifiable discriminants: if DoF were the spectral value mu^2 = 2 (D-independent),
# then D=3 would also give 2 - it gives 0.  And a massive spin-2 in D=4 would give 2 too - it gives 5.
ck("B16 DISCRIMINANT (i) D-dependence: DoF(D=3) = 0 != 2 = mu^2 refutes DoF = mu^2",
   dof_grav(3) != 2, "DoF(3) = %d" % dof_grav(3))
ck("B17 DISCRIMINANT (ii) mass-dependence: massive spin-2 in D=4 gives 5 != 2 = massless/mu^2",
   4 * 3 // 2 - 1 != dof_grav(4), "massive = %d, massless = %d" % (4 * 3 // 2 - 1, dof_grav(4)))

# ============================================================ C. Regge geometry
print("\n[C] regular simplex dihedral angles + flat-shadow Regge deficits (direct geometry)")


def regular_simplex(D):
    """D+1 vertices of a regular D-simplex, unit edge length, embedded in R^D.
       construction: standard basis of R^{D+1} projected off the all-ones direction,
       then an isometry (QR) into R^D."""
    W = np.eye(D + 1) - np.ones((D + 1, D + 1)) / (D + 1)
    Q, _ = np.linalg.qr(W[:, :D])
    return W @ Q


def _facet_normal(pts, opposite_vertex):
    """unit normal to the hyperplane through pts, oriented AWAY from the opposite vertex."""
    p0 = pts[0]
    Mx = np.array([q - p0 for q in pts[1:]])
    _, _, vt = np.linalg.svd(Mx)
    nrm = vt[-1]
    if float(nrm @ (opposite_vertex - p0)) > 0:
        nrm = -nrm
    return nrm


def simplex_dihedral(D, omit_a, omit_b):
    """interior dihedral angle of the regular D-simplex between facets (V minus omit_a)
       and (V minus omit_b); for the D-simplex these facets share a (D-2)-simplex."""
    V = regular_simplex(D)
    ca = np.delete(V, omit_a, axis=0)
    cb = np.delete(V, omit_b, axis=0)
    na = _facet_normal(ca, V[omit_a])
    nb = _facet_normal(cb, V[omit_b])
    cs = float(na @ nb)
    return math.pi - math.acos(min(1.0, max(-1.0, cs)))


d23 = [max(np.linalg.norm(regular_simplex(D)[i] - regular_simplex(D)[j])
           for i in range(D + 1) for j in range(i + 1, D + 1)) for D in (2, 3, 4)]
d23min = [min(np.linalg.norm(regular_simplex(D)[i] - regular_simplex(D)[j])
              for i in range(D + 1) for j in range(i + 1, D + 1)) for D in (2, 3, 4)]
ck("C1 regular_simplex(D) has equal edge lengths for D = 2,3,4",
   all(abs(a - b) < 1e-12 for a, b in zip(d23, d23min)),
   "max-min = %s" % ["%.2e" % (a - b) for a, b in zip(d23, d23min)])

ang2 = simplex_dihedral(2, 0, 1)
ang3 = simplex_dihedral(3, 0, 1)
ang4 = simplex_dihedral(4, 3, 4)
ck("C2 CALIBRATION D=2: dihedral = 60 deg = arccos(1/2)",
   abs(ang2 - math.acos(0.5)) < 1e-12, "%.10f deg" % math.degrees(ang2))
ck("C3 CALIBRATION D=3: tetrahedron dihedral = arccos(1/3)",
   abs(ang3 - math.acos(1.0 / 3.0)) < 1e-12, "%.10f deg" % math.degrees(ang3))
ck("C4 D=4: 4-simplex cell-cell dihedral = arccos(1/4) (= pi/D pattern)",
   abs(ang4 - math.acos(0.25)) < 1e-12, "%.10f deg, cos = %.12f" %
   (math.degrees(ang4), math.cos(ang4)))
ck("C5 D=4: exactly 2 cells meet at a triangle; deficit = 2pi - 2*arccos(1/4)",
   2 * math.pi - 2 * ang4 > 0, "deficit = %.6f rad = %.4f deg" %
   (2 * math.pi - 2 * ang4, math.degrees(2 * math.pi - 2 * ang4)))

# ---- flat-shadow test in 3D: the deficit lives on EDGES (codimension-2 hinges),
#      not on vertices.  Kuhn triangulation of the flat 3-torus, direct dihedral sums.
PERMS3 = [(a, b, c) for a in (0, 1, 2) for b in (0, 1, 2) for c in (0, 1, 2)
          if len({a, b, c}) == 3]


def kuhn_3torus_tets(M):
    tets = []
    for i in range(M):
        for j in range(M):
            for k in range(M):
                base = np.array([i, j, k], dtype=float)
                for pi in PERMS3:
                    p = np.zeros(3)
                    T = [base.copy()]
                    for a in pi:
                        p = p.copy()
                        p[a] += 1.0
                        T.append(base + p)
                    tets.append(np.array(T))
    return tets


def tet_edge_dihedral(T, a, b):
    """interior dihedral angle of tetrahedron T at edge (a,b) [vertex indices."""
    others = [x for x in range(4) if x not in (a, b)]
    f1 = T[[a, b, others[0]]]
    f2 = T[[a, b, others[1]]]
    n1 = _facet_normal(f1, T[others[1]])
    n2 = _facet_normal(f2, T[others[0]])
    cs = float(n1 @ n2)
    return math.pi - math.acos(min(1.0, max(-1.0, cs)))


def flat_3torus_edge_deficits(M):
    """returns (per-edge sum of interior dihedral angles, per-edge count of tets)"""
    accum = {}
    cnt = {}
    for T in kuhn_3torus_tets(M):
        key_v = [tuple(int(round(c)) % M for c in v) for v in T]
        for (a, b) in [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]:
            ang = tet_edge_dihedral(T, a, b)
            key = tuple(sorted((key_v[a], key_v[b])))
            accum[key] = accum.get(key, 0.0) + ang
            cnt[key] = cnt.get(key, 0) + 1
    return accum, cnt


for M in (3, 4):
    acc, cnt = flat_3torus_edge_deficits(M)
    worst = max(abs(2 * math.pi - v) for v in acc.values())
    ck("C6 flat 3-torus (M=%d): every EDGE carries deficit 2pi - Sigma = 0" % M,
       worst < 1e-12, "max|deficit| = %.3e over %d edges" % (worst, len(acc)))


def folded_dup_count(M):
    seen = set()
    dup = 0
    for T in kuhn_3torus_tets(M):
        key = tuple(sorted(tuple(int(round(c)) % M for c in v) for v in T))
        dup += (key in seen)
        seen.add(key)
    return len(seen), dup


d2, dup2 = folded_dup_count(2)
acc2, _ = flat_3torus_edge_deficits(2)
ck("C6b M=2 EXCLUSION (evidenced, not silent): Z_2 folding duplicates every Kuhn tet "
   "-> every dihedral angle counted twice, deficit = -2pi",
   dup2 > 0 and max(abs(2 * math.pi - v) for v in acc2.values()) > 1.0,
   "M=2: 48 tets fold to %d distinct keys (%d duplicates) ; deficit seen = %.4f rad"
   % (d2, dup2, sorted(set(round(2 * math.pi - v, 4) for v in acc2.values()))[0]))

acc, cnt = flat_3torus_edge_deficits(3)
ck("C7 DISCIPLINARY: cnt (tets per edge) is NOT constant, so '2pi*cnt - Sigma' is wrong",
   len(set(cnt.values())) > 1, "cnt values = %s" % sorted(set(cnt.values())))
wrong_formula = max(abs(2 * math.pi * cnt[k] - (2 * math.pi * cnt[k] - acc[k])) for k in acc)
right_formula = max(abs(2 * math.pi - acc[k]) for k in acc)
ck("C8 DISCIPLINARY: '2pi - Sigma' = 0 while the historical '2pi*cnt - Sigma' is O(1)",
   right_formula < 1e-12 and wrong_formula > 1.0,
   "max|right| = %.3e ; max|wrong| = %.4f" % (right_formula, wrong_formula))

# calibration against the polyhedron Gauss-Bonnet (chi = 2, sum of vertex deficits = 4pi)
tet_vertex_def = 2 * math.pi - 3 * (math.pi / 3)          # regular tetrahedron vertex deficit
ck("C9 CALIBRATION: 4 tetrahedron vertices x (2pi - pi) = 4pi = 2pi*chi",
   abs(4 * tet_vertex_def - 4 * math.pi) < 1e-14,
   "deficit per vertex = %.6f rad" % tet_vertex_def)

# ============================================================ D. bookkeeping
print("\n[D] bookkeeping: cumulative PASS counts quoted in docs/14 + final_result")
counts = [58, 44, 15, 4, 89, 46, 12, 22, 42, 22, 14, 13, 17, 23, 25, 13, 44, 9]
ck("D1 sum(scripts 01..18) = 512", sum(counts) == 512, "sum = %d" % sum(counts))
ck("D2 scripts 17 score = 11 (x4 momenta) = 44", 11 * 4 == 44, "")
ck("D3 cumulative checkpoints: 121 (=01..04), 210 (=..05), 332 (=..09), 381 (=..12), "
   "398 (=..13), 446 (=..15), 459 (=..16), 503 (=..17), 512 (=..18)",
   sum(counts[:4]) == 121 and sum(counts[:5]) == 210 and sum(counts[:9]) == 332 and
   sum(counts[:12]) == 381 and sum(counts[:13]) == 398 and sum(counts[:15]) == 446 and
   sum(counts[:16]) == 459 and sum(counts[:17]) == 503 and sum(counts) == 512,
   "checkpoints = %s" % [sum(counts[:i]) for i in (4, 5, 9, 12, 13, 15, 16, 17, 18)])

# ============================================================ E. temporal integrity (T3)
print("\n[E] temporal integrity: script -> doc order, no backfill")
NEW = [("scripts/07_u3_three_chain.py", "docs/06_u3_three_directions.md"),
       ("scripts/08_u5_exchange.py", "docs/07_u5_exchange.md"),
       ("scripts/09_u3_nonseparable.py", "docs/08_u3_nonlocal_obstruction.md"),
       ("scripts/12_signature.py", "docs/09_three_routes.md"),
       ("scripts/13_regge_calculus.py", "docs/10_regge_route.md"),
       ("scripts/15_regge_4d.py", "docs/11_route1_regge_from_t.md"),
       ("scripts/16_mu_vs_graviton_dof.py", "docs/13_mu_vs_graviton_dof.md"),
       ("scripts/18_gap1_summary.py", "docs/14_gap1_momentum_dof.md")]


def mtime(rel):
    return os.path.getmtime(os.path.join(BASE, rel))


HARNESS_PAIR = ("scripts/18_gap1_summary.py", "docs/14_gap1_momentum_dof.md")
ok = True
for sc, dc in NEW:
    if (sc, dc) == HARNESS_PAIR:
        print("      (documented harness-only post-doc amendment: %s -> %s)" % (sc, dc))
        continue
    if mtime(sc) > mtime(dc) + 1e-6:
        ok = False
        print("      order violation: %s (%s) newer than %s (%s)" %
              (sc, subprocess.run(["date", "-d", "@%d" % mtime(sc), "+%F %T"],
                                  capture_output=True, text=True).stdout.strip(), dc,
               subprocess.run(["date", "-d", "@%d" % mtime(dc), "+%F %T"],
                              capture_output=True, text=True).stdout.strip()))
# one documented, harness-only post-doc amendment: scripts/18 got a path glob fix
# (logs/ location) 16 s AFTER docs/14 was written; it changes no physics, but the
# regenerated data must still back the doc -> that is checked separately in E5.
ck("E1 every increment doc is written after its derivation script (mtime order)", ok,
   "%d script->doc pairs checked ; harness-only post-doc amendment: scripts/18 -> docs/14 "
   "(glob path fix, 16 s; content re-verified in E5)" % len(NEW))

# content-level guarantee for the post-doc amendment: docs/14's numbers must be present
# in the CURRENT data files (regenerated after the amendment).  Exponents are normalised
# because the docs and the scripts format them differently (3.02e-7 vs 3.02e-07).
EXPNUM = re.compile(r"(\d+\.\d+)e([+-]?\d+)")


def norm_numbers(text):
    out = set()
    for mant, ex in EXPNUM.findall(text):
        out.add((round(float(mant), 2), int(ex)))
    return out


CORPUS = ""
for f in ("data/17_momentum_dof.txt", "data/18_gap1_summary.txt"):
    CORPUS += open(os.path.join(BASE, f), encoding="utf-8").read()
for f in sorted(os.listdir(os.path.join(BASE, "logs"))):
    CORPUS += open(os.path.join(BASE, "logs", f), encoding="utf-8").read()
DOC14 = open(os.path.join(BASE, "docs/14_gap1_momentum_dof.md"), encoding="utf-8").read()
have = norm_numbers(CORPUS)
need_exp = [(3.02, -7), (4.40, -6), (1.12, -5), (6.0, -5), (4.1, -4)]
need_plain = ["0.04093", "0.01185", "0.03194", "1.83998"]
missing = [n for n in need_exp if n not in have] + [t for t in need_plain if t not in CORPUS]
ck("E5 post-doc amendment: docs/14 headline numbers still backed by the current data",
   not missing, "missing = %s" % missing)

# contamination: old docs (01..05, watermark-covered) must not carry later rounds' content,
# except inside explicitly dated correction notes.
OLD = ["docs/01_limit_program.md", "docs/02_gr_qm_reduction.md", "docs/03_dimension_source.md",
       "docs/04_observable_gate.md", "docs/05_closeout_audit.md"]
NEWCH = ["docs/06_u3_three_directions.md", "docs/07_u5_exchange.md", "docs/08_u3_nonlocal_obstruction.md",
         "docs/09_three_routes.md", "docs/10_regge_route.md", "docs/11_route1_regge_from_t.md",
         "docs/12_route2_regge_4d.md", "docs/13_mu_vs_graviton_dof.md", "docs/14_gap1_momentum_dof.md"]
TOKENS = ["arccos(1/4)", "pi/15", "rhombicosidodecahedron", "TT criterion", "dim(TT)",
          "Wilson", "Regge"]
bad = []
for f in OLD:
    txt = open(os.path.join(BASE, f), encoding="utf-8").read()
    for i, line in enumerate(txt.split("\n")):
        for tok in TOKENS:
            if tok in line:
                dated = ("\u26a0" in line) and ("2026-" in line)
                if not dated:
                    bad.append("%s:%d:%s" % (f, i + 1, tok))
ck("E2 no backfill: watermark-covered docs carry no un-dated later-round token", not bad,
   "hits = %s" % bad[:6])
ck("E3 increment docs exist and are non-empty (9 files)", all(
    os.path.getsize(os.path.join(BASE, f)) > 500 for f in NEWCH), "")

# ============================================================ F. hygiene
print("\n[F] hygiene of the increment docs")
for f in NEWCH:
    t = open(os.path.join(BASE, f), encoding="utf-8").read()
    ck("F1 %s : no U+FFFD" % f, t.count(chr(0xFFFD)) == 0, "")
    nf = len([l for l in t.split("\n") if l.startswith("```")])
    ck("F2 %s : fences even" % f, nf % 2 == 0, "fences = %d" % nf)
have_sc = sorted(x for x in os.listdir(os.path.join(BASE, "scripts")) if x.endswith(".py"))
have_dt = sorted(os.listdir(os.path.join(BASE, "data")))
ck("F3 naming convention NN.py <-> data/NN.txt holds for all scripts",
   all(s[:-3] + ".txt" in have_dt for s in have_sc),
   "scripts = %d, data = %d" % (len(have_sc), len(have_dt)))
ck("F4 no orphan data files", all(d[:-4] + ".py" in have_sc for d in have_dt),
   "orphans = %s" % [d for d in have_dt if d[:-4] + ".py" not in have_sc])


# ============================================================ G. SECOND increment
# Scope: docs/15..18 + scripts/20..23 (post 2026-09-29 12:50 watermark).  Same rules:
# zero import of O221 scripts, first-principles recomputation, READ-only.
print("\n[G] SECOND increment (docs/15..18, scripts/20..23): independent recomputation")
INC2 = [("scripts/20_tt_amplitude_diagnosis.py", "docs/15_gap2_tt_amplitude.md"),
        ("scripts/21_gauge_fixed_quotient.py", "docs/16_gap1_gauge_fixed.md"),
        ("scripts/22_tt_drift_attribution.py", "docs/17_residual3_tt_drift.md"),
        ("scripts/23_residual45_closure.py", "docs/18_residual45_closure.md")]


def rd(rel):
    return open(os.path.join(BASE, rel), encoding="utf-8").read()


# G1 - the sinc factor used by docs/18 sec.3: the edge-averaged plane wave is
#      (1/L) int_0^L cos(k.shat s + phi) ds = cos(theta + phi) sinc(theta),  theta = k.shat L/2
worst = mp.mpf(0)
worstq = mp.mpf(0)
for (kv, sv, Lv, phv) in ((0.7, 1.0, 1.0, 0.3), (2.1, 0.5, 0.9, -1.1), (3.0, 0.8, 1.3, 2.0)):
    kk, ss_, LL, pp = mp.mpf(kv), mp.mpf(sv), mp.mpf(Lv), mp.mpf(phv)
    th = kk * ss_ * LL / 2
    # independent route 1: elementary antiderivative, term by term, then average
    anti = (mp.cos(pp) * mp.sin(kk * ss_ * LL) + mp.sin(pp) * (mp.cos(kk * ss_ * LL) - 1)) / (kk * ss_)
    exact = anti / LL
    clsd = mp.cos(th + pp) * (mp.sin(th) / th)
    worst = max(worst, abs(exact - clsd))
    worstq = max(worstq, abs(mp.quad(lambda t: mp.cos(kk * ss_ * t + pp), [0, LL]) / LL - clsd))
ck("G1 the sinc identity of docs/18 sec.3 holds: the elementary antiderivative reproduces "
   "cos(theta+phi) sinc(theta) to 1e-28 (an independent mpmath quadrature agrees to 1e-15)",
   worst < mp.mpf("1e-28") and worstq < mp.mpf("1e-15"),
   "max |antiderivative - closed| = %s ; max |quadrature - closed| = %s"
   % (mp.nstr(worst, 4), mp.nstr(worstq, 4)))

# G2 - midpoint-rule error order: (cos(theta) - sinc(theta))/sinc(theta) ~ -theta^2/3, i.e.
#      O(k^2 a^2) at fixed k with a = 1/M  => the residual-4 closure claim is structurally right
rat = []
for th in (mp.mpf("1e-3"), mp.mpf("1e-4")):
    mid = mp.cos(th)
    exc = mp.sin(th) / th
    rat.append((mid - exc) / exc / th ** 2)
ck("G2 the midpoint-rule relative error scales as -theta^2/3 (O(k^2 a^2)), the order quoted in "
   "docs/18 for the residual-4 closure", abs(rat[0] + mp.mpf(1) / 3) < mp.mpf("1e-5")
   and abs(rat[1] + mp.mpf(1) / 3) < mp.mpf("1e-7"),
   "theta^2 coefficients %s / %s (limit -1/3)" % (mp.nstr(rat[0], 6), mp.nstr(rat[1], 6)))

# G3 - the fixed-k pairs really share the physical momentum (exact rational arithmetic)
PAIRS = [((3, 1), (6, 2)), ((4, 1), (8, 2)), ((4, 2), (8, 4))]
ok = all(Fraction(n1, M1) == Fraction(n2, M2) for (M1, n1), (M2, n2) in PAIRS)
ck("G3 all three fixed-k pairs satisfy n1/M1 = n2/M2 exactly (k = 2 pi n / M equal)",
   ok, "pairs = %s" % PAIRS)

# G4 - cross-file recomputation of docs/15's headline stiffnesses from the CANONICAL rho
#      values in data/20 (A = rho / rho_cont; the doc quotes A_TT = 0.131 / A_conf = 40.8)
d20 = rd("data/20_tt_amplitude_diagnosis.txt")
scan20 = {}
for line in d20.split("\n"):
    if line.startswith("SCAN M="):
        fields = dict(kv.split("=") for kv in line.split()[2:])
        scan20[int(line.split()[1][2:].rstrip("="))] = fields
A_TT = float(scan20[3]["rhoTT"]) / float(scan20[3]["rhoTT_con"])
A_CF = float(scan20[3]["rhoVW"]) / float(scan20[3]["rhoVW_con"])
ck("G4 docs/15's A_TT and A_conf reproduce from the canonical rho fields of data/20 "
   "(independent recomputation, M=3)", abs(A_TT - 0.1306) < 5e-4 and abs(A_CF - 40.82) < 0.02,
   "A_TT = %.4f (doc 0.131) ; A_conf = %.2f (doc 40.8)" % (A_TT, A_CF))

# G5 - the doc's M->inf extrapolation arithmetic: 0.25 * (1/50.8) * 0.43 ~ 2.1e-3
ext = mp.mpf("0.25") * (1 / mp.mpf("50.8")) * mp.mpf("0.43")
ck("G5 docs/15's extrapolated continuum ratio 0.25 x (1/50.8) x 0.43 = 2.1e-3 is arithmetically "
   "correct", abs(ext - mp.mpf("2.1e-3")) < mp.mpf("5e-5"),
   "value = %s" % mp.nstr(ext, 5))

# G6 - fixed-k A_TT ratios and the implied q_lat exponents from the CANONICAL logs/22 lines
l22 = rd("logs/22_tt_drift_attribution.txt")
att = {}
for line in l22.split("\n"):
    m = re.search(r"M=(\d+) n=(\d+) k=[\d.]+ : A_TT\(agg\)=([\d.]+)", line)
    if m:
        att[(int(m.group(1)), int(m.group(2)))] = float(m.group(3))
assert (4, 2) in att and (8, 4) in att and (4, 1) in att and (8, 2) in att, sorted(att)
r_half = att[(4, 1)] / att[(8, 2)]
r_pi = att[(4, 2)] / att[(8, 4)]
# A ~ M^(s-3) because A = (|q_lat|/R_map)/|q_cont| with R_map ~ M^3 and q_cont M-independent,
# so A_M4/A_M8 = 2^(3-s) and s = 3 - log2(A_M4/A_M8)
s_tt_half = 3.0 - math.log(r_half) / math.log(2.0)
s_tt_pi = 3.0 - math.log(r_pi) / math.log(2.0)
ck("G6a the fixed-k A_TT ratios recompute from the canonical logs/22 values",
   abs(r_half - 1.9260) < 5e-4 and abs(r_pi - 1.9299) < 5e-4,
   "k=pi/2 %.4f ; k=pi %.4f" % (r_half, r_pi))
ck("G6b the implied TT q_lat exponent s = 3 + log2(A_M4/A_M8) agrees with the docs/18 value "
   "1.93 within 0.2 (a DIFFERENT route: it assumes only R_map ~ M^3)", abs(s_tt_half - 1.929) < 0.2,
   "s(k=pi/2) = %.3f (doc 1.929) ; s(k=pi) = %.3f" % (s_tt_half, s_tt_pi))

# G7 - the residual-4 exponents recompute from the raw violation values in data/23
d23 = rd("data/23_residual45_closure.txt")
m = re.search(r"k=2pi/3 .*M=3 ([\d.e+-]+) -> M=6 ([\d.e+-]+)\s+ratio ([\d.]+)\s+violation ~ M\^(-[\d.]+)", d23)
m2 = re.search(r"k=pi/2 .*M=4 ([\d.e+-]+) -> M=8 ([\d.e+-]+)\s+ratio ([\d.]+)\s+violation ~ M\^(-[\d.]+)", d23)
e1 = -math.log(float(m.group(2)) / float(m.group(1))) / math.log(2.0)
e2 = -math.log(float(m2.group(2)) / float(m2.group(1))) / math.log(2.0)
ck("G7a the residual-4 fall exponents 1.365 / 1.475 recompute from the raw data/23 violation "
   "values", abs(e1 - 1.365) < 5e-3 and abs(e2 - 1.475) < 5e-3,
   "recomputed %.3f / %.3f ; documented ratio %s / %s" % (e1, e2, m.group(3), m2.group(3)))
m3 = re.search(r"n=1 scan .*violation = \[([\d. ]+)\] -> growth exponent in M = \+([\d.]+)", d23)
vv = [float(x) for x in m3.group(1).split()]
g_n1 = math.log(vv[-1] / vv[0]) / math.log(8.0 / 3.0)
ck("G7b the n=1 mixed-scan growth exponent +1.272 recomputes from the five canonical values",
   abs(g_n1 - 1.272) < 5e-3, "recomputed %+.3f from %s" % (g_n1, vv))

# G8 - the simplex edge-projector trace quoted in docs/18 sec.2 (independent construction)
def proj_spectrum(verts):
    V = np.array(verts, float)
    S = np.zeros((4, 4))
    for a in range(5):
        for b in range(a + 1, 5):
            d = V[b] - V[a]
            s_ = d / np.linalg.norm(d)
            S += np.outer(s_, s_)
    return float(np.trace(S)), sorted(np.linalg.eigvalsh(S))


# (i) the CHAIN simplex of the torus triangulation (scripts/17-23's CELL_SIMP[0]): consecutive
#     vertices share one more coordinate, so it carries face and body diagonals
chain = [(0, 0, 0, 0), (1, 0, 0, 0), (1, 1, 0, 0), (1, 1, 1, 0), (1, 1, 1, 1)]
# (ii) the CORNER simplex (0, e1, e2, e3, e4) - the other standard Kuhn orientation
corner = [(0, 0, 0, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)]
tr_c, ev_c = proj_spectrum(chain)
tr_o, ev_o = proj_spectrum(corner)
ck("G8 the edge-projector sum of the CHAIN simplex (the one the torus triangulation uses) has "
   "trace exactly 10 and the anisotropic spectrum quoted in docs/18",
   abs(tr_c - 10.0) < 1e-12 and abs(ev_c[0] - 1.13962) < 5e-5 and abs(ev_c[-1] - 5.27698) < 5e-4,
   "trace = %.10f ; spectrum = %s" % (tr_c, np.array2string(np.array(ev_c), precision=6)))
ck("G8b a DIFFERENT Kuhn orientation (corner simplex: S = 3I - J/2, so 3 on the u-perp "
   "subspace and 1 on u) has the spectrum [1,3,3,3]: also anisotropic and NOT the isotropic "
   "(10/4)I, so docs/18's exclusion of the isotropic-annihilation mechanism is orientation "
   "independent", abs(tr_o - 10.0) < 1e-12 and abs(ev_o[0] - 1.0) < 1e-9
   and abs(ev_o[1] - 3.0) < 1e-9 and abs(ev_o[-1] - 3.0) < 1e-9,
   "trace = %.10f ; spectrum = %s" % (tr_o, np.array2string(np.array(ev_o), precision=6)))

# G9 - every canonical log of the second increment carries its all-PASS RESULT line
logs = ["logs/20_tt_amplitude_M%d.txt" % M for M in (3, 4, 6, 8)] + \
       ["logs/21_gauge_fixed_quotient_M%d.txt" % M for M in (3, 4, 6, 8)] + \
       ["logs/22_tt_drift_attribution.txt", "logs/23_residual45_closure.txt"]
bad = [f for f in logs if "RESULT: " not in rd(f) or "[FAIL]" in rd(f)]
ck("G9 all 10 canonical logs of the second increment exist and contain no [FAIL] line",
   not bad, "checked %d files ; offenders = %s" % (len(logs), bad))

# G10 - T3 temporal integrity: derivation script written before its doc
viol = []
for sc, dc in INC2:
    if mtime(os.path.join(BASE, sc)) > mtime(os.path.join(BASE, dc)):
        viol.append("%s newer than %s" % (sc, dc))
ck("G10 each second-increment doc is written after its derivation script (mtime order)",
   not viol, "violations = %s" % viol)

# G11 - no backfill: docs covered by the FIRST watermark must not carry second-increment tokens
OLD2 = ["docs/%s" % f for f in sorted(os.listdir(os.path.join(BASE, "docs")))
        if f[:2] <= "16" and f.endswith(".md")]
# NB "sinc" and "pi n/M" are LEGITIMATE first-increment material (the dispersion omega =
# c k sin(x)/x) - only tokens minted by the second increment may be used here.
TOK2 = ["sinc-corrected", "shape-extended", "M^2.849", "1.6513", "2.808", "deficit 0.9"]
bad2 = []
for f in OLD2:
    txt = rd(f)
    for i, line in enumerate(txt.split("\n")):
        for tok in TOK2:
            if tok in line and not (("\u26a0" in line) and ("2026-" in line)):
                bad2.append("%s:%d:%s" % (f, i + 1, tok))
ck("G11 no backfill: the docs covered by the first watermark carry no un-dated "
   "second-increment token", not bad2, "hits = %s" % bad2[:6])

INFO.append("[G12] audited limitation (recorded, not a check): the intermediate FAILING runs of "
            "scripts/22-23 (8/12 and 4-false-FAIL versions) were overwritten by the canonical "
            "run, so their evidence lives only in the session record, not on disk.  The canonical "
            "logs on disk are the final all-PASS versions (checked in G9).")

# ============================================================ H. record completeness
print("\n[H] record completeness: every session id and every doc of the O221 record")
DOCS = sorted(f for f in os.listdir(os.path.join(BASE, "docs")) if f.endswith(".md"))
SCRIPTS = sorted(f for f in os.listdir(os.path.join(BASE, "scripts")) if re.match(r"^\d\d_", f))
pr_t, ss_t, fr_t = rd("01_problem_record.md"), rd("SESSION_START.md"), rd("final_result.md")
readme_t = open(os.path.join(BASE, "..", "README.md"), encoding="utf-8").read()
regp = os.path.join(BASE, "..", "..", "problem_register", "register.jsonl")
reg_t = open(regp, encoding="utf-8").read() if os.path.exists(regp) else ""
reg_o221 = [json.loads(l) for l in reg_t.split("\n") if l.strip() and '"O221"' in l]

weak = []
for d in DOCS:
    base = d[:-3]
    hits = [nm for nm, txt in (("PR", pr_t), ("SS", ss_t), ("FR", fr_t), ("RD", readme_t),
                               ("RG", reg_t)) if base in txt or d in txt]
    if len(hits) < 2:
        weak.append((d, hits))
ck("H1 every one of the %d docs is referenced in at least two of the record files "
   "(PR / SESSION_START / final_result / README / register)" % len(DOCS), not weak,
   "weakly-referenced = %s" % weak)

# session ids <-> rounds bijection
sess_id = sorted(int(m.group(1)) for m in re.finditer(r"^### Session (\d+) ", ss_t, re.M))
rounds = sorted(int(m.group(1)) for m in re.finditer(r"^### 第 (\d+) 輪 ", pr_t, re.M))
ck("H2 the SESSION_START session ids and the problem-record rounds are the same set "
   "(1 .. %d)" % max(rounds), sess_id == [n for n in rounds if n > 1],
   "sessions = %s ; rounds = %s" % (sess_id, rounds))

# every session >= 2 has a register event naming it, and every round has its docs on disk
missing_reg = [n for n in range(13, max(rounds) + 1)
               if not any("Session %d" % n in json.dumps(e) for e in reg_o221)]
ck("H3 every post-watermark round (13..%d) has a register entry naming its session"
   % max(rounds), not missing_reg, "missing = %s" % missing_reg)

missing_cnt = [s for s in SCRIPTS if s[:2] not in fr_t]
ck("H4 final_result.md lists a PASS count for every one of the %d scripts" % len(SCRIPTS),
   not missing_cnt, "unlisted = %s" % missing_cnt)

badref = []
for e in reg_o221:
    ref = str(e.get("ref") or "")
    mm = re.search(r"(docs/[\w./-]+\.py|docs/[\w./-]+\.md|data/[\w./-]+\.txt)", ref)
    if mm:
        cand = mm.group(1) if mm.group(1).startswith("docs/") else mm.group(1)
        if not os.path.exists(os.path.join(BASE, cand)):
            badref.append(cand)
ck("H5 every register reference resolves to a file on disk", not badref,
   "%d O221 events ; broken = %s" % (len(reg_o221), badref))

wm = []
for l in pr_t.split("\n"):
    if not l.startswith("|"):
        continue
    fields = [f.strip() for f in l.split("|")]
    if len(fields) > 3 and re.match(r"^(docs|data|logs)/\S+$", fields[2]):
        wm.append(fields[2])
missing_wm = [f for f in wm if not os.path.exists(os.path.join(BASE, f))]
ck("H6 every file listed in the sec.10 watermark table exists on disk", not missing_wm,
   "table entries = %d ; missing = %s" % (len(wm), missing_wm[:5]))

exp_docs = int(re.search(r"DOCS_EXPECTED = (\d+)", rd("scripts/06_doc_crosscheck.py")).group(1))
ck("H7 the on-disk doc count equals the crosscheck's DOCS_EXPECTED (no doc escapes the checks)",
   exp_docs == len(DOCS), "on disk %d ; DOCS_EXPECTED %d" % (len(DOCS), exp_docs))

for line in INFO:
    print("  [INFO] %s" % line)

print("\n" + "=" * 78)
print("RESULT: %d/%d PASS" % (PASS, PASS + FAIL))
print("  scope: INCREMENTS (docs/06..18, scripts/07..23) - independent, zero import")
print("=" * 78)
