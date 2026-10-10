#!/usr/bin/env python3
# O189 scripts/08b - EPS-CHL RADIUS LAW v2 (re-pre-registered AFTER v1 REFUTED)
#
# v1 (scripts/08, 2026-10-10) FAILED 0/4: pre-registered prefactor C=1.432
#   overshot; the law r-2t = 1.432 (ln 1/e)^{2/3} t^{1/3} was a mis-derivation
#   (tanh a - a series error: -2/3 sqrt2 not -7/12 sqrt2 AND missing the
#   prefactor log -(1/2) ln t inside the bracket).  v1 log preserved as FAIL.
#
# v2 DERIVED law (corrected, pre-registered BEFORE this run - no fitting):
#   Debye tail: |J_d(2t)| ~ (2 pi d tanh a)^-1/2 e^{d(tanh a - a)}, a=arccosh(d/2t)
#   with tanh a - a = -(2/3) sqrt2 delta^{3/2} + O(delta^{5/2}), delta = d/2t - 1.
#   Level equation (d - 2t) = 2t delta:
#        (4/3) sqrt2 t delta^{3/2} = ln(1/e) - (1/2) ln t - (1/4) ln delta
#                                    - (1/2) ln(4 pi sqrt2)  +  O(1)
#   =>  r_e(t) = 2t + C_eff(e,t) (ln 1/e)^{2/3} t^{1/3},
#        C_eff = C0 [1 - (1/2)(ln t)/(ln 1/e)]^{2/3},   C0 = 2(3/(4 sqrt2))^{2/3}
#              = 1.3106...   (0.5 ln t term dominates the bracket correction)
#   Regimes: coarse eps (1e-2) is PEAKS-LIMITED (edge set by last transition
#   layer oscillation) - NOT covered by the tail law; tested set eps <= 1e-4.
#
# BLIND WINDOWS (set from the derivation before run):
#   WA  ratio := (r-2t)/(C_eff (ln 1/e)^{2/3} t^{1/3}) in (0.70, 1.35)
#       for ALL cells eps in {1e-4,1e-6,1e-9}, t in {320,640,1280}
#   WB  same ratio at the most asymptotic cell (1e-9, 1280) in (0.90, 1.30)
#   WC  prefactor honesty: |J_{d*}(2t)|/eps at formula-d* (1e-9,1280)
#       in (0.03, 8)   [prefactor uncertainty: Debye constant vs Airy constant]
#
# Outputs: stdout [PASS]/[FAIL], data/08b_eps_chl_law_v2.json
import json
import mpmath as mp

mp.mp.dps = 30
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

print("=" * 78)
print("O189 / scripts/08b - eps-CHL radius law v2 (v1 REFUTED, corrected law)")
print("=" * 78)

import math
C0 = 2 * (3 / (4 * math.sqrt(2))) ** (2 / 3)
print("  C0 = 2(3/(4 sqrt2))^{2/3} = %.6f" % C0)

def C_eff(y, t):
    return C0 * (1 - 0.5 * math.log(t) / y) ** (2 / 3)

def r_eps(t, eps):
    d = 2 * t
    r = 2 * t
    below = 0
    while below < 20 and d < 30 * t:
        v = abs(mp.besselj(int(d), 2 * t))
        if v >= eps:
            r = int(d)
            below = 0
        else:
            below += 1
        d += 1
    return r

EPSES = ["1e-4", "1e-6", "1e-9"]
Ts = [320, 640, 1280]

data = {}
okWA = okWB = okWC = True
table = []
for es in EPSES:
    eps = mp.mpf(es)
    y = float(mp.log(1 / eps))
    row = {}
    for t in Ts:
        r = r_eps(t, eps)
        ceff = C_eff(y, t)
        pred = ceff * y ** (2 / 3) * t ** (1 / 3)
        ratio = (r - 2 * t) / pred
        row[str(t)] = {"r": r, "dmin2t": r - 2 * t, "ratio": round(ratio, 3)}
        if not (0.70 < ratio < 1.35):
            okWA = False
        table.append((es, t, r - 2 * t, round(ratio, 3)))
    data[es] = row

# WB: most asymptotic cell
wb_val = data["1e-9"]["1280"]["ratio"]
if not (0.90 < wb_val < 1.30):
    okWB = False

# WC: prefactor honesty at (1e-9, 1280)
y = float(mp.log(1e9))
t = 1280
ceff = C_eff(y, t)
d_star = int(2 * t + ceff * y ** (2 / 3) * t ** (1 / 3))
lev = abs(mp.besselj(d_star, 2 * t))
wc_ratio = float(lev / mp.mpf("1e-9"))
if not (0.03 < wc_ratio < 8):
    okWC = False

ck("WA ratio in (0.70, 1.35) for all eps in {1e-4,1e-6,1e-9}, t in {320,640,1280}",
   okWA, str(table))
ck("WB ratio at (1e-9, 1280) in (0.90, 1.30): %.3f" % wb_val, okWB)
ck("WC |J_{d*}(2560)|/eps at formula-d* (=%d) in (0.03, 8): %.3f"
   % (d_star, wc_ratio), okWC)

res = {"C0": C0, "law": "r_e(t) = 2t + C0[1 - 0.5 ln t / ln(1/e)]^{2/3} (ln 1/e)^{2/3} t^{1/3}",
       "windows": {"WA": "(0.70,1.35)", "WB": "(0.90,1.30)", "WC": "(0.03,8)"},
       "data": data, "prefactor_check": {"d_star": d_star, "J_over_eps": wc_ratio}}
with open("data/08b_eps_chl_law_v2.json", "w") as f:
    json.dump(res, f, indent=2)
print("\nJSON written: data/08b_eps_chl_law_v2.json")
print("=" * 78)
print("RESULT: %d PASS / %d FAIL" % (PASS, FAIL))
raise SystemExit(1 if FAIL else 0)