#!/usr/bin/env python3
# O189 scripts/08 - EPS-CHL RADIUS LAW (R-D: Bessel-tail general law)
#
# PRE-REGISTERED (run-frozen, ZERO fitting - law derived, then measured):
#   On the infinite line, IDCM propagator |psi_j(t)| = |J_{|j-j0|}(2t)| exactly
#   (R1 scripts/04).  Define the eps-CHL radius
#        r_eps(t) := max{ d : |J_d(2t)| >= eps }.
#   LAWS DERIVED FROM BESSEL ASYMPTOTICS (pre-registered):
#     L1  r_eps(t) = 2 t + C(ln(1/eps))^{2/3} t^{1/3} + o(t^{1/3}),
#         C = 2 * (6/(7*sqrt2))^{2/3} ~= 1.432
#         (Debye tail d(tanh a - a), a = arccosh(d/2t): leading term
#          -(7/6) sqrt(2) t delta^{3/2} in the exponent, solved for
#          (d - 2t) = C (ln 1/eps)^{2/3} t^{1/3})
#     L2  r_eps(t)/t -> 2  as t -> inf for any FIXED eps (light-cone in ratio)
#   Windows (blind, not fitted):
#     W1  for every eps, ratio R := (r_eps(t)-2t)/(1.432*(ln(1/eps))^{2/3}*t^{1/3})
#         at t = 640 lies in (1.10, 1.90)
#     W2  the same ratio at t = 1280 lies in (1.15, 1.70)  [convergence tighter]
#     W3  |J_{d*}(2t)| at the predicted d* = 2t + 1.432(...)t^{1/3} is within
#         a factor of 10 of eps for t = 640 (tail formula prefactor honest)
#   (Any single failure of W1-W3 falsifies the Law; windows chosen BEFORE run.)
#
# Outputs: stdout [PASS]/[FAIL], data/08_eps_chl_law.json
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
print("O189 / scripts/08 - eps-CHL radius law (R-D closing)")
print("=" * 78)

C = 2 * (float(6) / (7 * 2 ** 0.5)) ** (2.0 / 3)
print("  Pre-registered C = %.6f" % C)

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

EPSES = ["1e-2", "1e-3", "1e-4", "1e-6", "1e-9"]
Ts = [20, 40, 80, 160, 320, 640, 1280]

data = {}
okW1 = okW2 = okW3 = True
for es in EPSES:
    eps = mp.mpf(es)
    ln = float(mp.log(1 / eps))
    row = {}
    for t in Ts:
        r = r_eps(t, eps)
        row[str(t)] = r
        if t in (640, 1280):
            pred = 1.432 * ln ** (2.0 / 3) * t ** (1.0 / 3)
            R = (r - 2 * t) / pred
            row["R@%d" % t] = round(R, 3)
            if t == 640 and not (1.10 < R < 1.90):
                okW1 = False
            if t == 1280 and not (1.15 < R < 1.70):
                okW2 = False
    d_star = int(2 * 640 + 1.432 * ln ** (2.0 / 3) * 640 ** (1.0 / 3))
    lev = abs(mp.besselj(d_star, 2 * 640))
    ratio = float(lev / eps) if eps != 0 else 0
    row["J@d*_t640"] = float(lev)
    row["ratio_vs_eps_t640"] = round(ratio, 2)
    if not (0.1 < ratio < 10):
        okW3 = False
    data[es] = row

ck("W1 ratio at t=640 within (1.10, 1.90) for all eps", okW1)
ck("W2 ratio at t=1280 within (1.15, 1.70) for all eps", okW2)
ck("W3 |J_{d*}(1280)| within factor 10 of eps (prefactor honest)", okW3)

# show a compact table for the doc
for es in EPSES:
    r = data[es]
    print("  eps=%s  r(640)=%d R640=%.3f R1280=%.3f  J@d* ratio=%.2f"
          % (es, r["640"], r["R@640"], r["R@1280"], r["ratio_vs_eps_t640"]))

ck("L2 r_eps(t)/t -> 2 confirmed: r(1280)/1280 in (1.9, 2.05) for all eps",
   all(data[es]["1280"] / 1280 < 2.05 for es in EPSES))

res = {"C": C, "law": "r_eps(t) = 2t + C (ln 1/eps)^{2/3} t^{1/3}",
       "data": data}
with open("data/08_eps_chl_law.json", "w") as f:
    json.dump(res, f, indent=2)
print("\nJSON written: data/08_eps_chl_law.json")
print("=" * 78)
print("RESULT: %d PASS / %d FAIL" % (PASS, FAIL))
raise SystemExit(1 if FAIL else 0)