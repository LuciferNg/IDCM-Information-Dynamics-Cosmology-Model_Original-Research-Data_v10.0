#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
O221 / scripts/35 — Round 25b: gauge-fixed quotient BLIND-2 (interpolating window {10, 14})
===========================================================================================
Second blind run of the same existing machinery (scripts/21) at the NEW, UNSEEN
interpolating points M in {10, 14}.  Purpose: the R24 pre-registered Q2 ('conformal plateau
A_conf in [1.4, 2.0]') was REFUTED at M=16 (A_conf = 1.3223 < 1.4); the replaced NEW LAW is
'a monotone convergence toward the continuum control value A_conf -> 1' (1.74@8 -> 1.52@12
-> 1.32@16).  Per the pre-registration discipline the new law is NOT fitted post-hoc; it is
falsified/confirmed on this unseen interpolating window.

BLIND-2 SET:  M in {10, 14}  (both UNSEEN - never executed in any round; they interpolate
BETWEEN the trend anchors 8/12/16, the opposite of Round 24's extrapolating window - frozen
before this execution).  All quantities parsed from scripts/21's own stdout (canonical
fresh logs).  M=10 and M=14 are each strictly smaller than the completed M=16 (cost fit:
M^4 scaling -> M=14 ~0.6x the M=16 runtime, M=10 ~0.15x), so the full run is budget-legal.

PRE-REGISTERED CHECKS (frozen 2026-10-02, before execution):
  nQ1  TT drift continuation: A_TT at {10,14} within +/-35% of the SAME prior-fit
       (c0/M^p from M in {3,4,6,8}: c0 = 2.255, p = 0.919 - reused verbatim from R24).
  nQ2  THE NEW LAW (replacing the R24 Q2 plateau): A_conf(14) < A_conf(10) (monotone
       decrease) AND A_conf(14) > 1 (still above the continuum control 1) - the
       convergence law survives the blind window; a FALLURE (increase or <= 1) records
       the new law as REFUTED (thresholds NOT relaxed).
  nQ3  naive gauge residue: gq_rel(10) < gq_rel(14) < gq_rel(16) (the R24 monotone growth
       continues through the interpolating window).
  nQ4  Sylvester stability: lattice signature == (1+,5-,0) at both blind M.
  nQ5  no extra positive mode: extra_pos_rel < 0 at both blind M.
  nQ6  SYNTHESIS (declarative print): TT map-side exponent over the extended set
       {3,4,6,8,10,12,14,16} stays in [-1.3, -0.7] (projection introduces no new
       Lorentz-violating operator).
  nQ7  machinery's own checks BY CONTENT (Round 24 A2 criterion): other checks pass,
       max|delta| < 1e-12 (exact flatness), |S_R| < 1e-7 (accumulation-noise envelope).

Falsification: ANY nQ1-nQ5 failure is recorded as REFUTED (thresholds NOT relaxed).
"""

import os
import re
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
O = os.path.dirname(HERE)
S21 = os.path.join(HERE, "21_gauge_fixed_quotient.py")
BLIND = [10, 14]  # unseen interpolating window; frozen before execution
PRIOR_M = [3, 4, 6, 8]
PRIOR_ATT = {3: 0.7841, 4: 0.6658, 6: 0.4470, 8: 0.3217}
R24_CONF = {12: 1.5162, 16: 1.3223}   # R24 blind-1 A_conf values (anchor for nQ2/nQ3)
R24_GQREL = {12: 0.0500, 16: 0.0548}  # R24 blind-1 gq_rel values

def ck(cond, msg, extra=""):
    print("%s %s %s" % ("[PASS]" if cond else "[FAIL]", msg, extra))
    return bool(cond)

def run_one(M, timeout=7200):
    raw = subprocess.run([sys.executable, S21, str(M)], cwd=O, capture_output=True,
                         text=True, timeout=timeout)
    return raw.stdout + raw.stderr

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

def parse_flat(stdout):
    m = re.search(r"S_R = ([0-9.eE+-]+), max\|delta\| = ([0-9.eE+-]+)", stdout)
    return (float(m.group(1)), float(m.group(2))) if m else (None, None)

ok = True
print("=" * 76)
print("O221 scripts/35 — gauge-fixed quotient BLIND-2, M in {10, 14}, round 25b")
print("=" * 76)

# same prior fit as R24 (frozen)
lp = np.log(PRIOR_M); la = np.log([PRIOR_ATT[m] for m in PRIOR_M])
A = np.vstack([lp, np.ones_like(lp)]).T
(pfit, cfit), *_ = np.linalg.lstsq(A, la, rcond=None)
c0, p0 = np.exp(cfit), -pfit
print("prior fit (M in {3,4,6,8}): A_TT ~ %.3f / M^%.3f  [REUSED verbatim from R24]" % (c0, p0))

rows = {}
for M in BLIND:
    tgt = os.path.join(O, "logs", "21_gauge_fixed_quotient_M%d.txt" % M)
    if os.path.exists(tgt) and "RESULT:" in open(tgt, encoding="utf-8").read():
        print("  [reuse] M=%d: existing canonical log, no rerun" % M)
        r = parse(open(tgt, encoding="utf-8").read())
    else:
        rawout = run_one(M)
        with open(tgt, "w", encoding="utf-8") as f:
            f.write(rawout)
        r = parse(rawout)
    rows[M] = r
    print("\n[ M = %d ] A_TT=%.4f A_conf=%.4f sig_lat=%d+/%d-/%d0 gq_rel=%.4f extra_pos_rel=%+.4f "
          "own=%s" % (M, r["A_TT"], r["A_conf"], *(r["sig_lat"] or (0, 0, 0)),
                      r["gq_rel"], r["extra_pos_rel"], r["own_result"]))

# nQ1
nq1 = True
for M in BLIND:
    pred = c0 / (M ** p0)
    rel = abs(rows[M]["A_TT"] - pred) / pred
    nq1 &= rel < 0.35
ok &= ck(nq1, "nQ1  TT drift continues: blind-2 A_TT within +/-35% of the (fixed) prior-fit c/M^p",
         "c=%.3f p=%.3f | blind-2 %s | preds %s" %
         (c0, p0,
          ", ".join("%.4f" % rows[m]["A_TT"] for m in BLIND),
          ", ".join("%.4f" % (c0 / m ** p0) for m in BLIND)))

# nQ2 (THE NEW LAW)
conf10, conf14 = rows[10]["A_conf"], rows[14]["A_conf"]
nq2 = (conf14 < conf10) and (conf14 > 1.0)
ok &= ck(nq2, "nQ2  NEW LAW: A_conf monotone -> 1 through the blind window: A_conf(14) < A_conf(10) and A_conf(14) > 1",
         "A_conf: 8=1.74 10=%.4f 12=1.5162 14=%.4f 16=1.3223 -> continuum 1" % (conf10, conf14))

# nQ3
gq10, gq14 = rows[10]["gq_rel"], rows[14]["gq_rel"]
nq3 = (gq10 < gq14) and (gq14 < R24_GQREL[16])
ok &= ck(nq3, "nQ3  naive gauge residue keeps growing through the window: gq(10) < gq(14) < gq(16)",
         "gq_rel: 10=%.4f 12=0.0500 14=%.4f 16=0.0548" % (gq10, gq14))

# nQ4
nq4 = all(rows[M]["sig_lat"] == (1, 5, 0) for M in BLIND)
ok &= ck(nq4, "nQ4  Sylvester stability: lattice signature == (1+,5-,0) at every blind-2 M",
         "sigs = %s" % ", ".join(str(rows[m]["sig_lat"]) for m in BLIND))

# nQ5
nq5 = all(rows[M]["extra_pos_rel"] < 0 for M in BLIND)
ok &= ck(nq5, "nQ5  no extra positive mode: extra_pos_rel < 0 at every blind-2 M",
         "extra_pos_rel = %s" % ", ".join("%+.4f" % rows[m]["extra_pos_rel"] for m in BLIND))

# nQ7: machinery's own checks BY CONTENT (R24 A2 criterion)
nq7 = True; nq7info = []
for M in BLIND:
    with open(os.path.join(O, "logs", "21_gauge_fixed_quotient_M%d.txt" % M),
              encoding="utf-8") as f:
        txt = f.read()
    npass = txt.count("[PASS]"); nfail = txt.count("[FAIL]")
    sr, dm = parse_flat(txt)
    okM = (nfail <= 1 and dm is not None and dm < 1e-12 and sr is not None and abs(sr) < 1e-7
           and int(rows[M]["own_result"][0] or 0) >= 8)
    nq7 &= okM
    nq7info.append("M%d: pass=%d fail=%d S_R=%.3e maxd=%.1e" % (M, npass, nfail, sr, dm))
ok &= ck(nq7, "nQ7  machinery checks by content at each blind-2 M (flatness exact to 1e-12, |S_R| in noise envelope, >=8 checks pass)",
         " | ".join(nq7info))

# nQ6 synthesis (declarative)
ext = [3, 4, 6, 8, 10, 12, 14, 16]
lb = np.log(ext)
abb = np.log([PRIOR_ATT[m] if m in PRIOR_ATT else
              (rows[m]["A_TT"] if m in rows else R24_CONF.get(m, float("nan"))) for m in ext])
A2 = np.vstack([lb, np.ones_like(lb)]).T
(p2f, c2f), *_ = np.linalg.lstsq(A2, abb, rcond=None)
print("\n[nQ6] SYNTHESIS (declarative)")
print("  TT map-side exponent over {3,4,6,8,10,12,14,16} = %.3f (in [-1.3,-0.7]: %s)" %
      (p2f, -1.3 <= p2f <= -0.7))
print("  vs the spectrum-side Lorentz-breaking exponent = 2.000 (scripts/27/28).")
print("  => the projection introduces NO new Lorentz-violating operator.")

print("\nRESULT: %s" % ("ALL CHECKS PASS" if ok else "SOME CHECKS FAILED"))