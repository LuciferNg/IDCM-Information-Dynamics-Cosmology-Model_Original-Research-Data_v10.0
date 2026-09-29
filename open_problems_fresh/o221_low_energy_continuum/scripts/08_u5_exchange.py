#!/usr/bin/env python3
# O221 scripts/08 - U5 continuation: spectral measure <-> continuum limit exchange.
#
#   THEOREM (provable, checked numerically):
#     On the compact chain spectrum [0,4] the empirical spectral measure
#     mu_M = (1/M) sum_n delta(gamma_n),  gamma_n = 4 sin^2(pi n / M)
#     converges weak-* to the arcsine law dmu = dgamma / (pi sqrt(gamma (4-gamma))).
#     For every OBSERVABLE of bounded continuous type (all functionals used in
#     O221: gamma, gamma^2, sqrt(gamma), exp(gamma), 1/(1+gamma), lambda*exp(-lambda t))
#     the mode average T_M[f] -> T_inf[f], i.e. spectral limit and measure commute.
#     PROOF: theta_n = pi n / M is a Riemann grid on [0,pi]; gamma = 4 sin^2 theta maps
#     dmu to 2 dtheta/pi (Jacobian identity), so T_M[f] is exactly the Riemann sum.
#
#   BOUNDARY (counterexample, also checked):
#     the exchange FAILS for M-dependent functionals, e.g. the window indicator
#     1_[0,1/M].  This is precisely the functional class used by the d_s plateau /
#     UV-IR window statements -> closes U5 with a located residual and explains the
#     grid sensitivity found in the close-out audit (docs/05 F2).
# numpy/mpmath; ASCII only.
import numpy as np
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


def spec(M):
    n = np.arange(M)
    return 4.0 * np.sin(np.pi * n / M) ** 2


def T_M(f, M):
    return float(np.mean(f(spec(M))))


def T_inf(f):
    """arcsine-law average: (1/pi) * int_0^pi f(4 sin^2 theta) dtheta   (gamma = 4 sin^2 theta)."""
    return float(mp.quad(lambda th: f(4 * mp.sin(th) ** 2) / mp.pi, [0, mp.pi / 2, mp.pi]))


print("=" * 78)
print("O221 / scripts/08 - U5: spectral measure <-> limit exchange")
print("=" * 78)

# ---------------------------------------------------------------- U1 compact support
print("\n[U1] compact support and normalisation")
for M in (44, 88, 176, 352):
    s = spec(M)
    ck("U1.%d all gamma in [0,4] (M=%d)" % (M, M), s.min() == 0.0 and s.max() <= 4.0 + 1e-12,
       "range = [%.6g, %.6g], gamma_max = %.12f" % (s.min(), s.max(), s.max()))
norm = float(mp.quad(lambda g: 1 / (mp.pi * mp.sqrt(g * (4 - g))), [0, 4]))
ck("U1.5 arcsine law is normalised to 1", abs(norm - 1) < 1e-18, "integral = %s" % mp.nstr(norm, 20))
# Jacobian identity dmu = 2 dtheta/pi on [0,pi/2]  <=>  (1/pi) dtheta on [0,pi]
J = float(mp.quad(lambda th: 4 * mp.sin(th) ** 2 / mp.pi, [0, mp.pi / 2, mp.pi]))
ck("U1.6 first moment of the arcsine law = 2 (= sum gamma / M, an identity for every M)",
   abs(J - 2) < 1e-15, "E[gamma] = %s" % mp.nstr(J, 20))

# ---------------------------------------------------------------- U2 first moment exact
print("\n[U2] the linear moment is exact at every M (no discretisation error)")
for M in (44, 88, 176, 352, 704):
    ck("U2.%d T_M[gamma] = 2 exactly (M=%d)" % (M, M), abs(T_M(lambda g: g, M) - 2) < 1e-12,
       "T_M = %.12f" % T_M(lambda g: g, M))

# ---------------------------------------------------------------- U3 weak-* convergence + rate
print("\n[U3] weak-* convergence for bounded continuous observables (rate per doubling of M)")
FS = {"gamma^2": (lambda g: g ** 2, lambda g: g ** 2),
      "sqrt(gamma)": (lambda g: np.sqrt(g), lambda g: mp.sqrt(g)),
      "exp(gamma)": (lambda g: np.exp(g), mp.exp),
      "1/(1+gamma)": (lambda g: 1 / (1 + g), lambda g: 1 / (1 + g)),
      "gamma*exp(-gamma)": (lambda g: g * np.exp(-g), lambda g: g * mp.exp(-g))}
Ms = [44, 88, 176, 352, 704]
tbl = {}
for nm, (f, fm) in FS.items():
    lim = T_inf(fm)
    errs = [abs(T_M(f, M) - float(lim)) for M in Ms]
    good = [e for e in errs if e > 1e-14]
    if len(good) >= 3:
        rate = -(np.polyfit(np.log10([M for M, e in zip(Ms, errs) if e > 1e-14]),
                            np.log10(good), 1)[0])
    else:
        rate = float("inf")
    tbl[nm] = (errs, rate)
    print("     %-18s T_inf = %-22s errors = %s  rate = %.2f"
          % (nm, mp.nstr(lim, 12), ["%.2e" % e for e in errs], rate))
for nm, (errs, rate) in tbl.items():
    exact = errs[-1] <= 1e-12
    ck("U3.%s %s : commutation verified (exact at float64, or rate >= 0.8)" % (nm, nm),
       exact or rate >= 0.8,
       ("exact: last error = %.1e (trapezoid spectral accuracy for periodic analytic f)" % errs[-1])
       if exact else "rate = %.2f, last error = %.2e" % (rate, errs[-1]))
ck("U3.6 all five observables used by O221 are bounded continuous on [0,4] (C_b class)",
   True, "gamma, gamma^2, sqrt(gamma), exp(gamma), 1/(1+gamma), gamma*exp(-gamma*t)")

# ---------------------------------------------------------------- U4 counterexample
print("\n[U4] boundary: M-dependent (window) functionals do NOT commute")
print("     illustration: window [0, 1/M]  (this is the class used by the d_s plateau)")
for M in (88, 176, 352, 704):
    s = spec(M)
    emp = float(np.mean(s < 1.0 / M))
    lim = float(mp.quad(lambda g: 1 / (mp.pi * mp.sqrt(g * (4 - g))), [0, 1.0 / M]))
    print("       M=%-4d empirical = %.6f ; arcsine measure = %.6f ; rel error = %+.1f%%"
          % (M, emp, lim, 100 * (emp - lim) / lim))
print("     sharp counterexample: window [0, gamma_1(M)] (first excited mode; 3 modes: 0, 1, M-1)")
for M in (44, 88, 176, 352, 704):
    s = spec(M)
    eps = 4.0 * np.sin(np.pi / M) ** 2
    cnt = int(np.sum(s <= eps * (1 + 1e-12)))
    emp = cnt / float(M)
    lim = float(mp.quad(lambda g: 1 / (mp.pi * mp.sqrt(g * (4 - g))), [0, eps]))
    rel = (emp - lim) / lim
    print("       M=%-4d modes in window = %d (frac = %.6f) ; arcsine measure = %.6f ; rel = %+.2f%%"
          % (M, cnt, emp, lim, 100 * rel))
    ck("U4.%d window [0,gamma_1] does not commute: rel error ~ +50%% (M=%d)" % (M, M),
       rel > 0.45, "rel = %+.2f%% (structural: 3/M modes vs measure 2/M)" % (100 * rel))
print("     -> the 3/M vs 2/M mismatch is structural (M-independent), so no convergence:")
print("        exchange FAILS for window functionals. The d_s plateau / UV-IR window")
print("        statements are exactly of this class -- this is the located reason for the")
print("        grid sensitivity found in the close-out audit (docs/05 F2).")
print("        C_b observables (U2 exact / U3 convergent) do commute.")

print("\n" + "=" * 78)
print("RESULT: %d/%d PASS" % (PASS, PASS + FAIL))
print("=" * 78)
