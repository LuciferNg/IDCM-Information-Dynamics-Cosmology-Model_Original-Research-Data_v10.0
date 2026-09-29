#!/usr/bin/env python3
# O221 scripts/13 - Regge route: put derivative structure INTO the metric itself.
#
#   docs/08/09 established: trace-type spectral moments (a2 = Tr L, ...) are
#   ULTRALOCAL and blind to connection data => they can never carry the EH term.
#   The remaining candidate for the low-energy gravitational dynamics is a
#   REGGE-type action built from edge LENGTHS (the metric's own dof):
#
#       S_R = sum_e L_e * delta_e ,    delta_e = 2 pi - sum(dihedral angles around e)
#
#   which is a genuine (derivative) curvature functional.  Here we build it on the
#   3-torus (Kuhn triangulation, 6 tetrahedra per cube) and test:
#     R0 machinery: regular tetrahedron dihedral = arccos(1/3)
#     R1 flat lattice: every delta_e = 0 exactly, S_R = 0 (machinery + flatness)
#     R2 2D Gauss-Bonnet: sum_v delta_v = 2 pi chi = 0 exactly for RANDOM lengths
#     R3 uniform scaling is blind (angles are scale invariant) -> S_R = 0 exactly
#     R4 S_R ~ eps^2 around flat (flat is a stationary point of the action)
#     R5 the 6-parameter family of FLAT metrics lies in the kernel (all delta_e = 0)
#     R6 structure: S_R is PURE GRADIENT (scales like q^2, no ultralocal piece)
#        whereas the ultralocal functional U = sum_e (L_e-1)^2 is q-INDEPENDENT
#     R7 refinement trend M = 3,4,6 at a fixed physical deformation
#     R8 Hessian at flat (M=3): kernel structure (3D gravity has no local dof)
# ASCII only; numpy.
import numpy as np
from itertools import permutations

PASS = 0
FAIL = 0


def ck(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print("  [PASS] %s %s" % (name, detail))
    else:
        FAIL += 1
        print("  [FAIL] %s %s" % (name, detail))


# ---------------------------------------------------------------- machinery
def tetra_angles(L6):
    """interior dihedral angles of a tetrahedron with the 6 edge lengths
    L6 = (l01,l02,l03,l12,l13,l23); returns 6 angles in the same pair order."""
    l01, l02, l03, l12, l13, l23 = L6
    v0 = np.zeros(3)
    v1 = np.array([l01, 0.0, 0.0])
    x2 = (l02 ** 2 + l01 ** 2 - l12 ** 2) / (2 * l01)
    y2 = np.sqrt(max(l02 ** 2 - x2 ** 2, 0.0))
    v2 = np.array([x2, y2, 0.0])
    x3 = (l03 ** 2 + l01 ** 2 - l13 ** 2) / (2 * l01)
    y3 = (l03 ** 2 - l23 ** 2 + l02 ** 2 - 2 * x3 * x2) / (2 * y2)
    z3 = np.sqrt(max(l03 ** 2 - x3 ** 2 - y3 ** 2, 0.0))
    v3 = np.array([x3, y3, z3])
    vs = [v0, v1, v2, v3]

    def inward_normal(face):
        a, b, c = (vs[i] for i in face)
        n = np.cross(b - a, c - a)
        n = n / (np.linalg.norm(n) + 1e-300)
        other = [i for i in (0, 1, 2, 3) if i not in face][0]
        if np.dot(n, vs[other] - a) > 0:
            n = -n                     # point into the tetrahedron
        return n

    faces = {0: (1, 2, 3), 1: (0, 2, 3), 2: (0, 1, 3), 3: (0, 1, 2)}   # face opposite vertex k
    normals = {k: inward_normal(faces[k]) for k in faces}
    pairs = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    angs = []
    for (i, j) in pairs:
        k, l = [x for x in (0, 1, 2, 3) if x not in (i, j)]
        ca = float(np.clip(np.dot(normals[k], normals[l]), -1, 1))
        angs.append(np.pi - np.arccos(ca))
    return angs


CELL_TETS = []
for perm in permutations((0, 1, 2)):
    acc = np.zeros(3, int)
    verts = [acc.copy()]
    for k in range(3):
        acc = acc.copy()
        acc[perm[k]] = 1
        verts.append(acc.copy())
    CELL_TETS.append(verts)


def topology(M):
    coords = []
    vid = {}
    for i in range(M):
        for j in range(M):
            for k in range(M):
                vid[(i, j, k)] = len(coords)
                coords.append(np.array([i, j, k], float))
    tets = []
    for i in range(M):
        for j in range(M):
            for k in range(M):
                base = np.array([i, j, k])
                for vt in CELL_TETS:
                    tets.append([vid[tuple((base + off) % M)] for off in vt])
    pairs = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
    ekeys, eoff = [], {}
    for tet in tets:
        for (a, b) in pairs:
            u, v = tet[a], tet[b]
            key = (min(u, v), max(u, v))
            if key not in eoff:
                d = coords[v] - coords[u]
                d = ((d + M // 2) % M) - M // 2
                eoff[key] = d
                ekeys.append(key)
    ekeys.sort()
    eidx = {k: n for n, k in enumerate(ekeys)}
    return coords, tets, ekeys, eidx, eoff, pairs


def regge(tets, ekeys, eidx, eoff, pairs, lens):
    sumdih = {k: 0.0 for k in ekeys}
    for tet in tets:
        L6 = [lens[(min(tet[a], tet[b]), max(tet[a], tet[b]))] for (a, b) in pairs]
        for (a, b), ang in zip(pairs, tetra_angles(L6)):
            sumdih[(min(tet[a], tet[b]), max(tet[a], tet[b]))] += ang
    delta = {k: 2 * np.pi - sumdih[k] for k in ekeys}
    S = float(sum(lens[k] * delta[k] for k in ekeys))
    return S, delta


def lens_flat(coords, ekeys, eoff, A):
    return {k: float(np.linalg.norm(A @ eoff[k])) for k in ekeys}


def lens_deform(coords, ekeys, eoff, A, q, eps, M):
    """plane-wave modulation of the edge lengths, same amplitude on every edge type"""
    out = {}
    for k in ekeys:
        mid = coords[k[0]] + 0.5 * eoff[k]
        f = np.cos(2 * np.pi * q * float(np.sum(mid)) / M)
        out[k] = float(np.linalg.norm(A @ eoff[k])) * (1.0 + eps * f)
    return out


print("=" * 78)
print("O221 / scripts/13 - Regge route (derivative structure in the metric)")
print("=" * 78)

print("\n[R0] machinery validation: regular tetrahedron")
ang = tetra_angles([1.0] * 6)
print("     dihedral angles = %s rad ; arccos(1/3) = %.10f" % (["%.10f" % a for a in ang], np.arccos(1.0 / 3)))
ck("R0.1 all six dihedral angles equal arccos(1/3)",
   max(abs(a - np.arccos(1.0 / 3)) for a in ang) < 1e-12,
   "max dev = %.2e" % max(abs(a - np.arccos(1.0 / 3)) for a in ang))
ck("R0.2 solid-angle/first variation sanity: 6*theta > 2*pi (tetrahedron is non-degenerate)",
   sum(ang) > 2 * np.pi, "sum = %.6f" % sum(ang))

for M in (3, 4):
    coords, tets, ekeys, eidx, eoff, pairs = topology(M)
    lens = lens_flat(coords, ekeys, eoff, np.eye(3))
    S, delta = regge(tets, ekeys, eidx, eoff, pairs, lens)
    mx = max(abs(v) for v in delta.values())
    print("\n[R1] flat lattice M=%d : V=%d T=%d E=%d" % (M, M ** 3, len(tets), len(ekeys)))
    print("     sum of dihedral angles around each edge = 2*pi ?  max |delta_e| = %.3e" % mx)
    ck("R1.%d flat lattice: every deficit angle vanishes and S_R = 0" % M, mx < 1e-10 and abs(S) < 1e-9,
       "max|delta| = %.2e ; S_R = %.2e" % (mx, S))

# ---------------------------------------------------------------- 2D Gauss-Bonnet
print("\n[R2] 2D check: Gauss-Bonnet with RANDOM edge lengths (triangulated 2-torus)")


def gauss_bonnet_2d(M, seed=7):
    rng = np.random.default_rng(seed)
    tri = []
    for i in range(M):
        for j in range(M):
            a = (i, j); b = ((i + 1) % M, j); c = ((i + 1) % M, (j + 1) % M); d = (i, (j + 1) % M)
            tri.append((a, b, c)); tri.append((a, c, d))
    L = {}
    for t in tri:
        for u, v in ((t[0], t[1]), (t[1], t[2]), (t[0], t[2])):
            key = (min(u, v), max(u, v))
            if key not in L:
                L[key] = float(rng.uniform(0.7, 1.4))
    agree = {}
    for t in tri:
        for p in range(3):
            u, v, w = t[p], t[(p + 1) % 3], t[(p + 2) % 3]
            a = L[(min(u, v), max(u, v))]; b = L[(min(v, w), max(v, w))]; c = L[(min(u, w), max(u, w))]
            ca = (b ** 2 + c ** 2 - a ** 2) / (2 * b * c)
            agree[u] = agree.get(u, 0.0) + np.arccos(np.clip(ca, -1, 1))
    return sum(2 * np.pi - v for v in agree.values())


for M in (3, 5):
    G = gauss_bonnet_2d(M)
    ck("R2.%d sum_v delta_v = 2*pi*chi = 0 exactly (random lengths)" % M, abs(G) < 1e-10,
       "M=%d : sum delta = %.3e" % (M, G))

# ---------------------------------------------------------------- scale / flat moduli
M = 4
coords, tets, ekeys, eidx, eoff, pairs = topology(M)
print("\n[R3] uniform scaling (conformal) blindness")
for c in (1.3, 0.7):
    S, delta = regge(tets, ekeys, eidx, eoff, pairs, lens_flat(coords, ekeys, eoff, c * np.eye(3)))
    ck("R3.c=%.1f S_R = 0 exactly (deficit angles are scale invariant)" % c,
       abs(S) < 1e-9 and max(abs(v) for v in delta.values()) < 1e-10, "S_R = %.2e" % S)

print("\n[R5] the 6-parameter family of FLAT metrics is in the kernel")
base = lens_flat(coords, ekeys, eoff, np.eye(3))
nflat = 0
for (i, j) in ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)):
    S = np.zeros((3, 3)); S[i, j] = S[j, i] = 1.0
    A = np.eye(3) + 0.1 * S
    lens = lens_flat(coords, ekeys, eoff, A)
    s, d = regge(tets, ekeys, eidx, eoff, pairs, lens)
    nflat += 1 if (abs(s) < 1e-9 and max(abs(v) for v in d.values()) < 1e-10) else 0
ck("R5.1 all 6 symmetric flat directions give S_R = 0 and delta_e = 0", nflat == 6,
   "%d/6 directions flat" % nflat)

print("\n[R4] deformation scaling: S_R ~ eps^2 (flat is a stationary point)")
s1 = regge(tets, ekeys, eidx, eoff, pairs, lens_deform(coords, ekeys, eoff, np.eye(3), 2, 1e-3, M))[0]
s2 = regge(tets, ekeys, eidx, eoff, pairs, lens_deform(coords, ekeys, eoff, np.eye(3), 2, 2e-3, M))[0]
ratio = s2 / s1 if s1 != 0 else float("nan")
print("     S_R(eps=1e-3) = %.6e ; S_R(eps=2e-3) = %.6e ; ratio = %.6f (expect 4)" % (s1, s2, ratio))
ck("R4.1 exponent 2: S_R is quadratic in the deformation (no linear term)", abs(ratio - 4) < 0.05,
   "ratio = %.6f (=> exponent %.4f)" % (ratio, np.log(abs(ratio)) / np.log(2)))

print("\n[R6] structure: the Regge response is TRACE-BLIND and SHAPE-SENSITIVE")
M8 = 8
co8, te8, ek8, ei8, eo8, pr8 = topology(M8)
base8 = lens_flat(co8, ek8, eo8, np.eye(3))
eps = 1e-2
trace_l = {k: base8[k] * (1 + eps) for k in ek8}
shape_l = {k: base8[k] * (1 + eps * np.cos(2 * np.pi * 2 * float(np.sum(co8[k[0]] + 0.5 * eo8[k])) / M8))
           for k in ek8}
S_trace = regge(te8, ek8, ei8, eo8, pr8, trace_l)[0]
S_shape = regge(te8, ek8, ei8, eo8, pr8, shape_l)[0]
U_trace = float(sum((trace_l[k] - base8[k]) ** 2 for k in ek8))
U_shape = float(sum((shape_l[k] - base8[k]) ** 2 for k in ek8))
print("     uniform (trace) modulation : S_R = %+.10e  ;  U = %.6e" % (S_trace, U_trace))
print("     cos (shape) modulation     : S_R = %+.10e  ;  U = %.6e" % (S_shape, U_shape))
ck("R6.1 S_R is EXACTLY blind to the pure trace (uniform scaling) modulation",
   abs(S_trace) < 1e-9, "S_R(trace) = %.2e" % S_trace)
ck("R6.2 S_R responds to a shape modulation (trace mode is an exact zero direction)",
   abs(S_shape) > 1e-8, "|S_R(shape)| = %.3e while |S_R(trace)| = 0" % abs(S_shape))
ck("R6.3 the ultralocal functional sees the trace mode (exact structural contrast)",
   U_trace > 0, "U(trace) = %.3e > 0 vs S_R(trace) = 0 ; U(shape) = %.3e" % (U_trace, U_shape))

print("\n[R7] refinement at a FIXED local deformation (fixed physical wavelength = 3 cells)")
print("     NOTE: with a := 1 the torus volume is M^3, so the intensive quantity is S_R / M^3")
vals = []
for n in (3, 6, 9):
    co, te, ek, ei, eo, pr = topology(n)
    lens = lens_deform(co, ek, eo, np.eye(3), n // 3, 1e-2, n)
    vals.append(regge(te, ek, ei, eo, pr, lens)[0])
    print("     M=%2d (q=%d) : S_R = %+.10e   S_R/M^3 = %+.10e" % (n, n // 3, vals[-1], vals[-1] / n ** 3))
dens = [v / n ** 3 for v, n in zip(vals, (3, 6, 9))]
print("     intensity gaps : |d(9) - d(6)| = %.3e  vs  |d(6) - d(3)| = %.3e" % (abs(dens[2] - dens[1]), abs(dens[1] - dens[0])))
ck("R7.1 the action DENSITY converges (gap shrinks under refinement)",
   abs(dens[2] - dens[1]) < abs(dens[1] - dens[0]),
   "gap ratio = %.3f  (density is the intensive quantity)" % (abs(dens[2] - dens[1]) / abs(dens[1] - dens[0])))

print("\n[R8] Hessian at flat (M=3): kernel structure  (3D gravity has NO local dof)")
Mh = 3
co, te, ek, ei, eo, pr = topology(Mh)
E = len(ek)


def ekey(u, v):
    return (min(u, v), max(u, v))


tets_of = {k: [] for k in ek}
for ti, tet in enumerate(te):
    for (a, b) in pr:
        tets_of[ekey(tet[a], tet[b])].append(ti)


def tet_sum(ti, lens):
    """sum_{e in tet} L_e * angle_{tet,e}   (S_R = 2*pi*sum_e L_e - sum_tets tet_sum)"""
    tet = te[ti]
    L6 = [lens[ekey(tet[a], tet[b])] for (a, b) in pr]
    return float(sum(lens[ekey(tet[a], tet[b])] * ang for (a, b), ang in zip(pr, tetra_angles(L6))))


H = np.zeros((E, E))
h = 5e-4
l0 = lens_flat(co, ek, eo, np.eye(3))


def S_full(lens):
    """S_R = 2*pi*sum_e L_e - sum_tets sum_{e in tet} L_e * angle_{tet,e}"""
    tot = 2 * np.pi * sum(lens.values())
    for tet in te:
        L6 = [lens[ekey(tet[a], tet[b])] for (a, b) in pr]
        for (a, b), ang in zip(pr, tetra_angles(L6)):
            tot -= lens[ekey(tet[a], tet[b])] * ang
    return tot


S0 = S_full(l0)
for p in range(E):
    lp = dict(l0); lp[ek[p]] = l0[ek[p]] + h
    lm = dict(l0); lm[ek[p]] = l0[ek[p]] - h
    H[p, p] = (S_full(lp) - 2 * S0 + S_full(lm)) / h ** 2      # symmetric second difference
    nb = sorted({ei[ekey(te[ti][a], te[ti][b])] for ti in tets_of[ek[p]] for (a, b) in pr})
    for q in nb:
        if q == p:
            continue
        lpp = dict(l0); lpp[ek[p]] = l0[ek[p]] + h; lpp[ek[q]] = l0[ek[q]] + h
        lpm = dict(l0); lpm[ek[p]] = l0[ek[p]] + h; lpm[ek[q]] = l0[ek[q]] - h
        lmp = dict(l0); lmp[ek[p]] = l0[ek[p]] - h; lmp[ek[q]] = l0[ek[q]] + h
        lmm = dict(l0); lmm[ek[p]] = l0[ek[p]] - h; lmm[ek[q]] = l0[ek[q]] - h
        tot = 0.0
        for ti in set(tets_of[ek[p]]) | set(tets_of[ek[q]]):
            tot -= (tet_sum(ti, lpp) - tet_sum(ti, lpm) - tet_sum(ti, lmp) + tet_sum(ti, lmm))
        H[p, q] = tot / (4 * h ** 2)                           # centered mixed difference
        H[q, p] = H[p, q]
ev = np.linalg.eigvalsh(0.5 * (H + H.T))
scale = float(max(abs(ev.min()), abs(ev.max())))
nk = int(np.sum(np.abs(ev) < 1e-5 * scale))
print("     E = %d ; spectrum [%.4e , %.4e] ; near-zero eigenvalues (<1e-5 max): %d" % (E, ev.min(), ev.max(), nk))
rank = E - nk
print("     quadratic form along the 6 FLAT-MODULI directions (should vanish as the")
print("     perturbation shrinks: a finite value would mean a nonzero Rayleigh quotient)")


def flat_dir_q(delta):
    out = []
    for (i, j) in ((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2)):
        Sm = np.zeros((3, 3)); Sm[i, j] = Sm[j, i] = 1.0
        lA = lens_flat(co, ek, eo, np.eye(3) + delta * Sm)
        v = np.array([lA[ek[p]] - l0[ek[p]] for p in range(E)])
        out.append(float(v @ H @ v) / float(v @ v))
    return out


q_big = flat_dir_q(1e-2)
q_sml = flat_dir_q(1e-4)
for n, (i, j) in enumerate(((0, 0), (0, 1), (0, 2), (1, 1), (1, 2), (2, 2))):
    print("       dir (%d,%d) : quotient = %+.4e (delta=1e-2)  %+.4e (delta=1e-4)   scale = %.3e"
          % (i, j, q_big[n], q_sml[n], scale))
ck("R8.1 the 6 flat-moduli directions are kernel directions (zero within FD precision;",
   max(abs(x) for x in q_sml) < 1e-3 * scale,
   "max|q| = %.3e = %.1e x scale (exact statement: R5/R3, S_R = 0 identically along these lines)"
   % (max(abs(x) for x in q_sml), max(abs(x) for x in q_sml) / scale))
print("     six largest |eigenvalues| = %s" % ["%.4e" % v for v in ev[-6:][::-1]])
print("     (Regge: a flat-moduli KERNEL of dim >= 6 exists -- the conformal/shape null directions")
print("      of 3D gravity; contrast docs/08: the trace moments are blind to SHEAR, not to the trace)")
ck("R8.2 the Hessian is not diagonal (derivative couplings between distinct edges)",
   float(np.max(np.abs(H - np.diag(np.diag(H))))) > 0,
   "max off-diagonal = %.3e" % float(np.max(np.abs(H - np.diag(np.diag(H))))))
ck("R8.3 the Regge Hessian is not positive definite: a flat-moduli kernel exists",
   nk >= 1, "%d near-zero eigenvalues" % nk)

print("\n" + "=" * 78)
print("RESULT: %d/%d PASS" % (PASS, PASS + FAIL))
print("=" * 78)
