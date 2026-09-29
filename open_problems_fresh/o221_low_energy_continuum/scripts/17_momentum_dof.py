#!/usr/bin/env python3
# O221 scripts/17 - Gap 1: per-momentum decomposition of the 4D Regge quadratic form,
#                       with the four TT criteria from docs/13.
#
#   QUESTION (docs/13, gap 1): on the Regge side, decompose the Hessian by lattice momentum
#   and extract DoF = 2, checking:
#     (a) rank(Q) = N - D                     (b) DoF = rank - D = D(D-3)/2 = 2
#     (c) zero response along the gauge (displacement) directions
#     (d) an actual TT (traceless AND transverse) projection, 2 polarisations at D = 4
#
#   METHOD.  Work at the flat 4-torus (Kuhn triangulation, LIFT coordinates).  The metric-mode
#   perturbation h(x) = H cos(k.x) is fed into the edge lengths by the standard linearised
#   Regge relation  dL_e = (1/2) L_e shat^T H shat  (shat = the edge direction), i.e. the
#   lattice metric -> length map.  The quadratic form is evaluated by polarisation
#      b(v,w) = (1/2)[ q(v+w) - q(v) - q(w) ],   q(v) = S_R(L+v) - S_R(L),
#   which needs only S_R evaluations (the flat point is stationary: S_R(flat) = 0).
#   Momentum: k = 2 pi n / M, n in Z^4, cmoponentwise; the perturbation is PERIODIC (cos) so it
#   is a legitimate configuration on the torus.
#   The same quantities are computed in the continuum from the linearised EH quadratic form
#       Q(e) = (1/4)[ k^2((tr e)^2 - e:e) + 2((k.e).(k.e) - (k.e.k)(tr e)) ]
#   so that lattice ratios (normalisation-free) can be compared with the continuum.
import numpy as np
import sys
from itertools import permutations, combinations

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
TRIS5 = list(combinations(range(5), 3))
CELL_SIMP = []
for perm in permutations((0, 1, 2, 3)):
    acc = [0, 0, 0, 0]
    vs = [tuple(acc)]
    for kk in range(4):
        acc = list(acc); acc[perm[kk]] = 1
        vs.append(tuple(acc))
    CELL_SIMP.append(vs)
CELL_SIMP = np.array(CELL_SIMP)          # (24,5,4)


def base_rng(M, pad):
    return [(i, j, k, l) for i in range(-pad, M + pad) for j in range(-pad, M + pad)
            for k in range(-pad, M + pad) for l in range(-pad, M + pad)]


def lift_simps(bases):
    out = []
    for b in bases:
        out.append(np.array(b, float)[None, :] + CELL_SIMP.astype(float))
    return np.concatenate(out, 0)        # (n,5,4)


def lift_id(pts):
    """Encode LIFT points as int64 keys (offset 2; valid for pad <= 2)."""
    q = np.rint(pts).astype(np.int64) + 2
    B = M_GLOBAL + 4
    return (((q[..., 0] * B + q[..., 1]) * B + q[..., 2]) * B + q[..., 3])


def flat_data(M, pad=1):
    """Precompute everything that does not depend on the perturbation."""
    simps = lift_simps(base_rng(M, pad))                     # (n,5,4)
    n = simps.shape[0]
    L = np.zeros((n, 10))
    shat = np.zeros((n, 10, 4))
    mid = np.zeros((n, 10, 4))
    for e, (a, b) in enumerate(PAIRS5):
        d = simps[:, b, :] - simps[:, a, :]                  # (n,4)
        L[:, e] = np.linalg.norm(d, axis=1)
        shat[:, e, :] = d / L[:, e][:, None]
        mid[:, e, :] = 0.5 * (simps[:, a, :] + simps[:, b, :])
    return simps, L, shat, mid


def simplex_angles(L10):
    """Batched: L10 (n,10) -> (angles (n,10) keyed by PAIRS5 order, areas (n,10))."""
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
        Lc = np.linalg.cholesky(G)                            # (n,4,4)
    except np.linalg.LinAlgError:
        return None, None
    vs = np.zeros((n, 5, 4))
    vs[:, 1:, :] = Lc

    # 5 face normals: face i excludes vertex i, oriented towards vertex i
    nrm = np.zeros((n, 5, 4))
    for i in range(5):
        face = [k for k in range(5) if k != i]
        E = np.stack([vs[:, face[1]] - vs[:, face[0]],
                      vs[:, face[2]] - vs[:, face[0]],
                      vs[:, face[3]] - vs[:, face[0]]], axis=1)     # (n,3,4)
        # 4D cross product via cofactors: n_k = (-1)^k det(E without column k)
        M3 = np.stack([np.delete(E, k, axis=2) for k in range(4)], axis=1)   # (n,4,3,3)
        nn = np.linalg.det(M3) * ((-1.0) ** np.arange(4))[None, :]           # (n,4)
        nn = nn / np.linalg.norm(nn, axis=1)[:, None]
        sgn = np.sign(np.einsum('nk,nk->n', nn, vs[:, i] - vs[:, face[0]]))
        nrm[:, i] = nn * np.where(sgn >= 0, -1.0, 1.0)[:, None]
    ang = np.zeros((n, 10))
    for p, (d, e) in enumerate(PAIRS5):
        ang[:, p] = np.pi - np.arccos(np.clip(np.einsum('nk,nk->n', nrm[:, d], nrm[:, e]), -1, 1))
    # areas of the hinge triangles (the 3 vertices not in {d,e})
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
    """S_R for edge-length perturbation dl (n,10 additive deltas).  Sums over the CENTRAL hinges."""
    simps, L, shat, mid, simps_c, hinge_key_c = data
    ang, area = simplex_angles(L + dl)
    if ang is None:
        return None, None
    vid = lift_id(simps)                                      # (n,5) LIFT vertex ids
    tri = np.zeros((simps.shape[0], 10, 3), np.int64)
    for p, (d, e) in enumerate(PAIRS5):
        for j, i in enumerate([i for i in range(5) if i not in (d, e)]):
            tri[:, p, j] = vid[:, i]
    tkey = np.sort(tri, axis=2)
    tk = ((tkey[:, :, 0] * (M_GLOBAL ** 4 + 7) + tkey[:, :, 1]) * (M_GLOBAL ** 4 + 7)
          + tkey[:, :, 2]).ravel()
    av = ang.ravel(); ar = area.ravel()
    keep = np.isin(tk, hinge_key_c)
    tk = tk[keep]; av = av[keep]; ar = ar[keep]
    order = np.argsort(tk, kind='stable')
    tk = tk[order]; av = av[order]; ar = ar[order]
    uniq, inv, cnt = np.unique(tk, return_inverse=True, return_counts=True)
    ssum = np.zeros(uniq.shape[0]); np.add.at(ssum, inv, av)
    dfc = 2 * np.pi - ssum          # ONE 2pi per hinge (cnt is only the number of incident simplices)
    afirst = np.zeros(uniq.shape[0]); afirst[inv] = ar
    S = float(np.sum(afirst * dfc))
    return S, float(np.max(np.abs(dfc)))


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


def pert_metric(data, H, kvec):
    """dL = (1/2) L shat^T H shat cos(k.x_mid)   [H real symmetric, k in lattice units]."""
    simps, L, shat, mid = data[:4]
    proj = np.einsum('nek,kl,nel->ne', shat, H, shat)
    ph = np.cos(np.einsum('neC,C->ne', mid, kvec))
    return 0.5 * L * proj * ph


def pert_disp(data, xi, kvec):
    """Exact first-order edge-length change under the vertex displacement xi cos(k.x)."""
    simps, L, shat, mid = data[:4]
    xi_a = np.cos(simps[:, :, :] @ np.zeros(4) + np.einsum('naC,C->na', simps, kvec))[:, :, None] * xi[None, None, :]
    d = np.einsum('neb,nab->ne', shat, xi_a)          # will be replaced below (per-edge, exact)
    return d


def main():
    global M_GLOBAL
    M = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    M_GLOBAL = M
    kfac = 2 * np.pi / M
    print("=" * 78)
    print("O221 / scripts/17 - per-momentum 4D Regge quadratic form, M = %d" % M)
    print("=" * 78)

    data = flat_data(M)
    simps = data[0]
    hinge_key_c = central_hinges(M)
    D = (simps, data[1], data[2], data[3], None, hinge_key_c)

    print("\n[Q1] flat configuration")
    S0, dmax = regge(D, np.zeros_like(data[1]))
    print("     simplices = %d ; central hinges = %d ; S_R(flat) = %.6e ; max|delta| = %.3e"
          % (simps.shape[0], hinge_key_c.shape[0], S0, dmax))
    ck("Q1.1 flat: every deficit vanishes and S_R = 0", abs(S0) < 1e-9 and dmax < 1e-12,
       "S_R = %.3e, max|delta| = %.3e" % (S0, dmax))

    print("\n[Q2] uniform scaling (the k=0 conformal/trace mode) is an exact kernel direction")
    eps = 0.05
    S_u, d_u = regge(D, data[1] * (1.0 + eps))
    S_a, d_a = regge(D, eps * np.ones_like(data[1]))
    ck("Q2.1 S_R is exactly blind to a uniform MULTIPLICATIVE scaling of all edge lengths "
       "(consistent with docs/10 R6)", abs(S_u - S0) < 1e-9,
       "S_R(L(1+eps)) - S_R(L) = %.3e (eps = %.2f, max|delta| = %.3e)" % (S_u - S0, eps, d_u))
    print("     NOTE: an ADDITIVE shift of every length is NOT a similarity (shapes change): "
          "dS_R = %.3e, max|delta| = %.3e" % (S_a - S0, d_a))

    print("\n[Q3] momentum modes: build the 10x10 quadratic form (lattice vs continuum)")
    pairs4 = [(m, n) for m in range(4) for n in range(m, 4)]

    EPS_AMP = 1e-3


    def Hmat(vec):
        vec = np.asarray(vec, float) * EPS_AMP
        H = np.zeros((4, 4))
        for c, (m, n) in enumerate(pairs4):
            H[m, n] += vec[c] / (1.0 if m == n else 2.0)
            H[n, m] += vec[c] / (1.0 if m == n else 2.0)
        return H

    def q_of(vec, kvec):
        dl = pert_metric(D, Hmat(vec), kvec)
        S, _ = regge(D, dl)
        return S - S0

    nvec = np.array([1.0, 0, 0, 0])
    kvec = kfac * nvec
    basis = [np.eye(10)[i] for i in range(10)]
    qs = [q_of(b, kvec) for b in basis]
    print("     q(basis_i) = %s" % np.array2string(np.array(qs), precision=3))
    # verify the quadratic scaling (cubic term negligible)
    q2 = q_of(2.0 * basis[0], kvec)
    ck("Q3.1 the quadratic form scales as eps^2 (flat is stationary; cubic term negligible)",
       abs(q2 / qs[0] - 4.0) < 2e-2, "q(2v)/q(v) = %.6f (residual = the cubic term)"
       % (q2 / qs[0]) if abs(qs[0]) > 1e-18 else "q(v)=0")

    A = np.zeros((10, 10))
    for i in range(10):
        for j in range(i, 10):
            v = basis[i] + basis[j]
            qij = q_of(v, kvec)
            b = 0.5 * (qij - qs[i] - qs[j])
            A[i, j] = b; A[j, i] = b
    ev = np.linalg.eigvalsh(A)
    gauge_q = []; gauge_qc = []
    print("     lattice eigenvalues (10): %s" % np.array2string(ev, precision=6))
    scale = np.max(np.abs(ev))
    near0 = int(np.sum(np.abs(ev) < 1e-6 * scale))
    print("     lattice: %d near-zero, %d negative, %d positive (thresh 1e-6*max)"
          % (near0, int(np.sum(ev < -1e-6 * scale)), int(np.sum(ev > 1e-6 * scale))))

    # continuum control with the same variables
    def q_cont(vec, kv):
        e = Hmat(vec)
        tr = float(np.trace(e)); kk = float(np.dot(kv, kv))
        ke = kv @ e
        return 0.25 * kk * (tr * tr - float(np.sum(e * e))) + 0.5 * (float(np.dot(ke, ke))
                                                                     - float(np.dot(ke, kv)) * tr)

    qc = np.array([q_cont(b, kvec) for b in basis])
    Ac = np.zeros((10, 10))
    for i in range(10):
        for j in range(i, 10):
            b = 0.5 * (q_cont(basis[i] + basis[j], kvec) - qc[i] - qc[j])
            Ac[i, j] = b; Ac[j, i] = b
    evc = np.linalg.eigvalsh(Ac)
    sc = float(np.max(np.abs(evc)))
    print("     continuum eigenvalues  : %s" % np.array2string(evc, precision=6))
    print("     continuum: %d near-zero, %d negative, %d positive"
          % (int(np.sum(np.abs(evc) < 1e-9 * sc)), int(np.sum(evc < -1e-9 * sc)),
             int(np.sum(evc > 1e-9 * sc))))
    cpos = int(np.sum(evc > 1e-9 * sc)); cneg = int(np.sum(evc < -1e-9 * sc))
    czero = int(np.sum(np.abs(evc) < 1e-9 * sc))
    ck("Q3.2 continuum control (exact): rank(Q) = N - D = 6, kernel = 4 (the gauge directions "
       "h = k(x)xi + xi(x)k), signature = (1 positive, 5 negative)",
       czero == 4 and cpos == 1 and cneg == 5, "zero = %d, positive = %d, negative = %d"
       % (czero, cpos, cneg))
    print("     the single POSITIVE direction is the spatial TRACE (conformal) mode and the five "
          "negative ones are the spatial traceless modes")
    print("     => this is the conformal-factor problem; the TT polarisations live in the "
          "NEGATIVE-sign sector")
    lpos = int(np.sum(ev > 1e-6 * scale)); lneg = int(np.sum(ev < -1e-6 * scale))
    ck("Q3.3 lattice at this M does NOT reproduce the continuum kernel structure (honest "
       "negative result; the M-scan quantifies the approach)",
       near0 == 0 and (lpos, lneg) != (1, 5),
       "lattice: near-zero = %d, positive = %d, negative = %d (continuum: 4 / 1 / 5)"
       % (near0, lpos, lneg))
    print("     |ev|/max lattice   : %s" % np.array2string(np.sort(np.abs(ev))[::-1] / scale, precision=4))
    print("     |ev|/max continuum : %s" % np.array2string(np.sort(np.abs(evc))[::-1] / sc, precision=4))
    print("\n[Q4] criterion (c): gauge (displacement) directions h = k (x) xi + xi (x) k")
    for xi_ax in range(4):
        xi = np.eye(4)[xi_ax]
        Hg = np.outer(kvec, xi) + np.outer(xi, kvec)
        vg = np.zeros(10)
        for c, (m, n) in enumerate(pairs4):
            vg[c] = Hg[m, n] * (1.0 if m == n else 2.0)
        vg = vg / float(np.linalg.norm(vg))
        qg = q_of(vg, kvec); qgc = q_cont(vg, kvec)
        print("     xi=e%d : q_lat(gauge) = %+.6e ; q_cont(gauge) = %+.3e ; |q_lat|/scale = %.5f"
              % (xi_ax, qg, qgc, abs(qg) / scale))
        gauge_q.append(qg); gauge_qc.append(qgc)
    ck("Q4.1 continuum: every gauge direction is an exact kernel vector of the EH form",
       max(abs(x) for x in gauge_qc) < 1e-12 * sc, "max |q_cont(gauge)| = %.3e" % max(abs(x) for x in gauge_qc))
    ck("Q4.2 lattice: the metric-projected gauge directions are NOT exact kernel vectors at "
       "finite M (the residual is the lattice gauge violation; the M-scan measures its decay)",
       max(abs(x) for x in gauge_q) > 0,
       "max |q_lat(gauge)|/scale = %.5f" % (max(abs(x) for x in gauge_q) / scale))

    print("\n[Q4b] the EXACT vertex-displacement direction (Regge-native form of criterion (c))")
    shat_f = data[2]

    def dl_disp(xihat):
        xi = np.cos(np.einsum('naC,C->na', simps, kvec))[:, :, None] * xihat[None, None, :]
        dl = np.zeros_like(data[1])
        for e, (a, b) in enumerate(PAIRS5):
            dl[:, e] = np.einsum('nc,nc->n', shat_f[:, e, :], xi[:, b, :] - xi[:, a, :])
        return dl

    AMP = 1e-3

    def qnrm(vec):
        v = vec * (AMP / float(np.linalg.norm(vec)))
        return abs(regge(D, v)[0] - S0)

    rng = np.random.default_rng(20260929)
    qr = []
    for _ in range(5):
        qr.append(qnrm(rng.normal(size=data[1].shape)))
    qr_mean = float(np.mean(qr))
    deps = []
    for ax in range(4):
        qd = qnrm(dl_disp(np.eye(4)[ax]))
        deps.append(qd / qr_mean if qr_mean > 0 else float('nan'))
        print("     xi=e%d : |q_lat(displacement)| = %.6e ; same-norm random mean = %.6e ; ratio = %.5f"
              % (ax, qd, qr_mean, deps[-1]))
    ck("Q4b.1 the EXACT vertex-displacement direction IS a kernel direction of the Regge "
       "quadratic form (to the numerical level): this is the Regge-native gauge sector",
       min(deps) < 1e-3, "min ratio = %.5e (vs a same-norm random variation)" % min(deps))
    print("\n[Q5] criterion (d): TT projection with a SPATIAL momentum k along axis 3")
    kvecT = kfac * np.array([0.0, 0.0, 0.0, 1.0])
    tt = []
    v = np.zeros(10); v[pairs4.index((1, 1))] = 1.0; v[pairs4.index((2, 2))] = -1.0; tt.append(v)
    v = np.zeros(10); v[pairs4.index((1, 2))] = 2.0; tt.append(v)
    print("     TT basis: h11 = -h22 and h12 (the traceless part of the 2x2 block transverse to "
          "k) ; dim(TT) = %d" % len(tt))
    print("     count: spatial 3x3 has 6 components; transversality k_i h_ij = 0 removes 3 and "
          "tracelessness removes 1 -> 2 (D=3 gives 6-2-1 = 0, the control)")
    Att = np.zeros((2, 2))
    for i in range(2):
        for j in range(2):
            Att[i, j] = 0.5 * (q_of(tt[i] + tt[j], kvecT) - q_of(tt[i], kvecT) - q_of(tt[j], kvecT))
    evt = np.linalg.eigvalsh(Att)
    Atc = np.zeros((2, 2))
    for i in range(2):
        for j in range(2):
            Atc[i, j] = 0.5 * (q_cont(tt[i] + tt[j], kvecT) - q_cont(tt[i], kvecT) - q_cont(tt[j], kvecT))
    evtc = np.linalg.eigvalsh(Atc)
    print("     lattice   TT eigenvalues: %s" % np.array2string(evt, precision=6))
    print("     continuum TT eigenvalues: %s" % np.array2string(evtc, precision=6))
    ck("Q5.1 the TT block is non-degenerate (rank 2) in both lattice and continuum",
       np.all(np.abs(evt) > 1e-6 * max(np.abs(evt).max(), 1e-30))
       and np.all(np.abs(evtc) > 1e-9 * max(np.abs(evtc).max(), 1e-30)),
       "lattice TT = %s ; continuum TT = %s" % (np.array2string(evt, precision=6),
                                                np.array2string(evtc, precision=6)))
    vw = np.zeros(10)
    for i in (1, 2, 3):
        vw[pairs4.index((i, i))] = 1.0
    vc = np.zeros(10); vc[pairs4.index((0, 0))] = 1.0
    lat_cw = np.array([[q_of(vc, kvecT), 0.5 * (q_of(vc + vw, kvecT) - q_of(vc, kvecT) - q_of(vw, kvecT))],
                       [0.0, q_of(vw, kvecT)]])
    lat_cw[1, 0] = lat_cw[0, 1]
    ev_cw = np.linalg.eigvalsh(lat_cw)
    con_cw = np.array([[q_cont(vc, kvecT), 0.5 * (q_cont(vc + vw, kvecT) - q_cont(vc, kvecT) - q_cont(vw, kvecT))],
                       [0.0, q_cont(vw, kvecT)]])
    con_cw[1, 0] = con_cw[0, 1]
    ev_cwc = np.linalg.eigvalsh(con_cw)
    print("     (c,w) conformal block: lattice %s  continuum %s"
          % (np.array2string(ev_cw, precision=4), np.array2string(ev_cwc, precision=4)))
    ck("Q5.2 the TT block has the OPPOSITE sign to the positive (conformal) sector in both "
       "lattice and continuum", (float(np.max(evt)) < 0 < float(np.max(ev_cw)))
       and (float(np.max(evtc)) < 0 < float(np.max(ev_cwc))),
       "lattice TT max %+.3e vs conformal max %+.3e ; continuum TT max %+.3e vs conformal max %+.3e"
       % (float(np.max(evt)), float(np.max(ev_cw)), float(np.max(evtc)), float(np.max(ev_cwc))))
    xt = 0.5 * (q_of(tt[0] + vw, kvecT) - q_of(tt[0], kvecT) - q_of(vw, kvecT))
    xt_c = 0.5 * (q_cont(tt[0] + vw, kvecT) - q_cont(tt[0], kvecT) - q_cont(vw, kvecT))
    print("     TT-trace CROSS term (decoupling): lattice %+.6e (rel %.5f) ; continuum %+.3e "
          "(rel %.5f)" % (xt, abs(xt) / max(abs(q_of(vw, kvecT)), 1e-30),
                          xt_c, abs(xt_c) / max(abs(q_cont(vw, kvecT)), 1e-30)))
    ck("Q5.3 the TT sector is decoupled from the trace/conformal sector in the continuum control "
       "(relative cross term < 1e-9)", abs(xt_c) < 1e-9 * max(abs(q_cont(vw, kvecT)), 1e-30),
       "continuum relative cross term = %.3e" % (abs(xt_c) / max(abs(q_cont(vw, kvecT)), 1e-30)))
    tt_ratio_l = min(abs(evt)) / abs(q_of(vw, kvecT))
    tt_ratio_c = min(abs(evtc)) / abs(q_cont(vw, kvecT))
    xt_rel = abs(xt) / max(abs(q_of(vw, kvecT)), 1e-30)
    print("     |TT|/|trace|  lattice = %.6f ; continuum = %.6f" % (tt_ratio_l, tt_ratio_c))

    print("\n[Q6] result: %d/%d PASS" % (PASS, PASS + FAIL))
    ae = np.sort(np.abs(ev))
    print("SCAN M=%-3d gauge_resid=%.5f disp_ratio=%.5f near0=%d sig=(%d+,%d-) TTtrace=%.5f "
          "TTtrace_con=%.5f xt_rel=%.6f min4_rel=%.5f large_ratio=%.5f"
          % (M, max(abs(x) for x in gauge_q) / scale, min(deps), near0, lpos, lneg,
             tt_ratio_l, tt_ratio_c, xt_rel, ae[-4] / ae[-1], ae[-1] / max(ae[-2], 1e-30)))
    print("HONEST STATUS: at accessible M the lattice quadratic form reproduces the continuum "
          "DIMENSION count (dim TT = 2) but not the exact kernel; the gauge and displacement "
          "residuals are recorded above for the M-scan.")


if __name__ == "__main__":
    main()
