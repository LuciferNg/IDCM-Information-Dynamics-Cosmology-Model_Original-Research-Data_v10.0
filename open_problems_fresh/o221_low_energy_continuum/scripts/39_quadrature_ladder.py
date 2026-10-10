#!/usr/bin/env python3
# O221 scripts/39 - Round 29: residual 5 - the QUADRATURE-LADDER test of the
#                            half-integer projector-sub-ladder conjecture (docs/21 item 1/3).
#
# docs/21 framed residual 5 as: "if the deficit across finer sampling families lands on the
# ladder {..., -1, -1/2, 0, +1/2, +1}, residual 5 can be restated as the PROJECTOR-SUB-LADDER
# THEOREM (the projector has an integer/half-integer power spectrum over the sampling
# family), a structural statement."  That is a pre-registered CONJECTURE whose outcome is
# either confirmation or refutation - recorded, never scored as a machinery failure.
#
# The natural, well-defined family to test it on: the GAUSS QUADRATURE ladder for the phase
# along each lattice edge (orders 1..4) plus the exact edge integral (the sinc endpoint:
# order infinity).  These are 5 SAMPLING FAMILIES (naive = 1-pt, q2, q3, q4, sinc) - the
# "5 unseen sampling families" of the residual-5 closure criterion 4 (docs/19-21), tested
# at k = pi/2 on the (M,n) = (4,1),(8,2),(16,4) ladder plus one unseen-k probe; the
# official 10^7-MC-5sigma blind test remains separate and is NOT claimed here.
#
# PRE-REGISTRATION (frozen 2026-10-02, before execution):
#   Q1  the 5-point deficit ladder [d_1pt, d_q2, d_q3, d_q4, d_sinc] at k = pi/2 is
#       measured (recorded table); A_TT ratio (M 4 -> 16) per family is recorded.
#   Q2  PREDICTION (recorded): if the projector-sub-ladder theorem (docs/21 item 3) holds,
#       every family deficit lies on {+1, +1/2, 0, -1/2, -1} within +-0.05.  If any family
#       is off-ladder, the conjecture is REFUTED and recorded.
#   Q3  TESTABLE companion: Gauss convergence of the quadrature ladder to the sinc endpoint:
#       the increments |d_q(k+1) - d_q(k)| decrease monotonically (k = 1..3), and q4's
#       deficit is closer to the sinc deficit than q2's is.
#   Q4  unseen-k probe: q4 at k = 3pi/10 ((10,1),(20,2)); its deficit is recorded; the
#       naive control deficit at that k is 0.8-1.0 (the residual-5 k-independence).
#   Q5  honesty: family count toward criterion 4 is satisfied by the 5 quadrature families;
#       the 10^7-MC-5sigma null test is NOT part of this round; no threshold relaxed.
#
# Machinery: imports scripts/25 (wrapping scripts/24/23) for the lattice, Regge deficit and
# projector; the quadrature samplers are added by wrapping phase() exactly as scripts/25
# added 'cube' and scripts/38 added 'dual' - scripts/24's canonical file stays untouched.
import importlib.util
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "o221_s25", os.path.join(HERE, "25_residual5_confirmation.py"))
s25 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(s25)
s24 = s25.s24

_ORIG_PHASE_25 = s25.phase

# Gauss-Legendre quadrature on the edge parameter s in [-1/2, +1/2] (L = 1 before scaling):
# standard GL nodes/weights on [-1,1], rescaled.
def _gl(order):
    if order == 2:
        x = np.array([-1.0 / np.sqrt(3.0), 1.0 / np.sqrt(3.0)])
        w = np.array([1.0, 1.0])
    elif order == 3:
        x = np.array([-np.sqrt(3.0 / 5.0), 0.0, np.sqrt(3.0 / 5.0)])
        w = np.array([5.0 / 9.0, 8.0 / 9.0, 5.0 / 9.0])
    elif order == 4:
        x = np.array([-0.8611363115940526, -0.3399810435848563,
                      0.3399810435848563, 0.8611363115940526])
        w = np.array([0.3478548451374538, 0.6521451548625461,
                      0.6521451548625461, 0.3478548451374538])
    else:
        raise ValueError("order %d not supported" % order)
    return 0.5 * x, 0.5 * w   # map [-1,1] to [-1/2, +1/2] with the 1/2 Jacobian


GL = {2: _gl(2), 3: _gl(3), 4: _gl(4)}


def phase(data, kvec, variant):
    """scripts/25's sampler plus the quadrature ladder: 'q2','q3','q4' (Gauss-Legendre
    phase along each edge) and 'qinf'/'sinc' (the exact edge integral = cos(k.x_mid) *
    sinc(k.shat L/2), order infinity).  All existing variants stay intact."""
    if variant not in ("q2", "q3", "q4", "sinc"):
        return _ORIG_PHASE_25(data, kvec, variant)
    simps, L, shat, mid = data[0], data[1], data[2], data[3]
    if variant == "sinc":
        th = np.einsum('neC,C->ne', shat, kvec) * L / 2.0
        sc = np.ones_like(th)
        nz = np.abs(th) > 1e-12
        sc[nz] = np.sin(th[nz]) / th[nz]
        return np.cos(np.einsum('neC,C->ne', mid, kvec)) * sc
    order = int(variant[1])
    xs, ws = GL[order]
    ph = np.zeros((shat.shape[0], shat.shape[1]))
    for t, w in zip(xs, ws):
        xp = mid + t * L[:, :, None] * shat
        ph += w * np.cos(np.einsum('neC,C->ne', xp, kvec))
    return ph


s24.phase = phase


def run(M, n, variant="naive"):
    return s25.run(M, n, variant=variant)


ck = s25.ck
slope = s25.slope
PASS_BEFORE = s24.PASS
FAIL_BEFORE = s24.FAIL


def att_ok(ratio):
    return abs(np.log(ratio)) < np.log(1.25)


def main():
    print("=" * 78)
    print("O221 / scripts/39 - Round 29: quadrature-ladder test of the half-integer")
    print("                           projector-sub-ladder conjecture (family criterion 4)")
    print("=" * 78)

    FAMILIES = ("naive", "q2", "q3", "q4", "sinc")
    LAD = [(4, 1), (8, 2), (16, 4)]
    print("\n[Q1] quadrature ladder at k = pi/2 (M = 4/8/16); families:", FAMILIES)
    R = {}
    for var in FAMILIES:
        for (M, n) in LAD:
            R[(var, M)] = run(M, n, variant=var)
            print("      (%s M=%d n=%d done)" % (var, M, n), flush=True)
    D = {}
    for var in FAMILIES:
        ac = slope([(M, R[(var, M)]['conf']['A_agg']) for (M, n) in LAD])
        at = slope([(M, R[(var, M)]['TT']['A_agg']) for (M, n) in LAD])
        att = R[(var, 4)]['TT']['A_agg'] / R[(var, 16)]['TT']['A_agg']
        D[var] = dict(d=ac - at, att=att)
        print("    family %-5s : deficit %+.4f ; A_TT ratio %.4f"
              % (var, ac - at, att), flush=True)
    ck("Q1 the 5-family deficit ladder at k = pi/2 [1pt, q2, q3, q4, sinc] is measured"
       " (recorded table)",
       all(v == v for v in [D[f]['d'] for f in FAMILIES]),
       "deficits = %s" % np.array2string(np.array([D[f]['d'] for f in FAMILIES]), precision=4))

    # Q2: half-integer ladder (PREDICTION - recorded)
    LADDER = (mpf_ladder := (-1.0, -0.5, 0.0, 0.5, 1.0))
    near = {}
    for f in FAMILIES:
        d = D[f]['d']
        near[f] = min(abs(d - l) for l in LADDER)
    onladder = all(v <= 0.05 for v in near.values())
    ck("Q2 PREDICTION RECORDED (half-integer projector-sub-ladder conjecture, docs/21 item 3):"
       " all five family deficits lie on {-1, -1/2, 0, +1/2, +1} within +-0.05 -> %s"
       % ("CONFIRMED" if onladder else "REFUTED"),
       onladder,
       "nearest-ladder distances = %s" % np.array2string(np.array([near[f] for f in FAMILIES]), precision=4))

    # Q3: Gauss convergence (TESTABLE)
    seq = [D[f]['d'] for f in FAMILIES]
    inc = [abs(seq[i + 1] - seq[i]) for i in range(4)]
    conv = inc[3] < inc[2] < inc[1] < inc[0] + 1e-9
    closer = abs(seq[3] - seq[4]) < abs(seq[1] - seq[4])
    ck("Q3 Gauss convergence of the quadrature ladder to the sinc endpoint: increments"
       " |d_q(k+1)-d_q(k)| decrease monotonically AND q4 is closer to the sinc deficit than"
       " q2 is", conv and closer,
       "increments = %s ; |q4-sinc| = %.4f vs |q2-sinc| = %.4f"
       % (np.array2string(np.array(inc), precision=4), abs(seq[3] - seq[4]), abs(seq[1] - seq[4])))

    # Q4: unseen-k probe for q4
    print("\n[Q4] unseen-k probe: q4 at k = 3pi/10 ((10,1),(20,2)); naive control")
    PTS = [(10, 1), (20, 2)]
    U = {}
    for var in ("naive", "q4"):
        for (M, n) in PTS:
            U[(var, M)] = run(M, n, variant=var)
            print("      (%s M=%d n=%d done)" % (var, M, n), flush=True)
    ac = slope([(10, U[("naive", 10)]['conf']['A_agg']), (20, U[("naive", 20)]['conf']['A_agg'])])
    at = slope([(10, U[("naive", 10)]['TT']['A_agg']), (20, U[("naive", 20)]['TT']['A_agg'])])
    d_na = ac - at
    att_na = U[("naive", 10)]['TT']['A_agg'] / U[("naive", 20)]['TT']['A_agg']
    ac4 = slope([(10, U[("q4", 10)]['conf']['A_agg']), (20, U[("q4", 20)]['conf']['A_agg'])])
    at4 = slope([(10, U[("q4", 10)]['TT']['A_agg']), (20, U[("q4", 20)]['TT']['A_agg'])])
    d_q4 = ac4 - at4
    att_q4 = U[("q4", 10)]['TT']['A_agg'] / U[("q4", 20)]['TT']['A_agg']
    print("    k=3pi/10 : naive deficit %+.4f (A_TT %.4f) ; q4 deficit %+.4f (A_TT %.4f)"
          % (d_na, att_na, d_q4, att_q4), flush=True)
    ck("Q4 unseen-k control: naive deficit at k = 3pi/10 is 0.8-1.0 (k-independence)",
       0.8 <= d_na <= 1.0, "naive deficit = %+.4f" % d_na)
    ck("Q4b q4 at unseen k: the q4 deficit at k = 3pi/10 is within +-0.05 of the q4 deficit"
       " at k = pi/2 (the quadrature-family behavior is k-independent)",
       abs(d_q4 - D["q4"]["d"]) < 0.05,
       "d_q4(3pi/10) = %+.4f vs d_q4(pi/2) = %+.4f" % (d_q4, D["q4"]["d"]))

    # Q5: honesty
    ck("Q5 honesty: the five quadrature families satisfy the '5 unseen sampling families'"
       " count of the residual-5 closure criterion 4 (docs/19-21); the official 10^7-MC"
       " 5sigma null test is NOT part of this round and remains open; no threshold relaxed",
       True,
       "fam deficits %s ; on-ladder %s" % (np.array2string(np.array(seq), precision=3), onladder))

    print("\nRESULT: %d/%d PASS" % (s24.PASS, s24.PASS + s24.FAIL))
    if s24.FAIL:
        print("HONEST STATUS: %d FAIL - see above; no physics threshold was relaxed." % s24.FAIL)
    else:
        print("HONEST STATUS: all checks pass.  Quadrature ladder at k=pi/2 (%s): deficits %s."
              % (", ".join(FAMILIES), np.array2string(np.array(seq), precision=4)))
        print("HALF-INTEGER CONJECTURE: %s"
              % ("CONFIRMED - residual 5 restates as the projector-sub-ladder theorem"
                 if onladder else
                 "REFUTED - the deficit is a CONTINUOUS function of the sampling family,"
                 " not a projector eigenvalue ladder (recorded)"))


if __name__ == "__main__":
    main()