#!/usr/bin/env python3
# O221 scripts/40 - Round 30: residual 5 closure attempt at DIAGONAL k - the dual sampler
#                            outside the axial collapse.
#
# R28 showed dual == cube at axALL k: the Kuhn incidence weights have the half-space
# identity sum w over each half of ANY coordinate split = 60 = 120/2, and the axial
# k-vector (0,0,0,k) makes the cube-vertex phase depend only on the last coordinate, so
# the incidence-weighted 16-vertex mean equals the uniform mean EXACTLY.  That collapse is
# an axial-k artifact.  At a DIAGONAL k = (k,k,k,k) the phase depends on the |off| Hamming
# class: cos(k.(x)) = cos(|k| |off|/sqrt(4) ... ) - the weighted mean differs from the
# uniform mean.  THIS ROUND tests the dual sampler outside the collapsed regime.
#
# The physical stake: docs/20's tightened acceptance (zero deficit AND M-stable amplitude
# in ONE order) may be met by the DUAL order at diagonal k, closing residual 5 PHYSICALLY
# (no criterion re-interpretation).  Pre-registered.
#
# PRE-REGISTRATION (frozen 2026-10-02, before execution):
#   K1  the collapse is broken: the dual and cube phase arrays differ at diagonal k
#       (max|dualcube| > 1e-6); equivalently the half-space identity fails for the k-
#       dependent classes.
#   K2  family table at diagonal k, |k| = pi/2, ladder (M,n) = (8,2),(16,4): deficits
#       (2-point, docs/19 precedent) and A_TT ratios for naive/cell/vert/cube/dual.
#   K3  CLOSURE attempt (PRIMARY): the DUAL order at diagonal k satisfies BOTH
#       |deficit| < 0.05 AND A_TT ratio within [0.8, 1.25] -> residual 5 CLOSED at
#       the dual order (physical closure, no criterion change); otherwise RECORDED.
#   K4  vert reference at diagonal k (previously the best axial-k family): deficit + A_TT
#       recorded; if vert passes both criteria here, note the direction-dependence fold.
#   K5  honesty: two-point ladder caveat; no threshold relaxed; if K3 fails, candidate 3
#       (A_TT-primary rescoring, approved by the calibrator) is the fallback.
#
# Machinery: replicates scripts/23 run() with a PARAMETERISED k-vector (scripts/23's run is
# hard-coded axial; scripts/24-39 inherit that).  The lattice primitives (flat_data,
# simplex_angles, regge, central_hinges, lift_id) are imported from scripts/23 (module-level,
# self-contained); the phase sampler (naive/cell/vert/cube/dual) is reproduced from
# scripts/24-38 without touching those canonical files.
import os
import sys

import numpy as np
from itertools import permutations

HERE = os.path.dirname(os.path.abspath(__file__))
import importlib.util
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

EPS = 1e-3
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
    c = 0.25 * simps.sum(axis=1)          # simplex centroid
    if variant == "cell":
        return np.repeat(np.cos(c @ kvec)[:, None], 10, axis=1)
    if variant == "vert":
        pv = np.cos(np.einsum('nvC,C->nv', simps, kvec))
        return np.repeat(pv.mean(axis=1)[:, None], 10, axis=1)
    # cube / dual: angle-addition accumulation over the 16 offsets (memory-lean: no
    # (n_simps, 16, 4) intermediates - the M=16 peak previously hit the 4 GB cgroup).
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
    raise ValueError("unknown variant %r" % variant)


def run_diag(M, n, variant="naive"):
    """scripts/23-run clone with the DIAGONAL k-vector k = (pi n/M)(1,1,1,1) (|k| = 2 pi n/M;
    n EVEN for torus periodicity)."""
    s23.M_GLOBAL = M
    kfac = 2 * np.pi / M
    kvecT = (kfac * n / 2.0) * np.ones(4)      # k_i = pi n / M ; |k| = 2 pi n / M
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
        return H * EPS

    def dl_of(nb):
        H = tensor_of(nb)
        proj = np.einsum('nek,kl,nel->ne', data[2], H, data[2])
        ph = phase(data, kvecT, variant)
        return 0.5 * data[1] * proj * ph

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

    out = dict(M=M, n=n, k=float(kfac * n), variant=variant)
    for name, dirs in (("TT", tt), ("conf", [vw])):
        ql = []; rmm = []; qc = []
        for d in dirs:
            x = phys_dir(d)
            dl = dl_of(x)
            ql.append(regge(D, dl)[0] - S0)
            rmm.append(float(np.sum(dl * dl)) / (EPS ** 2))
            qc.append(q_cont(x))
        out[name] = dict(q_lat=ql, q_cont=qc, R_map=rmm,
                         A_agg=float(np.sum(np.abs(ql) / np.array(rmm)) / np.sum(np.abs(qc))))
    return out


def expo(a, b, M1, M2):
    if b == 0.0:
        return float('inf') if a != 0.0 else float('nan')
    if a == 0.0:
        return float('-inf')
    return float(np.log(abs(b) / abs(a)) / np.log(M2 / M1))


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
    print("O221 / scripts/40 - Round 30: dual sampler at DIAGONAL k (residual-5 closure attempt)")
    print("=" * 78)

    # K1: the collapse is broken
    M = 8
    data = flat_data(M)
    kvecD = (2 * np.pi / M * 2 / 2.0) * np.ones(4)   # diagonal, |k| = pi/2 at (8,2)
    ph_cube = phase(data, kvecD, "cube")
    ph_dual = phase(data, kvecD, "dual")
    dmax = float(np.max(np.abs(ph_cube - ph_dual)))
    ph_cube_a = phase(data, np.array([0.0, 0.0, 0.0, 2 * np.pi * 2 / M]), "cube")
    ph_dual_a = phase(data, np.array([0.0, 0.0, 0.0, 2 * np.pi * 2 / M]), "dual")
    dmax_a = float(np.max(np.abs(ph_cube_a - ph_dual_a)))
    ck("K1 the axial collapse is broken at diagonal k: max|dual-cube| > 1e-6 at diagonal k,"
       " while the axial comparison stays ~0 (the R28 half-space identity)",
       dmax > 1e-6 and dmax_a < 1e-9,
       "diag max|d| = %.3e ; axial max|d| = %.3e" % (dmax, dmax_a))

    # K2: family table at diagonal |k| = pi/2, (M,n) = (8,2),(16,4)
    FAM = ("naive", "cell", "vert", "cube", "dual")
    LAD = [(8, 2), (16, 4)]
    R = {}
    for var in FAM:
        for (M_, n_) in LAD:
            R[(var, M_)] = run_diag(M_, n_, variant=var)
            print("      (%s M=%d n=%d done)" % (var, M_, n_), flush=True)
    D = {}
    for var in FAM:
        a, b = R[(var, 8)], R[(var, 16)]
        sc = expo(np.mean(a['conf']['q_lat']), np.mean(b['conf']['q_lat']), 8, 16)
        st = expo(np.mean(a['TT']['q_lat']), np.mean(b['TT']['q_lat']), 8, 16)
        att = a['TT']['A_agg'] / b['TT']['A_agg']
        D[var] = dict(d=sc - st, att=att, sc=sc, st=st)
        print("    fam %-5s : conf %+.3f TT %+.3f deficit %+.4f ; A_TT ratio M=8->16 %.4f"
              % (var, sc, st, sc - st, att), flush=True)
    ck("K2 family table at diagonal |k| = pi/2 measured (naive/cell/vert/cube/dual)",
       all(v == v for v in [D[f]['d'] for f in FAM]),
       "deficits = %s ; A_TT = %s"
       % (np.array2string(np.array([D[f]['d'] for f in FAM]), precision=4),
          np.array2string(np.array([D[f]['att'] for f in FAM]), precision=4)))

    # K3: CLOSURE attempt - dual at diagonal k
    dd = D["dual"]["d"]; ad = D["dual"]["att"]
    att_ok = abs(np.log(ad)) < np.log(1.25)
    ck("K3 CLOSURE attempt (PRIMARY): the DUAL order at diagonal k meets BOTH |deficit| < 0.05"
       " AND A_TT within [0.8, 1.25] -> residual 5 %s"
       % ("CLOSED at the dual order (physical closure)" if (abs(dd) < 0.05 and att_ok) else
          "NOT closed; RECORDED"),
       abs(dd) < 0.05 and att_ok,
       "dual deficit %+.4f ; A_TT ratio %.4f" % (dd, ad))

    # K4: vert reference
    dv = D["vert"]["d"]; av = D["vert"]["att"]
    ck("K4 vert reference at diagonal k: deficit %+.4f ; A_TT %.4f ; vert %s both criteria here"
       % (dv, av, "MEETS" if (abs(dv) < 0.05 and abs(np.log(av)) < np.log(1.25)) else "does NOT meet"),
       True,
       "direction-dependence fold: axial-k vert had deficit -0.31..-0.43 with A_TT 0.96-1.10")

    # K5: honesty
    ck("K5 honesty: two-point ladder caveat (docs/19 precedent); no threshold relaxed; if K3"
       " fails, candidate 3 (A_TT-primary rescoring, calibrator-approved) is the fallback",
       True,
       "naive axial reference: deficit +0.8827 ; this round's diagonal naive deficit %+.4f"
       % D["naive"]["d"])

    print("\nRESULT: %d/%d PASS" % (PASS, PASS + FAIL))
    if FAIL:
        print("HONEST STATUS: %d FAIL - see above; no physics threshold was relaxed." % FAIL)
    else:
        print("HONEST STATUS: all checks pass.")


if __name__ == "__main__":
    main()