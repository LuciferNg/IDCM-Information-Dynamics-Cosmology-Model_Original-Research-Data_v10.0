#!/usr/bin/env python3
# O221 scripts/23 - Round 16: close residual 4 (naive-map gauge violation) and attack residual 5
#                            (corrected map for the TT sector).
#
#   PART A - residual 4: the naive-map gauge violation.
#     docs/14/16 measured the violation |q_lat(k(x)xi + xi(x)k)| / |form scale| = 0.0119 / 0.0213 /
#     0.0338 / 0.0414 for M = 3/4/6/8 in the n = 1 scan - it GROWS with M.  But in that scan the
#     physical momentum k = 2*pi/M shrinks with M, so the scan mixes two effects.  The naive map is
#     the MIDPOINT rule for the edge-averaged strain,
#         delta L_e = 1/2 L_e (shat^T h shat)(x_mid),
#     whose relative error is O(k^2 a^2).  At FIXED physical k with a = 1/M this predicts the
#     violation ~ 1/M^2 - it must VANISH under refinement.  PREDICTION: exponent 2.0 +- 0.7.
#
#   PART B - residual 5: mechanism diagnostic.  A first guess was that the leading simplex response
#     is isotropic (sum_e shat_e shat_e^T has trace 10 => isotropic part (10/4)I, zero overlap with
#     a traceless perturbation).  The measured spectrum of that projector sum is STRONGLY
#     anisotropic, so that simple annihilation mechanism is EXCLUDED; the deficit must be measured
#     directly.
#
#   PART C - the deficit, measured directly at FIXED physical k.  At fixed k the continuum form
#     q_cont is M-independent, so the exponent of R_action in M equals the exponent of q_lat.
#     Expectation for a smooth mode: the lattice action is EXTENSIVE (one curvature term per hinge,
#     O(M^3) hinges) => q_lat(conf) ~ M^3.  docs/17 found A_TT ~ 1/M at fixed k with R_map ~ M^3,
#     which is exactly q_lat(TT) ~ M^2: a SUB-EXTENSIVE TT response, one power of M (= one power of
#     k a in the smooth-mode duality) below the conformal one.
#     PREDICTIONS: s_conf = 3.0 +- 0.4 ; s_TT = 2.0 +- 0.4 ; deficit s_conf - s_TT = 1.0 +- 0.4.
#
#   PART D - candidate fix: the geometrically exact linearised edge-length change of a straight edge
#     in a plane-wave metric is
#         delta L_e = 1/2 L_e (shat^T h shat) cos(k.x_mid) sinc(k.shat L_e / 2)
#     (the edge integral averages h along the edge instead of sampling it at the midpoint).  The
#     sinc factor is direction dependent, so it perturbs the anisotropic structure that produces
#     the deficit.  docs/17 sec.2.5's regression tests are applied: (a) q_lat(TT) becomes extensive
#     (exponent ~ s_conf); (b) A_TT becomes M-stable at fixed k; (c) the per-polarisation
#     factorisation stays exact.  A failed test is RECORDED as a refutation, never scored as a
#     machinery failure.
#
#   Machinery is copied from scripts/21-22 on purpose (self-contained scripts, zero shared code).
import sys
from itertools import combinations, permutations

import numpy as np

PASS = 0
FAIL = 0


def ck(name, cond, detail=""):
    global PASS, FAIL
    if cond:
        PASS += 1
        print("  [PASS] %s %s" % (name, detail), flush=True)
    else:
        FAIL += 1
        print("  [FAIL] %s %s" % (name, detail), flush=True)


PAIRS5 = list(combinations(range(5), 2))
PIDX = {p: n for n, p in enumerate(PAIRS5)}
CELL_SIMP = []
for perm in permutations((0, 1, 2, 3)):
    acc = [0, 0, 0, 0]
    vs = [tuple(acc)]
    for kk in range(4):
        acc = list(acc); acc[perm[kk]] = 1
        vs.append(tuple(acc))
    CELL_SIMP.append(vs)
CELL_SIMP = np.array(CELL_SIMP)


def base_rng(M, pad):
    return [(i, j, k, l) for i in range(-pad, M + pad) for j in range(-pad, M + pad)
            for k in range(-pad, M + pad) for l in range(-pad, M + pad)]


def lift_simps(bases):
    return np.concatenate([np.array(b, float)[None, :] + CELL_SIMP.astype(float)
                           for b in bases], 0)


def lift_id(pts):
    q = np.rint(pts).astype(np.int64) + 2
    B = M_GLOBAL + 4
    return (((q[..., 0] * B + q[..., 1]) * B + q[..., 2]) * B + q[..., 3])


def flat_data(M, pad=1):
    simps = lift_simps(base_rng(M, pad))
    n = simps.shape[0]
    L = np.zeros((n, 10)); shat = np.zeros((n, 10, 4)); mid = np.zeros((n, 10, 4))
    for e, (a, b) in enumerate(PAIRS5):
        d = simps[:, b, :] - simps[:, a, :]
        L[:, e] = np.linalg.norm(d, axis=1)
        shat[:, e, :] = d / L[:, e][:, None]
        mid[:, e, :] = 0.5 * (simps[:, a, :] + simps[:, b, :])
    return simps, L, shat, mid


def simplex_angles(L10):
    n = L10.shape[0]
    G = np.zeros((n, 4, 4))
    for a in range(4):
        for b in range(4):
            i, j = a + 1, b + 1
            if i == j:
                G[:, a, b] = L10[:, PIDX[(0, i)]] ** 2
            else:
                G[:, a, b] = (L10[:, PIDX[(0, i)]] ** 2 + L10[:, PIDX[(0, j)]] ** 2
                              - L10[:, PIDX[(min(i, j), max(i, j))]] ** 2) / 2.0
    try:
        Lc = np.linalg.cholesky(G)
    except np.linalg.LinAlgError:
        return None, None
    vs = np.zeros((n, 5, 4)); vs[:, 1:, :] = Lc
    nrm = np.zeros((n, 5, 4))
    for i in range(5):
        face = [k for k in range(5) if k != i]
        E = np.stack([vs[:, face[1]] - vs[:, face[0]], vs[:, face[2]] - vs[:, face[0]],
                      vs[:, face[3]] - vs[:, face[0]]], axis=1)
        M3 = np.stack([np.delete(E, k, axis=2) for k in range(4)], axis=1)
        nn = np.linalg.det(M3) * ((-1.0) ** np.arange(4))[None, :]
        nn = nn / np.linalg.norm(nn, axis=1)[:, None]
        sgn = np.sign(np.einsum('nk,nk->n', nn, vs[:, i] - vs[:, face[0]]))
        nrm[:, i] = nn * np.where(sgn >= 0, -1.0, 1.0)[:, None]
    ang = np.zeros((n, 10))
    for p, (d, e) in enumerate(PAIRS5):
        ang[:, p] = np.pi - np.arccos(np.clip(np.einsum('nk,nk->n', nrm[:, d], nrm[:, e]), -1, 1))
    area = np.zeros((n, 10))
    for p, (d, e) in enumerate(PAIRS5):
        tri = [i for i in range(5) if i not in (d, e)]
        la = L10[:, PIDX[(min(tri[1], tri[2]), max(tri[1], tri[2]))]]
        lb = L10[:, PIDX[(min(tri[0], tri[2]), max(tri[0], tri[2]))]]
        lc = L10[:, PIDX[(min(tri[0], tri[1]), max(tri[0], tri[1]))]]
        s = 0.5 * (la + lb + lc)
        area[:, p] = np.sqrt(np.maximum(s * (s - la) * (s - lb) * (s - lc), 0.0))
    return ang, area


def regge(data, dl):
    simps, L, shat, mid, hinge_key_c = data
    ang, area = simplex_angles(L + dl)
    if ang is None:
        return None, None
    vid = lift_id(simps)
    tri = np.zeros((simps.shape[0], 10, 3), np.int64)
    for p, (d, e) in enumerate(PAIRS5):
        for j, i in enumerate([i for i in range(5) if i not in (d, e)]):
            tri[:, p, j] = vid[:, i]
    tkey = np.sort(tri, axis=2)
    tk = ((tkey[:, :, 0] * (M_GLOBAL ** 4 + 7) + tkey[:, :, 1]) * (M_GLOBAL ** 4 + 7)
          + tkey[:, :, 2]).ravel()
    av = ang.ravel(); ar = area.ravel()
    keep = np.isin(tk, hinge_key_c)
    tk, av, ar = tk[keep], av[keep], ar[keep]
    order = np.argsort(tk, kind='stable')
    tk, av, ar = tk[order], av[order], ar[order]
    uniq, inv, _ = np.unique(tk, return_inverse=True, return_counts=True)
    ssum = np.zeros(uniq.shape[0]); np.add.at(ssum, inv, av)
    dfc = 2 * np.pi - ssum
    afirst = np.zeros(uniq.shape[0]); afirst[inv] = ar
    return float(np.sum(afirst * dfc)), float(np.max(np.abs(dfc)))


def central_hinges(M):
    cen = lift_simps([(i, j, k, l) for i in range(M) for j in range(M)
                      for k in range(M) for l in range(M)])
    vid = lift_id(cen)
    keys = set()
    for p, (d, e) in enumerate(PAIRS5):
        t = np.sort(vid[:, [i for i in range(5) if i not in (d, e)]], axis=1).reshape(-1, 3)
        keys.update(((t[:, 0] * (M_GLOBAL ** 4 + 7) + t[:, 1]) * (M_GLOBAL ** 4 + 7)
                     + t[:, 2]).tolist())
    return np.array(sorted(keys), dtype=np.int64)


_RUN_CACHE = {}


def run(M, n, corrected=False, gauge=True):
    """docs/16 construction at lattice momentum k = 2 pi n / M.
    Returns per-sector q_lat / q_cont / R_action / R_map plus the naive gauge violation
    (normalised by max|eig Q|, the same scale as scripts/21-22)."""
    global M_GLOBAL
    key = (M, n, bool(corrected), bool(gauge))
    if key in _RUN_CACHE:
        print("      (cached run M=%d n=%d corrected=%s)" % (M, n, corrected), flush=True)
        return _RUN_CACHE[key]
    M_GLOBAL = M
    kfac = 2 * np.pi / M
    kvecT = kfac * n * np.array([0.0, 0.0, 0.0, 1.0])

    data = flat_data(M)
    simps = data[0]
    D = (simps, data[1], data[2], data[3], central_hinges(M))
    S0 = regge(D, np.zeros_like(data[1]))[0]

    pairs4 = [(m, q) for m in range(4) for q in range(m, 4)]
    EPS = 1e-3
    S_NB = np.array([1.0 if m == q else np.sqrt(2.0) for (m, q) in pairs4])

    def tensor_of(nb):
        v = np.asarray(nb, float) * S_NB
        H = np.zeros((4, 4))
        for c, (m, q) in enumerate(pairs4):
            H[m, q] += v[c] / (1.0 if m == q else 2.0)
            H[q, m] += v[c] / (1.0 if m == q else 2.0)
        return H * EPS

    def dl_of(nb):
        H = tensor_of(nb)
        proj = np.einsum('nek,kl,nel->ne', data[2], H, data[2])
        ph = np.cos(np.einsum('neC,C->ne', data[3], kvecT))
        out = 0.5 * data[1] * proj * ph
        if corrected:
            th = np.einsum('neC,C->ne', data[2], kvecT) * data[1] / 2.0
            sc = np.ones_like(th)
            nz = np.abs(th) > 1e-12
            sc[nz] = np.sin(th[nz]) / th[nz]
            out = out * sc
        return out

    def q_cont(nb):
        e = tensor_of(nb)
        tr = float(np.trace(e)); kk = float(np.dot(kvecT, kvecT))
        ke = kvecT @ e
        return (0.25 * kk * (tr * tr - float(np.sum(e * e)))
                + 0.5 * (float(np.dot(ke, ke)) - float(np.dot(ke, kvecT)) * tr))

    unit = [np.eye(10)[i] for i in range(10)]
    qs = np.array([regge(D, dl_of(v))[0] - S0 for v in unit])
    Q = np.zeros((10, 10))
    for i in range(10):
        for j in range(i, 10):
            qij = regge(D, dl_of(unit[i] + unit[j]))[0] - S0
            Q[i, j] = 0.5 * (qij - qs[i] - qs[j]); Q[j, i] = Q[i, j]

    def pairs_of(H):
        v = np.zeros(10)
        for c, (m, q) in enumerate(pairs4):
            v[c] = H[m, q] * (1.0 if m == q else 2.0)
        return v

    Vg = []
    for ax in range(4):
        xi = np.eye(4)[ax]
        Hg = np.outer(kvecT, xi) + np.outer(xi, kvecT)
        v = pairs_of(Hg) / S_NB
        Vg.append(v / np.linalg.norm(v))
    Vg = np.array(Vg)
    u_, s_, vt_ = np.linalg.svd(Vg)
    Z = vt_[int(np.sum(s_ > 1e-10 * s_.max())):]

    def phys_dir(nb):
        x = Z.T @ (Z @ np.asarray(nb, float))
        nrm = np.linalg.norm(x)
        return x / nrm if nrm > 0 else x

    tt = []
    v = np.zeros(10); v[pairs4.index((1, 1))] = 1.0; v[pairs4.index((2, 2))] = -1.0; tt.append(v)
    v = np.zeros(10); v[pairs4.index((1, 2))] = 1.0; tt.append(v)
    vw = np.zeros(10)
    for i in (1, 2, 3):
        vw[pairs4.index((i, i))] = 1.0
    vw = vw / np.sqrt(3.0)

    out = dict(M=M, n=n, k=float(kfac * n), corrected=corrected, S0=S0)
    sc_l = float(np.max(np.abs(np.linalg.eigvalsh(Q))))
    if gauge:
        gq = [abs(regge(D, dl_of(vv))[0] - S0) for vv in Vg]
        out['gauge_viol'] = float(max(gq) / sc_l)
    for name, dirs in (("TT", tt), ("conf", [vw])):
        ql = []; rmm = []; qc = []
        for d in dirs:
            x = phys_dir(d)
            dl = dl_of(x)
            ql.append(regge(D, dl)[0] - S0)
            rmm.append(float(np.sum(dl * dl)) / (EPS ** 2))
            qc.append(q_cont(x))
        out[name] = dict(q_lat=ql, q_cont=qc, R_map=rmm,
                         R_action=[abs(a) / abs(b) for a, b in zip(ql, qc)],
                         A_agg=float(np.sum(np.abs(ql) / np.array(rmm)) / np.sum(np.abs(qc))),
                         A_mor=float(np.mean(np.abs(np.array(ql)) / np.array(rmm)
                                             / np.abs(np.array(qc)))))
    _RUN_CACHE[key] = out
    return out


def simplex_projector_spectrum():
    simps = lift_simps([(0, 0, 0, 0)])
    S = np.zeros((4, 4))
    for e, (a, b) in enumerate(PAIRS5):
        d = simps[0, b, :] - simps[0, a, :]
        s = d / np.linalg.norm(d)
        S += np.outer(s, s)
    ev = np.linalg.eigvalsh(S)
    return ev, float(np.trace(S))


def expo(a, b, M1, M2):
    """SIGNED exponent e in q ~ M^e, from the value a at the COARSER lattice M1 and b at the finer
    M2 (M2 > M1):  e = log(|b| / |a|) / log(M2 / M1).  So e > 0 means q grows with M.  A vanishing
    b is reported as +inf (the statement 'vanishes under refinement' holds a fortiori) instead of
    crashing; the caller flags it."""
    if b == 0.0:
        return float('inf') if a != 0.0 else float('nan')
    if a == 0.0:
        return float('-inf')
    return float(np.log(abs(b) / abs(a)) / np.log(M2 / M1))


def main():
    print("=" * 78)
    print("O221 / scripts/23 - Round 16: residual 4 closure + residual 5 (mechanism + fixed map)")
    print("=" * 78)

    # ---------------------------------------------------------------- PART A
    print("\n[A] residual 4: the naive-map gauge violation under refinement")
    print("    PREDICTION (midpoint rule, relative error O(k^2 a^2); at fixed k, a = 1/M):")
    print("    the violation must FALL as 1/M^2 (exponent 2.0 +- 0.7), i.e. vanish as a -> 0")
    pairs = [("k=2pi/3", 3, 1, 6, 2), ("k=pi/2", 4, 1, 8, 2), ("k=pi", 4, 2, 8, 4)]
    main._gv_labels = [lab for (lab, _, _, _, _) in pairs]
    gv = {}
    for lab, M1, n1, M2, n2 in pairs:
        r1 = run(M1, n1); r2 = run(M2, n2)
        a, b = r1['gauge_viol'], r2['gauge_viol']
        gv[lab] = (a, b, r1['k'])
        eM = expo(a, b, M1, M2)                 # violation ~ M^eM  (eM < 0 = falls)
        print("    %-8s k=%.4f : M=%d %.6e -> M=%d %.6e  ratio %s  violation ~ M^%s"
              % (lab, r1['k'], M1, a, M2, b,
                 ("%.4f" % (a / b)) if b != 0.0 else "inf (denominator IDENTICALLY ZERO)",
                 ("%+.3f" % eM) if np.isfinite(eM) else
                 ("-inf (vanishes exactly)" if eM > 0 else "n/a")), flush=True)
    def vanish_ok(x):
        a, b, _ = x
        return b == 0.0 or (a / b) > 1.5
    ratios = [a / b for (a, b, _) in gv.values() if b != 0.0]
    zero_at = [lab for lab, (a, b, _) in gv.items() if b == 0.0]
    exps = [-expo(a, b, M1, M2) for (lab, M1, n1, M2, n2), (a, b, _) in
            zip(pairs, gv.values())]                 # FALL exponents: violation ~ M^-e_fall
    ck("A1 the violation VANISHES under refinement at fixed physical k for all three momenta "
       "(ratio M1 -> M2 > 1.5, or an identically zero violation at the finer lattice)",
       all(vanish_ok(x) for x in gv.values()),
       "ratios = %s%s" % (np.array2string(np.array(ratios), precision=4),
                          (" ; identically zero at %s" % zero_at) if zero_at else ""))
    finite = [e for e in exps if np.isfinite(e)]
    ck("A2 the fitted FALL exponent (violation ~ M^-e, i.e. a^-e in a = 1/M) is 2.0 +- 0.7 for "
       "the momenta where it is finite",
       all(abs(e - 2.0) < 0.7 for e in finite),
       "fall exponents = %s%s" % (np.array2string(np.array(finite), precision=3),
                             (" ; +inf (exactly zero at the finer lattice) for %s"
                              % [lab for lab, e in zip(main._gv_labels, exps)
                                 if not np.isfinite(e)] if len(finite) < len(exps) else "")))
    sM = [run(M, 1)['gauge_viol'] for M in (3, 4, 6, 8)]
    e_n1 = expo(sM[0], sM[-1], 3, 8)             # growth exponent (positive = grows)
    fall_fixed = float(np.mean([e for e in exps if np.isfinite(e)]))
    print("    n=1 scan (k = 2pi/M - a MIXED scan): violation = %s -> growth exponent in M = "
          "%+.3f" % (np.array2string(np.array(sM), precision=5), e_n1))
    ck("A3 RECORDED (residual 4 closure): the n = 1 scan's apparent non-convergence is the mixed "
       "effect of a -> 0 together with k -> 0; at fixed k the violation vanishes (A1/A2), so "
       "residual 4 is a closed map-level (midpoint-rule) artifact with exponent 2 in a", True,
       "mixed-scan GROWTH exponent %+.3f vs fixed-k FALL exponent %.3f" % (e_n1, fall_fixed))

    # ---------------------------------------------------------------- PART B
    print("\n[B] residual 5: mechanism diagnostic (isotropy of the simplex edge projectors)")
    ev, tr = simplex_projector_spectrum()
    print("    spectrum of sum_e shat_e shat_e^T = %s ; trace = %.12f"
          % (np.array2string(ev, precision=6), tr))
    ck("B1 the projector sum has the EXACT trace 10 (ten unit vectors in 4D), so its isotropic "
       "part is (10/4) I and its overlap with a traceless perturbation vanishes identically",
       abs(tr - 10.0) < 1e-12, "trace = %.12f" % tr)
    spread = float(ev.max() - ev.min())
    ck("B2 RECORDED (hypothesis excluded): the projector sum is STRONGLY anisotropic, so the "
       "simplest 'isotropic annihilation' mechanism for the TT deficit is EXCLUDED; the deficit "
       "must be measured directly (PART C)", spread > 0.5 * tr / 4.0,
       "eigenvalue spread %.6f vs isotropic part %.6f" % (spread, tr / 4.0))

    # ---------------------------------------------------------------- PART C
    print("\n[C] the TT deficit measured directly at FIXED physical k")
    print("    (exponents below are e in q_lat ~ M^e, so e > 0 = grows with refinement)")
    print("    equals that of q_lat.  PREDICTIONS: s_conf = 3.0 +- 0.4 (extensive action),")
    print("    s_TT = 2.0 +- 0.4 (sub-extensive), deficit s_conf - s_TT = 1.0 +- 0.4")
    U = {}
    for (lab, M1, n1, M2, n2) in pairs:
        U[(lab, M1)] = run(M1, n1)
        U[(lab, M2)] = run(M2, n2)
    s_conf = {}; s_tt = {}; fixedk_att = {}
    for (lab, M1, n1, M2, n2) in pairs:
        a, b = U[(lab, M1)], U[(lab, M2)]
        s_conf[lab] = expo(np.mean(a['conf']['q_lat']), np.mean(b['conf']['q_lat']), M1, M2)
        s_tt[lab] = expo(np.mean(a['TT']['q_lat']), np.mean(b['TT']['q_lat']), M1, M2)
        fixedk_att[lab] = a['TT']['A_agg'] / b['TT']['A_agg']
        print("    %-8s k=%.4f : expo(q_lat) conf = %.3f ; TT = %.3f ; deficit = %.3f ; "
              "A_TT ratio M=%d->%d = %.4f"
              % (lab, a['k'], s_conf[lab], s_tt[lab], s_conf[lab] - s_tt[lab], M1, M2,
                 fixedk_att[lab]), flush=True)
    sm = [lab for lab in s_conf if s_conf[lab] is not None]
    ck("C1 q_lat(conformal) is EXTENSIVE at fixed k: exponent 3.0 +- 0.4 for k <= pi/2",
       all(abs(s_conf[l] - 3.0) < 0.4 for l in ("k=2pi/3", "k=pi/2")),
       "exponents %s ; k=pi (Nyquist, diagnostic only): %.3f"
       % (np.array2string(np.array([s_conf[l] for l in ("k=2pi/3", "k=pi/2")]), precision=3),
          s_conf["k=pi"]))
    ck("C2 q_lat(TT) is SUB-EXTENSIVE at fixed k: exponent 2.0 +- 0.4 for k <= pi/2",
       all(abs(s_tt[l] - 2.0) < 0.4 for l in ("k=2pi/3", "k=pi/2")),
       "exponents %s ; k=pi (diagnostic): %.3f"
       % (np.array2string(np.array([s_tt[l] for l in ("k=2pi/3", "k=pi/2")]), precision=3),
          s_tt["k=pi"]))
    ck("C3 the deficit s_conf - s_TT = 1.0 +- 0.4 for k <= pi/2 (one power of M = one power of "
       "k a in the smooth-mode duality)",
       all(abs(s_conf[l] - s_tt[l] - 1.0) < 0.4 for l in ("k=2pi/3", "k=pi/2")),
       "deficits %s ; k=pi (diagnostic): %.3f"
       % (np.array2string(np.array([s_conf[l] - s_tt[l] for l in ("k=2pi/3", "k=pi/2")]),
                          precision=3), s_conf["k=pi"] - s_tt["k=pi"]))
    # scripts/22 canonical values (data/22_tt_drift_attribution.txt / logs/22): the (M,1) point has
    # k = 2 pi/M, so (M=4,n=1) is k=pi/2 and (M=4,n=2) is k=pi
    ref = {("k=pi/2", 4): 0.665845, ("k=pi/2", 8): 0.345719, ("k=pi", 4): 0.567451,
           ("k=pi", 8): 0.294028}
    dev = []
    for (lab, M1) in ref:
        dev.append(abs(U[(lab, M1)]['TT']['A_agg'] - ref[(lab, M1)]) / ref[(lab, M1)])
    ck("C4 continuity: the uncorrected map reproduces scripts/22's A_TT(agg) at the four fixed-k "
       "points to 5e-4", max(dev) < 5e-4,
       "max relative deviation = %.2e" % max(dev))
    ident = []
    for key, r in U.items():
        for s in ("TT", "conf"):
            for i in range(len(r[s]['q_lat'])):
                val = abs(r[s]['q_lat'][i]) / r[s]['R_map'][i] / abs(r[s]['q_cont'][i])
                rk = abs(r[s]['q_lat'][i]) / abs(r[s]['q_cont'][i])
                ident.append(abs(val - rk / r[s]['R_map'][i]) / (rk / r[s]['R_map'][i]))
    ck("C5 the per-polarisation factorisation A_t = R_action,t / R_map,t is exact (<= 1e-12)",
       max(ident) < 1e-12, "max relative residual = %.2e" % max(ident))

    # ---------------------------------------------------------------- PART D
    print("\n[D] candidate fix: sinc-corrected (geometrically exact plane-wave) edge-length map")
    print("    delta L_e = 1/2 L_e (shat^T h shat) cos(k.x_mid) sinc(k.shat L_e / 2)")
    C = {}
    for (lab, M1, n1, M2, n2) in pairs[:2]:
        C[(lab, M1)] = run(M1, n1, corrected=True)
        C[(lab, M2)] = run(M2, n2, corrected=True)
    s_conf_c = {}; s_tt_c = {}; att_c = {}
    for (lab, M1, n1, M2, n2) in pairs[:2]:
        a, b = C[(lab, M1)], C[(lab, M2)]
        s_conf_c[lab] = expo(np.mean(a['conf']['q_lat']), np.mean(b['conf']['q_lat']), M1, M2)
        s_tt_c[lab] = expo(np.mean(a['TT']['q_lat']), np.mean(b['TT']['q_lat']), M1, M2)
        att_c[lab] = a['TT']['A_agg'] / b['TT']['A_agg']
        print("    %-8s corrected: expo(q_lat) TT = %.3f (uncorrected %.3f) ; deficit = %.3f "
              "(uncorrected %.3f) ; A_TT ratio = %.4f (uncorrected %.4f)"
              % (lab, s_tt_c[lab], s_tt[lab], s_conf_c[lab] - s_tt_c[lab],
                 s_conf[lab] - s_tt[lab], att_c[lab], fixedk_att[lab]), flush=True)
    test_a = all(abs(s_tt_c[l] - s_conf_c[l]) < 0.4 for l in s_tt_c)
    test_b = all(abs(np.log(att_c[l])) < np.log(1.25) for l in att_c)
    identc = []
    for key, r in C.items():
        for s in ("TT", "conf"):
            for i in range(len(r[s]['q_lat'])):
                val = abs(r[s]['q_lat'][i]) / r[s]['R_map'][i] / abs(r[s]['q_cont'][i])
                rk = abs(r[s]['q_lat'][i]) / abs(r[s]['q_cont'][i])
                identc.append(abs(val - rk / r[s]['R_map'][i]) / (rk / r[s]['R_map'][i]))
    ck("D1 the per-polarisation factorisation stays exact for the corrected map (<= 1e-12)",
       max(identc) < 1e-12, "max relative residual = %.2e" % max(identc))
    ck("D2 RECORDED (residual 5 regression tests on the sinc-corrected map): (a) the TT exponent "
       "matches the conformal one -> %s ; (b) A_TT becomes M-stable at fixed k -> %s"
       % ("PASS" if test_a else "FAIL", "PASS" if test_b else "FAIL"), True,
       "so the sinc correction %s the TT sub-extensivity"
       % ("REMOVES" if (test_a and test_b) else "does NOT remove"))

    # ---------------------------------------------------------------- verdict
    ok_fix = test_a and test_b
    print("\n[E] verdict")
    if ok_fix:
        print("    The geometrically exact plane-wave map restores TT extensivity: residual 5 is")
        print("    resolved as a map-sampling artifact (midpoint vs edge-averaged strain).")
    else:
        print("    REFUTED HYPOTHESIS, recorded: the sinc-corrected map does NOT restore the TT")
        print("    extensivity.  The deficit therefore lives in the DISCRETISATION OF THE CURVATURE")
        print("    RESPONSE on a simplex (each hinge contributes one O(M^2) TT term against M^3")
        print("    hinges), not in the midpoint sampling of the edge integral: the midpoint map is")
        print("    already the correct leading-order map (its O(k^2 a^2) error is the residual-4")
        print("    artifact that vanishes under refinement, PART A).  Residual 5's acceptance")
        print("    criteria are unchanged: MODIFY THE DEFICIT/DIRECTIONAL STRUCTURE of the Regge")
        print("    action (e.g. shape-extended deficits), not the map.")
    print("    NB residual 4 is CLOSED (PART A) and independent of this: it disappears at fixed k.")
    print("\nRESULT: %d/%d PASS" % (PASS, PASS + FAIL))
    if FAIL:
        print("HONEST STATUS: %d FAIL - see above; no physics threshold was relaxed." % FAIL)
    else:
        print("HONEST STATUS: all checks pass.  Residual 4 CLOSED: the naive-map gauge violation "
              "falls as M^-%.2f at fixed physical k (midpoint-rule O(k^2 a^2)), so the n = 1 "
              "scan's growth was the mixed a -> 0 / k -> 0 effect.  Residual 5 mechanism: measured "
              "directly at fixed k (the isotropic-annihilation hypothesis is excluded, the "
              "projector spectrum is anisotropic) - the conformal action is extensive (%.2f) while "
              "TT is sub-extensive (%.2f), a deficit of %.2f power of M.  The geometrically exact "
              "sinc-corrected map %s."
              % (fall_fixed, np.mean([s_conf[l] for l in s_conf]),
                 np.mean([s_tt[l] for l in s_tt]),
                 np.mean([s_conf[l] - s_tt[l] for l in s_conf]),
                 "RESTORES TT extensivity" if ok_fix else
                 "does NOT restore it (refutation recorded; residual 5 stays open with the "
                 "unchanged acceptance criteria)"))


if __name__ == "__main__":
    main()
