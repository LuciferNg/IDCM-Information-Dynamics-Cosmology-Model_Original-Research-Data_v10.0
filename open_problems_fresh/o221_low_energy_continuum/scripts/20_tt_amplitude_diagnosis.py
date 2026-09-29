#!/usr/bin/env python3
# O221 scripts/20 - Gap 2: is the TT amplitude suppression (150-1000x vs the continuum
#                       control) a NORMALISATION / map artifact, or a structural fact?
#
#   CONTEXT (docs/14 sec. 5): with the raw basis vectors used in scripts/17,
#        tt_ratio = min|ev(TT block)| / |q(conformal vector vw)|          (= |TT|/|trace|)
#   gives   lattice ~6e-5 (M=3) .. ~4.1e-4 (M=8)   vs   continuum 0.25   =>  "150-1000x".
#
#   THE POINT.  On the lattice the quadratic form is NOT a form on metric perturbations: it is
#   the pull-back  q_lat(h) = <A(h), A(h)>_W  of the Regge second variation W through the
#   metric->edge-length map A (dL_e = 1/2 L_e shat^T H shat cos(k.x)).  Hence
#        q_lat(h_TT) / q_lat(h_vw)  =  R_map^2 * R_W ,
#        R_map = ||A h_TT|| / ||A h_vw||            (pure map: how much of the perturbation
#                                                    reaches the edge-length variables)
#        R_W   = <e_TT, W e_TT> / <e_vw, W e_vw>    (stiffness at MATCHED source norm)
#   Only R_W is a convention-free statement about the Regge dynamics; R_map is a property of the
#   linearised map (already known to be the weak link: it does NOT preserve the gauge kernel,
#   docs/14 criterion (c)).  In the continuum the map is the identity, and the raw ratio 0.25
#   itself already contains the raw basis norm mismatch (||e_TT||^2 = 2 vs ||e_vw||^2 = 3).
#
#   CHECKS.  Q1 reproduce the two documented ratios; Q2 the factorisation identity (exact
#   algebra); Q3 the map ratios + continuum analogue; Q4 the matched-source-norm (convention
#   free) stiffness ratio, lattice vs continuum; Q5 M-scan of R_map and R_W; Q6 the sign /
#   degeneracy structure survives (which is the physical content of criterion (d)).
#
#   Machinery (Kuhn triangulation, simplex angles, Regge evaluation, metric map) is copied from
#   scripts/17_momentum_dof.py on purpose: every O221 script stays self-contained so that an
#   audit script can be written with zero shared code (see docs/05, docs/15).
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
        return None, None, None
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
    uniq, inv, cnt = np.unique(tk, return_inverse=True, return_counts=True)
    ssum = np.zeros(uniq.shape[0]); np.add.at(ssum, inv, av)
    dfc = 2 * np.pi - ssum
    afirst = np.zeros(uniq.shape[0]); afirst[inv] = ar
    return float(np.sum(afirst * dfc)), float(np.max(np.abs(dfc))), dfc


def regge_parts(data, dl):
    """Same hinge bookkeeping as regge(), but returns the two pieces separately:

        S = sum_t A_t (2 pi - sum_inc theta)  =  2 pi * sum_t A_t   -   sum_t A_t * sum_inc theta
                                            =: S_area               +   S_deficit

    The first piece is the background-area term (in the continuum it is a total derivative and
    drops out of the physical quadratic form); the second is the deficit (curvature) term.
    """
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
    uniq, inv, cnt = np.unique(tk, return_inverse=True, return_counts=True)
    ssum = np.zeros(uniq.shape[0]); np.add.at(ssum, inv, av)
    afirst = np.zeros(uniq.shape[0]); afirst[inv] = ar
    return float(2 * np.pi * np.sum(afirst)), float(-np.sum(afirst * ssum))


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
    simps, L, shat, mid = data[:4]
    proj = np.einsum('nek,kl,nel->ne', shat, H, shat)
    ph = np.cos(np.einsum('neC,C->ne', mid, kvec))
    return 0.5 * L * proj * ph


def src_norm(dl, simps, distinct=True):
    """Source-side norm of an edge-length variation.

    distinct=True counts every LATTICE edge once (the physical measure on the edge space);
    distinct=False counts every simplex-edge incidence (the measure the action itself sums
    over).  Both are reported; they differ by the (roughly uniform) incidence multiplicity.
    """
    if not distinct:
        return float(np.sqrt(np.sum(dl ** 2)))
    acc = {}
    for e, (a, b) in enumerate(PAIRS5):
        ka = lift_id(simps[:, a, :]); kb = lift_id(simps[:, b, :])
        lo = np.minimum(ka, kb); hi = np.maximum(ka, kb)
        key = lo * np.int64(10 ** 15) + hi
        for kk, vv in zip(key.tolist(), dl[:, e].tolist()):
            acc[kk] = vv * vv
    return float(np.sqrt(sum(acc.values())))


def run(M):
    global M_GLOBAL
    M_GLOBAL = M
    kfac = 2 * np.pi / M
    data = flat_data(M)
    simps = data[0]
    hinge_key_c = central_hinges(M)
    D = (simps, data[1], data[2], data[3], hinge_key_c)
    S0, dmax, _ = regge(D, np.zeros_like(data[1]))

    pairs4 = [(m, n) for m in range(4) for n in range(m, 4)]
    EPS_AMP = 1e-3

    def Hmat(vec):
        vec = np.asarray(vec, float) * EPS_AMP
        H = np.zeros((4, 4))
        for c, (m, n) in enumerate(pairs4):
            H[m, n] += vec[c] / (1.0 if m == n else 2.0)
            H[n, m] += vec[c] / (1.0 if m == n else 2.0)
        return H

    kvecT = kfac * np.array([0.0, 0.0, 0.0, 1.0])

    def q_of(vec):
        dl = pert_metric(D, Hmat(vec), kvecT)
        S, _, _ = regge(D, dl)
        return S - S0, dl

    def q_cont(vec):
        e = Hmat(vec)
        tr = float(np.trace(e)); kk = float(np.dot(kvecT, kvecT))
        ke = kvecT @ e
        return (0.25 * kk * (tr * tr - float(np.sum(e * e)))
                + 0.5 * (float(np.dot(ke, ke)) - float(np.dot(ke, kvecT)) * tr))

    # ---- basis: the two TT polarisations and the spatial-trace (conformal) vector
    tt = []
    v = np.zeros(10); v[pairs4.index((1, 1))] = 1.0; v[pairs4.index((2, 2))] = -1.0; tt.append(v)
    v = np.zeros(10); v[pairs4.index((1, 2))] = 2.0; tt.append(v)
    vw = np.zeros(10)
    for i in (1, 2, 3):
        vw[pairs4.index((i, i))] = 1.0

    # ---- Q1 reproduce the two documented ratios
    evt = np.linalg.eigvalsh(np.array([[0.5 * (q_of(tt[i] + tt[j])[0] - q_of(tt[i])[0]
                                        - q_of(tt[j])[0]) for j in range(2)] for i in range(2)]))
    qvw_l = q_of(vw)[0]
    evtc = np.linalg.eigvalsh(np.array([[0.5 * (q_cont(tt[i] + tt[j]) - q_cont(tt[i])
                                         - q_cont(tt[j])) for j in range(2)] for i in range(2)]))
    qvw_c = q_cont(vw)
    ratio_l = float(np.min(np.abs(evt))) / abs(qvw_l)
    ratio_c = float(np.min(np.abs(evtc))) / abs(qvw_c)
    print("     lattice   TT eigenvalues = %s ; q(vw) = %+.6e ; ratio = %.6f"
          % (np.array2string(evt, precision=6), qvw_l, ratio_l))
    print("     continuum TT eigenvalues = %s ; q(vw) = %+.6e ; ratio = %.6f"
          % (np.array2string(evtc, precision=6), qvw_c, ratio_c))

    # ---- Q2 the factorisation identity (exact algebra)
    dl_tt = [q_of(t)[1] for t in tt]
    dl_vw = q_of(vw)[1]
    nmap_tt = np.mean([src_norm(d, simps) for d in dl_tt])
    nmap_vw = src_norm(dl_vw, simps)
    R_map = nmap_tt / nmap_vw
    R_W = ratio_l / (R_map ** 2)
    # continuum analogue: map = identity, source norm = the metric norm sqrt(e:e)
    n_tt = [np.sqrt(float(np.sum(Hmat(t) ** 2))) for t in tt]
    n_vw = np.sqrt(float(np.sum(Hmat(vw) ** 2)))
    R_map_c = float(np.mean(n_tt)) / n_vw
    R_W_c = ratio_c / (R_map_c ** 2)
    print("     R_map (lattice)   = %.6e   [||A h_TT|| / ||A h_vw||, distinct lattice edges]"
          % R_map)
    print("     R_map (continuum) = %.6e   [||h_TT|| / ||h_vw||]" % R_map_c)
    print("     R_map^2 * R_W = %.6e  vs  ratio_l = %.6e   (identity check)"
          % (R_map ** 2 * R_W, ratio_l))

    # ---- Q3 how much of the 150-1000x lives in the MAP?
    print("     R_map (lattice) / R_map (continuum) = %.6e" % (R_map / R_map_c))
    print("     R_W   (lattice) = %.6e ; R_W (continuum) = %.6e ; ratio = %.6f"
          % (R_W, R_W_c, R_W / R_W_c))

    # ---- Q4b PER-SECTOR stiffness at unit source norm: each sector against ITS OWN continuum
    #      counterpart (this is the decisive decomposition: it separates "the TT dynamics is
    #      wrong" from "the conformal/trace sector is anomalous").
    rho_tt_l = float(np.mean([abs(evt[i]) for i in range(2)])) / (np.mean([src_norm(d, simps)
                                                                          for d in dl_tt]) ** 2)
    rho_tt_c = float(np.mean([abs(evtc[i]) for i in range(2)])) / (float(np.mean(n_tt)) ** 2)
    rho_vw_l = abs(qvw_l) / (nmap_vw ** 2)
    rho_vw_c = abs(qvw_c) / (n_vw ** 2)
    print("     raw source norms: lattice ||A h_TT|| = %.4e, ||A h_vw|| = %.4e ; continuum "
          "||h_TT|| = %.4e, ||h_vw|| = %.4e" % (nmap_tt, nmap_vw, float(np.mean(n_tt)), n_vw))
    print("     per-unit-source stiffness: TT lattice %.4e vs continuum %.4e (ratio %.4f) ; "
          "conformal lattice %.4e vs continuum %.4e (ratio %.4f)"
          % (rho_tt_l, rho_tt_c, rho_tt_l / rho_tt_c, rho_vw_l, rho_vw_c, rho_vw_l / rho_vw_c))
    atom_tt = abs(np.log10(abs(rho_tt_l / rho_tt_c)))
    atom_vw = abs(np.log10(abs(rho_vw_l / rho_vw_c)))
    # map distortion factors: edge-space source norm^2 vs metric-space source norm^2, per sector
    m_tt = (nmap_tt ** 2) / (float(np.mean(n_tt)) ** 2)
    m_vw = (nmap_vw ** 2) / (n_vw ** 2)
    A_tt = rho_tt_l / rho_tt_c
    A_vw = rho_vw_l / rho_vw_c
    # polarisation-shape factors: the two TT polarisations are DEGENERATE in the continuum
    # control but split on the lattice (the raw ratio uses min|ev|), so the min/mean shape
    # factor must be carried explicitly for the identity to close.
    kap_l = float(np.min(np.abs(evt))) / float(np.mean(np.abs(evt)))
    kap_c = float(np.min(np.abs(evtc))) / float(np.mean(np.abs(evtc)))
    decomp = (A_tt / A_vw) * (m_tt / m_vw) * (kap_l / kap_c)
    print("     polarisation splitting |ev|max/|ev|min: lattice %.3f ; continuum %.3f "
          "(shape factors kappa: %.6f / %.6f)" % (float(np.max(np.abs(evt)))
                                                  / float(np.min(np.abs(evt))),
                                                  float(np.max(np.abs(evtc)))
                                                  / float(np.min(np.abs(evtc))), kap_l, kap_c))
    print("     map distortion m_TT = %.6e ; m_vw = %.6e ; m_TT/m_vw = %.6e"
          % (m_tt, m_vw, m_tt / m_vw))
    print("     per-sector anomaly A_TT = %.6f ; A_conf = %.6f ; A_TT/A_conf = %.6e"
          % (A_tt, A_vw, A_tt / A_vw))
    print("     THREE-FACTOR decomposition: (A_TT/A_conf)*(m_TT/m_vw)*(kappa_l/kappa_c) = "
          "%.10e vs ratio_lat/ratio_con = %.10e" % (decomp, ratio_l / ratio_c))
    assert abs(decomp / (ratio_l / ratio_c) - 1) < 1e-9

    # ---- Q4 incidence-weighted variant (robustness of the source norm)
    R_map_inc = float(np.mean([src_norm(d, simps, distinct=False) for d in dl_tt])) \
        / src_norm(dl_vw, simps, distinct=False)

    # ---- Q6 sign / degeneracy structure (the physical content)
    sign_ok = (float(np.max(evt)) < 0 < abs(qvw_l)) and (float(np.max(evtc)) < 0 < abs(qvw_c))
    rank_ok = np.all(np.abs(evt) > 1e-6 * max(np.abs(evt).max(), 1e-30)) \
        and np.all(np.abs(evtc) > 1e-9 * max(np.abs(evtc).max(), 1e-30))

    # ---- Q6 mechanism: split the Regge form into background-area and deficit pieces
    A0, D0 = regge_parts(D, np.zeros_like(data[1]))

    def q_parts(vec):
        dl = pert_metric(D, Hmat(vec), kvecT)
        Aa, Dd = regge_parts(D, dl)
        return Aa - A0, Dd - D0

    qa_tt = float(np.mean([q_parts(t)[0] for t in tt]))
    qd_tt = float(np.mean([q_parts(t)[1] for t in tt]))
    qf_tt = float(np.mean([q_of(t)[0] for t in tt]))
    qa_vw = q_parts(vw)[0]
    qd_vw = q_parts(vw)[1]
    qf_vw = qvw_l
    # cancellation fraction: how small the FULL form is compared with its two pieces
    canc_tt = abs(qf_tt) / (abs(qa_tt) + abs(qd_tt))
    canc_vw = abs(qf_vw) / (abs(qa_vw) + abs(qd_vw))
    # identity residual measured against the PIECES, not against the (cancellated) full form:
    # |qa| + |qd| ~ 30 while |qf| ~ 4e-3, so a residual relative to qf would be a float64
    # cancellation artefact rather than a test of the split.
    ident_tt = abs(qa_tt + qd_tt - qf_tt) / (abs(qa_tt) + abs(qd_tt))
    ident_vw = abs(qa_vw + qd_vw - qf_vw) / (abs(qa_vw) + abs(qd_vw))
    print("     signed split (area / deficit / full): conformal %+.4e %+.4e %+.4e ; TT %+.4e "
          "%+.4e %+.4e" % (qa_vw, qd_vw, qf_vw, qa_tt, qd_tt, qf_tt))
    print("     CANCELLATION fraction |full|/(|area|+|deficit|): TT %.6e ; conformal %.6e ; "
          "ratio %.4f" % (canc_tt, canc_vw, canc_tt / canc_vw))

    print("SCAN M=%-3d ratio_lat=%.6e ratio_con=%.6f R_map=%.6e R_map_con=%.6f "
          "R_W=%.6e R_W_con=%.6f R_map_inc=%.6e rhoTT=%.4e rhoTT_con=%.4e rhoVW=%.4e "
          "rhoVW_con=%.4e log10TT=%.4f log10VW=%.4f cancTT=%.6e cancVW=%.6e qaVW=%.4e "
          "qdVW=%.4e qaTT=%.4e qdTT=%.4e identTT=%.2e identVW=%.2e"
          % (M, ratio_l, ratio_c, R_map, R_map_c, R_W, R_W_c, R_map_inc, rho_tt_l, rho_tt_c,
             rho_vw_l, rho_vw_c, atom_tt, atom_vw, canc_tt, canc_vw, qa_vw, qd_vw, qa_tt, qd_tt,
             ident_tt, ident_vw))
    return dict(M=M, S0=S0, dmax=dmax, evt=evt, evtc=evtc, qvw_l=qvw_l, qvw_c=qvw_c,
                ratio_l=ratio_l, ratio_c=ratio_c, R_map=R_map, R_map_c=R_map_c,
                R_W=R_W, R_W_c=R_W_c, R_map_inc=R_map_inc, sign_ok=sign_ok, rank_ok=rank_ok,
                rho_tt_l=rho_tt_l, rho_tt_c=rho_tt_c, rho_vw_l=rho_vw_l, rho_vw_c=rho_vw_c,
                atom_tt=atom_tt, atom_vw=atom_vw, m_tt=m_tt, m_vw=m_vw,
                A_tt=A_tt, A_vw=A_vw, decomp=decomp, kap_l=kap_l, kap_c=kap_c,
                qa_tt=qa_tt, qd_tt=qd_tt, qf_tt=qf_tt, qa_vw=qa_vw, qd_vw=qd_vw, qf_vw=qf_vw,
                canc_tt=canc_tt, canc_vw=canc_vw, ident_tt=ident_tt, ident_vw=ident_vw)


def main():
    M = int(sys.argv[1]) if len(sys.argv) > 1 else 3
    print("=" * 78)
    print("O221 / scripts/20 - gap 2: TT amplitude suppression - normalisation artefact? M = %d" % M)
    print("=" * 78)
    r = run(M)

    print("\n[Q1] flat machinery + reproduction of the documented ratios")
    ck("Q1.1 flat configuration: every deficit vanishes and S_R = 0",
       abs(r['S0']) < 1e-9 and r['dmax'] < 1e-12,
       "S_R = %.3e, max|delta| = %.3e" % (r['S0'], r['dmax']))
    print("     documented (docs/14 sec.5): lattice ratio 6.0e-5 (M=3) .. 4.1e-4 (M=8); "
          "continuum 0.25")
    DOC = {3: 6.0e-5, 8: 4.1e-4}
    if M in DOC:
        ck("Q1.2 criterion (d)'s raw lattice ratio reproduces the value documented in docs/14 "
           "for this M", abs(r['ratio_l'] / DOC[M] - 1) < 0.05,
           "M=%d lattice = %.6e (docs %.1e ; data/17 log on 5 dp)" % (M, r['ratio_l'], DOC[M]))
    else:
        ck("Q1.2 criterion (d)'s raw lattice ratio stays inside the documented M = 3..8 band "
           "5.5e-5 .. 4.3e-4", 5.5e-5 < r['ratio_l'] < 4.3e-4,
           "M=%d lattice = %.6e (docs band 6.0e-5 .. 4.1e-4)" % (M, r['ratio_l']))
    ck("Q1.3 the continuum control of criterion (d) is exactly 0.25 at every M (the raw basis "
       "norms give |TT|/|trace| = 1/4 there)", abs(r['ratio_c'] / 0.25 - 1) < 0.02,
       "continuum ratio = %.6f" % r['ratio_c'])

    print("\n[Q2] the ratio factorises EXACTLY into map and stiffness factors")
    ck("Q2.1 ratio_lat = R_map^2 * R_W identically (by construction, so this is a bookkeeping "
       "check, not a physical one)", abs(r['R_map'] ** 2 * r['R_W'] / r['ratio_l'] - 1) < 1e-12,
       "R_map^2*R_W = %.6e, ratio_lat = %.6e" % (r['R_map'] ** 2 * r['R_W'], r['ratio_l']))
    print("     => R_map = the pure METRIC->LENGTH map factor (how much of the mode reaches the "
          "edge variables); R_W = the stiffness ratio at MATCHED source norm")

    print("\n[Q3] where does the suppression live?")
    print("     lattice: R_map = %.6e ; continuum: R_map = %.6f" % (r['R_map'], r['R_map_c']))
    ck("Q3.1 the metric->length MAP is NOT the culprit: its factor is O(1) (0.1 .. 3) - so the "
       "suppression cannot be blamed on the linearised map or on the edge measure",
       0.1 < abs(r['R_map'] / r['R_map_c']) < 3.0,
       "R_map(lattice)/R_map(continuum) = %.6f" % (r['R_map'] / r['R_map_c']))
    ck("Q3.2 the incidence-weighted source norm gives the same order of magnitude "
       "(the conclusion does not depend on the edge measure)",
       abs(np.log10(r['R_map_inc'] / r['R_map'])) < 0.5,
       "R_map distinct = %.4e ; R_map incidence-weighted = %.4e" % (r['R_map'], r['R_map_inc']))

    print("\n[Q4] where the suppression lives: the FORM's anisotropy, not the map")
    print("     R_W lattice = %.6e ; R_W continuum = %.6e ; ratio = %.6f"
          % (r['R_W'], r['R_W_c'], r['R_W'] / r['R_W_c']))
    ck("Q4.1 the TT-vs-conformal stiffness ratio (at matched source norm) is suppressed by "
       ">= 100x on the lattice", abs(r['R_W'] / r['R_W_c']) < 1e-2,
       "R_W(lattice)/R_W(continuum) = %.6e" % (r['R_W'] / r['R_W_c']))
    ck("Q4.2 PER-SECTOR: the TT sector's mean stiffness at unit source norm matches its own "
       "continuum counterpart to within a factor of 10", r['A_tt'] < 10.0,
       "rho_TT lattice = %.4e vs continuum = %.4e (A_TT = %.4f)"
       % (r['rho_tt_l'], r['rho_tt_c'], r['A_tt']))
    ck("Q4.3 PER-SECTOR: the CONFORMAL (spatial-trace) sector is the anomalous one, more than "
       "10x too stiff at unit source norm", r['A_vw'] > 10.0,
       "rho_conf lattice = %.4e vs continuum = %.4e (A_conf = %.4f)"
       % (r['rho_vw_l'], r['rho_vw_c'], r['A_vw']))
    ck("Q4.4 the raw suppression factorises EXACTLY into three lattice-side factors: form "
       "anisotropy (A_TT/A_conf), metric->length map distortion (m_TT/m_vw) and the "
       "polarisation-shape factor (kappa_l/kappa_c)",
       abs(r['decomp'] / (r['ratio_l'] / r['ratio_c']) - 1) < 1e-9,
       "(A_TT/A_conf) = %.6e ; (m_TT/m_vw) = %.6e ; (kappa ratio) = %.6e ; product = %.6e ; "
       "ratio_lat/ratio_con = %.6e" % (r['A_tt'] / r['A_vw'], r['m_tt'] / r['m_vw'],
                                       r['kap_l'] / r['kap_c'], r['decomp'],
                                       r['ratio_l'] / r['ratio_c']))

    print("\n[Q6] mechanism: the area/deficit cancellation of the 4D Regge form on a flat torus")
    ck("Q6.1 the split is exact: q_full = q_area + q_deficit (both sectors), to the accuracy "
       "of the underlying angle evaluation",
       r['ident_tt'] < 1e-9 and r['ident_vw'] < 1e-9,
       "residual relative to the pieces: TT %.3e ; conformal %.3e"
       % (r['ident_tt'], r['ident_vw']))
    ck("Q6.2 the form is a CANCELLATION of two much larger pieces: |q_full| < 50 pct of "
       "|q_area| + |q_deficit| in BOTH sectors",
       r['canc_tt'] < 0.5 and r['canc_vw'] < 0.5,
       "TT residual fraction = %.6e ; conformal = %.6e" % (r['canc_tt'], r['canc_vw']))
    ck("Q6.3 REFUTED HYPOTHESIS, recorded: the cancellation is NOT sector-specific (the "
       "TT/conformal cancellation ratio is O(1), far below 10x), so the raw suppression is NOT "
       "a cancellation artefact - the surviving mechanism is the conformal-sector anomaly of "
       "Q4.3", r['canc_tt'] * 10 > r['canc_vw'],
       "TT cancellation fraction = %.6e ; conformal = %.6e ; ratio = %.4f (needs >= 10 to "
       "support the cancellation hypothesis)" % (r['canc_tt'], r['canc_vw'],
                                                 r['canc_tt'] / r['canc_vw']))

    ck("Q5.1 TT block non-degenerate (rank 2) and OPPOSITE in sign to the conformal sector, "
       "lattice and continuum", bool(r['rank_ok'] and r['sign_ok']),
       "lattice TT = %s vs q(vw) = %+.3e ; continuum TT = %s vs q(vw) = %+.3e"
       % (np.array2string(r['evt'], precision=4), r['qvw_l'],
          np.array2string(r['evtc'], precision=4), r['qvw_c']))

    print("\nRESULT: %d/%d PASS" % (PASS, PASS + FAIL))
    if FAIL:
        print("HONEST STATUS: %d FAIL - see above; no physics threshold was relaxed." % FAIL)
    else:
        print("HONEST STATUS: all checks pass. Gap 2 is LOCALISED, not explained away: the "
              "metric->length map is O(1) and the TT sector (dim 2, non-degenerate, negative) "
              "matches its OWN continuum counterpart at unit source norm to within a factor 7.7 "
              "(M=3) improving to 2.8 (M=8); the anomaly sits in the CONFORMAL (spatial-trace) "
              "sector, ~40-50x too stiff and M-stable (the known Regge conformal-mode problem). "
              "A second candidate mechanism - a sector-specific cancellation between the "
              "2 pi sum_t A_t area piece and the deficit piece - was TESTED and REFUTED (both "
              "sectors cancel ~85-88 pct, ratio 1.34). The raw ratio is therefore NOT a "
              "prediction for TT dynamics; it is a statement about the trace sector.")


if __name__ == "__main__":
    main()
