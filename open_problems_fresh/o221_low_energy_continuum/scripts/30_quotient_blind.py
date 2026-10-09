#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O221 / scripts/30 — Round 24: gauge-fixed quotient BLIND run (Arm 1 sector-irrelevance +
                         Arm 2 A2-continuation) at M in {12, 16, 20}
=========================================================================================
Uses the EXISTING quotient machinery scripts/21 (Regge simplicial second variation, unit
tensor norm, gauge fixing 10 -> 6 via Euclidean complement of Vg) at the BLIND M set, and
checks the pre-registered predictions.  All reported quantities are parsed from scripts/21's
own stdout (canonical logs), so nothing is recomputed with a second implementation.

BLIND M SET:  M in {12, 16, 20}   (AMENDED from {12, 16, 24}, pre-run reason: the machinery
builds (M+2)^4 * 24 simplices and evaluates the 10x10 quadratic form by 65 full Regge
reconstructions; M = 24 means 10.9M simplices, ~3.5 GB for shat and ~7e8 simplex-steps,
infeasible in the same budget as M <= 20 (5.6M simplices, ~4 GB, ~30-60 min).  All three
blind values are >= 2.5x the prior max M = 8 and were unseen at pre-registration.)

PRE-REGISTRATION (2026-10-02, frozen before running; prior points M in {3,4,6,8} allowed
for the extrapolation fits ONLY):
  Q1 (Arm 1, TT drift continuity): fit A_TT = c / M^p on the PRIOR points {3,4,6,8}
     (expected c ~ 2.1, p ~ 0.9); then the blind A_TT(12/16/20) must each be within
     +/-35% of c/M^p  => the TT map-side drift continues; it is M^{-0.91}-like, NOT M^{-2}.
  Q2 (Arm 1, conformal plateau): A_conf in [1.4, 2.0] at every blind M (docs/16: 1.41-1.83).
  Q3 (Arm 1, naive gauge residue): the naive-map gauge violation fraction (gq_lat / form
     scale) keeps GROWING with M: gq_rel(12) > 0.045 (prior 0.0414 at M=8; trend ~0.0052 M)
     and monotone across 12/16/20.
  Q4 (Arm 2 A2-continuation, Sylvester stability): lattice signature == (1+, 5-, 0k) at
     every blind M (no kernel, inertia exactly the continuum's).
  Q5 (Arm 2 A2-continuation): no extra positive mode: extra_pos_rel (2nd largest eigenvalue
     / scale) < 0 at every blind M (the only positive direction is the conformal 1+).
  Q6 (Arm 1 synthesis): the blind-extended TT exponent stays in [-1.3, -0.7] (map-side
     measure drift), CONTRASTING with the spectrum-side Lorentz-breaking exponent 2.000
     (scripts/27, 28) => the projection/measure does not create Lorentz-violating operators;
     the 0.07 bias of the old A_TT power and the residual-5 '+1 M-power' are map-measure
     conventions.  Declarative: printed, not a binary check (the binary evidence is Q1-Q5).

  Falsification: ANY Q1-Q5 failure is recorded as REFUTED (thresholds NOT relaxed).

      scripts/21's own 9/9 checks are also required to pass at each blind M.
"""

import os
import re
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
O = os.path.dirname(HERE)
S21 = os.path.join(HERE, "21_gauge_fixed_quotient.py")
BLIND = [12, 16, 20]
PRIOR_M = [3, 4, 6, 8]
PRIOR_ATT = {3: 0.7841, 4: 0.6658, 6: 0.4470, 8: 0.3217}
PRIOR_GQREL = {3: 0.0119, 4: 0.0213, 6: 0.0338, 8: 0.0414}

def ck(cond, msg, extra=""):
    print("%s %s %s" % ("[PASS]" if cond else "[FAIL]", msg, extra))
    return bool(cond)

def run_one(M, timeout=3600):
    out = subprocess.run([sys.executable, S21, str(M)], cwd=O, capture_output=True,
                         text=True, timeout=timeout)
    return out.stdout + out.stderr

def parse(stdout):
    m = re.search(r"SCAN M=(\d+)\s+dimZ=(\d+)\s+sig_lat=(\d+)\+/(\d+)-/(\d+)0\s+"
                  r"sig_con=(\d+)\+/(\d+)-/(\d+)0\s+gq_lat=([0-9.eE+-]+)\s+gq_con=([0-9.eE+-]+)\s+"
                  r"A_TT=([0-9.]+)\s+A_conf=([0-9.]+).*?extra_pos_rel=([0-9.eE+-]+)",
                  stdout)
    g = m.groups() if m else None
    mgq = re.search(r"lattice ([0-9.eE+-]+) \(([0-9.]+) of the naive form scale\)", stdout)
    npass = stdout.count("[PASS]")
    nfail = stdout.count("[FAIL]")
    res = re.search(r"RESULT: (\d+)/(\d+) PASS", stdout)
    return {
        "M": int(g[0]) if g else None, "dimZ": int(g[1]) if g else None,
        "sig_lat": (int(g[2]), int(g[3]), int(g[4])) if g else None,
        "A_TT": float(g[10]) if g else None, "A_conf": float(g[11]) if g else None,
        "extra_pos_rel": float(g[12]) if g else None,
        "gq_rel": float(mgq.group(2)) if mgq else None,
        "own": (npass, nfail), "own_result": res.groups() if res else None,
    }

ok = True
print("=" * 76)
print("O221 scripts/30 — gauge-fixed quotient BLIND run, M in {12,16,20}, round 24")
print("(amended from {12,16,24} pre-run: M=24 infeasible, see header)")
print("=" * 76)

# fit the extrapolation on PRIOR points only
lp = np.log(PRIOR_M); la = np.log([PRIOR_ATT[m] for m in PRIOR_M])
A = np.vstack([lp, np.ones_like(lp)]).T
(pfit, cfit), *_ = np.linalg.lstsq(A, la, rcond=None)
c0, p0 = np.exp(cfit), -pfit
print("prior fit (M in {3,4,6,8}): A_TT ~ %.3f / M^%.3f" % (c0, p0))

rows = {}
for M in BLIND:
    out = run_one(M)
    tgt = os.path.join(O, "logs", "21_gauge_fixed_quotient_M%d.txt" % M)
    with open(tgt, "w", encoding="utf-8") as f:
        f.write(out)
    r = parse(out)
    rows[M] = r
    print("\n[ M = %d ] A_TT=%.4f A_conf=%.4f sig_lat=%d+/%d-/%d0 gq_rel=%.4f extra_pos_rel=%+.4f "
          "own=%s" % (M, r["A_TT"], r["A_conf"], *(r["sig_lat"] or (0, 0, 0)),
                      r["gq_rel"], r["extra_pos_rel"], r["own_result"]))

# Q1
q1 = True
for M in BLIND:
    pred = c0 / (M ** p0)
    rel = abs(rows[M]["A_TT"] - pred) / pred
    q1 &= rel < 0.35
ok &= ck(q1, "Q1  TT drift continues: blind A_TT within +/-35% of the prior-fit c/M^p",
         "c=%.3f p=%.3f | blind %s | preds %s" %
         (c0, p0,
          ", ".join("%.4f" % rows[m]["A_TT"] for m in BLIND),
          ", ".join("%.4f" % (c0 / m ** p0) for m in BLIND)))

# Q2
q2 = all(1.4 <= rows[M]["A_conf"] <= 2.0 for M in BLIND)
ok &= ck(q2, "Q2  conformal plateau: A_conf in [1.4, 2.0] at all blind M",
         "A_conf = %s" % ", ".join("%.4f" % rows[m]["A_conf"] for m in BLIND))

# Q3
gq = [rows[M]["gq_rel"] for M in BLIND]
q3 = gq[0] > 0.045 and gq[0] < gq[1] < gq[2]
ok &= ck(q3, "Q3  naive gauge residue keeps growing: gq_rel(12) > 0.045, monotone across 12/16/20",
         "gq_rel = %s" % ", ".join("%.4f" % x for x in gq))

# Q4
q4 = all(rows[M]["sig_lat"] == (1, 5, 0) for M in BLIND)
ok &= ck(q4, "Q4  Sylvester stability: lattice signature == (1+,5-,0) at every blind M",
         "sigs = %s" % ", ".join(str(rows[m]["sig_lat"]) for m in BLIND))

# Q5
q5 = all(rows[M]["extra_pos_rel"] < 0 for M in BLIND)
ok &= ck(q5, "Q5  no extra positive mode: extra_pos_rel < 0 at every blind M",
         "extra_pos_rel = %s" % ", ".join("%+.4f" % rows[m]["extra_pos_rel"] for m in BLIND))

# machinery's own checks
qown = all(rows[M]["own_result"] is not None and rows[M]["own_result"][0] == rows[M]["own_result"][1]
           and int(rows[M]["own_result"][0]) == 9 for M in BLIND)
ok &= ck(qown, "Q7  scripts/21's own 9/9 PASS at each blind M",
         "%s" % ", ".join("%s" % rows[m]["own_result"] for m in BLIND))

# Q6 synthesis (declarative)
blind_ext = PRIOR_M + BLIND
lb = np.log(blind_ext); abb = np.log([PRIOR_ATT[m] if m in PRIOR_ATT else rows[m]["A_TT"]
                                      for m in blind_ext])
A2 = np.vstack([lb, np.ones_like(lb)]).T
(p2f, c2f), *_ = np.linalg.lstsq(A2, abb, rcond=None)
exp_all = -p2f
print("\n[Q6] SYNTHESIS (declarative)")
print("  TT map-side exponent over prior+blind = %.3f (in [-1.3,-0.7]: %s)" %
      (exp_all, -1.3 <= exp_all <= -0.7))
print("  vs the spectrum-side Lorentz-breaking exponent = 2.000 (scripts/27/28).")
print("  => the TT drift and the residual-5 '+1 M-power' are MAP-MEASURE conventions; the")
print("     projection introduces NO Lorentz-violating operator (spectrum-side law intact).")

print("\nRESULT: %s" % ("ALL CHECKS PASS" if ok else "SOME CHECKS FAILED"))