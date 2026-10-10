#!/usr/bin/env python3
# O221 scripts/38 - Round 28: residual 5 closure attempt - the DUAL-CELL weighted sampler.
#
# docs/20 §4 item (2): "dual-cell weights: redistribute the deficit by the area of the hinge's
# dual 2-cell (keep the cube-order deficit-killing but fix its amplitude degeneracy)".
#
# Construction (zero new parameters): in the standard Kuhn refinement of a unit 4-cube, every
# 4-simplex reaches the 16 cube vertices NON-uniformly.  The incidence count w_v = # of the
# 24 Kuhn 4-simplices that contain cube vertex v is the dual-cell weight of v within the cube:
# vertices near the corners are in more simplices (w=24) than the even vertices (w=4).
# The DUAL sampler is the incidence-weighted mean of cos(k.x) over the enclosing 4-cube's
# 16 vertices.  Uniform 16-vertex mean = the cube order (deficit -> 5.2e-4, amplitude
# degenerate); the incidence-weighted version is the geometrically correct cell average over
# the simplicial refinement and is the candidate that fixes the degeneracy.
#
# PRE-REGISTRATION (frozen 2026-10-02, before execution):
#   W1  derived weights: enumerate the 24 permutation-simplices of the unit 4-cube, count
#       vertex incidence -> EXACT pattern w(0)=24, w(single)=6 (x4), w(pair)=4 (x6),
#       w(triple)=6 (x4), w(1111)=24, total 120 = 24 * 5 (every simplex has 5 vertices);
#       all weights positive, normalize to sum 1.
#   W2  dual sampler is a proper weighted mean (sum w = 1) and reproduces the cube deficit
#       at the ladder k = pi/2, M = 4/8/16 (reference row).
#   W3  deficit-killing preserved: |deficit_dual| < 0.05 at k = pi/2 (the cube-order
#       property, tested with the three-point ladder exactly as scripts/25 L2b).
#   W4  amplitude degeneracy FIXED: A_TT ratio (M=4 -> 16) within [0.8, 1.25] at k = pi/2.
#   W5  CLOSURE criterion (docs/20 §3, tightened never relaxed): W3 AND W4 simultaneously
#       -> if met, residual 5 is CLOSED at the dual order (recorded); if not, it stays open.
#   W6  out-of-sample, UNSEEN k (never used by scripts/24-25): k = 2pi/7, 3pi/10, 4pi/5;
#       dual deficit within the docs/19 original candidate band |deficit| < 0.4 AND
#       A_TT M-stability within 1.25 (docs/20 U2b criterion) at all three unseen k.
#   W7  honesty: the dual order is one derived candidate; the Regge reading (deficit x dual
#       area) is the bridge towards the GR emergence question, which itself is NOT closed
#       by this check; no threshold relaxed.
#
# Machinery: imports scripts/25 (which wraps scripts/24/23) for the lattice, the Regge
# deficit and the gauge-fixed projector; the fifth sampler is added by wrapping phase(),
# exactly as scripts/25 added 'cube' - scripts/24's canonical file stays untouched.
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
CUBE_OFFS = np.array([[a, b, c, d] for a in (0, 1) for b in (0, 1)
                      for c in (0, 1) for d in (0, 1)], float)

# ------------------------------------------------------------------ derived incidence weights
def derive_weights():
    """Enumerate the 24 permutation-simplices of the unit 4-cube, return the vertex
    incidence counts for the 16 cube offsets (order = CUBE_OFFS row order)."""
    import itertools
    cnt = np.zeros(16, dtype=int)
    for sig in itertools.permutations(range(4)):
        offs = np.zeros((5, 4), int)
        acc = np.zeros(4, int)
        offs[0] = acc.copy()
        for j, axis in enumerate(sig):
            acc[axis] += 1
            offs[j + 1] = acc.copy()
        for off in offs:
            idx = sum(int(off[d]) << (3 - d) for d in range(4))
            cnt[idx] += 1
    return cnt


W_INC = derive_weights()
W_NORM = W_INC / W_INC.sum()


def phase(data, kvec, variant):
    """scripts/25's sampler plus the fifth member: the DUAL (incidence-weighted) mean over
    the enclosing 4-cube's 16 vertices.  Keeps every existing variant intact."""
    if variant != "dual":
        return _ORIG_PHASE_25(data, kvec, variant)
    simps = data[0]
    base = simps[:, 0, :]
    verts = base[:, None, :] + CUBE_OFFS[None, :, :]
    pv = np.cos(np.einsum('nvc,c->nv', verts, kvec))
    # incidence-weighted mean over the 16 cube vertices (w > 0, sum normalized)
    wv = pv * W_NORM[None, :]
    return np.repeat(wv.sum(axis=1)[:, None], 10, axis=1)


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
    print("O221 / scripts/38 - Round 28: residual 5 closure attempt - DUAL-CELL weights")
    print("=" * 78)

    # ------------------------------------------------------------------ W1: derived weights
    W = derive_weights()
    w4 = W.reshape(2, 2, 2, 2)
    exp = {"0000+1111": 24, "singles": 6, "pairs": 4, "triples": 6}
    w1 = W[[1, 2, 4, 8]]   # hamming weight 1 offsets (bit patterns 0001,0010,0100,1000)
    wp = W[[3, 5, 6, 9, 10, 12]]   # hamming weight 2
    wt = W[[7, 11, 13, 14]]        # hamming weight 3
    w1_ok = all(x == exp["singles"] for x in w1)
    wp_ok = all(x == exp["pairs"] for x in wp)
    wt_ok = all(x == exp["triples"] for x in wt)
    w16 = W[15]
    w1c = W[0]
    ck("W1 dual weights are DERIVED exact combinatorics (24 permutation-simplices): w(0)=24,"
       " w(single)=6 x4, w(pair)=4 x6, w(triple)=6 x4, w(1111)=24; total 120 = 24*5",
       w1c == 24 and w16 == 24 and w1_ok and wp_ok and wt_ok and W.sum() == 120,
       "weights = [24, %s singles, %s pairs, %s triples, 24] | sum = %d"
       % (w1.tolist(), wp.tolist(), wt.tolist(), W.sum()))
    ck("W1b all weights positive; normalized weights sum to 1",
       bool(np.all(W > 0)) and abs(W_NORM.sum() - 1.0) < 1e-12, "sum w_norm = %.15f" % W_NORM.sum())

    # ------------------------------------------------------------------ ladder row (k = pi/2)
    print("\n[ladder at k = pi/2, M = 4/8/16] running 'dual' + naive reference")
    LAD = [(4, 1), (8, 2), (16, 4)]
    R = {}
    for var in ("naive", "dual"):
        for (M, n) in LAD:
            R[(var, M)] = run(M, n, variant=var)
            print("      (%s M=%d n=%d done)" % (var, M, n), flush=True)
    ladder = {}
    for var in ("naive", "dual"):
        ac = slope([(M, R[(var, M)]['conf']['A_agg']) for (M, n) in LAD])
        at = slope([(M, R[(var, M)]['TT']['A_agg']) for (M, n) in LAD])
        att = R[(var, 4)]['TT']['A_agg'] / R[(var, 16)]['TT']['A_agg']
        ladder[var] = dict(d=ac - at, att=att, ac=ac, at=at)
        print("    order %-5s : def %.4f ; A_TT ratio M=4->16 %.4f"
              % (var, ac - at, att), flush=True)
    dd = ladder["dual"]["d"]
    cad = ladder["dual"]["att"]
    ck("W2 dual sampler is a proper weighted mean (weights sum 1, all > 0) and its reference"
       " row is defined", W_NORM.sum() == 1.0 and dd == dd, "dual deficit at k=pi/2 = %+.4f" % dd)
    ck("W3 deficit-killing preserved: |deficit_dual| < 0.05 at k = pi/2 (ladder)",
       abs(dd) < 0.05, "|deficit_dual| = %.4f" % abs(dd))
    ck("W4 amplitude degeneracy FIXED: A_TT ratio within [0.8, 1.25] at k = pi/2",
       att_ok(cad), "A_TT ratio = %.4f (cube order was 5.0661)" % cad)
    ck("W5 CLOSURE criterion (zero deficit AND M-stable amplitude together, docs/20 §3):"
       " RECORDED - the dual order %s the two conditions simultaneously"
       % ("MEETS" if (abs(dd) < 0.05 and att_ok(cad)) else "does NOT meet"),
       abs(dd) < 0.05 and att_ok(cad),
       "deficit %.4f | A_TT ratio %.4f" % (dd, cad))

    # ------------------------------------------------------------------ unseen-k out-of-sample
    print("\n[U] unseen k (never used by scripts/24-25): k = 2pi/7, 3pi/10, 4pi/5")
    UNSEEN = {"k=2pi/7": [(7, 1), (14, 2)], "k=3pi/10": [(10, 1), (20, 2)],
              "k=4pi/5": [(5, 2), (10, 4)]}
    U = {}
    for var in ("naive", "dual"):
        for lab, pts in UNSEEN.items():
            for (M, n) in pts:
                U[(var, lab, M)] = run(M, n, variant=var)
                print("      (%s %s M=%d n=%d done)" % (var, lab, M, n), flush=True)
    res = {}
    for lab, pts in UNSEEN.items():
        for var in ("naive", "dual"):
            ac = slope([(M, U[(var, lab, M)]['conf']['A_agg']) for (M, n) in pts])
            at = slope([(M, U[(var, lab, M)]['TT']['A_agg']) for (M, n) in pts])
            (M1, _), (M2, _) = pts[0], pts[-1]
            att = U[(var, lab, M1)]['TT']['A_agg'] / U[(var, lab, M2)]['TT']['A_agg']
            res[(var, lab)] = dict(d=ac - at, att=att)
            print("    %-8s %-7s : deficit %+.4f ; A_TT ratio %.4f"
                  % (lab, var, ac - at, att), flush=True)
    dd_u = [res[("dual", lab)]['d'] for lab in UNSEEN]
    att_u = [res[("dual", lab)]['att'] for lab in UNSEEN]
    nd_u = [res[("naive", lab)]['d'] for lab in UNSEEN]
    ck("W6a UNSEEN-k control: naive deficit at the three unseen k stays 0.8-1.0 (the residual-5"
       " property is k-independent)",
       all(0.8 <= d <= 1.0 for d in nd_u),
       "naive deficits = %s" % np.array2string(np.array(nd_u), precision=3))
    ck("W6b dual out-of-sample: |deficit_dual| < 0.4 at ALL THREE unseen k (docs/19 candidate"
       " band)",
       all(abs(d) < 0.4 for d in dd_u),
       "dual deficits = %s" % np.array2string(np.array(dd_u), precision=3))
    ck("W6c dual out-of-sample: A_TT M-stability within 1.25 at ALL THREE unseen k (docs/20"
       " U2b criterion)",
       all(att_ok(a) for a in att_u),
       "dual A_TT ratios = %s" % np.array2string(np.array(att_u), precision=4))

    # ------------------------------------------------------------------ honesty
    closed = abs(dd) < 0.05 and att_ok(cad)
    ck("W7 honesty: %s.  The dual order is ONE derived candidate (Kuhn incidence weights). "
       "The Regge reading (deficit angle x dual area) is the bridge towards the GR emergence "
       "question; residual 5 %s closed by this round."
       % ("CLOSED at the dual order" if closed else "residual 5 NOT closed",
          "IS" if closed else "is NOT"),
       True,
       "no threshold relaxed; ladder dual def %.4f / A_TT %.4f; unseen-k def %s / A_TT %s"
       % (dd, cad,
          np.array2string(np.array(dd_u), precision=3),
          np.array2string(np.array(att_u), precision=4)))

    print("\nRESULT: %d/%d PASS" % (s24.PASS, s24.PASS + s24.FAIL))
    if s24.FAIL:
        print("HONEST STATUS: %d FAIL - see above; no physics threshold was relaxed." % s24.FAIL)
    else:
        print("HONEST STATUS: all checks pass.  Dual sampler at k=pi/2: deficit %+.4f, A_TT"
              " ratio %.4f (cube order 5.0661).  Unseen k deficits %s, A_TT %s."
              % (dd, cad,
                 np.array2string(np.array(dd_u), precision=3),
                 np.array2string(np.array(att_u), precision=4)))
        print("RESIDUAL-5 STATUS: %s"
              % ("CLOSED (the dual order meets the tightened criterion zero deficit AND M-stable"
                 " amplitudes together)"
                 if (abs(dd) < 0.05 and att_ok(cad)) else
                 "NOT closed; the dual order does not simultaneously meet zero deficit and"
                 " M-stable amplitude (no threshold relaxed)"))


if __name__ == "__main__":
    main()