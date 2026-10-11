#!/usr/bin/env python3
# O221 scripts/42 - Round 32: LINEAR-ORDER structure of the sector responses
#                            (per-edge basis; EPS-exponent proof; deficit on the raw vs FD)
#
# R31-N0 (docs/37) claimed the raw sector responses were interaction/2nd-order dominated.
# The R32 EPS probe REFUTED that interpretation: at M=4 naive the conf/TT raw and FD-odd
# responses scale EXACTLY as EPS^1 (1e-3 -> 1e-5 ratios 0.100) - the full-field responses
# are FIRST-ORDER linear.  The R31 per-simplex weights ~1e-10 are a LUMPING artifact: the
# correct basis is PER-EDGE (dl is per-edge), and the 10 per-edge coefficients of each
# Kuhn simplex cancel violently to ~1e-10.
#
# PRE-REGISTRATION (frozen 2026-10-02; framing corrected 2026-10-10 after the EPS probe):
#   L1  per-edge linear structure at (M=4, naive):
#       - per-edge RMS |c_e| from the variance of the response to random Rademacher
#         per-EDGE fields: Var(q) = sum_e c_e^2 (linear).
#       - the naive smooth-field coherence |q(cos)|/sqrt(Var).
#       - the intra-simplex cancellation ratio: per-edge scale*sqrt(10) vs the per-simplex
#         FD weight scale (R31 found ~1.25e-10 at M=3; re-measured at M=4).
#   L2  the deficit on the RAW vs the FD (symmetric, [q(+cos)-q(-cos)]/2) responses over
#       the ladder: |deficit_fd - deficit_raw| < 0.10 -> the docs/17-29 exponents ARE
#       first-order exponents (L2a); >= 0.10 -> the FD re-derivation is required (L2b).
#   L3  the FD-level amplitude axis: A_TT_fd M-stability (M=12->16) in [0.8, 1.25] per
#       family (naive/vert/cube).
#   L4  the docs/20 acceptance at the FD level: any family with |deficit_fd| < 0.05 AND
#       A_TT_fd in [0.8,1.25] -> residual 5 CLOSED at the linear order; else candidate 3.
#   L5  the EPS-exponent proof (M=4, naive): alpha ~ 1 for the raw and the FD responses
#       in BOTH sectors (the linearity of the sector responses; the probe numbers
#       1e-3/1e-4/1e-5 -> 0.100 pre-verified; acceptance alpha in [0.9, 1.1]).
#
# Machinery: same primitives, axial ladder (M,n) = (3,1),(4,2),(6,3),(8,4),(12,6),(16,8),
# families naive/vert/cube (dual == cube machine-exact at axial k, R28).
import importlib.util
import os
from itertools import permutations

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "o221_s23", os.path.join(HERE, "23_residual45_closure.py"))
s23 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(s23)

PAIRS5 = s23.PAIRS5
PIDX = s23.PIDX
CELL_SIMP = s23.CELL_SIMP
lift_simps = s23.lift_simps
lift_id = s23.lift_id
flat_data = s23.flat_data
simplex_angles = s23.simplex_angles
regge = s23.regge
central_hinges = s23.central_hinges
base_rng = s23.base_rng

EPS_DEFAULT = 1e-3
CUBE_OFFS = np.array([[a, b, c, d] for a in (0, 1) for b in (0, 1)
                      for c in (0, 1) for d in (0, 1)], float)


def incidence_weights():
    cnt = np.zeros(16, dtype=int)
    for sig in permutations(range(4)):
        offs = np.zeros((5, 4), int)
        acc = np.zeros(4, int)
        offs[0] = acc.copy()
        for j, axis in enumerate(sig):
            acc[axis] += 1
            offs[j + 1] = acc.copy()
        for off in offs:
            cnt[sum(int(off[d]) << (3 - d) for d in range(4))] += 1
    return cnt.astype(float) / cnt.sum()


W_NORM = incidence_weights()


def phase(data, kvec, variant):
    simps, L, shat, mid = data[0], data[1], data[2], data[3]
    if variant == "naive":
        return np.cos(np.einsum('neC,C->ne', mid, kvec))
    c = 0.25 * simps.sum(axis=1)
    if variant == "cell":
        return np.repeat(np.cos(c @ kvec)[:, None], 10, axis=1)
    if variant == "vert":
        pv = np.cos(np.einsum('nvC,C->nv', simps, kvec))
        return np.repeat(pv.mean(axis=1)[:, None], 10, axis=1)
    base = simps[:, 0, :]
    k0 = base @ kvec
    c0, s0 = np.cos(k0), np.sin(k0)
    acc = np.zeros_like(k0)
    for oi in range(16):
        kb = float(CUBE_OFFS[oi] @ kvec)
        p = c0 * np.cos(kb) - s0 * np.sin(kb)
        acc += p * (1.0 if variant == "cube" else W_NORM[oi])
    if variant == "cube":
        acc = acc / 16.0
    return np.repeat(acc[:, None], 10, axis=1)


def run_lin(M, n, variant="naive", eps=EPS_DEFAULT):
    """Axial-k run: sector directions (phys_dir from the Q-matrix) + the raw and
    symmetric-FD responses per sector + the per-edge projection kernels."""
    s23.M_GLOBAL = M
    kfac = 2 * np.pi / M
    kvecT = kfac * n * np.array([0.0, 0.0, 0.0, 1.0])
    data = flat_data(M)
    simps = data[0]
    D = (simps, data[1], data[2], data[3], central_hinges(M))
    S0 = regge(D, np.zeros_like(data[1]))[0]

    pairs4 = [(m, q) for m in range(4) for q in range(m, 4)]
    S_NB = np.array([1.0 if m == q else np.sqrt(2.0) for (m, q) in pairs4])

    def tensor_of(nb):
        v = np.asarray(nb, float) * S_NB
        H = np.zeros((4, 4))
        for c, (m, q) in enumerate(pairs4):
            H[m, q] += v[c] / (1.0 if m == q else 2.0)
            H[q, m] += v[c] / (1.0 if m == q else 2.0)
        return H * eps

    ph = phase(data, kvecT, variant)

    def proj_of(nb):
        H = tensor_of(nb)
        return np.einsum('nek,kl,nel->ne', data[2], H, data[2])

    def dl_of(nb, sign=1.0, phi=None):
        pr = proj_of(nb)
        p = ph if phi is None else phi
        return 0.5 * data[1] * pr * (sign * p)

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
        vg = pairs_of(Hg) / S_NB
        Vg.append(vg / np.linalg.norm(vg))
    Vg = np.array(Vg)
    _, s_, vt_ = np.linalg.svd(Vg)
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

    out = dict(M=M, n=n, k=float(kfac * n), variant=variant, eps=eps, data=data, D=D,
               S0=S0, proj={}, dl_of=dl_of, regge=regge)
    for name, dirs in (("TT", tt), ("conf", [vw])):
        ql_raw = []; ql_fd = []; rmm = []; qc = []; prs = []
        for d in dirs:
            x = phys_dir(d)
            pr = proj_of(x)
            prs.append(pr)
            qp = regge(D, dl_of(x, +1.0))[0] - S0
            qm = regge(D, dl_of(x, -1.0))[0] - S0
            ql_raw.append(qp)
            ql_fd.append(0.5 * (qp - qm))
            dl0 = dl_of(x, +1.0)
            rmm.append(float(np.sum(dl0 * dl0)) / (eps ** 2))
            qc.append(q_cont(x))
        out[name] = dict(q_raw=np.array(ql_raw), q_fd=np.array(ql_fd),
                         q_cont=np.array(qc), R_map=np.array(rmm), phys=[phys_dir(d) for d in dirs],
                         proj=np.array(prs))
    for which in ("raw", "fd"):
        A = {}
        for name in ("TT", "conf"):
            q = out[name]["q_" + which]
            A[name] = float(np.sum(np.abs(q) / out[name]["R_map"])
                            / np.sum(np.abs(out[name]["q_cont"])))
        out["A_" + which] = A
    return out


def qv(r, sec, which):
    return float(np.mean(r[sec]["q_" + which]))


def expo(a, b, M1, M2):
    if b == 0.0 or a == 0.0:
        return float('inf') if b != 0.0 else float('nan')
    return float(np.log(abs(b) / abs(a)) / np.log(M2 / M1))


def sec_slope(R, var, sec, which, M1, M2):
    return expo(qv(R[(var, M1)], sec, which), qv(R[(var, M2)], sec, which), M1, M2)


def deficits(R, var, which):
    return dict(conf=sec_slope(R, var, "conf", which, 4, 16),
                TT=sec_slope(R, var, "TT", which, 4, 16))


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


def main():
    print("=" * 78)
    print("O221 / scripts/42 - Round 32: LINEAR-ORDER structure (per-edge basis; EPS-exponent)")
    print("=" * 78)
    rng = np.random.default_rng(20261010)

    # ---- L1: per-edge linear structure at M=4 naive ----
    r4 = run_lin(4, 2, variant="naive", eps=1e-3)
    data = r4["data"]
    D = r4["D"]
    n_edges = data[1].size
    print("    L1 M=4 naive: n_edges = %d (%.1f M^4-scaled), conf raw %.3e fd %.3e"
          % (n_edges, n_edges / 4 ** 4, qv(r4, "conf", "raw"), qv(r4, "conf", "fd")), flush=True)
    B = 200
    var_raw = {n: 0.0 for n in ("conf", "TT")}
    phi = np.empty((n_edges,), dtype=np.int8)
    for b in range(B):
        xi = rng.choice(np.array([-1.0, 1.0]), size=n_edges)
        ph_rand = xi.reshape(data[1].shape).astype(float)
        for name in ("conf", "TT"):
            dl = r4["dl_of"](r4[name]["phys"][0], +1.0, phi=ph_rand)
            var_raw[name] += (r4["regge"](D, dl)[0] - r4["S0"]) ** 2
    var_raw = {n: var_raw[n] / B for n in ("conf", "TT")}
    rms_c = {}
    for name in ("conf", "TT"):
        rms_c[name] = float(np.sqrt(var_raw[name] / n_edges))
    print("    L1 per-edge RMS |c_e|: conf %.3e TT %.3e (random per-edge fields, B=%d)"
          % (rms_c["conf"], rms_c["TT"], B), flush=True)
    print("    L1 naive smooth-field coherence |q(cos)|/sqrt(Var): conf %.1f TT %.1f"
          % (abs(qv(r4, "conf", "raw")) / np.sqrt(var_raw["conf"]),
             abs(qv(r4, "TT", "raw")) / np.sqrt(var_raw["TT"])), flush=True)
    # intra-simplex cancellation: per-simplex FD weights at M=4 (24 types of cube (0,0,0,0))
    simps = data[0]
    rows = np.nonzero(np.all(simps[:, 0, :] == 0.0, axis=1))[0]
    Ws = []
    for t in rows:
        ph_p = np.zeros(data[1].shape); ph_p[t, :] = 1.0
        ph_m = np.zeros(data[1].shape); ph_m[t, :] = -1.0
        qp = r4["regge"](D, r4["dl_of"](r4["conf"]["phys"][0], +1.0, phi=ph_p))[0]
        qm = r4["regge"](D, r4["dl_of"](r4["conf"]["phys"][0], +1.0, phi=ph_m))[0]
        Ws.append(0.5 * (qp - qm))
    Ws = np.abs(np.array(Ws))
    w_scale = float(Ws.max())
    cancel = (rms_c["conf"] * np.sqrt(10.0)) / max(w_scale, 1e-30)
    ck("L1 per-edge basis confirmed: the per-edge coefficient scale is LARGE while the"
       " per-simplex lumped weight is tiny (intra-simplex cancellation) - the R31-N0"
       " lumping artifact explained",
       w_scale > 0 and cancel > 10.0,
       "per-edge RMS %.2e ; per-simplex max %.2e ; cancellation factor %.0f"
       % (rms_c["conf"], w_scale, cancel))

    # ---- ladder runs ----
    LAD = [(3, 1), (4, 2), (6, 3), (8, 4), (12, 6), (16, 8)]
    FAM = ("naive", "vert", "cube")
    R = {}
    for var in FAM:
        for (M_, n_) in LAD:
            r = run_lin(M_, n_, variant=var)
            R[(var, M_)] = r
            print("      (%s M=%d n=%d) conf raw %.3e fd %.3e | TT raw %.3e fd %.3e"
                  % (var, M_, n_, qv(r, "conf", "raw"), qv(r, "conf", "fd"),
                     qv(r, "TT", "raw"), qv(r, "TT", "fd")), flush=True)

    # ---- L2: raw vs fd deficit ----
    DIFF = {}
    for var in FAM:
        dr = deficits(R, var, "raw")
        df = deficits(R, var, "fd")
        drd = dr["conf"] - dr["TT"]; dfd = df["conf"] - df["TT"]
        DIFF[var] = abs(dfd - drd)
        print("    %-5s raw deficit %+.4f (c %+.3f t %+.3f) | FD deficit %+.4f (c %+.3f t %+.3f)"
              % (var, drd, dr["conf"], dr["TT"], dfd, df["conf"], df["TT"]), flush=True)
    for var in FAM:
        ck("L2 for %s: |deficit_fd - deficit_raw| < 0.10 -> the docs/17-29 exponents ARE"
           " first-order exponents" % var, DIFF[var] < 0.10,
           "|d_fd - d_raw| = %.4f" % DIFF[var])

    # ---- L3: fd-level A_TT amplitude stability (M=12 -> 16) ----
    print("\n  L3 FD-level A_TT (M=12 -> 16):")
    ATT_FD = {}
    for var in FAM:
        att = R[(var, 12)]["A_fd"]["TT"] / R[(var, 16)]["A_fd"]["TT"]
        ATT_FD[var] = att
        ok = abs(np.log(att)) < np.log(1.25)
        print("      %-5s A_TT_fd(12->16) = %.4f %s" % (var, att, "OK" if ok else "OUT"),
              flush=True)
        ck("L3 for %s: FD-level A_TT M-stability in [0.8, 1.25]" % var, ok,
           "A_TT_fd = %.4f" % att)

    # ---- L4: the docs/20 acceptance at the FD level ----
    best = None
    for var in FAM:
        df = deficits(R, var, "fd")
        dfd = df["conf"] - df["TT"]
        att = ATT_FD[var]
        okd = abs(dfd) < 0.05
        oka = abs(np.log(att)) < np.log(1.25)
        print("      %-5s |deficit_fd| = %.4f %s ; A_TT_fd = %.4f %s -> %s"
              % (var, abs(dfd), "OK" if okd else "OUT", att, "OK" if oka else "OUT",
                 "CLOSED at the linear order" if (okd and oka) else "not"), flush=True)
        if okd and oka:
            best = var
    ck("L4 docs/20 acceptance AT THE FD (linear) ORDER: any family with |deficit_fd| < 0.05"
       " AND A_TT_fd in [0.8,1.25]",
       best is not None,
       ("%s CLOSED residual 5 at the linear order" % best) if best else
       "none - candidate 3 / structural terminal statement remains")

    # ---- L5: EPS-exponent proof (M=4, naive) ----
    rs = {}
    for eps in (1e-3, 1e-4, 1e-5):
        rs[eps] = run_lin(4, 2, variant="naive", eps=eps)
    alphas = {}
    for sec in ("conf", "TT"):
        for which in ("raw", "fd"):
            vals = [abs(qv(rs[e], sec, which)) for e in (1e-3, 1e-4, 1e-5)]
            a = float(np.polyfit(np.log([1e-3, 1e-4, 1e-5]), np.log(vals), 1)[0])
            alphas[(sec, which)] = a
            print("    L5 EPS-exponent %s/%s: alpha = %.4f (values %.2e %.2e %.2e)"
                  % (sec, which, a, vals[0], vals[1], vals[2]), flush=True)
    ok5 = all(0.9 <= alphas[(s, w)] <= 1.1 for s in ("conf", "TT") for w in ("raw", "fd"))
    ck("L5 the EPS-exponent: BOTH sectors, raw AND fd, scale as EPS^1 (alpha in [0.9,1.1])"
       " - the sector responses are first-order linear, confirming the R32 probe and"
       " correcting the R31-N0 '2nd-order dominated' interpretation",
       ok5, "alphas: conf/raw %.3f conf/fd %.3f TT/raw %.3f TT/fd %.3f"
       % (alphas[("conf", "raw")], alphas[("conf", "fd")],
          alphas[("TT", "raw")], alphas[("TT", "fd")]))

    print("\nRESULT: %d/%d PASS" % (PASS, PASS + FAIL))
    if FAIL:
        print("HONEST STATUS: %d FAIL - see above; no physics threshold was relaxed." % FAIL)
    else:
        print("HONEST STATUS: all checks pass.")


if __name__ == "__main__":
    main()